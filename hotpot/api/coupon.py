from datetime import datetime

import frappe
from frappe.utils import today


@frappe.whitelist(allow_guest=True)
def get_current_coupon_type():
	time = datetime.now()
	# Define time ranges
	coupon_type_list = frappe.get_list(
		"Hotpot Coupon Type",
		filters=[
			["start_hour", "<=", time.hour * 100 + time.minute],
			["end_hour", ">", time.hour * 100 + time.minute],
			["is_active", "=", True],
		],
		pluck="name",
	)

	if len(coupon_type_list) > 1:
		frappe.throw("Error: Multiple coupons found for this time of day. Please contact system manager")

	if len(coupon_type_list) == 1:
		return coupon_type_list[0]
	else:
		return frappe.throw("No coupon available at this time")


@frappe.whitelist(allow_guest=True)
def get_coupon_for_employee_id(employee_id):
	if not frappe.db.exists("Hotpot User", employee_id):
		return frappe.throw(f"Employee ID: {employee_id} does not exist")
	title = get_current_coupon_type()
	coupon_date = today()

	if not frappe.db.exists("Hotpot Coupon", f"{title}_{employee_id}_{coupon_date}"):
		coupon = frappe.new_doc(doctype="Hotpot Coupon")
		coupon.employee_id = employee_id
		coupon.coupon_date = datetime.now().date()
		coupon.coupon_time = datetime.now().replace(microsecond=0).time()
		coupon.title = title
		return coupon
	else:
		return frappe.get_doc("Hotpot Coupon", f"{title}_{employee_id}_{coupon_date}")


@frappe.whitelist(allow_guest=True)
def coupon_exists(name):
	if not frappe.db.exists("Hotpot Coupon", name):
		return None
	else:
		return frappe.get_doc("Hotpot Coupon", name)


@frappe.whitelist(allow_guest=True)
def create_coupon(data):
	if not frappe.db.exists("Hotpot Coupon", extract_coupon_info(data)):
		coupon = frappe.get_doc(coupon_from_info(data))
		coupon.served_by = frappe.session.user
		coupon.save(ignore_permissions=True)
		return {"created": True, "coupon": coupon}
	else:
		print(extract_coupon_info(data))
		return {"created": False, "coupon": frappe.get_doc("Hotpot Coupon", extract_coupon_info(data))}


@frappe.whitelist(allow_guest=True)
def get_coupon_for_guest(data):
	if not frappe.exists("Hotpot User", data.mobile):
		new_user = frappe.new_doc("Hotpot User")
		new_user.employee_name = data["name"]
		new_user.employee_id = data["mobile"]
		new_user.is_guest = True
		new_user.save(ignore_permissions=True)

	created_coupons = []
	meal_types = {
		"Breakfast": data.get("breakfast", False),
		"Lunch": data.get("lunch", False),
		"Evening Snack": data.get("evening_snacks", False),
		"Dinner": data.get("dinner", False),
	}

	for meal, is_selected in meal_types.items():
		if is_selected:
			coupon = {
				"employee_name": data["name"],
				"mobile": data["mobile"],
				"coupon_date": datetime.now().date(),
				"coupon_time": datetime.now().replace(microsecond=0).time(),
				"meal_title": meal,
			}

			created_coupons.append(coupon)

	return created_coupons


def extract_coupon_info(input_str: str) -> str | None:
	# Split the string by underscore
	parts = input_str.split("_")

	# Check if we have at least 3 parts (Breakfast, ID, and Date)
	if len(parts) < 3:
		print("Invalid input format")
		return None

	# Extract the first two parts (Breakfast and ID)
	prefix = "_".join(parts[:2])

	# Extract the date part (assuming it's always in YYYY-MM-DD format)
	date_part = parts[2][:10]

	# Combine the parts
	return f"{prefix}_{date_part}"


def coupon_from_info(input_str: str) -> str | None:
	# Split the string by underscore
	parts = input_str.split("_")

	# Check if we have at least 3 parts (Breakfast, ID, and Date)
	if len(parts) < 3:
		print("Invalid input format")
		return None

	# Extract the title
	title = parts[0]
	employee_id = parts[1]

	# Extract the date part (assuming it's always in YYYY-MM-DD format)
	coupon_date = parts[2][:10]
	coupon_time = parts[2][11:]

	# Combine the parts
	return frappe._dict(
		doctype="Hotpot Coupon",
		title=title,
		employee_id=employee_id,
		coupon_date=coupon_date,
		coupon_time=coupon_time,
	)
