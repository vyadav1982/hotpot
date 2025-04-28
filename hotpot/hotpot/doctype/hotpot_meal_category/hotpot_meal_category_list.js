frappe.listview_settings["Hotpot Meal Category"] = {
    hide_name_column: true,
    onload: function (listview) {
        const roles = frappe.user_roles;
        const isAdmin = roles.includes("Administrator");
        if(!isAdmin) {

            listview.page.clear_menu();
            listview.page.clear_actions();
            // listview.page.hide_menu();
            // listview.page.hide_actions_menu();
            listview.page.add_menu_item(__("Add Hotpot Meal Category", null, "Button in list view menu"), function () {
                if (!frappe.boot.read_only && listview.can_create) {
                    frappe.new_doc("Hotpot Meal Category");
                } else {
                    frappe.msgprint(__("You do not have permission to create a Hotpot Meal Category."));
                }
            });
           
        }
        listview.settings.formatters = {
            start_time: formatUtcToLocal,
            end_time: formatUtcToLocal,
        };
          
    },
    refresh: function (listview) {
        const roles = frappe.user_roles;
        const isAdmin = roles.includes("Administrator");
        if(!isAdmin) {
            listview.page.clear_menu();
            listview.page.clear_actions();
            // listview.page.hide_menu();
            // listview.page.hide_actions_menu();
            listview.page.add_menu_item(__("Add Hotpot Meal Category", null, "Button in list view menu"), function () {
                if (!frappe.boot.read_only && listview.can_create) {
                    frappe.new_doc("Hotpot Meal Category");
                } else {
                    frappe.msgprint(__("You do not have permission to create a Hotpot Meal Category."));
                }
            });
            listview.toggle_actions_menu_button =  function (toggle){
                return
            }
        }
    },
}
function formatUtcToLocal(utc_datetime) {
    if (!utc_datetime) return "";

    let user_timezone = frappe.sys_defaults.time_zone || Intl.DateTimeFormat().resolvedOptions().timeZone;

    let date = new Date(utc_datetime + "Z");

    let localTime = date.toLocaleTimeString("en-US", {
        timeZone: user_timezone,
        hour: "2-digit",
        minute: "2-digit",
        hour12: true
    });

    return localTime;
}