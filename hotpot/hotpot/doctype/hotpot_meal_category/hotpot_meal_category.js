// Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hotpot Meal Category", {
	refresh(frm) {
		const userRoles = frappe.user_roles;
		const isAdmin = userRoles.includes("Administrator");
		if (!isAdmin) {
			frm.page.wrapper.find(".comment-box").css({ display: "none" });
			frm.page.hide_menu();
		}

		// On form load, populate local fields from UTC fields if local fields are empty
		if (frm.doc.start_time) {
			const localTime = convertUtcToLocal(frm.doc.start_time);
			frm.set_value("start_time_local", localTime);
		}

		if (frm.doc.end_time) {
			const localTime = convertUtcToLocal(frm.doc.end_time);
			frm.set_value("end_time_local", localTime);
		}

		// Ensure fields are properly configured for time picking
		setupTimeFields(frm);
	},

	start_time_local(frm) {
		// When local time changes, update the hidden UTC field
		if (frm.doc.start_time_local) {
			const utcTime = convertLocalToUtc(frm.doc.start_time_local);
			frm.set_value("start_time", utcTime);
			updateTimeDescription(frm, "start_time_local");
		} else {
			frm.set_value("start_time", "");
			frm.set_df_property("start_time_local", "description", "");
		}
	},

	end_time_local(frm) {
		// When local time changes, update the hidden UTC field
		if (frm.doc.end_time_local) {
			const utcTime = convertLocalToUtc(frm.doc.end_time_local);
			frm.set_value("end_time", utcTime);
			updateTimeDescription(frm, "end_time_local");
		} else {
			frm.set_value("end_time", "");
			frm.set_df_property("end_time_local", "description", "");
		}
	},

	validate(frm) {
		// Only update start_time if user provided a local value
		if (frm.doc.start_time_local) {
			frm.set_value("start_time", convertLocalToUtc(frm.doc.start_time_local));
		}

		// Only update end_time if user provided a local value
		if (frm.doc.end_time_local) {
			frm.set_value("end_time", convertLocalToUtc(frm.doc.end_time_local));
		}
	},
});

function setupTimeFields(frm) {
	// If using Time fields, ensure they work properly
	const startField = frm.get_field("start_time_local");
	const endField = frm.get_field("end_time_local");

	if (startField && startField.df.fieldtype === "Time") {
		// Time fields should work automatically
		console.log("Start time field is properly configured as Time field");
	}

	if (endField && endField.df.fieldtype === "Time") {
		// Time fields should work automatically
		console.log("End time field is properly configured as Time field");
	}
}

function convertLocalToUtc(local_time) {
	if (!local_time) return "";

	let localDate;

	// Handle different input formats
	if (local_time.includes(" ")) {
		// Full datetime format: "2024-01-01 14:30:00"
		localDate = new Date(local_time.replace(" ", "T"));
	} else if (local_time.includes(":")) {
		// Time only format: "14:30:00" or "14:30"
		const today = new Date().toISOString().split("T")[0]; // Get today's date
		localDate = new Date(`${today}T${local_time}`);
	} else {
		return "";
	}

	if (isNaN(localDate)) return "";

	// The key fix: localDate is already in local time, we just need to get its UTC representation
	// When we call getUTC methods, it gives us the UTC equivalent of the local time
	const yyyy = localDate.getUTCFullYear();
	const mm = String(localDate.getUTCMonth() + 1).padStart(2, "0");
	const dd = String(localDate.getUTCDate()).padStart(2, "0");
	const hh = String(localDate.getUTCHours()).padStart(2, "0");
	const min = String(localDate.getUTCMinutes()).padStart(2, "0");
	const ss = String(localDate.getUTCSeconds()).padStart(2, "0");

	return `${yyyy}-${mm}-${dd} ${hh}:${min}:${ss}`;
}

function convertUtcToLocal(utc_datetime) {
	if (!utc_datetime) return "";

	// Parse UTC datetime (add Z to indicate UTC)
	const utcDate = new Date(utc_datetime.replace(" ", "T") + "Z");
	if (isNaN(utcDate)) return "";

	// For Time fields, return only time portion
	const hh = String(utcDate.getHours()).padStart(2, "0");
	const min = String(utcDate.getMinutes()).padStart(2, "0");
	const ss = String(utcDate.getSeconds()).padStart(2, "0");

	return `${hh}:${min}:${ss}`;
}

function updateTimeDescription(frm, fieldname) {
	const fieldValue = frm.doc[fieldname];
	if (!fieldValue) return;

	const utcFieldName = fieldname.replace("_local", "");
	const utcValue = frm.doc[utcFieldName];

	if (utcValue) {
		const localDisplay = formatTimeForDisplay(fieldValue);
		const utcDisplay = formatTimeForDisplay(utcValue);
		frm.set_df_property(fieldname, "description", `Local: ${localDisplay}`);
	}
}

function formatTimeForDisplay(time_string) {
	if (!time_string) return "";

	let date;

	// Handle different time formats
	if (time_string.includes(" ")) {
		// Full datetime: "2024-01-01 14:30:00"
		date = new Date(time_string.replace(" ", "T"));
	} else if (time_string.includes(":")) {
		// Time only: "14:30:00"
		date = new Date(`1970-01-01T${time_string}`);
	} else {
		return time_string; // Return as-is if format is unknown
	}

	if (isNaN(date)) return time_string;

	const hours = date.getHours();
	const minutes = date.getMinutes();

	// Convert to 12-hour format
	const displayHours = hours % 12 || 12;
	const ampm = hours >= 12 ? "PM" : "AM";
	const displayMinutes = minutes.toString().padStart(2, "0");

	return `${displayHours}:${displayMinutes} ${ampm}`;
}
