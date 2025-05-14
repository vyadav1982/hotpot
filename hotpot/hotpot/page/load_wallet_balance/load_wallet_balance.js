frappe.pages["load-wallet-balance"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Load Balance in Employee Wallet",
		single_column: true,
	});

	page.set_title_sub("Load Balance in Employee Wallet");

	page.set_secondary_action("Refresh", () => page.refresh(), "refresh");
	page.start = 0;

	page.form = new mrxaudit.LoadEmployeeBalance(page);

	page.refresh = function () {
		page.form.clear();
	};
};

mrxaudit.LoadEmployeeBalance = class LoadEmployeeBalance {
	constructor(page) {
		this.page = page;
		this.make_form();
	}

	clear() {
		this.form.clear();
	}

	make_form() {
		this.form = new frappe.ui.FieldGroup({
			fields: [
				{
					fieldname: "selected_employee",
					label: __("Select Employee"),
					fieldtype: "Link",
					options: "Hotpot User",
				},
				{
					fieldname: "loading_amount",
					label: __("Amount to Load"),
					fieldtype: "Currency",
					default: 0.0,
				},
				{
					fieldname: "load_balance",
					label: __("Load Balance"),
					fieldtype: "Button",
				},
			],
			body: this.page.body,
		});
		this.form.make();
		this.form.fields_dict.load_balance.input.onclick = () => {
			this.load_balance_form();
		};
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
