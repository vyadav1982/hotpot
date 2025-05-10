// Copyright (c) 2024, Bytepanda Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hotpot User", {
	onload: function (frm) {
		const roles = frappe.user_roles;
		const isAdmin = roles.includes("Administrator");
		if (!frm.doc.__islocal && !isAdmin) {
			frm.page.hide_menu();
			frm.toggle_enable("email", false);
		}
		frm.set_query("guest_of", function () {
			return {
				filters: {
					is_vendor: 1,
				},
			};
		});
	},
	refresh: function (frm) {
		const roles = frappe.user_roles;
		const isAdmin = roles.includes("Administrator");
		if (!isAdmin) {
			frm.page.wrapper.find(".comment-box").css({ display: "none" });
			frm.page.hide_menu();
		}

		if (!frm.doc.__islocal && !isAdmin) {
			frm.toggle_enable("email", false);
		}
	},
	is_vendor: function (frm) {
		if (frm.doc.is_vendor) {
			frm.doc.is_employee = 0;
			frm.doc.is_server = 0;
			frm.doc.is_guest = 0;
			frm.doc.employee = null;
			frm.doc.employee_id = null;
			frm.doc.employee_name = null;
			frm.doc.tag_id = null;
			frm.doc.discount = -1;
		} else {
			if (!frm.doc.is_employee && !frm.doc.is_server && !frm.doc.is_guest) {
				frm.doc.is_vendor = 1;
			}
		}
		frm.refresh();
	},
	is_server: function (frm) {
		if (frm.doc.is_server) {
			frm.doc.is_employee = 0;
			frm.doc.is_vendor = 0;
			frm.doc.is_guest = 0;
			frm.doc.employee = null;
			frm.doc.employee_id = null;
			frm.doc.employee_name = null;
			frm.doc.tag_id = null;
			frm.doc.discount = -1;
		} else {
			if (!frm.doc.is_employee && !frm.doc.is_vender && !frm.doc.is_guest) {
				frm.doc.is_server = 1;
			}
		}
		frm.refresh();
	},
	is_employee: function (frm) {
		if (frm.doc.is_employee) {
			frm.doc.is_vendor = 0;
			frm.doc.is_server = 0;
			frm.doc.is_guest = 0;
		} else {
			if (!frm.doc.is_server && !frm.doc.is_vender && !frm.doc.is_guest) {
				frm.doc.is_employee = 1;
			}
		}
		frm.refresh();
	},
	is_guest: function (frm) {
		if (frm.doc.is_guest) {
			frm.doc.is_employee = 0;
			frm.doc.is_vendor = 0;
			frm.doc.is_server = 0;
			frm.doc.employee = null;
			frm.doc.employee_id = null;
			frm.doc.employee_name = null;
			frm.doc.tag_id = null;
			frm.doc.discount = -1;
		} else {
			if (!frm.doc.is_employee && !frm.doc.is_vender && !frm.doc.is_server) {
				frm.doc.is_guest = 1;
			}
		}
		frm.refresh();
	},
});
