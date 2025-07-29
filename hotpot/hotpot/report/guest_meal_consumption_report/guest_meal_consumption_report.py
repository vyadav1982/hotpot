# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe


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

	# start_date = get_utc_datetime_obj(f"{start_date} 00:00:00")
	# end_date = get_utc_datetime_obj(f"{end_date} 23:59:59")

	columns = [
		# {"label": "Meal Id", "fieldname": "meal_id", "fieldtype": "Data", "width": 120},
		{"label": "Employee Id", "fieldname": "employee_id", "fieldtype": "Data", "width": 120},
		{"label": "Employee Name", "fieldname": "full_name", "fieldtype": "Data", "width": 120},
		{"label": "Meal Title", "fieldname": "meal_title", "fieldtype": "Data", "width": 120},
		{"label": "Coupon Status", "fieldname": "coupon_status", "fieldtype": "Data", "width": 120},
		{"label": "Coupon Date", "fieldname": "coupon_date", "fieldtype": "Date", "width": 120},
		{"label": "Vendor Name", "fieldname": "vendor_name", "fieldtype": "Data", "width": 120},
		{"label": "Guest Email", "fieldname": "email", "fieldtype": "Data", "width": 120},
		{"label": "Guest Name", "fieldname": "guest_name", "fieldtype": "Data", "width": 120},
		{"label": "Guest Moble No.", "fieldname": "guest_mobile_no", "fieldtype": "Phone", "width": 120},
		{"label": "Actual Rate", "fieldname": "actual_rate", "fieldtype": "Currency", "width": 120},
		{"label": "Discounted Rate", "fieldname": "discounted_rate", "fieldtype": "Currency", "width": 120},
		{"label": "Penalty", "fieldname": "penalty", "fieldtype": "Currency", "width": 120},
		{"label": "Coupon Location", "fieldname": "location", "data": "Data", "width": 120},
	]
	user_timezone = get_user_timezone() or "Asia/Kolkata"

	query = """
        SELECT
			hm.name AS meal_id,
			hm.meal_title AS meal_title,
			vendor.employee_id AS vendor_id,
			vendor.full_name AS vendor_name,
			hc.name AS coupon_id,
			DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %s)) AS coupon_date,
			employee.employee_id AS employee_id,
			employee.full_name,
			approval.guest_name AS guest_name,
            hc.email AS email,
            approval.guest_mobile_no AS guest_mobile_no,

			IFNULL(hm.actual_meal_rate, 0) AS actual_rate,
			CASE
				WHEN hc.coupon_status = '-1' THEN 0
				ELSE hc.coupon_weight
			END AS discounted_rate,
			CASE
				WHEN hc.coupon_status = '-1' THEN IFNULL(hm.actual_meal_rate, 0)
				ELSE 0
			END AS penalty,

			CASE
				WHEN hc.coupon_status = '-1' THEN 'Expired'
				WHEN hc.coupon_status = '0' THEN 'Consumed'
				WHEN hc.coupon_status = '2' THEN 'Cancelled'
				ELSE 'Unknown'
			END AS coupon_status,

			hc.location AS location

		FROM
			`tabHotpot Coupons` AS hc
		INNER JOIN
			`tabHotpot Meal` AS hm ON hm.name = hc.parent
		LEFT JOIN
			`tabHotpot User` AS vendor ON vendor.name = hm.vendor_id
		LEFT JOIN
			`tabHotpot User` AS employee ON employee.name = hc.employee_id
		LEFT JOIN
			`tabHotpot Approvals` AS approval ON approval.name = hc.approval_id
		WHERE
			hc.guest_of IS NOT NULL
            AND hc.coupon_status != 1
			AND DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %s)) BETWEEN %s AND %s
    """

	params = [user_timezone, user_timezone, start_date, end_date]

	if vendor_id:
		query += " AND hm.vendor_id = %s"
		params.append(vendor_id)

	query += " ORDER BY hc.coupon_date DESC;"

	data = frappe.db.sql(query, tuple(params), as_dict=True)

	return columns, data
