frappe.listview_settings["Data Import"] = {
    onload(listview) {
        console.log("Data Import List View Loaded");
        const roles = frappe.user_roles;
        const isAdmin = roles.includes("Administrator");
        const isVendor = roles.includes("Hotpot Vendor");
        if (isVendor && !isAdmin) {
            $(".filter-selector").hide();
            setTimeout(() => {
                $('.filter-x-button').click();
                listview.filter_area.add([["Data Import", "owner", "=", frappe.session.user]]);
            }, 50);
        }
        const doctype = this.doctype;
        if (!isAdmin) {
            listview.page.clear_menu();
            listview.page.clear_actions();
            listview.page.hide_menu();
            // listview.page.hide_actions_menu();
            listview.page.add_inner_button(__("Add Data Import", null, "Button in list view menu"), function () {
                if (!frappe.boot.read_only && listview.can_create) {
                    frappe.new_doc("Data Import");
                } else {
                    frappe.msgprint(__("You do not have permission to create a Hotpot User."));
                }
            });

        }
    },
    refresh: function (listview) {
        const roles = frappe.user_roles;
        const doctype = this.doctype;
        const isAdmin = roles.includes("Administrator");
        const isVendor = roles.includes("Hotpot Vendor");
        if (isVendor && !isAdmin) {
            $(".filter-selector").hide();
            setTimeout(() => {
                $('.filter-x-button').click();
                listview.filter_area.add([["Data Import", "owner", "=", frappe.session.user]]);
            }, 50);
        }
        if (!isAdmin) {
            listview.page.clear_menu();
            listview.page.clear_actions();
            listview.page.hide_menu();
            // listview.page.hide_actions_menu();
            listview.page.add_inner_button(__("Add Data Import", null, "Button in list view menu"), function () {
                if (!frappe.boot.read_only && listview.can_create) {
                    frappe.new_doc("Data Import");
                } else {
                    frappe.msgprint(__("You do not have permission to create a Hotpot User."));
                }
            });
            listview.toggle_actions_menu_button = function (toggle) {
                return
            }
        }
    },

};

