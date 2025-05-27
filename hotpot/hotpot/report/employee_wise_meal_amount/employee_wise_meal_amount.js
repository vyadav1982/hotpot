// Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Wise Meal Amount"] = {
	onload: function (report) {
		report.page.trigger_ready = false;
		const roles = frappe.user_roles;
		const hasAdminRole = roles.includes('Administrator');
		if (!hasAdminRole) {
			report.page.clear_menu();
			report.add_card_button_to_toolbar = () => { };
			report.add_chart_buttons_to_toolbar = () => { };
			report.page.remove_inner_button(__("Download Report"), __("Actions"));
			report.page.add_inner_button("Print", () => {
				let dialog = frappe.ui.get_print_settings(
					false,
					(print_settings) => report.print_report(print_settings),
					report.report_doc.letter_head,
					report.get_visible_columns()
				);
				report.add_portrait_warning(dialog);
			},)
			report.page.add_inner_button("PDF", () => {
				let dialog = frappe.ui.get_print_settings(
					false,
					(print_settings) => report.pdf_report(print_settings),
					report.report_doc.letter_head,
					report.get_visible_columns()
				);

				report.add_portrait_warning(dialog);
			},)
			report.page.add_inner_button("Export", () => {
				report.export_report();
			},)

		}
	},
	filters: [
		{
			fieldname: "employee_id",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Hotpot User", 
			get_query: () => {
				return {
					filters: {
						is_employee : 1
					}
				};
			}
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			width: "80",
			reqd: 1,
			default: frappe.datetime.add_days(frappe.datetime.get_today(), -1),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			width: "80",
			reqd: 1,
			default: frappe.datetime.get_today(),
		},
	],
	refresh: function (report) {
		report.page.trigger_ready = false;
		const roles = frappe.user_roles;
		const hasAdminRole = roles.includes('Administrator');
		if (!hasAdminRole) {
			report.add_card_button_to_toolbar = () => { };
			report.add_chart_buttons_to_toolbar = () => { };
			report.page.remove_inner_button(__("Download Report"), __("Actions"));
			report.page.clear_menu();
			report.page.add_inner_button("Print", () => {
				let dialog = frappe.ui.get_print_settings(
					false,
					(print_settings) => report.print_report(print_settings),
					report.report_doc.letter_head,
					report.get_visible_columns()
				);
				report.add_portrait_warning(dialog);
			},)
			report.page.add_inner_button("PDF", () => {
				let dialog = frappe.ui.get_print_settings(
					false,
					(print_settings) => report.pdf_report(print_settings),
					report.report_doc.letter_head,
					report.get_visible_columns()
				);

				report.add_portrait_warning(dialog);
			},)
			report.page.add_inner_button("Export", () => {
				report.export_report();
			},)
		}
	}
};
