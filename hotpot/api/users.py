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
			["is_guest", "=", 0],
		],
	)


def set_response(http_status_code, status, message, data=None):
	frappe.local.response["http_status_code"] = http_status_code
	frappe.response["status"] = status
	frappe.response["message"] = message
	frappe.response["data"] = data


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
	doc.message = (
		f"You Cancelled a coupon for {coupon['title']} ({coupon['coupon_date']})"
	)
	doc.insert()
	return {"message": "Coupon count updated successfully"}


def set_response(http_status_code, status, message, data=None):
	frappe.local.response["http_status_code"] = http_status_code
	frappe.response["status"] = status
	frappe.response["message"] = message
	frappe.response["data"] = data


@frappe.whitelist(allow_guest=True)
def get_coupons_history(employee_id):
	try:
		if frappe.request.method != "GET":
				set_response(500, False, "Only GET method is allowed")
				return

		user_doc = get_hotpot_user_by_email()
		print(user_doc.get("employee_id")==employee_id)
		if not user_doc or not user_doc.get("employee_id")==(employee_id):
			set_response(404, False, "User Not found")
			return

		if not user_doc.get("role") == "Hotpot User":
			set_response(403, False, "Not Permitted to access this resource")
			return 

		result = []
		query = """ SELECT modified_by, data, docname, creation FROM tabVersion WHERE docname = %s AND ref_doctype LIKE '%%Hotpot%%' ORDER BY creation DESC LIMIT 10; """
		result = frappe.db.sql(query, (employee_id), as_dict=True)
		result += frappe.db.get_list(
			"Hotpot Coupons History",
			fields=["employee_id", "type", "message", "creation"],
			filters=[["employee_id", "=", employee_id]],
			order_by="creation desc",
			limit=25,
		)
		set_response(200,True,"History fetched successfully",result)
	except Exception as e:
		frappe.db.rollback()
		print(frappe.get_traceback())
		frappe.log_error(frappe.get_traceback(), "History Error")
		return set_response(500, False, f"Server error: {str(e)}")


def reset_coupon_count():
	users = frappe.db.get_list(
		"Hotpot User",
		filters=[["is_active", "=", 1], ["is_guest", "=", 0]],
		pluck="name",
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
def get_hotpot_user_by_email():
	try:
		email = frappe.session.user
		if not email:
			set_response(404, False, "No auth token found")
			return

		if not frappe.has_permission("Hotpot User", "read"):
			set_response(404, False, "No auth token found")
			return
		user = frappe.db.get_list(
			"Hotpot User",
			filters=[["email", "=", email]],
			fields=[
				"name",
				"Id",
				"employee_name",
				"employee_id",
				"email",
				"mobile_no",
				"is_active",
				"role",
				"is_guest",
				"guest_of",
				"coupon_count",
			],
		)
		if user:
			return user[0]

		return None

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Hotpot User by Email Error")
		return None


@frappe.whitelist(allow_guest=True)
def get_hotpot_loggedin_user():
	try:
		user = get_hotpot_user_by_email()
		print(user)
		if user:
			set_response(200, True, "Data fetched successfully", user)
			return 

		set_response(500, False, "No user found with the given email")
		return
	except frappe.PermissionError:
		# Handle permission errors
		set_response(403, False, "You do not have permission to access this resource")
		return

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Hotpot User by Email Error")
		set_response(500, False, f"An error occurred: {str(e)}")
		return
