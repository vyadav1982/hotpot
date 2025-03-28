frappe.ui.toolbar.user_profile_menu = function () {
    let menu_items = [
        {
            label: __("My Profile"),
            action: function () {
                frappe.set_route("Form", "User", frappe.session.user);
            },
        },
        {
            label: __("Change Password"),
            action: function () {
                frappe.set_route("Form", "User", frappe.session.user, "change-password");
            },
        },
        {
            label: __("Logout"),
            action: function () {
                frappe.app.logout();
            },
        },
    ];

    // Fetch the roles of the current user
    frappe.call({
        method: "frappe.client.get_value",
        args: {
            doctype: "User",
            filters: { name: frappe.session.user },
            fieldname: "role_profile_name",
        },
        callback: function (response) {
            if (response.message) {
                let user_role = response.message.role_profile_name;

                // Example: Remove "Change Password" for users with "Employee" role
                if (user_role === "Employee") {
                    menu_items = menu_items.filter((item) => item.label !== "Change Password");
                }

                // Render the updated menu
                frappe.ui.toolbar.add_user_action_menu(menu_items);
            }
        },
    });
};
