// Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hotpot Meal Items", {
	refresh(frm) {
		const userRoles = frappe.user_roles;
		const isAdmin = userRoles.includes("Administrator");
		const isVendor = userRoles.includes("Hotpot Vendor");
		frm.set_query("vendor_id", function () {
			return {
				filters: {
					is_vendor: 1,
				},
			};
		});
		if (!isAdmin) {
			frm.page.wrapper.find(".comment-box").css({ display: "none" });
			frm.page.hide_menu();
		}
		if (isVendor && !isAdmin) {
			// frm.disable_form()
			frm.toggle_display("vendor_id", false);
			// if (frm.doc.is_deleted == 1) {
			// 	frm.disable_form();
			// }
		}
	},
});
