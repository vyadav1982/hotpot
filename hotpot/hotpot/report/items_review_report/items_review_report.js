// Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Items Review Report"] = {
	formatter: function (value, row, column, data, default_formatter) {
        if (column.fieldname === "all_feedbacks" && value) {
            return value;
        }
        return default_formatter(value, row, column, data);
    },
	onload: function (report) {
		report.page.trigger_ready = false;
		const roles = frappe.user_roles;
		const hasAdminRole = roles.includes('Administrator');
		const custom_css = `
            /* Allow rows to expand */
            .datatable .dt-row {
                height: auto !important;
            }

            /* Allow cells to wrap multi-line content */
            .datatable .dt-cell, 
            .datatable .dt-cell__content {
                height: auto !important;
                white-space: normal !important;
                overflow: visible !important;
                line-height: 1.4em !important;
                padding-top: 4px !important;
                padding-bottom: 4px !important;
            }
        `;

        // inject only once
        if (!document.getElementById("datatable-row-height-fix")) {
            const style_element = document.createElement("style");
            style_element.id = "datatable-row-height-fix";
            style_element.innerHTML = custom_css;
            document.head.appendChild(style_element);
        }

		setTimeout(() => {
            if (report.datatable) {
                report.datatable.refresh();
            }
        }, 300);
        
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
			fieldname: "vendor_id",
			label: __("Vendor"),
			fieldtype: "Link",
			width: "80",
			options: "Hotpot User",
			hidden: frappe.user.has_role("Hotpot Vendor") && !frappe.user.has_role("Administrator"),
			get_query: () => {
				return {
					query: "hotpot.hotpot.doctype.hotpot_user.get_all_vendor",
				};
			},
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
}
