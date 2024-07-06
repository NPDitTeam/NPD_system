import re
import os
import base64
import pytz
import zipfile
import calendar
import logging
import threading

from io import BytesIO
from dateutil import rrule
from requests import get
from datetime import timedelta, datetime, time, date
from requests.exceptions import SSLError, ConnectionError
from PIL import Image, ImageChops
from functools import wraps
from psycopg2 import sql

from odoo import models, fields, _, api, registry
from odoo.exceptions import UserError, ValidationError
from odoo.tools import remove_accents, date_utils, relativedelta, config
from odoo.models import PREFETCH_MAX

from ..controllers.my_ip import MY_IP_ROUTE

_logger = logging.getLogger(__name__)


def after_commit(func):
    """
    Decorator to add some custom tasks after things are commit (and cursor is closed)
    """

    @wraps(func)
    def wrapped(self, *args, **kwargs):
        dbname = self.env.cr.dbname
        context = self.env.context
        uid = self.env.uid

        @self.env.cr.postcommit.add
        def called_after():
            db_registry = registry(dbname)
            with api.Environment.manage(), db_registry.cursor() as cr:
                env = api.Environment(cr, uid, context)
                try:
                    func(self.with_env(env), *args, **kwargs)
                except Exception as e:
                    _logger.warning("Could not sync record now: %s" % self)
                    _logger.exception(e)

    return wrapped


