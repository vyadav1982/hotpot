from datetime import datetime, timedelta

import frappe
import frappe.utils
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_coupon_type_list():
	coupon_type_list = frappe.db.get_list(
		"Hotpot Coupon Type",
		fields=["name", "start_hour", "end_hour"],
		order_by="start_hour",
	)
	return coupon_type_list


@frappe.whitelist(allow_guest=True)
def get_coupon_list(params):
	params = frappe.parse_json(params)
	from_date = params.get("from")
	to_date = params.get("to")
	month1, date1, year1 = from_date.split("/")
	month2, date2, year2 = to_date.split("/")
	from_date = year1 + "-" + month1 + "-" + date1
	to_date = year2 + "-" + month2 + "-" + date2
	users = get_users(from_date, to_date)
	if len(users) == 0:
		return []
	user_Id = []
	for user in users:
		user_Id.append(user.get("employee_id"))
	placeholders = ", ".join(["%s"] * len(user_Id))
	query = f"""
		SELECT
			a.employee_id,
			a.title,
			b.employee_name,
			a.coupon_date,
			a.coupon_time,
			a.served_by
		FROM `tabHotpot Coupon` AS a
		INNER JOIN `tabHotpot User` AS b
		ON a.employee_id = b.employee_id
		WHERE a.coupon_date >= %s
		AND a.coupon_date <= %s
		AND a.employee_id IN ({placeholders})
		ORDER BY a.coupon_date DESC;
	"""
	params_sql = [from_date, to_date] + [str(uid) for uid in user_Id]

	coupon_list = frappe.db.sql(query, params_sql, as_dict=True)
	return coupon_list


@frappe.whitelist(allow_guest=True)
def get_users(from_date, to_date):
	params = (from_date, to_date)

	query = """
	    SELECT u.employee_id
	    FROM `tabHotpot User` AS u
	    INNER JOIN (
	    SELECT employee_id
	    FROM `tabHotpot Coupon`
	    WHERE coupon_date >= %s AND coupon_date <= %s
	    GROUP BY employee_id
	        ) c ON c.employee_id = u.employee_id
	        ORDER BY
	            u.employee_id;
	"""

	users = frappe.db.sql(query, params, as_dict=True)
	return users


@frappe.whitelist(allow_guest=True)
def get_coupon_type_count(params):
	params = frappe.parse_json(params)
	from_date = (datetime.strptime(params.get("from"), "%m/%d/%Y"),)
	to_date = (datetime.strptime(params.get("to"), "%m/%d/%Y"),)
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