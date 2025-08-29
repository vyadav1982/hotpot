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
                        let status = doc["approval_status"]
                        let changes = [];
                        Object.keys(newValues).forEach(key => {
                            if (key.startsWith("old_")) return;
                            let oldKey = "old_" + key;
                            if (oldKey in newValues) {
                                let fieldLabel = frappe.meta.get_docfield("Hotpot Draft Meal", key)?.label;
                                if (!fieldLabel) {
                                    fieldLabel = key.replace(/_/g, " ")
                                        .replace(/\w\S*/g, w => w.charAt(0).toUpperCase() + w.slice(1));
                                }
                                let oldVal = newValues[oldKey];
                                let newVal = newValues[key];
                                if (fieldLabel === "Meal Items") {
                                    let oldItems = oldVal ? oldVal.split(",") : [];
                                    let newItems = newVal ? newVal.split(",") : [];

                                    let added = newItems.filter(i => !oldItems.includes(i));
                                    let removed = oldItems.filter(i => !newItems.includes(i));
                                    let unchanged = newItems.filter(i => oldItems.includes(i));

                                    let message = `🍽️ <b>${fieldLabel}</b><br>`;

                                    if (added.length) {
                                        message += `&nbsp;&nbsp;✅ Added: <span style="color:#27ae60"><b>${added.join(", ")}</b></span><br>`;
                                    }
                                    if (removed.length) {
                                        message += `&nbsp;&nbsp;❌ Removed: <span style="color:#e74c3c"><b>${removed.join(", ")}</b></span><br>`;
                                    }
                                    if (unchanged.length && (added.length || removed.length)) {
                                        message += `&nbsp;&nbsp;↔️ Unchanged: ${unchanged.join(", ")}<br>`;
                                    }

                                    changes.push(message);
                                } else {
                                    changes.push(
                                        `🔹 <b>${fieldLabel}</b><br>` +
                                        `&nbsp;&nbsp;${oldVal ? `<span style="color:#e74c3c"><b>${oldVal}</b></span>` : "—"} ` +
                                        `➡️ ` +
                                        `${newVal ? `<span style="color:#27ae60"><b>${newVal}</b></span>` : "—"}`
                                    );
                                }

                            }
                        });

                        if (changes.length > 0) {
                            let msg = "";
                            if (status === "Pending") {
                                msg += "✨ <b>Some updates are requested by the vendor:</b><br><br>";
                            } else {
                                msg += "✨ <b>The vendor had requested the following updates:</b><br><br>";
                            }
                            msg += changes.join("<br><br>");

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
