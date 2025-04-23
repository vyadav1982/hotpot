frappe.listview_settings["Hotpot User"] = {
    hide_name_column: true,

    onload(listview) {
        const doctype = listview.doctype;
        listview.page.clear_menu();
        listview.page.clear_actions();
        listview.page.hide_menu();
        listview.page.hide_actions_menu();

        listview.page.add_button(__("Import", null, "Button in list view menu"), function () {
            frappe.set_route("list", "data-import", {
                reference_doctype: doctype,
            });
        });
        listview.page.add_button(__("Add Hotpot User", null, "Button in list view menu"), function () {
            if (!frappe.boot.read_only && listview.can_create) {
                frappe.new_doc("Hotpot User");
            } else {
                frappe.msgprint(__("You do not have permission to create a Hotpot User."));
            }
        });

        let disableBtn = listview.page.add_inner_button(__("Disable User"), function () {
            let selectedUsers = listview.get_checked_items().map(doc => doc.name);

            if (selectedUsers.length > 0) {
                frappe.call({
                    method: "hotpot.hotpot.doctype.hotpot_user.disable_users",
                    freeze: true,
                    args: {
                        user_list: selectedUsers
                    },
                    callback: function () {
                        frappe.show_alert({
                            message: __("Users Disabled Successfully"),
                            indicator: "green"
                        }, 5);
                        listview.refresh();
                    }
                });
            } else {
                frappe.msgprint(__("Please select at least one user to disable."));
            }
        });

        disableBtn.hide();

        listview.page.wrapper.on("change", ":checkbox", function () {
            let selectedUsers = listview.get_checked_items();
            disableBtn.toggle(selectedUsers.length > 0);
        });
    },
    refresh: function (listview) {
        listview.page.clear_menu();
        listview.page.clear_actions();
        listview.page.hide_menu();
        listview.page.hide_actions_menu();
        listview.toggle_actions_menu_button =  function (toggle){
            return
        }
    },
   
};

