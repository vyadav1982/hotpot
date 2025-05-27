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
		{"label": "Employee ID", "fieldname": "employee_code", "fieldtype": "Data", "width": 140},
		{"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 200},
		{"label": "Total Coupons", "fieldname": "total_coupons", "fieldtype": "Int", "width": 120},
		{"label": "Total Discounted Price", "fieldname": "total_price", "fieldtype": "Currency", "width": 160}
	]

	user_timezone = get_user_timezone() or "Asia/Kolkata"

	query = """
		SELECT
			hc.employee_code,
			hu.full_name,
			COUNT(*) AS total_coupons,
			SUM(IFNULL(hc.coupon_weight, 0)) AS total_price
		FROM `tabHotpot Coupons` hc
		LEFT JOIN `tabHotpot User` hu ON hc.employee_code = hu.name
		WHERE
			hc.coupon_status IN (0, -1)
			AND DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %s)) BETWEEN %s AND %s
	"""
	params = [user_timezone, start_date, end_date,]
	if employee:
		query+=" AND hc.employee_code = %s"
		params.append(employee)
	
	query +="GROUP BY hc.employee_code, hu.full_name ORDER BY total_price DESC"

	data = frappe.db.sql(query, params, as_dict=True)

	return columns, data
