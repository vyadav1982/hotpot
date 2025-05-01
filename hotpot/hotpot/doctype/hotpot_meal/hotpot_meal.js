frappe.ui.form.on("Hotpot Meal", {
    refresh: function(frm) {
        const userRoles = frappe.user_roles;
        const isAdmin = userRoles.includes("Administrator") 
        const isHotpotAdmin=userRoles.includes("Hotpot Admin");
        if(!isAdmin || !isHotpotAdmin){
            frm.toggle_enable("coupons", false);
            frm.toggle_enable("ratings", false);
        }
        if(!isAdmin && !frm.doc.__islocal){
            frm.toggle_enable("vendor_id", false);
            frm.toggle_enable("start_time", false);
            frm.toggle_enable("end_time", false);
            frm.toggle_enable("meal_date", false);
        } 
        if(!isAdmin){
            frm.page.hide_menu();
            frm.toggle_display("repeat_type", false);
            frm.toggle_display("repeat_days", false);
            frm.toggle_display("approval_id", false);
        }  
        
    },
    onload(frm) {       
        updateLocalDescriptions(frm);
    },

    // start_time(frm) {
    //     updateLocalDescriptions(frm);
    // },

    // end_time(frm) {
    //     updateLocalDescriptions(frm);
    // }
});
function updateLocalDescriptions(frm) {
    if (frm.doc.start_time) {
        const localStartTime = formatUtcToLocal(frm.doc.start_time);
        frm.set_df_property('start_time', 'description', `Local Time: ${localStartTime}`);
    } else {
        frm.set_df_property('start_time', 'description', '');
    }

    if (frm.doc.end_time) {
        const localEndTime = formatUtcToLocal(frm.doc.end_time);
        frm.set_df_property('end_time', 'description', `Local Time: ${localEndTime}`);
    } else {
        frm.set_df_property('end_time', 'description', '');
    }
    if (frm.doc.meal_date) {
        const localDate = formatUtcToLocalDate(frm.doc.meal_date);
        frm.set_df_property('meal_date', 'description', `Local Date: ${localDate}`);
    } else {
        frm.set_df_property('meal_date', 'description', '');
    }
}

function formatUtcToLocalDate(utc_datetime) {
    if (!utc_datetime) return "";

    let user_timezone = frappe.sys_defaults.time_zone || Intl.DateTimeFormat().resolvedOptions().timeZone;

    let date = new Date(utc_datetime + "Z");
    return date.toLocaleDateString("en-GB", {
        timeZone: user_timezone,
        day: "2-digit",
        month: "short",
        year: "2-digit"
    });
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
