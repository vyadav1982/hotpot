// Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hotpot Approvals", {
    refresh(frm) {
        const roles = frappe.user_roles;
        const isAdmin = roles.includes("Administrator");
        frappe.db.get_doc('Hotpot Approvals', frm.doc.name)
            .then(doc => {
                if (doc["request_type"] === 'Meal Edit') {
                    frappe.db.get_doc('Hotpot Draft Meal', frm.doc.draft_meal).then(d_doc => {
                        let newValues = {};
                        try {
                            newValues = JSON.parse(d_doc.new_values || "{}");
                        } catch (e) {
                            console.error("Invalid JSON in new_values:", e);
                        }

                        let changes = [];
                        Object.keys(newValues).forEach(key => {
                            if (key.startsWith("old_")) return;
                            let oldKey = "old_" + key;
                            if (oldKey in newValues) {
                                // Try to get label from meta
                                let fieldLabel = frappe.meta.get_docfield("Hotpot Draft Meal", key)?.label;
                                // If not found, prettify fieldname (e.g., meal_title → Meal Title)
                                if (!fieldLabel) {
                                    fieldLabel = key.replace(/_/g, " ")
                                        .replace(/\w\S*/g, w => w.charAt(0).toUpperCase() + w.slice(1));
                                }
                                let oldVal = newValues[oldKey];
                                let newVal = newValues[key];
                                changes.push(`🔹 <b>${fieldLabel}</b><br> &nbsp;&nbsp;<b>${oldVal}</b> ➡️ <b>${newVal}</b>`);
                            }
                        });

                        if (changes.length > 0) {
                            let msg = __("✨ Some updates were requested by the vendor:<br><br>") +
                                changes.join("<br><br>");

                            frm.dashboard.clear_headline();
                            frm.dashboard.set_headline_alert(msg, "blue");
                        }
                    });
                }
            });



        if (!isAdmin) {
            frm.page.wrapper.find(".comment-box").css({ 'display': 'none' });
            frm.page.hide_menu();
            frm.toggle_display("is_active", false);
            if (frm.doc.approval_status !== "Pending") {
                frm.disable_form();
            }

        }
    },
});
