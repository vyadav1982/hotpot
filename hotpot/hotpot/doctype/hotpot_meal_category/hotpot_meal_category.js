// Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hotpot Meal Category", {
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

