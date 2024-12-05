from datetime import datetime

import frappe
from frappe.utils import today


def get_meal_of_time(time):
	return "Breakfast"
	# Define time ranges
	if 7 <= time.hour < 10:
		return "Breakfast"
	elif 13 <= time.hour < 15:
		return "Lunch"
	elif 17 <= time.hour < 19:
		return "Evening Snack"
	elif 19 <= time.hour < 24:
		return "Dinner"
	else:
		return None


@frappe.whitelist(allow_guest=True)
def get_coupon_for_employee_id(employee_id):
	if not frappe.db.exists("Hotpot User", employee_id):
		return frappe.throw(f"Employee ID: {employee_id} does not exist")
	title = get_meal_of_time(datetime.now())
	coupon_date = today()
	if not title:
		return frappe.throw("No coupon available at this time")
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
