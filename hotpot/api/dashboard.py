from datetime import datetime, timedelta

import frappe
import frappe.utils
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_coupon_type_list():
	coupon_type_list = frappe.db.get_list("Hotpot Coupon Type", fields=["name", "start_hour", "end_hour"])
	return coupon_type_list


@frappe.whitelist(allow_guest=True)
def get_coupon_list(params):
	params = frappe.parse_json(params)
	from_date = params.get("from")
	to_date = params.get("to")
	page_no = params.get("page")
	users = get_users(
		page_no,
		from_date,
		to_date,
		limit=5,
	)
	user_Id = []
	for user in users:
		user_Id.append(user.get("employee_id"))
	filters = {"coupon_date": ["between", [from_date, to_date]], "employee_id": ["in", user_Id]}
	coupon_list = frappe.db.get_list(
		"Hotpot Coupon",
		filters=filters,
		fields=["employee_id", "title", "coupon_date", "coupon_time", "served_by"],
		limit_start=(page_no - 1) * 10,
		limit_page_length=4,
	)
	return coupon_list


@frappe.whitelist(allow_guest=True)
def get_users(page_no, from_date, to_date, limit=2):
	offset = (page_no - 1) * limit
	limit = 3
	from_date = datetime.strptime(from_date, "%d/%m/%Y").strftime("%Y-%m-%d")
	to_date = datetime.strptime(to_date, "%d/%m/%Y").strftime("%Y-%m-%d")

	params = (from_date, to_date, limit, offset)
	# users = frappe.db.get_all(
	# 	"Hotpot User",
	# 	fields=["employee_id"],
	# 	limit_page_length=limit,
	# 	limit_start=offset,
	# 	pluck="employee_id",
	# )
	# return users
	query = """
        SELECT u.employee_id
        FROM `tabHotpot User` AS u
        INNER JOIN (
        SELECT employee_id, MAX(modified) AS last_activity
        FROM `tabHotpot Coupon`
        WHERE coupon_date >= %s AND coupon_date <= %s
        GROUP BY employee_id
            ) c ON c.employee_id = u.employee_id
            ORDER BY 
                c.last_activity DESC,
                u.employee_id
            LIMIT %s OFFSET %s;
    """
	users = frappe.db.sql(query, params, as_dict=True)
	print("++__--" * 2, from_date, to_date, users)
	return users


@frappe.whitelist(allow_guest=True)
def get_coupon_type_count(params):
	params = frappe.parse_json(params)
	# print(
	#     "++" * 30,
	#     datetime.strptime(params.get("from"),  "%m/%d/%Y"),
	#     datetime.strptime(params.get("to"),  "%m/%d/%Y"),
	# )
	from_date = (datetime.strptime(params.get("from"), "%m/%d/%Y"),)
	to_date = (datetime.strptime(params.get("to"), "%m/%d/%Y"),)
	# print(type( datetime.strptime(params.get("from"),  "%m/%d/%Y")))
	# print(type((datetime.strptime(params.get("from"), "%m/%d/%Y") - timedelta(days=1))))
	# from_date = (datetime.strptime(params.get("from"),  "%m/%d/%Y") - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
	# to_date = (datetime.strptime(params.get("to"),  "%m/%d/%Y") + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
	# print("//" * 30, from_date, to_date)
	total_coupons = frappe.db.count("Hotpot Coupon", {"coupon_date": ["between", [from_date, to_date]]})
	breakfast_coupons = frappe.db.count(
		"Hotpot Coupon", {"title": "Breakfast", "coupon_date": ["between", [from_date, to_date]]}
	)
	lunch_coupons = frappe.db.count(
		"Hotpot Coupon", {"title": "Lunch", "coupon_date": ["between", [from_date, to_date]]}
	)
	evening_snacks_coupons = frappe.db.count(
		"Hotpot Coupon", {"title": "Evening Snack", "coupon_date": ["between", [from_date, to_date]]}
	)
	dinner_coupons = frappe.db.count(
		"Hotpot Coupon", {"title": "Dinner", "coupon_date": ["between", [from_date, to_date]]}
	)
	return {
		"total_coupons": total_coupons,
		"breakfast_coupons": breakfast_coupons,
		"lunch_coupons": lunch_coupons,
		"evening_snacks_coupons": evening_snacks_coupons,
		"dinner_coupons": dinner_coupons,
	}
