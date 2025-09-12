frappe.pages['meal-bulk-booking'].on_page_load = async function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Meal Bulk Booking',
		single_column: true
	});

	let container = $('<div></div>').appendTo(page.body);

	// -------------------------
	// Location dropdown
	let location_field = frappe.ui.form.make_control({
		df: { fieldname: 'location', label: 'Select Location', fieldtype: 'Select', options: [], reqd: 1 },
		parent: container,
		render_input: 1
	});
	location_field.refresh();

	// Vendor dropdown
	let vendor_field = frappe.ui.form.make_control({
		df: { fieldname: 'vendor', label: 'Select Vendor', fieldtype: 'Select', options: [], reqd: 1 },
		parent: container,
		render_input: 1
	});
	vendor_field.$input.prop('disabled', true); // initially disabled
	vendor_field.refresh();


	// Date picker
	let date_field = frappe.ui.form.make_control({
		df: { fieldname: 'meal_date', label: 'Select Date', fieldtype: 'Date', reqd: 1 },
		parent: container,
		render_input: 1
	});
	date_field.$input.prop('disabled', true);
	date_field.refresh();

	// Meals dropdown
	let meals_field = frappe.ui.form.make_control({
		df: { fieldname: 'meal', label: 'Select Meal', fieldtype: 'Select', options: [], reqd: 1 },
		parent: container,
		render_input: 1
	});
	meals_field.$input.prop('disabled', true);
	meals_field.refresh();

	// Employee search bar
	// let search_input = $('<input type="text" placeholder="Search Employees..." class="input-xs form-control mb-2">').appendTo(container);

	// Companies container
	let companies_container = $('<div class="companies-container mb-3"></div>').appendTo(container);

	// Booking button
	let book_btn = $('<button class="btn btn-primary">Book</button>').appendTo(container);

	let userId = null;

	// -------------------------
	// Fetch user first
	async function fetchUser() {
		try {
			let response = await frappe.call({
				method: "hotpot.api.users.get_hotpot_user_by_email",
				type: "GET",
			});
			if (response.message) {
				userId = response.message.name;
				fetchLocations();
			} else {
				alert("Could not find user.");
			}
		} catch (error) {
			console.error("Error fetching user:", error);
			alert("Failed to load user.");
		}
	}

	// -------------------------
	// Fetch locations
	async function fetchLocations() {
		try {
			const response = await frappe.call({
				method: "frappe.client.get_list",
				args: {
					doctype: "Company Locations",
					fields: ["name", "location_name"],
					limit_page_length: 100
				}
			});

			const locations = response.message || [];
			location_field.df.options = [''].concat(locations.map(loc => loc.name));
			location_field.refresh();
		} catch (error) {
			console.error("Error fetching locations:", error);
			alert("Failed to retrieve locations.");
		}
	}

	// -------------------------
	// Fetch vendors when location changes
	location_field.$input.on('change', async function () {
		let location = location_field.get_value();
		if (!location) {
			vendor_field.$input.prop('disabled', true).val('');
			return;
		}

		vendor_field.$input.prop('disabled', false);

		try {
			let vendorSelect = vendor_field.$input[0]; // get native <select> element
			vendorSelect.innerHTML = '<option value="">Loading...</option>';

			const filters = JSON.stringify([
				["is_active", "=", 1],
				["location", "=", location],
				["is_vendor", "=", 1]
			]);

			const fields = JSON.stringify(["name", "full_name"]);

			const response = await fetch(
				`/api/v2/document/Hotpot User?filters=${encodeURIComponent(filters)}&fields=${encodeURIComponent(fields)}`,
				{
					method: "GET",
					headers: {
						"Content-Type": "application/json",
					},
				}
			);

			const data = await response.json();

			// Reset vendor options
			vendorSelect.innerHTML = '<option value="">Select Vendor</option>';

			if (data.data && data.data.length > 0) {
				data.data.forEach(vendor => {
					let option = document.createElement("option");
					option.value = vendor.name;
					option.textContent = vendor.full_name;
					vendorSelect.appendChild(option);
				});
			} else {
				let option = document.createElement("option");
				option.value = "";
				option.textContent = "No vendors found";
				vendorSelect.appendChild(option);
			}

			// reset dependent fields
			date_field.$input.prop('disabled', true).val('');
			meals_field.$input.prop('disabled', true).val('');

		} catch (err) {
			console.error("Error fetching vendors:", err);
			vendor_field.$input.prop('disabled', true).val('');
		}
	});


	// Enable date picker when vendor is selected
	vendor_field.$input.on('change', function () {
		let vendor = vendor_field.get_value();
		date_field.$input.prop('disabled', !vendor).val('');
		meals_field.$input.prop('disabled', true).val('');
	});

	// Fetch meals when vendor and date are selected
	let last_date_value = null;

	date_field.$input.on('change', async function () {
		let vendor = vendor_field.get_value();
		let date = date_field.get_value();

		// Prevent duplicate triggers
		if (date === last_date_value) return;
		last_date_value = date;

		if (!vendor || !date) {
			meals_field.$input.prop('disabled', true).val('');
			return;
		}

		meals_field.$input.prop('disabled', true);
		try {
			let response = await frappe.call({
				method: "hotpot.api.meal.get_meals",
				args: { vendor_id: vendor, date: date },
				type: "GET",
			});

			let meals = response.data || [];
			meals_field.df.options = ['']
				.concat(meals.map(m => ({ label: m.meal_title, value: m.name })));
			meals_field.refresh();
			meals_field.$input.prop('disabled', meals.length === 0);

			if (meals.length === 0) {
				frappe.msgprint("No meal found.");
			}
		} catch (error) {
			console.error(error);
			meals_field.$input.prop('disabled', true).val('');
			frappe.msgprint("Error in fetching meal.");
		}
	});


	// -------------------------
	// Load companies
	function loadCompanies() {
		frappe.call({
			method: 'frappe.client.get_list',
			args: { doctype: 'Company', fields: ['name'] },
			callback: function (res) {
				companies_container.empty();
				res.message.forEach(company => {
					let company_div = $(`
                        <div class="company mb-2" data-company="${company.name}">
                            <input type="checkbox" class="company-checkbox"> ${company.name}
                            <input type="checkbox" class="select-all-emp ml-2"> Select All
                            <div class="employees ml-4 mt-1"></div>
                        </div>
                    `);
					companies_container.append(company_div);
				});
			}
		});
	}

	// -------------------------
	// Lazy load employees
	companies_container.on('change', '.company-checkbox', function () {
		let company_div = $(this).closest('.company');
		let checked = $(this).is(':checked');
		let company_name = company_div.data('company');
		let emp_container = company_div.find('.employees');

		if (!company_div.data('loaded')) {
			frappe.call({
				method: 'frappe.client.get_list',
				args: {
					doctype: 'Employee',
					fields: ['first_name', 'name'],
					filters: { company: company_name, status: 'Active' },
					limit_page_length: 1000   // fetch all employees
				},
				callback: function (res) {
					let employees = res.message || [];
					emp_container.empty(); // clear any old data

					// Wrap in a row for flex layout
					let row = $('<div class="employee-row" style="display:flex; flex-wrap:wrap; gap:20px;"></div>');

					// Split into columns of 20
					for (let i = 0; i < employees.length; i += 20) {
						let chunk = employees.slice(i, i + 20);
						let col_div = $('<div class="employee-col" style="flex:0 0 auto;"></div>');

						chunk.forEach(emp => {
							col_div.append(`
                            <div>
                                <input type="checkbox" class="employee-checkbox" data-employee="${emp.name}" ${checked ? "checked" : ""}>
                                ${emp.first_name}
                            </div>
                        `);
						});

						row.append(col_div);
					}

					emp_container.append(row);
					company_div.data('loaded', true);
				}
			});
		} else {
			// Toggle existing employees
			emp_container.find('.employee-checkbox').prop('checked', checked);
		}
	});



	// -------------------------
	// Select All per company
	companies_container.on('change', '.select-all-emp', function () {
		let company_div = $(this).closest('.company');
		let checked = $(this).is(':checked');
		company_div.find('.employees .employee-checkbox').prop('checked', checked);
		company_div.find('.company-checkbox').prop('checked', checked);
	});

	// -------------------------
	// Server-side employee search
	// search_input.on('input', function () {
	// 	let query = $(this).val();
	// 	frappe.call({
	// 		method: 'your_app.api.search_employees',
	// 		args: { search_text: query },
	// 		callback: function (res) {
	// 			$('.employees').empty();
	// 			let employees_by_company = {};
	// 			res.message.forEach(emp => {
	// 				if (!employees_by_company[emp.company]) employees_by_company[emp.company] = [];
	// 				employees_by_company[emp.company].push(emp);
	// 			});
	// 			for (let company_name in employees_by_company) {
	// 				let company_div = $(`.company[data-company="${company_name}"]`);
	// 				let emp_container = company_div.find('.employees');
	// 				employees_by_company[company_name].forEach(emp => {
	// 					emp_container.append(`<div>
	//                         <input type="checkbox" class="employee-checkbox" data-employee="${emp.name}">${emp.employee_name}
	//                     </div>`);
	// 				});
	// 			}
	// 		}
	// 	});
	// });
	// -------------------------
	// Book button
	book_btn.on('click', function () {
		let meal = meals_field.get_value();
		if (!meal) return frappe.msgprint('Please select a meal!');

		let selected_employees = [];
		$('.employee-checkbox:checked').each(function () {
			selected_employees.push($(this).data('employee'));
		});

		if (selected_employees.length === 0) return frappe.msgprint('Please select at least one employee!');

		frappe.call({
			method: 'hotpot.api.coupons.generate_for_all',
			args: { docname: meal, employees: selected_employees },
			callback: function (r) {
				if (r.message.status === "success") {
					frappe.msgprint('Booking successful!');
				}
				else {
					let errors = r.message.errors;

					// Join array into single string with line breaks
					let errorMsg = errors.join("<br>");

					frappe.msgprint(errorMsg);
				}
			}
		});
	});

	// -------------------------
	// Initialize
	await fetchUser(); // only if user exists, locations will be fetched
	loadCompanies();
};
