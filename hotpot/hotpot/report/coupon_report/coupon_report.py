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
		{"label": "Email (Guest Only)", "fieldname": "email", "fieldtype": "Data", "width": 180},
		{"label": "Coupon Type", "fieldname": "coupon_type", "fieldtype": "Data", "width": 120},
		{"label": "Coupon Status", "fieldname": "coupon_status", "fieldtype": "Data", "width": 120},
		{"label": "Actual Rate", "fieldname": "actual_rate", "fieldtype": "Float", "width": 150},
		{"label": "Discounted Rate", "fieldname": "discounted_rate", "fieldtype": "Float", "width": 160},
	]

	user_timezone = get_user_timezone() or "Asia/Kolkata"

	query = """
		SELECT
			hc.employee_code,
			CASE WHEN hc.guest_of IS NOT NULL THEN hc.email ELSE NULL END AS email,
			CASE
				WHEN hc.guest_of IS NOT NULL THEN 'Guest'
				WHEN hc.joining_day = 1 THEN 'Joining Day'
				WHEN hc.birthday_coupon = 1 THEN 'Birthday'
				ELSE 'Normal'
			END AS coupon_type,
			CASE
				WHEN hc.coupon_status = '-1' THEN 'Expired'
				WHEN hc.coupon_status = '0' THEN 'Consumed'
				ELSE 'Unknown'
			END AS coupon_status,
			IFNULL(hm.meal_weight, 0) AS actual_rate,
			hc.coupon_weight AS discounted_rate
		FROM `tabHotpot Coupons` hc
		LEFT JOIN `tabHotpot Meal` hm ON hc.parent = hm.name
		WHERE
			hc.coupon_status NOT IN (1, 2)
			AND DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %s)) BETWEEN %s AND %s
	"""

	params = [user_timezone, start_date, end_date]

	if vendor_id:
		query += " AND hm.vendor_id = %s"
		params.append(vendor_id)

	query += " ORDER BY hc.coupon_date DESC"

	data = frappe.db.sql(query, params, as_dict=True)
	return columns, data
