frappe.pages["load-wallet-balance"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Load Balance in Employee Wallet",
		single_column: true,
	});

	page.set_title_sub("Load Balance in Employee Wallet");

	//page.set_secondary_action("Refresh", () => page.refresh(), "refresh");
	page.start = 0;

	page.form = new mrxaudit.LoadEmployeeBalance(page);

	// page.refresh = function () {
	// 	page.form.clear();
	// };
};

mrxaudit.LoadEmployeeBalance = class LoadEmployeeBalance {
	constructor(page) {
		this.page = page;
		this.make_form();
	}

	// clear() {
	// 	this.form.clear();
	// 	if (this.form.fields_dict.coupon_count) {
	// 		this.form.replace_field("coupon_count", {
	// 			fieldname: "coupon_count",
	// 			label: __("Coupon Count"),
	// 			fieldtype: "Read Only",
	// 			hidden: true,
	// 		});
	// 	}
	// }

	make_form() {
		this.form = new frappe.ui.FieldGroup({
			fields: [
				{
					fieldname: "selected_employee",
					label: __("Select Employee"),
					fieldtype: "Link",
					options: "Hotpot User",
					get_query: () => {
						return {
							filters: {
								is_employee: 1,
							},
						};
					},
					onchange: () => {
						let selected_employee = this.form.get_value("selected_employee");

						// Check if the value has actually changed
						if (this.last_selected_employee === selected_employee) {
							return; // Do nothing if the value hasn't changed
						}

						this.last_selected_employee = selected_employee; // Update the last selected value

						if (selected_employee) {
							frappe.call({
								method: "frappe.client.get_value",
								args: {
									doctype: "Hotpot User",
									fieldname: "coupon_count",
									filters: { name: selected_employee },
								},
								callback: (r) => {
									if (r.message) {
										// Add or update the coupon_count field
										if (!this.form.fields_dict.coupon_count) {
											this.form.add_fields([
												{
													fieldname: "coupon_count",
													label: __("Coupon Count"),
													fieldtype: "Read Only",
													default: r.message.coupon_count || 0,
												},
												{
													fieldname: "load_balance",
													label: __("Load Balance"),
													fieldtype: "Button",
												},
											]);
											// Attach the click event for the Load Balance button
											if (this.form.fields_dict.load_balance) {
												this.form.fields_dict.load_balance.input.onclick =
													() => {
														this.load_balance_form();
													};
											}
										} else {
											this.form.replace_field("coupon_count", {
												fieldname: "coupon_count",
												label: __("Coupon Count"),
												fieldtype: "Read Only",
												hidden: false, // Hide the field instead of removing it
											});
											// Update the coupon_count field value
											this.form.set_value(
												"coupon_count",
												r.message.coupon_count || 0
											);
										}
									}
								},
							});
						} else {
							// Hide or reset the coupon_count field if no employee is selected
							if (this.form.fields_dict.coupon_count) {
								this.form.fields_dict.coupon_count.wrapper.style.display = "none";
							}
						}
					},
				},
				{
					fieldname: "loading_amount",
					label: __("Amount to Load"),
					fieldtype: "Currency",
					default: 0.0,
				},
			],
			body: this.page.body,
		});
		this.form.make();

		// Attach the click event for the Load Balance button
		if (this.form.fields_dict.load_balance) {
			this.form.fields_dict.load_balance.input.onclick = () => {
				this.load_balance_form();
			};
		}
	}

	load_balance_form() {
		let retval = this.validate();
		if (retval) {
			frappe.call({
				method: "hotpot.hotpot.page.load_wallet_balance.load_balance",
				args: this.form.get_values(),
				freeze: true,
				callback: (r) => {
					frappe.show_alert(
						{
							message: __("Success: Value Loaded in Employee Wallet"),
							indicator: "green",
						},
						5
					);
					this.form.clear();
					// Remove the coupon_count field if no employee is selected
					if (this.form.fields_dict.coupon_count) {
						if (this.form.fields_dict.coupon_count) {
							this.form.replace_field("coupon_count", {
								fieldname: "coupon_count",
								label: __("Coupon Count"),
								fieldtype: "Read Only",
								hidden: true, // Hide the field instead of removing it
							});
						}
					}
					this.last_selected_employee = null; // Reset the last selected employee
				},
			});
		}
	}

	validate() {
		let { selected_employee, loading_amount } = this.form.get_values();

		if (loading_amount == undefined || loading_amount == "" || loading_amount <= 0) {
			frappe.msgprint({
				message: __("Loading Amount should be greater than 0"),
				indicator: "orange",
				clear: true,
			});
			return false;
		}

		if (selected_employee == undefined) {
			frappe.msgprint({
				message: __("Select an Employee to load balance"),
				indicator: "orange",
				clear: true,
			});
			return false;
		}

		return true;
	}
};
