// Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hotpot Configurations", {
    refresh(frm) {
        const userRoles = frappe.user_roles;
        const isAdmin = userRoles.includes("Administrator")
        if (!isAdmin) {
            frm.page.wrapper.find(".comment-box").css({ 'display': 'none' });
            frm.page.hide_menu();
        }
    },
});
