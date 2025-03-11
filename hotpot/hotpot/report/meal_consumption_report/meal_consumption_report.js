// Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
const get_all_vendor = import('.hotpot.hotpot.doctype.hotpot_user.get_all_vendor');


frappe.query_reports["Meal Consumption Report"] = {
	filters: [
    {
      fieldname: "vendor_id",
      label: __("Vendor"),
      fieldtype: "Link",
      width: "80",
      options: "Hotpot User",
      get_query: () => {
        return {
          query: get_all_vendor,
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
};
