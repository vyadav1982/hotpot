# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from hotpot.utils.utc_time import *


def execute(filters=None):
	if not filters:
		filters = {}

	start_date = filters.get("from_date")
	end_date = filters.get("to_date")
	vendor_id = filters.get("vendor_id")

	if not start_date or not end_date:
		frappe.throw("Please select both Start Date and End Date")

	columns = [
		{"label": "Employee Code", "fieldname": "employee_code", "fieldtype": "Data", "width": 120},
		{"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 120},
		{"label": "Vendor", "fieldname": "vendor", "fieldtype": "Data", "width": 120},
		{"label": "Meal", "fieldname": "meal", "fieldtype": "Data", "width": 120},
		{"label": "Category", "fieldname": "category", "fieldtype": "Data", "width": 120},
		{"label": "Email (Guest Only)", "fieldname": "email", "fieldtype": "Data", "width": 180},
		{"label": "Coupon Date", "fieldname": "coupon_date", "fieldtype": "Date", "width": 120},
		{"label": "Coupon Type", "fieldname": "coupon_type", "fieldtype": "Data", "width": 120},
		{"label": "Coupon Location", "fieldname": "location", "fieldtype": "Data", "width": 120},
		{"label": "Coupon Status", "fieldname": "coupon_status", "fieldtype": "Data", "width": 120},
		{"label": "Actual Rate", "fieldname": "actual_rate", "fieldtype": "Currency", "width": 150},
		{"label": "Discounted Rate", "fieldname": "discounted_rate", "fieldtype": "Currency", "width": 160},
		{"label": "Penalty", "fieldname": "penalty", "fieldtype": "Currency", "width": 140},

	]

	user_timezone = get_user_timezone() or "Asia/Kolkata"

	query = """
		SELECT
			hu.full_name AS vendor,
			hc.employee_code,
			DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %s)) AS coupon_date,
			hm.meal_title AS meal,
			hm.category,
			CASE WHEN hc.guest_of IS NOT NULL THEN hc.email ELSE NULL END AS email,
			
			CASE
				WHEN hc.guest_of IS NOT NULL THEN 'Guest'
				WHEN hc.joining_day = 1 THEN 'Joining Day'
				WHEN hc.birthday_coupon = 1 THEN 'Birthday'
				WHEN hc.location IS NOT NULL AND hu_user.location IS NOT NULL AND hc.location != hu_user.location THEN 'Outer Location'
				ELSE 'Normal'
			END AS coupon_type,

			CASE
				WHEN hc.coupon_status = '-1' THEN 'Expired'
				WHEN hc.coupon_status = '0' THEN 'Consumed'
				WHEN hc.coupon_status = '2' THEN 'Cancelled'
				ELSE 'Unknown'
			END AS coupon_status,

			IFNULL(hm.meal_weight, 0) AS actual_rate,

			CASE
				WHEN hc.coupon_status = '-1' THEN 0
				ELSE hc.coupon_weight
			END AS discounted_rate,

			CASE
				WHEN hc.coupon_status = '-1' THEN IFNULL(hm.meal_weight, 0)
				ELSE 0
			END AS penalty,

			hu_user.full_name AS employee_name,

			hc.location AS location

		FROM `tabHotpot Coupons` hc
		LEFT JOIN `tabHotpot Meal` hm ON hc.parent = hm.name
		LEFT JOIN `tabHotpot User` hu ON hm.vendor_id = hu.name
		LEFT JOIN `tabHotpot User` hu_user ON hc.employee_id = hu_user.name
		WHERE
			hc.coupon_status NOT IN (1)
			AND DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %s)) BETWEEN %s AND %s
	"""


	params = [user_timezone,user_timezone, start_date, end_date]
	roles = frappe.get_roles()


	if "Hotpot Vendor" in roles and "Administrator" not in roles:
		vendor_id = frappe.session.user

	if vendor_id:
		query += " AND hm.vendor_id = %s"
		params.append(vendor_id)

	query += " ORDER BY hc.coupon_date DESC"

	data = frappe.db.sql(query, params, as_dict=True)

	if "Hotpot Vendor" in roles and "Administrator" not in roles:
		columns = [col for col in columns if col.get("fieldname") not in ["discounted_rate", "penalty"]]

		for row in data:
			row.pop("discounted_rate", None)
			row.pop("penalty", None)


	return columns, data

