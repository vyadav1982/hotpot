frappe.ui.form.on("Hotpot Meal", {
	refresh: function (frm) {
		const userRoles = frappe.user_roles;
		const isAdmin = userRoles.includes("Administrator");
		const isHotpotAdmin = userRoles.includes("Hotpot Admin");
		const isVendor = userRoles.includes("Hotpot Vendor");

		frm.set_query("vendor_id", function () {
			return {
				filters: {
					is_vendor: 1,
				},
			};
		});

		frm.set_df_property("vendor_id", "only_select", true);

		if (!isAdmin) {
			frm.page.wrapper.find(".comment-box").css({ display: "none" });
			frm.page.hide_menu();
			frm.toggle_display("repeat_type", false);
			frm.toggle_display("repeat_days", false);
			frm.toggle_display("approval_id", false);

			if (frm.doc.__islocal == 1) {
				frm.toggle_display("start_time", false);
				frm.toggle_display("end_time", false);
				frm.toggle_display("meal_weight", false);
				frm.toggle_display("lead_time", false);
				frm.toggle_display("cancellation_time", false);
			}

			if (isVendor) {
				frm.toggle_display("coupons", false);
				frm.toggle_display("ratings", false);
			}
			if (isVendor && frm.doc.__islocal != 1) {
				frm.disable_form();
			}
			if (isVendor && frm.doc.__islocal == 1) {
				frm.toggle_display("vendor_id", false);
			}
			if (isHotpotAdmin && frm.doc.__islocal == 1) {
				frm.toggle_display("coupons", false);
				frm.toggle_display("ratings", false);
			}

			if(isVendor && !frm.doc.__islocal){
			    frm.toggle_display("vendor_id",false)
			    frm.disable_form()
			}

			if (!isHotpotAdmin) {
			    frm.toggle_enable("coupons", false);
			    frm.toggle_enable("ratings", false);
			}
			if (!frm.doc.__islocal) {
			    frm.toggle_enable("vendor_id", false);
			    frm.toggle_enable("start_time", false);
			    frm.toggle_enable("end_time", false);
			    frm.toggle_enable("meal_date", false);
			}
			else{
			    frm.toggle_enable("coupons", false);
			    frm.toggle_enable("ratings", false);
			    frm.toggle_display("start_time",false);
			    frm.toggle_display("end_time",false);
			    frm.toggle_display("lead_time",false)
			    frm.toggle_display("cancellation_time",false)
			    frm.toggle_display("meal_weight",false)
			}
		}
	},
	onload(frm) {
		frm.set_query("vendor_id", function () {
			return {
				filters: {
					is_vendor: 1,
				},
			};
		});

		frm.set_df_property("vendor_id", "only_select", true);
		updateLocalDescriptions(frm);
		const localStartTime = formatUtcToLocalObject(frm.doc.start_time);
		const localEndTime = formatUtcToLocalObject(frm.doc.end_time);

		console.log(frm.doc.start_time);
		console.log(localStartTime);

		frm.doc.start_time = localStartTime;
		frm.doc.end_time = localEndTime;

		frm.refresh_field("start_time");
		frm.refresh_field("end_time");
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
	if (frm.doc.meal_date) {
		const localDate = formatUtcToLocalDate(frm.doc.meal_date);
		frm.set_df_property("meal_date", "description", `Local Date: ${localDate}`);
	} else {
		frm.set_df_property("meal_date", "description", "");
	}
}

function formatUtcToLocalDate(utc_datetime) {
	if (!utc_datetime) return "";

	let user_timezone =
		frappe.sys_defaults.time_zone || Intl.DateTimeFormat().resolvedOptions().timeZone;

	let date = new Date(utc_datetime + "Z");
	return date.toLocaleDateString("en-GB", {
		timeZone: user_timezone,
		day: "2-digit",
		month: "short",
		year: "2-digit",
	});
}

function formatUtcToLocal(utc_datetime) {
	if (!utc_datetime) return "";

	let user_timezone =
		frappe.sys_defaults.time_zone || Intl.DateTimeFormat().resolvedOptions().timeZone;

	let date = new Date(utc_datetime + "Z");

	let localTime = date.toLocaleTimeString("en-US", {
		timeZone: user_timezone,
		hour: "2-digit",
		minute: "2-digit",
		hour12: true,
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