class TOBase(models.AbstractModel):
    _name = 'to.base'
    _description = 'TVTMA Base Model'

    def barcode_exists(self, barcode, model_name=None, barcode_field='barcode', inactive_rec=True):
        """
        Method to check if the barcode exists in the input model

        :param barcode: the barcode to check its existance in the model
        :param model_name: The technical name of the model to check. For example, product.template, product.product, etc. If not passed, the current model will be used
        :param barcode_field: the name of the field storing barcode in the corresponding model
        :param inactive_rec: search both active and inactive records of the model for barcode existance check. Please pass False for this arg if the model does not have active field

        :return: Boolean
        """
        Object = self.env[model_name] if model_name else self
        domain = [(barcode_field, '=', barcode)]
        if inactive_rec:
            found = Object.with_context(active_test=False).search(domain)
        else:
            found = Object.search(domain)
        if found:
            return True
        return False

    def get_ean13(self, base_number):
        if len(str(base_number)) > 12:
            raise UserError(_("Invalid input base number for EAN13 code"))
        # weight number
        ODD_WEIGHT = 1
        EVEN_WEIGHT = 3
        # Build a 12 digits base_number_str by adding 0 for missing first characters
        base_number_str = '%s%s' % ('0' * (12 - len(str(base_number))), str(base_number))
        # sum_value
        sum_value = 0
        for i in range(0, 12):
            if i % 2 == 0:
                sum_value += int(base_number_str[i]) * ODD_WEIGHT
            else:
                sum_value += int(base_number_str[i]) * EVEN_WEIGHT
        # calculate the last digit
        sum_last_digit = sum_value % 10
        calculated_digit = 0
        if sum_last_digit != 0:
            calculated_digit = 10 - sum_last_digit
        barcode = base_number_str + str(calculated_digit)
        return barcode

    def convert_time_to_utc(self, dt, tz_name=None, is_dst=None, naive=False):
        """
        :param dt: an instance of datetime object to convert to UTC
        :param tz_name: the name of the timezone to convert. In case of no tz_name passed, this method will try to find the timezone in context or the login user record
        :param is_dst: respecting daylight saving time or not

        :return: an instance of datetime object in UTC (with or without timezone notation depending on the given naive value)
        :rtype: datetime
        """
        tz_name = tz_name or self._context.get('tz') or self.env.user.tz
        if not tz_name:
            raise ValidationError(_("Local time zone is not defined. You may need to set a time zone in your user's Preferences."))
        local = pytz.timezone(tz_name)
        local_dt = local.localize(dt, is_dst=is_dst)
        if naive:
            return local_dt.astimezone(pytz.utc).replace(tzinfo=None)
        else:
            return local_dt.astimezone(pytz.utc)

    def convert_utc_time_to_tz(self, utc_dt, tz_name=None, is_dst=None, naive=False):
        """
        Method to convert UTC time to local time
        :param utc_dt: datetime in UTC
        :param tz_name: the name of the timezone to convert. In case of no tz_name passed, this method will try to find the timezone in context or the login user record
        :param is_dst: respecting daylight saving time or not

        :return: datetime object presents local time
        """
        tz_name = tz_name or self._context.get('tz') or self.env.user.tz
        if not tz_name:
            raise ValidationError(_("Local time zone is not defined. You may need to set a time zone in your user's Preferences."))
        tz = pytz.timezone(tz_name)
        res = pytz.utc.localize(utc_dt, is_dst=is_dst).astimezone(tz)
        if naive:
            res = res.replace(tzinfo=None)
        return res

    def time_to_float_hour(self, dt):
        """
        This method will convert a datetime object to a float that present the corresponding time without date. For example,
            datetime.datetime(2019, 3, 24, 12, 44, 0, 307664) will become 12.733418795555554
        :param dt: datetime object
        :param type: datetime

        :return: The extracted time in float. For example, 12.733418795555554 for datetime.time(12, 44, 0, 307664)
        :rtype: float
        """
        return dt.hour + dt.minute / 60.0 + dt.second / (60.0 * 60.0) + dt.microsecond / (60.0 * 60.0 * 1000000.0)

    def float_hours_to_time(self, float_hours, tzinfo=None):
        """
        Convert hours in float to datetime.time object
        :param float_hours: a float indicate hours. For example: 10.5 for 10:30
        :param tzinfo: set timezone for the converted time to return

        :return: datetime.time object that presents the given float_hours
        :rtype: time
        """
        hours = int(float_hours)
        float_minutes = (float_hours - hours) * 60
        minutes = int(float_minutes)
        float_seconds = (float_minutes - minutes) * 60
        seconds = int(float_seconds)
        microsecond = int((float_seconds - seconds) * 1000000)
        if isinstance(tzinfo, str):
            tzinfo = pytz.timezone(tzinfo)
        return date_utils.time(hours, minutes, seconds, microsecond, tzinfo)

    def _find_last_date_of_period_from_period_start_date(self, period_name, period_start_date):
        """
        This method finds the last date of the given period defined by the period_name and the start date of the period. For example:
        - if you pass 'monthly' as the period_name, date('2018-05-20') as the period_start_date, the result will be date('2018-06-20')
        - if you pass 'quarterly' as the period_name, date('2018-05-20') as the date, the result will be date('2018-08-20')

        :param period_name: (string) the name of the given period which is either 'weekly' or 'monthly' or 'quarterly' or 'biannually' or 'annually'
        :param period_start_date: (datetime.datetime | datetime.date) the starting date of the period from which the period will be started

        :return: (datetime.datetime) the last date of the period
        :raise ValidationError: when the passed period_name is invalid
        """
        if not isinstance(period_start_date, date):
            raise ValidationError(_("The given period_start_date must be either date or datetime type. This could be programming error..."))
        ret, msg = self._validate_period_name(period_name)
        if not ret:
            raise ValidationError(msg)
        if period_name == 'weekly':
            dt = period_start_date + relativedelta(days=7)
        elif period_name == 'monthly':
            dt = period_start_date + relativedelta(months=1)
        elif period_name == 'quarterly':
            dt = period_start_date + relativedelta(months=3)
        elif period_name == 'biannually':
            dt = period_start_date + relativedelta(months=6)
        else:
            dt = period_start_date + relativedelta(years=1)
        if not isinstance(period_start_date, datetime):
            dt = dt - relativedelta(days=1)
        else:
            dt = dt - relativedelta(microseconds=1)
        return dt

    def _validate_period_name(self, period_name):
        msg = ''
        if period_name not in ('weekly', 'monthly', 'quarterly', 'biannually', 'annually'):
            msg = _("Wrong value passed to the argument `period_name` of the method `find_last_date_of_period`."
                    " The value for `period_name` should be either 'weekly' or 'monthly' or 'quarterly' or 'biannually' or 'annually'")
            return False, msg
        else:
            return True, msg

    def find_first_date_of_period(self, period_name, given_date, start_day_offset=0):
        """
        This method finds the first date of the given period defined by period name and any date of the period

        :param period_name: (string) the name of the given period which is either 'weekly' or 'monthly' or 'quarterly' or 'biannually' or 'annually'
        :param given_date: datetime.datetime | datetime.date any datetime or date of the period to find
        :param start_day_offset: integer to offset the first date of the given period.

        :return: datetime.datetime | datetime.date the first date of the period
        :rtype: datetime.datetime | datetime.date datetime or date, according to the type of the given given_date

        :raise ValidationError: when the passed period_name is invalid
        """
        ret, msg = self._validate_period_name(period_name)
        if not ret:
            raise ValidationError(msg)

        if period_name == 'weekly':
            dt = given_date - relativedelta(days=given_date.weekday())
        elif period_name == 'monthly':
            # force day as 1
            dt = given_date + relativedelta(day=1)
        elif period_name == 'quarterly':
            if given_date.month >= 1 and given_date.month <= 3:
                dt = datetime(given_date.year, 1, 1)
            elif given_date.month >= 4 and given_date.month <= 6:
                dt = datetime(given_date.year, 4, 1)
            elif given_date.month >= 7 and given_date.month <= 9:
                dt = datetime(given_date.year, 7, 1)
            else:
                dt = datetime(given_date.year, 10, 1)
        elif period_name == 'biannually':
            if given_date.month <= 6:
                dt = datetime(given_date.year, 1, 1)
            else:
                dt = datetime(given_date.year, 7, 1)
        else:
            dt = datetime(given_date.year, 1, 1)

        if start_day_offset > 0:
            dt = dt + relativedelta(days=start_day_offset)
        if isinstance(dt, date) and not isinstance(dt, datetime):
            dt = datetime.combine(dt, time.min)
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)

        # ensure the return type is as the same as the input given_date type
        if isinstance(given_date, date) and not isinstance(given_date, datetime):
            dt = dt.date()

        return dt

    def find_last_date_of_period(self, period_name, given_date, date_is_start_date=False):
        """
        This method finds the last date of the given period defined by period name and any date of the period. For example:
        - if you pass 'monthly' as the period_name, date('2018-05-20') as the date, the result will be date('2018-05-31')
        - if you pass 'quarterly' as the period_name, date('2018-05-20') as the date, the result will be date('2018-06-30')
        :param period_name: (string) the name of the given period which is either 'weekly' or 'monthly' or 'quarterly' or 'biannually' or 'annually'
        :param date: (datetime.datetime) either the start date of the given period or any date of the period, depending on the passed value of the arg. date_is_start_date
        :param date_is_start_date: (bool) True to indicate the given date is also the starting date of the given period_name, otherwise, the given date is any of the period's dates
        :return: (datetime.datetime) the last date of the period
        :raise ValidationError: when the passed period_name is invalid
        """
        ret, msg = self._validate_period_name(period_name)
        if not ret:
            raise ValidationError(msg)

        # If the given date is the start date of the period
        if date_is_start_date:
            return self._find_last_date_of_period_from_period_start_date(period_name=period_name, period_start_date=given_date)

        dt = self.find_first_date_of_period(period_name, given_date, start_day_offset=0)
        # else
        if period_name == 'weekly':
            dt = dt + relativedelta(days=7, microseconds=-1)
        elif period_name == 'monthly':
            dt = dt + relativedelta(months=1, microseconds=-1)
        elif period_name == 'quarterly':
            dt = dt + relativedelta(months=3, microseconds=-1)
        elif period_name == 'biannually':
            dt = dt + relativedelta(months=6, microseconds=-1)
        else:
            dt = dt + relativedelta(years=1, microseconds=-1)

        # ensure the return type is as the same as the input given_date type
        if isinstance(given_date, date) and not isinstance(given_date, datetime):
            dt = dt.date()
        return dt

    def period_iter(self, period_name, dt_start, dt_end, start_day_offset=0):
        """
        Method to generate sorted dates for periods of the given period_name and dt_start and dt_end
        :param period_name: (string) the name of the given period which is either 'weekly' or 'monthly' or 'quarterly' or 'biannually' or 'annually'
        :param dt_start: datetime.datetime | datetime.date
        :param dt_end: datetime.datetime | datetime.date
        :param start_day_offset: default value is zero, which means that the start days are always the very first day of the period

        :return: [list] list of datetime | date objects contain dt_start and end dates of found periods. For example:
                if we pass [datetime.date(2018, 7, 4) and datetime.date(2018, 10, 31) and 0 as the dt_start and the dt_end and the
                start_day_offset correspondingly, the result will be
                    [datetime.date(2018, 7, 4),
                    datetime.date(2018, 7, 31), datetime.date(2018, 8, 31), datetime.date(2018, 9, 30), datetime.date(2018, 10, 31)]
        :rtype: list
        """
        if type(dt_start) != type(dt_end):
            raise ValidationError(_("The given dt_start and dt_end passed into the method `period_iter(period_name, dt_start, dt_end, start_day_offset)`"
                                    " must be in the same type. This could be a programming error..."))
        if not start_day_offset >= 0:
            raise ValidationError(_("The `start_day_offset` passed to the method `period_iter` must be greater than or equal to zero!"))

        if isinstance(dt_start, datetime):
            delta = relativedelta(microseconds=1)
        else:
            delta = relativedelta(days=1)

        res = [dt_start]
        period_start_date = self.find_first_date_of_period(period_name, dt_start) + relativedelta(days=start_day_offset)

        if period_start_date > dt_start:
            res.append(period_start_date - delta)

        while period_start_date <= dt_end:
            last_dt = self._find_last_date_of_period_from_period_start_date(period_name=period_name, period_start_date=period_start_date)
            if last_dt > dt_end:
                last_dt = dt_end
            res.append(last_dt)
            period_start_date = last_dt + delta

        res.sort()
        return res

    def get_days_of_month_from_date(self, dt):
        return calendar.monthrange(dt.year, dt.month)[1]

    def get_day_of_year_from_date(self, date):
        """
        Return the day of year from date. For example, 2018-01-06 will return 6

        :param date: date object
        """
        first_date = fields.Date.to_date('%s-01-01' % date.year)
        day = self.get_days_between_dates(first_date, date) + 1
        return day

    def get_days_between_dates(self, dt_from, dt_to):
        """
        Return number of days between two dates
        """
        return (dt_to - dt_from).days

    def get_months_between_dates(self, dt_from, dt_to):
        """
        Calculate number of months (in float) between two given dates (include both ends) that respects odd/even months

        :return: number of months (in float) between two given dates
        :rtype: float
        """
        if not isinstance(dt_from, date):
            raise ValidationError(_("The given dt_from must be either date or datetime."))
        if not isinstance(dt_to, date):
            raise ValidationError(_("The given dt_to must be either date or datetime."))

        if not isinstance(dt_from, datetime):
            dt_from = datetime.combine(dt_from, time.min)
        if not isinstance(dt_to, datetime):
            dt_to = datetime.combine(dt_to, time.max)

        months = 0.0
        dates_list = [dt_from]
        for dt in rrule.rrule(freq=rrule.MONTHLY, dtstart=dt_from, bymonthday=1, until=dt_to):
            if dt not in dates_list:
                dates_list.append(dt)
        if dt_to not in dates_list:
            dates_list.append(dt_to)

        dates_count = len(dates_list)
        last_seen_date = False
        for idx, dt in enumerate(dates_list):
            if not last_seen_date:
                last_seen_date = dt
                continue
            if idx == 1 or idx == dates_count - 1:
                months += ((dt - last_seen_date).days / self.get_days_of_month_from_date(last_seen_date))
            else:
                months += 1
            last_seen_date = dt
        return months

    def get_number_of_years_between_dates(self, dt_from, dt_to):
        """
        Calculate number of years (in float) between two given dates (excl. the dt_to) that respects leap years

        :param dt_from: datetime | date
        :param dt_to: datetime | date

        :return: number of years (in float) between two given dates (excl dt_to)
        :rtype: float
        """
        if not isinstance(dt_from, date):
            raise ValidationError(_("The given dt_from must be either date or datetime."))
        if not isinstance(dt_to, date):
            raise ValidationError(_("The given dt_to must be either date or datetime."))

        if not isinstance(dt_from, datetime):
            dt_from = datetime.combine(dt_from, time.min)
        if not isinstance(dt_to, datetime):
            dt_to = datetime.combine(dt_to, time.min)

        # if the dt_to >= the last moment of the February, the dt_to's year will be taken for leap year test
        if dt_to.month > 2 or (dt_to.month == 2 and dt_to == fields.Datetime.end_of(dt_to, 'month')):
            is_leap_year = dt_to.year % 4 == 0
        # otherwise, the previous year of the dt_to's year will be
        else:
            is_leap_year = (dt_to.year - 1) % 4 == 0
        days_in_years = 366 if is_leap_year else 365
        diff = relativedelta(dt_to, dt_from)
        return diff.years + \
            diff.months / 12 + \
            diff.days / days_in_years + \
            ((diff.hours + diff.minutes / 60 + diff.seconds / 3600 + diff.microseconds / (1000000 * 3600)) / 24) / days_in_years

    def get_weekdays_for_period(self, dt_from, dt_to):
        """
        Method to return the a dictionary in form of {int0:date, wd1:date, ...} where int0/int1
            are integer 0~6 presenting weekdays and date1/date2 are dates that are the correspong weekdays
        :param dt_from: datetime.datetime|datetime.date
        :param dt_to: datetime.datetime|datetime.date
        :return: dict{int0:date, wd1:date, ...}
        """
        nb_of_days = self.get_days_between_dates(dt_from, dt_to) + 1
        if nb_of_days > 7:
            raise ValidationError(_("The method get_weekdays_for_period(dt_from, dt_to) does not support the periods having more than 7 days"))
        weekdays = {}
        for day in range(0, nb_of_days):
            day_rec = dt_from + timedelta(days=day)
            weekdays[day_rec.weekday()] = day_rec.date()
        return weekdays

    def next_weekday(self, date, weekday=None):
        """
        Method to get the date in the nex tweek of the given `date`'s week with weekday is equal to the given `weekday`. For example,
        - date: 2018-10-18 (Thursday)
        - weekday:
            0: will return 2018-10-22 (Monday next week)
            1: will return 2018-10-23 (Tuesday next week)
            2: will return 2018-10-24 (Wednesday next week)
            3: will return 2018-10-25 (Thursday next week)
            4: will return 2018-10-26 (Friday next week)
            5: will return 2018-10-27 (Saturday next week)
            6: will return 2018-10-28 (Sunday next week)
            None: will return 2018-10-25 (the same week day next week)
        :param date: (datetime.datetime or datetime.date) the given date to find the date next week
        :param weekday: week day of the next week which is an integer from 0 to 6 presenting a day of week, or None to find the date of the same week day next week

        :return: date of the same weekday next week
        """
        # if weekday is None, set it as the same as the weekday of the given date
        result = date + timedelta(7)
        if weekday is not None:
            if not 0 <= weekday <= 6:
                raise ValidationError(_("Wrong value passed to the argument `weekday` of the method `next_weekday`."
                                        " The value for `weekday` must be >= 0 and <= 6"))
            result = self.find_first_date_of_period('weekly', result)
            result += timedelta(weekday)
        return result

    def split_date(self, date):
        """
        Method to split a date into year,month,day separatedly
        :param date date:
        """
        year = date.year
        month = date.month
        day = date.day
        return year, month, day

    def hours_time_string(self, hours):
        """ convert a number of hours (float) into a string with format '%H:%M' """
        minutes = int(round(hours * 60))
        return "%02d:%02d" % divmod(minutes, 60)

    def _zip_dir(self, path, zf, incl_dir=False):
        """
        :param path: the path to the directory to zip
        :param zf: the ZipFile object which is an instance of zipfile.ZipFile
        :type zf: ZipFile

        :return: zipfile.ZipFile object that contain all the content of the path
        """
        path = os.path.normpath(path)

        dlen = len(path)
        if incl_dir:
            dir_name = os.path.split(path)[1]
            minus = len(dir_name) + 1
            dlen -= minus
        for root, dirs, files in os.walk(path):
            for name in files:
                full = os.path.join(root, name)
                rel = root[dlen:]
                dest = os.path.join(rel, name)
                zf.write(full, dest)
        return zf

    def zip_dir(self, path, incl_dir=False):
        """
        zip a directory tree into a bytes object which is ready for storing in Binary field

        :param path: the absolute path to the directory to zip
        :type path: string

        :return: return bytes object containing data for storing in Binary fields
        :rtype: bytes
        """
        # initiate A BytesIO object
        file_data = BytesIO()

        # open file_data as ZipFile with write mode
        with zipfile.ZipFile(file_data, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            self._zip_dir(path, zf, incl_dir=incl_dir)

        # Change the stream position to the start of the stream
        # see https://docs.python.org/3/library/io.html#io.IOBase.seek
        file_data.seek(0)
        # read bytes to the EOF
        file_data_read = file_data.read()
        # encode bytes for output to return
        out = base64.encodebytes(file_data_read)
        return out

    def zip_dirs(self, paths):
        """
        zip a tree of directories (defined by paths) into a bytes object which is ready for storing in Binary field

        :param paths: list of absolute paths (string) to the directories to zip
        :type paths: list

        :return: return bytes object containing data for storing in Binary fields
        :rtype: bytes
        """
        # initiate A BytesIO object
        file_data = BytesIO()

        # open file_data as ZipFile with write mode
        with zipfile.ZipFile(file_data, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in paths:
                self._zip_dir(path, zf, incl_dir=True)

        # Change the stream position to the start of the stream
        # see https://docs.python.org/3/library/io.html#io.IOBase.seek
        file_data.seek(0)
        # read bytes to the EOF
        file_data_read = file_data.read()
        # encode bytes for output to return
        out = base64.encodebytes(file_data_read)
        return out

    def guess_lang(self, sample):
        """
        This method is for others to implement.
        """
        raise NotImplementedError(_("the method guess_lang has not been implemented yet"))

    def strip_accents(self, s):
        s = remove_accents(s)
        return self._no_accent_vietnamese(s)

    def _no_accent_vietnamese(self, s):
        """
        Convert Vietnamese unicode string from 'Tiếng Việt có dấu' thanh 'Tieng Viet khong dau'
        :param s: text: input string to be converted
        :return : string converted
        """
    #     s = s.decode('utf-8')
        s = re.sub(u'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
        s = re.sub(u'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
        s = re.sub(u'[èéẹẻẽêềếệểễ]', 'e', s)
        s = re.sub(u'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
        s = re.sub(u'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
        s = re.sub(u'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
        s = re.sub(u'[ìíịỉĩ]', 'i', s)
        s = re.sub(u'[ÌÍỊỈĨ]', 'I', s)
        s = re.sub(u'[ùúụủũưừứựửữ]', 'u', s)
        s = re.sub(u'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
        s = re.sub(u'[ỳýỵỷỹ]', 'y', s)
        s = re.sub(u'[ỲÝỴỶỸ]', 'Y', s)
        s = re.sub(u'[Đ]', 'D', s)
        s = re.sub(u'[đ]', 'd', s)
        return s

    def no_accent_vietnamese(self, s):
        _logger.warning('The method `no_accent_vietnamese()` is deprecated. Please use the `_no_accent_vietnamese()` instead')
        return self._no_accent_vietnamese(s)

    def sum_digits(self, n, number_of_digit_return=None):
        """
        This will sum all digits of the given number until the result has x digits where x is number_of_digit_return
        :param n: the given number for sum of its digits
        :type n: int|float
        :param number_of_digit_return: the number of digist in the return result.
            For example, if n=178 and number_of_digit_return=2, the result will be 16. However, if number_of_digit_return <= 1, the result will be 7 (=1+6 again)

        :return: the sum of all the digits until the result has `number_of_digit_return` digits
        :rtype: int
        """
        s = 0
        for d in str(n):
            if d.isdigit():
                s += int(d)

        str_len = len(str(s))
        if isinstance(number_of_digit_return, int) and str_len > number_of_digit_return and str_len > 1:
            return self.sum_digits(s)
        return s

    def find_nearest_lucky_number(self, n, rounding=0, round_up=False):
        """
        9 is lucky number
        This will find the nearest integer if the given number that have digits sum = 9 (sum digits until 1 digit is returned)
        :param n: the given number for finding its nearest lucky number
        :type n: int|float
        :param rounding: the number of digist for rounding
            For example, if n=178999 and rounding=2, the result will be 178900. However, if rounding = 4, the result will be 170000

        :return: the lucky number
        :rtype: int
        """
        if rounding < 0:
            rounding = 0
        # replace last x digits with zero by rounding up/down, where x is the given round_digits
        n = round(n, rounding) if round_up else round(n, -rounding)
        # calculate adjusting step
        step = 1
        for x in range(rounding):
            step = step * 10

        while self.sum_digits(n, 1) != 9:
            if isinstance(n, int):
                if round_up:
                    n += step
                else:
                    n -= step
            else:
                n = round(n)
        return n

    def get_host_ip(self):
        """
        This method return the IP of the host where the Odoo instance is running.
        If the instance is deployed behind a reverse proxy, the returned IP will be the IP of the proxy instead.
        """
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + MY_IP_ROUTE
        try:
            respond = get(url)
        # catch SSLError when the url comes with an invalid SSL certificate (e.g, a self-signed one)
        except SSLError as e:
            _logger.warning("SSLError occurred while getting URL %s. Here is the details: %s. Now trying without SSL verification...", url, str(e))
            # ignore ssl certificate validation
            respond = get(url, verify=False)
        # catch the ConnectionError that occurs when it failed to establish a new connection to the given URL
        except ConnectionError as e:
            _logger.error("Failed to establish connection to the given URL %s. Here is the details: %s.", url, str(e))
        # catch the remaining possible errors
        except Exception as e:
            _logger.error("Error occurred while getting URL %s. Here is the details: %s.", url, str(e))
        try:
            return respond.text
        except NameError as e:
            return '127.0.0.1'

    def identical_images(self, img1, img2):
        """
        Compare 2 given image object of :class:`fields.Image` if they are identical
        PIL module do not support `.svg` format (ref: https://pillow.readthedocs.io/en/5.1.x/handbook/image-file-formats.html)
        So please don't compare 2 unsupported type images
        :param: img1: fields.Image object
        :param: img2: fields.Image object

        :return: return True if 2 images ARE identical, otherwise return False
        :rtype: boolean
        :raise: OSError when image(s) in pillow unsupported type
        """

        # img1 and img2 can be False depends on condition we given
        if img1 and img2:
            try:
                img1 = Image.open(BytesIO(base64.decodebytes(img1)))
                img2 = Image.open(BytesIO(base64.decodebytes(img2)))
                if not ImageChops.difference(image1=img1, image2=img2).getbbox():
                    return True
                else:
                    return False
            except OSError:
                # OSError: cannot identify image file <_io.BytesIO object at 0x7fbac2950f10>
                _logger.error("You are comparing 2 images which are not supported file type of PIL. "
                              "Please follow this link to see what PIL supported: "
                              "(https://pillow.readthedocs.io/en/5.1.x/handbook/image-file-formats.html)"
                              "You should either choose to convert image type back to PIL supported types with python libraries,"
                              " or accept binary string comparing as last result.")
                raise OSError
            except Exception as e:
                # Raise `ValueError: images do not match` when you are trying to compare 2 images
                # with different types (E.g: jpeg and png)
                _logger.error(e)
                return False
        else:
            return False

    def validate_year(self, year):
        """
        This method validates the given year and return the year in integer.

        :param year: str|int the given year to validate
        :return: the given year in integer that was validated
        :rtype: int
        :raise ValidationError: if the input year is neither a digit nor a digest > 0 and <= 9999
        """
        if year and (type(year) == int or year.isdigit()):
            year_int = int(year)
            if year_int > 0 and year_int <= 9999:
                return year
        raise ValidationError(_("Invalid year '%s'") % year)

    def break_timerange_for_midnight(self, start_dt, end_dt):
        """
        generate intervals broken by midnight (00:00:00)
        for example datetime(2021-02-02 20:00:00) ~ datetime(2021-02-03 20:00:00) will produce
        [datetime(2021-02-02 20:00:00), datetime(2021-02-03 00:00:00), datetime(2021-02-03 20:00:00)]
        :param start_dt: datetime
        :param end_dt: datetime

        :return: list of datetimes with midnight inside
        :rtype: list
        """
        dates = []
        for dt in rrule.rrule(freq=rrule.DAILY, dtstart=start_dt, until=end_dt):
            if not dates:
                dates.append(dt)
                continue
            if dates[-1].date().weekday() != dt.date().weekday():
                dates.append(datetime.combine(dt.date(), time.min))
            if dates[-1] != dt:
                dates.append(dt)
        if end_dt not in dates:
            if dates[-1].date().weekday() != end_dt.date().weekday():
                dates.append(datetime.combine(end_dt.date(), time.min))
            if end_dt not in dates:
                dates.append(end_dt)
        return dates

    @api.model
    def splittor(self, recordset, max_rec_in_batch=None):
        """ Splits the given recordset in batches of the given max_rec_in_batch or 1000
        (if prefetch_max is not passed) to avoid entire-recordset-prefetch-effects
        and & removes the previous batch from the cache after it's been iterated in full
        :param recordset: the recordset to split into batches
        :param max_rec_in_batch: max number of records in each splitted batch.
            If not give or False evaluated, PREFETCH_MAX will be taken

        :return: return an iterator
        """
        max_rec_in_batch = max_rec_in_batch or PREFETCH_MAX
        for idx in range(0, len(recordset), max_rec_in_batch):
            sub = recordset[idx:idx + max_rec_in_batch]
            yield sub
            recordset.invalidate_cache(ids=sub.ids)

    @api.model
    def _update_brand_icon(self):
        from odoo.addons.to_base import _update_brand_web_icon_data
        _update_brand_web_icon_data(self.env)

    def mile2km(self, miles):
        return miles * 1.60934

    def km2mile(self, km):
        return km / 1.60934

    def _remove_orphan_mail_messages(self):
        """
        This method finds mail.message records that link to res_id that do not exists
        due to the bug https://github.com/odoo/odoo/pull/84863 and remove them
        """

        def _remove_messages(batch, idx_from, idx_to, total):
            with api.Environment.manage(), self.pool.cursor() as cr:
                _logger.info(
                    "Start removing all the %s orphan mail messages of the batch [%s~%s] in total %s ones",
                    idx_to - idx_from,
                    idx_from,
                    idx_to,
                    total
                    )
                env = self.env(cr=cr)
                # split the batch into smaller batches of max 1000 records
                # then delete each and commit as soon as deletion is done
                for smaller_batch in self.splittor(batch, 1000):
                    with env.cr.savepoint():
                        smaller_batch.with_env(env).unlink()
                    env.cr.commit()
                _logger.info(
                    "Finished removing %s orphan messages from the batch [%s~%s] in total %s ones",
                    idx_to - idx_from,
                    idx_from,
                    idx_to,
                    total
                    )

        def _threaded_remove_messages(messages):
            """
            slice the given messages into pieces of smaller batches as long as
            total number of batches is equal to half of db_maxconn to avoid
            error of "connection pool is full"
            Then put each batch into a thread for parallel exec
            """
            total = len(messages)
            jobs = []
            max_threads = config['db_maxconn'] // 4  # db_maxconn is 64 by default
            batch_count = (total // max_threads) + 1  # +1 for roundup
            idx_from = 0
            while messages:
                slices = messages[:batch_count]
                t = threading.Thread(
                    name="Remove %s Orphan Mail Messages" % batch_count,
                    target=_remove_messages,
                    args=(slices, idx_from, batch_count + idx_from, total)
                    )
                t.setDaemon(True)
                t.start()
                messages -= slices
                jobs.append(t)
                idx_from += batch_count
            # wait for all threads to finish the work
            for j in jobs:
                j.join()
            return jobs

        self.env.cr.execute("""SELECT DISTINCT(model) FROM mail_message WHERE model IS NOT NULL""")
        models = [r[0] for r in self.env.cr.fetchall()]

        query_list = []
        for model in models:
            try:
                obj = self.env[model]
                table_name = obj._table
                query_list.append(
                    sql.SQL("""
                    SELECT mm.id FROM mail_message AS mm
                    JOIN %s ON %s.id = mm.res_id
                    WHERE mm.model = '%s'
                    """
                    % (table_name, table_name, model)
                    )
                )
            except KeyError as e:  # if messages refer to a model of an uninstalled module, KeyError raised
                _logger.info("Model %s does not exists. Their associated mail messages will be removed...", model)

        query = sql.SQL("""
        UNION ALL
        """).join(query_list)

        self.env.cr.execute(query)
        non_orphan_ids = [r[0] for r in self.env.cr.fetchall()]
        non_orphan_ids = set(non_orphan_ids)

        self.env.cr.execute("""
        SELECT id
        FROM mail_message
        WHERE model in %s
        """, (tuple(models),))
        exist_ids = [r[0] for r in self.env.cr.fetchall()]

        orphan_ids = [msg_id for msg_id in exist_ids if msg_id not in non_orphan_ids]
        to_remove = self.env['mail.message'].browse(orphan_ids)

        _threaded_remove_messages(to_remove)
