// Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hotpot Meal Category", {
    onload(frm) {
        updateLocalDescriptions(frm);
        const localStartTime = formatUtcToLocalObject(frm.doc.start_time);
		const localEndTime = formatUtcToLocalObject(frm.doc.end_time);
		
		frm.doc.start_time = localStartTime;
		frm.doc.end_time = localEndTime;

		frm.refresh_field("start_time");
		frm.refresh_field("end_time");
    },
    refresh(frm) {
        const userRoles = frappe.user_roles;
        const isAdmin = userRoles.includes("Administrator")
        if (!isAdmin) {
            frm.page.wrapper.find(".comment-box").css({'display':'none'});
            frm.page.hide_menu();
        }
    },
        start_time(frm) {
            updateLocalDescriptions(frm);
        },

        end_time(frm) {
            updateLocalDescriptions(frm);
        }
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

function formatUtcToLocalObject(utc_datetime) {
	if (!utc_datetime) return "";

	let utcIsoString = utc_datetime.replace(" ", "T") + "Z";

	let date = new Date(utcIsoString);

	let dd = String(date.getDate()).padStart(2, "0");
	let mm = String(date.getMonth() + 1).padStart(2, "0");
	let yyyy = date.getFullYear();

	let hh = String(date.getHours()).padStart(2, "0");
	let min = String(date.getMinutes()).padStart(2, "0");
	let ss = String(date.getSeconds()).padStart(2, "0");

	return `${yyyy}-${mm}-${dd} ${hh}:${min}:${ss}`;
}
