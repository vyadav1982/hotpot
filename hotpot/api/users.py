from datetime import datetime

import frappe
import pytz


@frappe.whitelist(methods=["GET"])
def get_current_user():
	return frappe.get_cached_doc("User", frappe.session.user)


@frappe.whitelist(methods=["GET"])
def get_list():
	return frappe.db.get_list(
		"Hotpot User",
		fields=["name", "employee_id", "employee_name"],
		filters=[
			["is_active", "=", 1],
			# ["is_guest", "=", 0],
		],
	)


@frappe.whitelist(allow_guest=True)
def update_coupon_count(params):
	params = frappe.parse_json(params)
	employee_id = params.get("userId")
	coupon_count = params.get("token")
	coupon = params.get("coupon")
	doc = frappe.get_doc("Hotpot User", employee_id)
	doc.coupon_count = int(coupon_count)
	doc.save()
	frappe.db.commit()
	doc = frappe.new_doc("Hotpot Coupons History")
	doc.employee_id = employee_id
	doc.type = "Cancellation"
	doc.message = f"You Cancelled a coupon for {coupon['title']} ({coupon['coupon_date']})"
	doc.insert()
	return {"message": "Coupon count updated successfully"}


@frappe.whitelist(allow_guest=True)
def get_coupons_history(employee_id):
	result = []
	# params = frappe.parse_json(params)
	# employee_id = params.get("userId")
	query = """ SELECT modified_by, data, docname, creation FROM tabVersion WHERE docname = %s AND ref_doctype LIKE '%%Hotpot%%' ORDER BY creation DESC LIMIT 10; """
	result = frappe.db.sql(query, (employee_id), as_dict=True)
	result += frappe.db.get_list(
		"Hotpot Coupons History",
		fields=["employee_id", "type", "message", "creation"],
		filters=[["employee_id", "=", employee_id]],
		order_by="creation desc",
		limit=25,
	)
	return result


def reset_coupon_count():
	users = frappe.db.get_list(
		"Hotpot User", filters=[["is_active", "=", 1], ["is_guest", "=", 0]], pluck="name"
	)

	for name in users:
		doc = frappe.get_doc("Hotpot User", name)
		doc.coupon_count = 60
		doc.save()
	frappe.db.commit()


@frappe.whitelist(methods=["POST"])
def get_hotpot_user_by_employee_id(employee_id):
	return frappe.get_doc("Hotpot User", employee_id)


@frappe.whitelist(allow_guest=True)
@frappe.whitelist()
def get_hotpot_user_by_email(email):
	try:
		user = frappe.db.get_list("Hotpot User", filters=[["email", "=", email]], fields=["*"])
		if user:
			return {"status": "success", "data": user[0]}
		else:
			return {"status": "error", "message": "No user found with the given email."}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Hotpot User by Email Error")
		return {"status": "error", "message": f"An error occurred: {str(e)}"}
