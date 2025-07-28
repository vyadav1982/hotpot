# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

from hotpot.utils.utc_time import *


def execute(filters=None):
	if not filters:
		filters = {}

	start_date = filters.get("from_date")
	end_date = filters.get("to_date")
	employee = filters.get("employee_id")

	if not start_date or not end_date:
		frappe.throw("Please select both Start Date and End Date")

	columns = [
		{"label": "Employee ID", "fieldname": "employee_code", "fieldtype": "Data", "width": 120},
		{"label": "Employee Name", "fieldname": "full_name", "fieldtype": "Data", "width": 120},
		{"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 120},
		{"label": "Band", "fieldname": "band", "fieldtype": "Data", "width": 120},
		{"label": "Location", "fieldname": "location", "fieldtype": "Data", "width": 120},
		{"label": "Total Coupons", "fieldname": "total_coupons", "fieldtype": "Int", "width": 120},
		{"label": "Actual Rate", "fieldname": "total_actual_price", "fieldtype": "Currency", "width": 120},
		{"label": "Discounted Rate", "fieldname": "total_price", "fieldtype": "Currency", "width": 120},
		{"label": "Penalty", "fieldname": "penalty", "fieldtype": "Currency", "width": 120},
		{"label": "Total Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 120},
		{
			"label": "Meal Cost To Company",
			"fieldname": "company_amount",
			"fieldtype": "Currency",
			"width": 120,
		},
	]

	user_timezone = get_user_timezone() or "Asia/Kolkata"

	query = """
		SELECT
			hc.employee_code,
			hu.full_name,
			emp.department,
			emp.band,
			emp.branch AS location,
			COUNT(*) AS total_coupons,

			SUM(IFNULL(hm.meal_weight, 0)) AS total_actual_price,

			SUM(
				CASE
					WHEN hc.coupon_status = -1 THEN 0
					ELSE IFNULL(hc.coupon_weight, 0)
				END
			) AS total_price,

			SUM(
				CASE
					WHEN hc.coupon_status = -1 THEN IFNULL(hm.meal_weight, 0)
					ELSE 0
				END
			) AS penalty,

			SUM(
				CASE
					WHEN hc.coupon_status = -1 THEN IFNULL(hm.meal_weight, 0)
					ELSE IFNULL(hc.coupon_weight, 0)
				END
			) AS total_amount,

			SUM(IFNULL(hm.meal_weight, 0))  -
			SUM(
				CASE
					WHEN hc.coupon_status = -1 THEN IFNULL(hm.meal_weight, 0)
					ELSE IFNULL(hc.coupon_weight, 0)
				END
			) AS company_amount

		FROM `tabHotpot Coupons` hc
		LEFT JOIN `tabHotpot User` hu ON hc.employee_code = hu.employee
		LEFT JOIN `tabHotpot Meal` hm ON hc.parent = hm.name
		LEFT JOIN `tabEmployee` emp ON hc.employee_id = emp.name
		WHERE
			hc.coupon_status IN (0, -1)
			AND DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %s)) BETWEEN %s AND %s
			AND hc.guest_of IS NULL
			AND hc.coupon_weight > -1
	"""

	params = [
		user_timezone,
		start_date,
		end_date,
	]
	if employee:
		query += " AND hc.employee_code = %s"
		params.append(employee)

	query += "GROUP BY hc.employee_code  ORDER BY total_price DESC"

	data = frappe.db.sql(query, params, as_dict=True)

	return columns, data
