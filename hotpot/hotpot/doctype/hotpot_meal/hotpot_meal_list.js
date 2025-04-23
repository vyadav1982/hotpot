frappe.listview_settings["Hotpot Meal"] = {
    hide_name_column: true,

    onload: function (listview) {
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
        console.log(listview)
        if (!listview.datatable) {
            setTimeout(() => {
                applyColumnWidths(listview);
            }, 500);
        } else {
            applyColumnWidths(listview);
        }

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
    }
};

function applyColumnWidths(listview) {
    if (listview.datatable) {
        listview.datatable.options.columnWidths = {
            meal_title: 450,
            start_time: 150,
            end_time: 150,
            vendor_id: 120,
            is_special: 120,
            is_active: 120
        };
        listview.datatable.refresh();
    }
}

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