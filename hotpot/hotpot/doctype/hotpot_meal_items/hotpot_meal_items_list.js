frappe.listview_settings["Hotpot Meal Items"] = {
    hide_name_column: true,
    onload: function (listview) {
        const roles = frappe.user_roles;
        const doctype = this.doctype;
        const isAdmin = roles.includes("Administrator");
        if(!isAdmin) {

            listview.page.clear_menu();
            listview.page.clear_actions();
            listview.page.hide_menu();
            // listview.page.hide_actions_menu();
            listview.page.add_inner_button(__("Import"),  () => {
                frappe.set_route("list", "data-import", {
                    reference_doctype: doctype,
                });
            });
            listview.page.add_inner_button(__("Add Hotpot Meal Items", null, "Button in list view menu"), function () {
                if (!frappe.boot.read_only && listview.can_create) {
                    frappe.new_doc("Hotpot Meal Items");
                } else {
                    frappe.msgprint(__("You do not have permission to create a Hotpot Meal Items."));
                }
            });
           
        }
          
    },
    refresh: function (listview) {
        const roles = frappe.user_roles;
        const isAdmin = roles.includes("Administrator");
        const doctype = this.doctype;
        if(!isAdmin) {
            listview.page.clear_menu();
            listview.page.clear_actions();
            listview.page.hide_menu();
            // listview.page.hide_actions_menu();
            listview.page.add_inner_button(__("Import"),  () => {
                frappe.set_route("list", "data-import", {
                    reference_doctype: doctype,
                });
            });
            listview.page.add_inner_button(__("Add Hotpot Meal Items", null, "Button in list view menu"), function () {
                if (!frappe.boot.read_only && listview.can_create) {
                    frappe.new_doc("Hotpot Meal Items");
                } else {
                    frappe.msgprint(__("You do not have permission to create a Hotpot Meal Items."));
                }
            });
            listview.toggle_actions_menu_button =  function (toggle){
                return
            }
        }
    },
}