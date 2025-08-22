frappe.pages["generate-guest-qr"].on_page_load = function (wrapper) {
	var userId;
	var coupons;
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Guest QR Generation",
		single_column: true,
	});
	function loadScript(url, callback) {
		let script = document.createElement("script");
		script.type = "text/javascript";
		script.src = url;

		script.onload = function () {
			if (callback) callback();
		};

		document.head.appendChild(script);
	}

	loadScript("https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js", function () {
		console.log("QR Code library loaded successfully!");
	});

	$(wrapper).append(`
        <script type="module" src="generate_guest_qr.js"></script>
        <div class="container">
            <div class="row justify-content-center">
			 	<div class="form-group col-md-4">
                    <label for="locationSelect">Location Name:</label>
                    <select id="locationSelect" class="form-control">
                        <option value="">Select Location</option>
                    </select>
                </div>
                <div class="form-group col-md-4">
                    <label for="vendorSelect">Vendor Name:</label>
                    <select id="vendorSelect" class="form-control">
                        <option value="">Select Vendor</option>
                    </select>
                </div>
                <div class="form-group col-md-4">
                    <label for="datePicker">Date:</label>
                    <input type="date" id="datePicker" class="form-control" value="${
						new Date().toISOString().split("T")[0]
					}">
                </div>
            </div>

            <div class="row justify-content-center">
                <div class="form-group col-md-6">
                    <label for="mealSelect">Meal:</label>
                    <select id="mealSelect" class="form-control" disabled>
                        <option value="">Select Meal</option>
                    </select>
                </div>
                <div class="form-group col-md-6">
                    <label for="quantity">Quantity:</label>
                    <div class="input-group">
                        <button class="btn btn-outline-secondary" id="decreaseQty">-</button>
                        <input type="number" id="quantity" class="form-control text-center" style="width: 50px;" value="1" min="1">
                        <button class="btn btn-outline-secondary" id="increaseQty">+</button>
                    </div>
                </div>
            </div>

            <div id="emailFields" class="d-flex flex-column align-items-center">
            <div class="form-group" style="width: 40%;">
                <label for="email1">Email:</label>
                <input type="email" id="email1" class="form-control" placeholder="Enter email">
            </div>
        </div>

        <div class="d-flex justify-content-center">
            <button class="btn btn-primary" id="generateQR">Send QR</button>
        </div>
        <div id="qrContainer" class="mt-3 text-center hidden"></div>
        <div class="d-flex align-items-center mt-3">
            <div class="text-center">
                <label for="prevDatePicker">Select Date:</label>
                <input type="date" id="prevDatePicker" value="${
					new Date().toISOString().split("T")[0]
				}" class="form-control" style="width: 150px; display: inline-block;">
            </div>
            <button class="btn btn-secondary ml-3" id="refreshTable">Refresh Table</button>
        </div>
        <table class="table table-bordered mt-3" id="couponTable" style="margin: 20px; padding: 15px;">
            <thead>
                <tr>
                    <th>Meal Title</th>
                    <th>Coupon Date</th>
                    <th>Vendor Name</th>
                    <th>Created On</th>
					<th>Email</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    `);

	function updateEmailFields() {
		let qty = parseInt($("#quantity").val());
		let emailContainer = $("#emailFields");

		let existingEmails = {};
		emailContainer.find("input[type='email']").each(function () {
			existingEmails[$(this).attr("id")] = $(this).val();
		});

		emailContainer.empty();

		for (let i = 1; i <= qty; i++) {
			let emailId = `email${i}`;
			let savedValue = existingEmails[emailId] || "";

			emailContainer.append(`
                <div class="form-group" style="width: 40%;">
                    <label for="${emailId}">Email ${i}:</label>
                    <input type="email" id="${emailId}" class="form-control" placeholder="Enter email" value="${savedValue}">
                </div>
            `);
		}
	}

	$(document).ready(function () {
		const today = new Date().toISOString().split("T")[0];
		const datePicker = document.getElementById("datePicker");
		datePicker.value = today;
		datePicker.min = today;
		fetchLocations();

		$("#locationSelect").on("change", function () {
			const location = $(this).val();
			if (location) {
				console.log('if')
				fetchVendors(location);
			} else {
				$("#vendorSelect").html('<option value="">Select Vendor</option>');
			}
		});
		// fetchVendors();
		fetchUser();
	});

	$("#vendorSelect, #datePicker").on("change", function () {
		let vendor = $("#vendorSelect").val();
		let date = $("#datePicker").val();
		$("#mealSelect").prop("disabled", !(vendor && date));
	});

	$("#increaseQty").click(() => {
		let qty = parseInt($("#quantity").val());
		$("#quantity").val(qty + 1);
		updateEmailFields();
	});

	$("#decreaseQty").click(() => {
		let qty = parseInt($("#quantity").val());
		if (qty > 1) $("#quantity").val(qty - 1);
		updateEmailFields();
	});
	$("#vendorSelect, #datePicker, #mealSelect").on("input change", function () {
		$("#generateQR").prop(
			"disabled",
			!($("#vendorSelect").val() && $("#datePicker").val() && $("#mealSelect").val())
		);
	});

	$("#generateQR").click(async () => {
		let emails = [];
		let isValid = true;
		$("#emailFields input").each(function () {
			let email = $(this).val().trim();
			if (email) emails.push(email);
			else {
				alert("Please enter all emails");
				isValid = false;
				return false;
			}
		});
		if (!isValid) return;

		let qrData = {
			vendor: $("#vendorSelect").val(),
			date: $("#datePicker").val(),
			meal: $("#mealSelect").val(),
			quantity: $("#quantity").val(),
		};
		var meal_title = $("#mealSelect option:selected").text();

		for (let key in qrData) {
			if (!qrData[key] || qrData[key].toString().trim() === "") {
				isValid = false;
				alert(`Please fill in the ${key} field`);
				return false;
			}
		}
		if (!isValid) return;
		if (!userId) {
			isValid = false;
			alert("User Not found");
			return false;
		}
		if (!isValid) return;
		let d = {
			meal_id: $("#mealSelect").val(),
			date: $("#datePicker").val(),
			guest: true,
			qty: $("#quantity").val(),
			email: emails,
		};

		try {
			var couponGenerated = await generateCoupon(d);
			if (!couponGenerated) return;
		} catch (error) {
			console.error("Error generating coupon:", error);
			return;
		}
		let coupons = couponGenerated;
		if (!coupons || coupons.length === 0) {
			alert("No coupons generated.");
			return;
		}

		// try {
		// 	let response = await frappe.call({
		// 		method: "hotpot.api.coupons.get_admin_guest_coupon",
		// 		type: "GET",
		// 		args: {
		// 			date: $("#datePicker").val(),
		// 			qty: $("#quantity").val(),
		// 		},
		// 	});
		// 	console.log(response);
		// 	if (response.status === false) {
		// 		alert(response.message);
		// 		return;
		// 	} else {
		// 		coupons = response.data;
		// 	}
		// } catch (error) {
		// 	console.error("Error in fetching coupon:", error);
		// 	alert("Failed to fetch coupons. Please try again.");
		// 	return;
		// }

		let unsentEmails = [];

		let sendPromises = [];

		for (let i = 0; i < emails.length; i++) {
			if (i >= coupons.length) {
				unsentEmails.push(emails[i]);
				continue;
			}

			// let coupon = coupons[i];
			// let qrData = `hotpot${coupon},${$("#mealSelect").val()},${userId}`;

			let qrContainer = document.createElement("div");
			// let qrCode = new QRCode(qrContainer, {
			// 	text: qrData,
			// 	width: 128,
			// 	height: 128,
			// });

			let promise = new Promise((resolve, reject) => {
				setTimeout(() => {
					let qrImage = qrContainer.querySelector("img");
					if (!qrImage) {
						console.error(`QR Code image not found for ${emails[i]}`);
						unsentEmails.push(emails[i]);
						return reject(`QR not generated for ${emails[i]}`);
					}

					const rawDate = $("#datePicker").val();
					const dateObj = new Date(rawDate);

					const day = dateObj.getDate();
					const month = dateObj.toLocaleString("default", { month: "short" });
					const year = dateObj.getFullYear().toString().slice(-2);

					const formattedDate = `${day} ${month} ${year}`;

					let qrLink = qrImage.src;

					frappe.call({
						method: "hotpot.utils.email.send_email",
						args: {
							template_name: "qr_email",
							to_email: emails[i],
							context: JSON.stringify({
								meal_title: meal_title,
							}),
							subject: `Your Meal QR Code - ${meal_title} on ${formattedDate}`,
							qr_code_base64: qrLink,
						},
						callback: function (response) {
							resolve(response);
						},
						error: function (err) {
							unsentEmails.push(emails[i]);
							reject(err);
						},
					});
				}, 500);
			});

			sendPromises.push(promise);
		}

		Promise.allSettled(sendPromises).then((results) => {
			if (unsentEmails.length > 0) {
				alert(`These emails did not receive a coupon: \n${unsentEmails.join("\n")}`);
			} else {
				alert("✅ All emails sent successfully!");
			}
		});

	});

	async function generateCoupon(d) {
		return new Promise((resolve, reject) => {
			$.ajax({
				url: "/api/method/hotpot.api.coupons.generate_coupon_admin",
				type: "POST",
				data: JSON.stringify(d),
				contentType: "application/json",
				dataType: "json",
				headers: {
					"X-Frappe-CSRF-Token": window.csrf_token || frappe.csrf_token,
				},
				success: function (response) {
					if (response.message && response.message.status === false) {
						alert(response.message.message || "Failed to generate coupon");
						reject(false); // Rejecting promise to indicate failure
					} else {
						alert("Coupon generated successfully and emails sent!");
						console.log("Response:", response.message);
						resolve(response.data); // Resolving promise to indicate success
					}
				},
				error: function (xhr, status, error) {
					console.error("AJAX Error:", status, error);
					console.log("Response Text:", xhr.responseText);
					alert("Error generating coupon: " + JSON.parse(xhr.responseText).message);
					reject(false); // Rejecting promise on error
				},
			});
		});
	}

	$("#prevDatePicker").on("change", function () {
		fetchCoupons($(this).val());
	});

	$("#refreshTable").click(() => {
		let date = $("#prevDatePicker").val();
		fetchCoupons(date);
	});

	function fetchCoupons(date) {
		frappe.call({
			method: "hotpot.api.coupons.get_admin_guest_coupon",
			type: "GET",
			args: { date: date },
			callback: function (response) {
				let coupons = response.data || [];
				let tableBody = $("#couponTable tbody");
				tableBody.empty();

				if (coupons.length > 0) {
					coupons.forEach((coupon) => {
						const formatDate = (dateString) => {
							const options = { day: "2-digit", month: "short", year: "2-digit" };
							return new Date(dateString)
								.toLocaleDateString("en-GB", options)
								.replace(",", "");
						};

						const formatDateTime = (dateString) => {
							return new Date(dateString).toLocaleString();
						};

						tableBody.append(`
                            <tr>
                                <td>${coupon.meal_title}</td>
                                <td>${formatDate(coupon.coupon_date)}</td>
                                <td>${coupon.full_name}</td>
                                <td>${formatDateTime(coupon.modified)}</td>
                                <td>${coupon.email}</td>
                                </tr>
                        `);
					});
				} else {
					tableBody.append(
						`<tr><td colspan="5" class="text-center">No data found</td></tr>`
					);
				}
			},
		});
	}

	async function fetchVendors(locationName) {
		try {
			let vendorSelect = document.getElementById("vendorSelect");
			vendorSelect.innerHTML = '<option value="">Loading...</option>';

			const filters = JSON.stringify([
				["is_active", "=", 1],
				["location", "=", locationName],
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
			if (response.status === false) {
				alert(response.message);
				return;
			}
			let vlist = await response.json() || [];
			let vendors = vlist.data;
			vendorSelect.innerHTML = '';

			if (vendors.length === 0) {
				vendorSelect.innerHTML = '<option value="">No vendors found</option>';
				vendorSelect.disabled = true;
				mealSelect.disabled = true;
				return;
			}
	
			vendorSelect.disabled = false;
			vendorSelect.innerHTML = '<option value="">Select Vendor</option>';

			let fragment = document.createDocumentFragment();
			vendors.forEach((vendor) => {
				let option = document.createElement("option");
				option.value = vendor.name;
				option.textContent = vendor.full_name;
				fragment.appendChild(option);
			});
			vendorSelect.appendChild(fragment);
		} catch (error) {
			console.error("Error fetching vendors:", error);
			alert("Failed to load vendors. Please try again.");
		}
	}

	// Fetch user location from a Frappe DocType
	async function fetchLocations() {
		try {
			const response = await frappe.call({
				method: "frappe.client.get_list",
				type: "GET",
				args: {
					doctype: "Company Locations",
					fields: ["name","location_name"],
					limit_page_length: 10
				}
			});

			if (response.status === false) {
				alert(response.message);
				return;
			}

			const locations = response.message || response.data;
			const $locationSelect = $("#locationSelect");
			$locationSelect.html('<option value="">Select Location</option>');
	
			locations.forEach(location => {
				$locationSelect.append(
					`<option value="${location.name}">${location.location_name}</option>`
				);
			});
		} catch (error) {
			console.error("Error fetching user location:", error);
			alert("Failed to retrieve user location.");
		}
	}
	async function fetchUser() {
		try {
			let response = await frappe.call({
				method: "hotpot.api.users.get_hotpot_user_by_email",
				type: "GET",
			});
			console.log(response)
			if (response.message) {
				userId = response.message.name;
			} else {
				alert("Could not find user.");
			}
		} catch (error) {
			console.error("Error fetching user:", error);
			alert("Failed to load user. Please try again.");
		}
	}

	$("#vendorSelect, #datePicker").on("change", handleVendorOrDateChange);

	async function handleVendorOrDateChange() {
		let vendor = $("#vendorSelect").val();
		let date = $("#datePicker").val();
		let mealSelect = document.getElementById("mealSelect");

		if (!vendor || !date) {
			mealSelect.innerHTML = '<option value="">Select Meal</option>';
			mealSelect.disabled = true;
			return;
		}

		mealSelect.innerHTML = '<option value="">Loading...</option>';
		mealSelect.disabled = true;

		try {
			let response = await frappe.call({
				method: "hotpot.api.meal.get_meals",
				args: { vendor_id: vendor, date: date },
				type: "GET",
			});
			if (response.status === false) {
				alert(response.message);
				return;
			} else {
				if (response.data.length === 0) {
					alert("No meals available for the selected vendor and date.");
				}
			}
			let meals = response.data || [];
			mealSelect.innerHTML = '<option value="">Select Meal</option>';

			let fragment = document.createDocumentFragment();
			meals.forEach((meal) => {
				let option = document.createElement("option");
				option.value = meal.name;
				option.textContent = meal.meal_title;
				fragment.appendChild(option);
			});
			mealSelect.appendChild(fragment);

			mealSelect.disabled = meals.length === 0;
		} catch (error) {
			console.error("Error fetching meals:", error);
			alert("Failed to load meals. Please try again.");
			mealSelect.innerHTML = '<option value="">Select Meal</option>';
			mealSelect.disabled = true;
		}
	}
	updateEmailFields();
};
