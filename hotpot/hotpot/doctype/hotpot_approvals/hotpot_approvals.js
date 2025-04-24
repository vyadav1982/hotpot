// Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hotpot Approvals", {
	refresh(frm) {
        const roles = frappe.user_roles;
        const isAdmin = roles.includes("Administrator");
        if(!isAdmin) {
            frm.toggle_display("is_active", false);
            if(frm.doc.approval_status !== "Pending"){
                frm.disable_form();
            }
            
        }
	},
});
