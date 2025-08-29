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
		frm.add_custom_button(__('Refresh Fetched Data'), function () {
			frappe.call({
				method: 'hotpot.api.meal.refresh_fetched_data',
				args: { docname: frm.doc.name },
				callback: function (r) {
					frm.reload_doc();
				}
			});
		});

		if (!isAdmin) {
			frm.page.wrapper.find(".comment-box").css({ display: "none" });
			frm.page.clear_menu();
			frm.page.clear_actions();
			frm.page.hide_menu();
			frm.toggle_display("repeat_type", false);
			frm.toggle_display("repeat_days", false);
			frm.toggle_display("approval_id", false);
			frm.toggle_display("menu_items", false);
			frm.toggle_display("ratings", false);
			// frm.toggle_display("coupons", false);


			if (frm.doc.__islocal == 1) {
				frm.toggle_display("start_time", false);
				frm.toggle_display("end_time", false);
				frm.toggle_display("meal_weight", false);
				frm.toggle_display("lead_time", false);
				frm.toggle_display("cancellation_time", false);
			}

			if (isVendor) {
				let msg = `
					⚠️ <b>Heads up!</b><br>
					If you're only changing the <b>Buffer Coupon Count</b>.  
					This <b>won’t create any new request</b> and <span style="color:red;">may affect the Remaining Coupon Count</span>.  
					Please double-check before saving ✅
					`;

				frm.dashboard.clear_headline();
				frm.dashboard.set_headline_alert(msg, "blue");

				frm.toggle_display("coupons", false);
				frm.toggle_display("ratings", false);
			}
			// if (isVendor && frm.doc.__islocal != 1) {
			// 	frm.disable_form();
			// }
			if (isVendor && frm.doc.__islocal == 1) {
				frm.toggle_display("vendor_id", false);
			}
			if (isHotpotAdmin && frm.doc.__islocal == 1) {
				frm.toggle_display("coupons", false);
				frm.toggle_display("ratings", false);
			}

			if (isVendor && !frm.doc.__islocal) {
				frm.toggle_display("vendor_id", false);

				frm.fields_dict && Object.keys(frm.fields_dict).forEach(fieldname => {
					frm.set_df_property(fieldname, "read_only", 1);
				});

				const editable_fields = [
					"meal_title",
					"meal_items",
					"meal_date",
					"buffer_coupon_count"
				];
				let coupons = false;

				if (frm.doc.coupons && frm.doc.coupons.length > 0) {
					for (let i = 0; i < frm.doc.coupons.length; i++) {
						const coupon = frm.doc.coupons[i];
						if (coupon.coupon_status == 1 || coupon.coupon_status == 0) {
							coupons = true;
							break;
						}
					}
				}

				if (!coupons) {
					editable_fields.forEach(field => {
						frm.set_df_property(field, "read_only", 0);
					});
					return;
				}
				const approval_id = frm.doc.approval_id;

				if (approval_id) {
					frappe.db.get_doc('Hotpot Approvals', approval_id)
						.then(doc => {

							if (doc.is_active === 1 && doc.approval_status === "Pending") {
								frappe.msgprint("Approval is pending. You cannot edit this document.");
								frm.disable_save();
							}
						})
						.catch(err => {
							frappe.msgprint(`Error fetching document: ${err.message}`);
							console.error(err);
						});
				} else {
					editable_fields.forEach(field => {
						frm.set_df_property(field, "read_only", 0);
					});

					let buttonAdded = false;
					editable_fields.forEach(fieldname => {
						const field = frm.fields_dict[fieldname];
						if (field) {
							field.df.onchange = () => {
								if (!buttonAdded) {
									buttonAdded = true;
									frm.disable_save();

									frm.page.add_inner_button("Create Request", () => {
										frappe.prompt(
											[
												{
													label: 'Request Reason',
													fieldname: 'reason',
													fieldtype: 'Data',
													reqd: 1
												}
											],
											(values) => {
												frappe.db.get_doc("Hotpot Meal", frm.doc.name).then(original_doc => {
													const draft_payload = {};
													const editable_fields = [
														"meal_title",
														"meal_items",
														"meal_date",
														"buffer_coupon_count"
													];

													editable_fields.forEach(field => {
														let current_value = frm.get_field(field).get_value();
														let original_value = original_doc[field];

														if ((current_value ?? "").toString().trim() !== (original_value ?? "").toString().trim()) {
															draft_payload[field] = current_value;
															draft_payload[`old_${field}`] = original_value;
														}
													});

													if ("buffer_coupon_count" in draft_payload) {
														frappe.call({
															method: "frappe.client.set_value",
															args: {
																doctype: "Hotpot Meal",
																name: frm.doc.name,
																fieldname: "buffer_coupon_count",
																value: draft_payload["buffer_coupon_count"]
															},
															callback: function (r) {
																if (!r.exc) {
																	frappe.msgprint("✅ Buffer Coupon Count updated successfully!");
																}
															}
														});

														delete draft_payload["buffer_coupon_count"];
														delete draft_payload["old_buffer_coupon_count"];
													}

													if (Object.keys(draft_payload).length === 0) {
														frappe.msgprint("⚠️ No actual changes detected. Approval request not created.");
														return;
													}


													const new_approval = {
														request_type: "Meal Edit",
														requested_by: frappe.session.user,
														meal_id: frm.doc.name,
														description: values.reason
													};

													frappe.call({
														method: "frappe.client.insert",
														args: {
															doc: {
																doctype: "Hotpot Approvals",
																...new_approval
															}
														},
														callback: function (response) {
															if (!response.exc) {
																frappe.msgprint(`Request Created with reason: ${values.reason}. To edit the fields, please wait for approval.`);
																const approval_id = response.message.name;
																const meal_id = frm.doc.name;
																frappe.call({
																	method: "frappe.client.insert",
																	args: {
																		doc: {
																			doctype: "Hotpot Draft Meal",
																			meal: meal_id,
																			approval: approval_id,
																			new_values: JSON.stringify(draft_payload)
																		}
																	},
																	callback: function (r) {
																		if (!r.exc) {
																			// frappe.msgprint("Draft meal created successfully.");
																		} else {
																			frappe.msgprint("Failed to create draft meal.");
																		}
																	}
																});

																editable_fields.forEach(field => {
																	frm.set_df_property(field, "read_only", 1);
																});
																frm.disable_save();

																// Optionally refresh or update approval_id field
																// frm.set_value("approval_id", response.message.name);
																// frm.refresh_fields();
															} else {
																frappe.msgprint("Failed to create request. Please try again.");
															}
														}
													});
												});
											},
											'Create Request',
											'Create'
										);
									});
								}

							};
						}

					});
				}

				frm.refresh_fields();
			}

			if (!isHotpotAdmin) {
				frm.toggle_enable("coupons", false);
				frm.toggle_enable("ratings", false);
			}
			if (!frm.doc.__islocal) {
				frm.toggle_enable("vendor_id", false);
				frm.toggle_enable("start_time", false);
				frm.toggle_enable("end_time", false);
				// frm.toggle_enable("meal_date", false);
			}
			else {
				frm.toggle_enable("coupons", false);
				frm.toggle_enable("ratings", false);
				frm.toggle_display("start_time", false);
				frm.toggle_display("end_time", false);
				frm.toggle_display("lead_time", false)
				frm.toggle_display("cancellation_time", false)
				frm.toggle_display("meal_weight", false)
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