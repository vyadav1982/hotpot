frappe.listview_settings["Hotpot User"] = {
    hide_name_column: true,
    onload(listview) {
        let buttonText = __("Disable User");
        setTimeout(() => {
            const $menuList = $(listview.page.menu[0]);
            $menuList.find("li").each(function () {
                const text = $(this).text().trim();
                if (text !== "Import") {
                    $(this).remove();
                }
            });
            listview.page.actions.hide()
            // const $body = $(listview.page.body[0]);
            // console.log(body)
            // $body.find('input.list-row-checkbox').remove();
            // $body.find('input.list-check-all').remove();
        }, 100);

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
