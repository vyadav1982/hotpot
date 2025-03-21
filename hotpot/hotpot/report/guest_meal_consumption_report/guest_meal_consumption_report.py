# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe


import frappe

from ....utils.utc_time import *


def execute(filters=None):
    if not filters:
        filters = {}

    start_date = filters.get("from_date")
    end_date = filters.get("to_date")
    vendor_id = filters.get("vendor_id")

    if not start_date or not end_date:
        frappe.throw("Please select both Start Date and End Date")

    start_date = get_utc_datetime_obj(f"{start_date} 00:00:00")
    end_date = get_utc_datetime_obj(f"{end_date} 23:59:59")

    columns = [
        # {"label": "Meal Id", "fieldname": "meal_id", "fieldtype": "Data", "width": 120},
        {"label": "Employee Id", "fieldname": "employee_id", "fieldtype": "Data", "width": 120},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": "Meal Title", "fieldname": "meal_title", "fieldtype": "Data", "width": 200},
        {"label": "Guest Name", "fieldname": "guest_name", "fieldtype": "Data", "width": 120},
        {"label": "Guest Moble No.", "fieldname": "guest_mobile_no", "fieldtype": "Phone", "width": 150},
        # {"label": "Vendor Id", "fieldname": "vendor_id", "fieldtype": "Data", "width": 120},
        {"label": "Coupon Date", "fieldname": "coupon_date", "fieldtype": "Date", "width": 120},
        {"label": "Vendor Name", "fieldname": "vendor_name", "fieldtype": "Data", "width": 150},
        # {"label": "Coupon Id", "fieldname": "coupon_id", "fieldtype": "Data", "width": 120},
    ]

    query = """
        SELECT
			hm.name AS meal_id,
			hm.meal_title AS meal_title,
			vendor.employee_id AS vendor_id,
			vendor.employee_name AS vendor_name,
			hc.name AS coupon_id,
			hc.coupon_date AS coupon_date,
			employee.employee_id AS employee_id,
			employee.employee_name AS employee_name,
			approval.guest_name AS guest_name,
            approval.guest_mobile_no AS guest_mobile_no    
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
			AND hc.coupon_date BETWEEN %s AND %s
    """

    params = [start_date, end_date]

    if vendor_id:
        query += " AND hm.vendor_id = %s"
        params.append(vendor_id)

    query += " ORDER BY hc.coupon_date DESC;"

    data = frappe.db.sql(query, tuple(params), as_dict=True)

    return columns, data


