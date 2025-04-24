// Copyright (c) 2024, Bytepanda Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hotpot User", {
    onload: function(frm) {
        if (!frm.doc.__islocal) {
            frm.toggle_enable("role", false);
        }
    },

    refresh: function(frm) {
        frm.toggle_display("approval_id", false);
        frm.toggle_display("fcm_token", false);
        frm.toggle_display("latitude", false);
        frm.toggle_display("longitude", false);
        frm.toggle_display("timezone", false);
        frm.toggle_display("guest_of", false);

        if (frm.doc.role === "Hotpot Vendor") {
            frm.toggle_display("is_vendor", false);
            frm.toggle_display("guest_of", false);
            frm.toggle_display("tag_id", false);
        }
    },

    role: function(frm) {
        console.log(frm.doc)
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
});

