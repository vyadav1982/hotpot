// Copyright (c) 2024, Bytepanda Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hotpot User", {
    onload: function(frm) {
        const roles = frappe.user_roles;
        const isAdmin = roles.includes("Administrator");
        if (!frm.doc.__islocal && !isAdmin) {
            frm.page.hide_menu();
            frm.toggle_enable("role", false);
            frm.toggle_enable("email", false);
        }
    },

    refresh: function(frm) {
        const roles = frappe.user_roles;
        const isAdmin = roles.includes("Administrator");
        if(!isAdmin){
            frm.page.wrapper.find(".comment-box").css({'display':'none'});
            frm.page.hide_menu();
            frm.toggle_display("approval_id", false);
            frm.toggle_display("fcm_token", false);
            frm.toggle_display("latitude", false);
            frm.toggle_display("longitude", false);
            frm.toggle_display("timezone", false);
            frm.toggle_display("guest_of", false);
        }

        if (frm.doc.role === "Hotpot Vendor" && !isAdmin) {
            frm.toggle_display("is_vendor", false);
            frm.toggle_display("guest_of", false);
            frm.toggle_display("tag_id", false);
        }
        if (!frm.doc.__islocal && !isAdmin) {
            frm.toggle_enable("role", false);
            frm.toggle_enable("email", false);
        }
    },

    role: function(frm) {
        const roles = frappe.user_roles;
        const isAdmin = roles.includes("Administrator");
        if(!isAdmin){
            if (frm.doc.role === "Hotpot Vendor") {
                frm.toggle_display("is_vendor", false);
                frm.toggle_display("guest_of", false);
                frm.toggle_display("tag_id", false);
            } else if (frm.doc.role === "Hotpot Server") {
                frm.toggle_display("guest_of", true);
                frm.toggle_display("tag_id", false);
            }else{
                frm.toggle_display("is_vendor", false);
                frm.toggle_display("guest_of", false);
                frm.toggle_display("tag_id", true);
            }
        }
    }
});

