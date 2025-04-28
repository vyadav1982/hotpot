frappe.listview_settings["Hotpot Meal Types"] = {
    hide_name_column: true,
    onload: function (listview) {
        const roles = frappe.user_roles;
        const isAdmin = roles.includes("Administrator");
        if(!isAdmin) {

            listview.page.clear_menu();
            listview.page.clear_actions();
            // listview.page.hide_menu();
            // listview.page.hide_actions_menu();
            listview.page.add_menu_item(__("Add Hotpot Meal Type", null, "Button in list view menu"), function () {
                if (!frappe.boot.read_only && listview.can_create) {
                    frappe.new_doc("Hotpot Meal Types");
                } else {
                    frappe.msgprint(__("You do not have permission to create a Hotpot Meal Type."));
                }
            });
           
        }
          
    },
    refresh: function (listview) {
        const roles = frappe.user_roles;
        const isAdmin = roles.includes("Administrator");
        if(!isAdmin) {
            listview.page.clear_menu();
            listview.page.clear_actions();
            // listview.page.hide_menu();
            // listview.page.hide_actions_menu();
            listview.page.add_menu_item(__("Add Hotpot Meal Type", null, "Button in list view menu"), function () {
                if (!frappe.boot.read_only && listview.can_create) {
                    frappe.new_doc("Hotpot Meal Types");
                } else {
                    frappe.msgprint(__("You do not have permission to create a Hotpot Meal Type."));
                }
            });
            listview.toggle_actions_menu_button =  function (toggle){
                return
            }
        }
    },
}