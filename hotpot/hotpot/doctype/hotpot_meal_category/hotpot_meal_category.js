// Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hotpot Meal Category", {
	onload(frm) {
		updateLocalDescriptions(frm);
		if (frm.doc.start_time) {
			const localStart = formatUtcToLocalObject(frm.doc.start_time);
			frm.set_value("start_time", localStart);
		}
		if (frm.doc.end_time) {
			const localEnd = formatUtcToLocalObject(frm.doc.end_time);
			frm.set_value("end_time", localEnd);
		}
	},
	validate(frm) {
		// Convert back from local to UTC before save
		if (frm.doc.start_time) {
			const utcStart = formatLocalToUtcString(frm.doc.start_time);
			frm.set_value("start_time", utcStart);
		}
		if (frm.doc.end_time) {
			const utcEnd = formatLocalToUtcString(frm.doc.end_time);
			frm.set_value("end_time", utcEnd);
		}
	},
	refresh(frm) {
		const userRoles = frappe.user_roles;
		const isAdmin = userRoles.includes("Administrator");
		if (!isAdmin) {
			frm.page.wrapper.find(".comment-box").css({ display: "none" });
			frm.page.hide_menu();
		}
	},
	start_time(frm) {
		updateLocalDescriptions(frm);
	},

	end_time(frm) {
		updateLocalDescriptions(frm);
	},
});

function updateLocalDescriptions(frm) {
	if (frm.doc.start_time) {
		const localStartTime = formatUtcToLocal(frm.doc.start_time);
		frm.set_df_property("start_time", "description", `Local Time: ${localStartTime}`);
	} else {
		frm.set_df_property("start_time", "description", "");
	}

	if (frm.doc.end_time) {
		const localEndTime = formatUtcToLocal(frm.doc.end_time);
		frm.set_df_property("end_time", "description", `Local Time: ${localEndTime}`);
	} else {
		frm.set_df_property("end_time", "description", "");
	}
}

function formatUtcToLocal(utc_datetime) {
	if (!utc_datetime) return "";

	const date = new Date(utc_datetime.replace(" ", "T") + "Z");
	const localTime = date.toLocaleTimeString("en-US", {
		hour: "2-digit",
		minute: "2-digit",
		hour12: true,
	});
	return localTime;
}

function formatUtcToLocalObject(utc_datetime) {
	if (!utc_datetime) return "";

	const date = new Date(utc_datetime.replace(" ", "T") + "Z");

	const yyyy = date.getFullYear();
	const mm = String(date.getMonth() + 1).padStart(2, "0");
	const dd = String(date.getDate()).padStart(2, "0");
	const hh = String(date.getHours()).padStart(2, "0");
	const min = String(date.getMinutes()).padStart(2, "0");
	const ss = String(date.getSeconds()).padStart(2, "0");

	return `${yyyy}-${mm}-${dd} ${hh}:${min}:${ss}`;
}

function formatLocalToUtcString(local_datetime) {
	if (!local_datetime) return "";

	const localDate = new Date(local_datetime.replace(" ", "T"));
	if (isNaN(localDate)) return "";

	const yyyy = localDate.getUTCFullYear();
	const mm = String(localDate.getUTCMonth() + 1).padStart(2, "0");
	const dd = String(localDate.getUTCDate()).padStart(2, "0");
	const hh = String(localDate.getUTCHours()).padStart(2, "0");
	const min = String(localDate.getUTCMinutes()).padStart(2, "0");
	const ss = String(localDate.getUTCSeconds()).padStart(2, "0");

	return `${yyyy}-${mm}-${dd} ${hh}:${min}:${ss}`;
}
