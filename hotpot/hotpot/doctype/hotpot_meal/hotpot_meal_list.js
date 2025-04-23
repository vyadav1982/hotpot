frappe.listview_settings["Hotpot Meal"] = {
    hide_name_column: true,
    onload: function (listview) {
        const doctype = this.doctype;
        listview.page.clear_menu();
        listview.page.clear_actions();
        listview.page.hide_menu();
        listview.page.hide_actions_menu();
        listview.page.add_button(__("Import", null, "Button in list view menu"), function () {
            frappe.set_route("list", "data-import", {
                reference_doctype: doctype,
            })})
        listview.page.add_button(__("Add Hotpot Meal", null, "Button in list view menu"), function () {
            if (!frappe.boot.read_only && listview.can_create) {
                frappe.new_doc("Hotpot Meal");
            } else {
                frappe.msgprint(__("You do not have permission to create a Hotpot Meal."));
            }
        });
            
            

        const allowedFields = [
            "meal_title", "start_time", "end_time", "meal_items",
            "repeat_type", "repeat_days", "meal_weight", "vendor_id",
            "is_special", "is_active"
        ];

        listview.columns = listview.columns.filter(column =>
            column.df && allowedFields.includes(column.df.fieldname)
        );

        listview.settings.formatters = {
            start_time: formatUtcToLocal,
            end_time: formatUtcToLocal,
            repeat_type: formatRepeatType,
            repeat_days: formatRepeatDays,
            is_special: formatIsSpecial
        };
    },
    refresh: function (listview) {
        listview.page.clear_menu();
        listview.page.clear_actions();
        listview.page.hide_menu();
        listview.page.hide_actions_menu();
        listview.toggle_actions_menu_button =  function (toggle){
            return
        }
    }
};

function formatIsSpecial(value) {
    return value == 1 ? "Yes" : "No";
}

function formatRepeatDays(value) {
    if (value && value.startsWith('"') && value.endsWith('"')) {
        value = value.slice(1, -1);
    }
    return value && value.trim() !== "" ? value : "-----";
}

function formatRepeatType(value) {
    return {
        daily: "Daily",
        once: "Once",
        specific_days: "Specific Days"
    }[value] || value;
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