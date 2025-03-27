frappe.listview_settings["Hotpot User"] = {
    hide_name_column: true,
    onload(listview) {
        let buttonText = __("Disable User");
        console.log()

        let disableBtn = listview.page.add_inner_button(buttonText, function () {
            let selectedUsers = listview.get_checked_items().map(doc => doc.name);

            if (selectedUsers.length > 0) {
                frappe.call({
                    method: "hotpot.hotpot.doctype.hotpot_user.disable_users",
                    freeze: true,
                    args: {
                        user_list: selectedUsers
                    },
                    callback: function (r) {
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
            if (selectedUsers.length > 0) {
                disableBtn.show();
            } else {
                disableBtn.hide();
            }
        });
    }
};
