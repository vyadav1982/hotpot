frappe.listview_settings["Hotpot Approvals"] = {
    hide_name_column: true,
    onload: function (listview) {
        const roles = frappe.user_roles;
        const isAdmin = roles.includes("Administrator");
        if(!isAdmin) {

            listview.page.clear_menu();
            listview.page.clear_actions();
            listview.page.hide_menu();
            listview.page.hide_actions_menu();
           
        }
          
    },
    refresh: function (listview) {
        const roles = frappe.user_roles;
        const isAdmin = roles.includes("Administrator");
        if(!isAdmin) {
        listview.page.clear_menu();
            listview.page.clear_actions();
            listview.page.hide_menu();
            listview.page.hide_actions_menu();
            listview.toggle_actions_menu_button =  function (toggle){
                return
            }
        }
    },
    get_columns: function() {
        const columns = frappe.listview_settings['Hotpot Approvals'].__default_columns;

        // Filter out the column you want to remove
        return columns.filter(column =>
            column.df && column.df.fieldname !== "name"
        );
    }
}