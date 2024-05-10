
{
    'name': 'NPD Module Install Thai Accounting Standard ',
    'version': '14.0.5',
    'author': 'npd',
    'license': 'AGPL-3',
    'website': 'https://npd9.com/',
    'category': 'Modules',
    'depends': [
        'npd_module_install',
        'bi_non_moving_product',
        'web_widget_x2many_2d_matrix',
        'account_invoice_section_sale_order',
        'account_menu',
        'account_advance',
        'account_analytic_distribution_required',
        'account_analytic_sequence',
        'account_billing_advance',
        'account_cheque',
        'account_clear_tb',
        'account_comment_template',
        'account_config',
        'account_cutoff_base',
        'account_cutoff_start_end_dates',
        'ks_account_dashboard',
        'account_fiscal_year',
        'account_invoice_report_grouped_by_picking',
        'account_invoice_line_report',
        'account_invoice_report_due_list',
        'account_invoice_search_by_reference',
        'account_invoice_start_end_dates',
        'account_journal_lock_date',
        'account_journal_sequences',
        'account_journal_sequence_date',
        'account_lock_date_update',
        'account_move_force_removal',
        'account_move_line_menu',
        'account_move_line_tax_editable',
        'account_move_template',
        'account_move_tier_validation',
        'account_payment_invoice',
        'account_payment_return',
        'account_payment_sequence',
        'account_payment_term_discount',
        'account_reconciliation_widget',
        'account_dynamic_reports',
        'analytic',
        'account_analytic_wip',
        'analytic_tag_dimension',
        'analytic_tag_dimension_enhanced',
        'analytic_activity_based_cost',
        'account_asset_management',
        'account_asset_management_transfer',
        'auditlog',
        'stock_barcode',
        'base',
        'analytic_base_department',
        'base_cancel_confirm',
        'base_comment_template',
        'base_import',
        'base_location_geonames_import',
        'base_product_mass_addition',
        'report_xlsx',
        'base_revision',
        'base_tier_validation',
        'base_tier_validation_correction',
        'base_tier_validation_formula',
        'base_tier_validation_forward',
        'account_billing',
        'calendar',
        'calendar_sms',
        'base_address_city',
        'ls_web_m2x_options_config',
        'contacts',
        'bi_convert_purchase_from_sales',
        'bi_copy_sale_purchase_line',
        'currency_rate_inverted',
        'currency_rate_update',
        'portal',
        'rating',
        'ks_dashboard_ninja',
        'ks_dn_advance',
        'board',
        'date_range',
        'date_range_account',
        'account_debit_note',
        'sale_partner_incoterm',
        'delivery',
        'account_chart_update',
        'mail',
        'dms',
        'web_drop_target',
        'fetchmail',
        'hr_contract',
        'app_hr_superbar',
        'jt_employee_sequence',
        'hr',
        'excel_import_export',
        'base_exception',
        'stock_inventory_preparation_filter',
        'account_fiscal_year_closing',
        'fiscal_year_sequence_extensible',
        'payment_fix_register_token',
        'stock_force_date_app',
        'account_invoice_force_number',
        'web_kanban_gauge',
        'generic_excel_reports',
        'hide_any_menu',
        'hr_department_code',
        'hr_org_chart',
        'hr_organizational_chart',
        'iap_mail',
        'bus',
        'bi_import_chart_of_accounts',
        'account_edi',
        'account_edi_facturx',
        'account_edi_ubl',
        'iap',
        'inbox_notif_email',
        'base_setup',
        'partner_aging',
        'stock',
        'ks_inventory_dashboard',
        'account',
        'account_lock',
        'procurement_jit',
        'digest',
        'analytic_partner',
        'ks_list_view_manager',
        'base_location',
        'mail_preview_base',
        'mail_bot_hr',
        'mis_builder',
        'stock_move_location',
        'sale_purchase_stock',
        'muk_rest',
        'uninstall_multi_module',
        'dev_non_moving_stock_report',
        'mail_bot',
        'onchange_helper',
        'hr_reward_warning',
        'sale_outgoing_product',
        'partner_autocomplete',
        'partner_company_type',
        'partner_fax',
        'partner_firstname',
        'partner_industry_secondary',
        'npd_partner_name_unq',
        'partner_phone_extension',
        'partner_priority',
        'partner_tier_validation',
        'payment',
        'payment_method',
        'account_payment_term_extension',
        'account_due_list',
        'petty_cash',
        'npd_account_invoice_reset_tax',
        'account_menu_hide',
        'npd_account_move',
        'psn_account_menu',
        'npd_purchase_orderdate',
        'npd_std_purchase_request_report',
        'npd_std_add_priority_pr',
        'npd_asset_duplicate',
        'npd_std_asset_free_field',
        'npd_std_cheque_qweb',
        'npd_company_custom',
        'npd_std_access_confirm_rfq',
        'npd_customer_pricelist',
        'npd_std_default_uom_pr',
        'npd_std_accounting_qweb',
        'npd_std_pnd_qweb',
        'npd_generate_subsequences',
        'npd_std_po_document_type',
        'npd_std_show_only_child',
        'npd_std_stock_inventory',
        'phone_validation',
        'stock_picking_back2draft',
        'portal_rating',
        'product_brand',
        'product_category_code',
        'product_category_product_link',
        'product_category_tax',
        'product_cost_security',
        'sale_last_price_info',
        'aspl_product_alert_qty',
        'npd_product_name_unq',
        'dev_secondary_uom',
        'product_sequence',
        'product_state',
        'product_template_tags',
        'product_variant_default_code',
        'product_variant_sale_price',
        'product_warranty',
        'product_weight',
        'product',
        'product_expiry',
        'psn_is_customer_is_vendor',
        'psn_journal_sequence',
        'purchase',
        'purchase_requisition',
        'purchase_requisition_tier_validation',
        'purchase_cancel_reason',
        'purchase_commercial_partner',
        'purchase_delivery_split_date',
        'purchase_deposit',
        'purchase_rfq_number',
        'purchase_invoice_plan',
        'purchase_isolated_rfq',
        'purchase_isolated_seq_date',
        'purchase_open_qty',
        'purchase_order_archive',
        'purchase_order_line_menu',
        'purchase_order_line_price_history',
        'purchase_discount',
        'purchase_security',
        'purchase_order_uninvoiced_amount',
        'purchase_last_price_info',
        'purchase_reception_notify',
        'purchase_reception_status',
        'purchase_request',
        'purchase_request_department',
        'purchase_requests_seq_date',
        'purchase_request_tier_validation',
        'purchase_request_tier_validation',
        'purchase_requisition_stock',
        'purchase_stock',
        'purchase_tier_validation',
        'purchase_tier_validation',
        'purchase_work_acceptance',
        'contract',
        'report_xlsx_helper',
        'resource',
        'account_voucher',
        'sale_comment_template',
        'sale_commitment_date_mandatory',
        'sale_exception',
        'sale_force_invoiced',
        'sale_invoice_blocking',
        'sale_isolated_quotation',
        'sale_isolated_quotation_seq_date',
        'sale_order_archive',
        'sale_order_line_date',
        'sale_order_line_description',
        'sale_order_line_menu',
        'sale_order_line_variant_description',
        'sale_order_revision',
        'sale_order_note_template',
        'sale_product_category_menu',
        'sale_product_multi_add',
        'sale_product_set',
        'sale_product_set_packaging_qty',
        'sale_purchase',
        'sale_shipping_info_helper',
        'npd_sale_quotation_date',
        'sale_stock_picking_blocking',
        'sale_tier_validation',
        'sale_order_line_note',
        'sale_management',
        'sale_management',
        'sale_stock',
        'ks_sale_dashboard_ninja',
        'sale_invoice_plan',
        'sales_team',
        'scrap_reason_code',
        'account_invoice_refund_link',
        'auth_signup',
        'sms',
        'snailmail',
        'snailmail_account',
        'stock_quant_manual_assign',
        'stock_sms',
        'stock_available',
        'stock_card_report',
        'stock_cycle_count',
        'stock_delivery_note',
        'stock_demand_estimate',
        'stock_demand_estimate_matrix',
        'stock_no_negative',
        'stock_free_quantity',
        'bi_stock_expiry_report',
        'dev_inventory_ageing_report',
        'stock_inventory_discrepancy',
        'stock_inventory_exclude_sublocation',
        'stock_location_children',
        'stock_move_line_auto_fill',
        'stock_picking_cancel_confirm',
        'stock_picking_filter_lot',
        'stock_picking_invoice_link',
        'stock_picking_line_sequence',
        'stock_pull_list',
        'stock_putaway_hook',
        'stock_request',
        'npd_stock_request_cost_price',
        'stock_request_tier_validation',
        'stock_request_tier_validation',
        'stock_restrict_lot',
        'stock_return_request',
        'stock_valuation_layer_by_category',
        'stock_warehouse_calendar',
        'account_cash_basis_group_base_line',
        'l10n_th_tax_invoice',
        'l10n_th_base_location',
        'l10n_th_amount_to_text',
        'l10n_th_currency_rate_update',
        'l10n_th_fonts',
        'l10n_th_partner',
        'l10n_th_tin_service',
        'l10n_th_withholding_tax',
        'l10n_th_withholding_tax_cert',
        'l10n_th_withholding_tax_cert_form',
        'l10n_th_asset_register_report',
        'l10n_th_tax_report',
        'l10n_th_withholding_tax_report',
        'auth_totp_portal',
        'web_tour',
        'payment_transfer',
        'auth_totp',
        'product_code_unique',
        'uom',
        'web_unsplash',
        'account_invoice_date_due',
        'utm',
        'stock_picking_report_valued',
        'npd_vendor_priority',
        'web',
        'web_editor',
        'web_refresher',
        'web_responsive',
        'http_routing',
        'web_widget_many2many_tags_link',
        'web_m2x_options',
        'withholding_tax_cert_amount',
        'stock_account',
        'stock_landed_costs',
        'npd_account_inherit',
        'l10n_th_npd',
        'multi_update_modules',

    ],
    'installable': True,
}
