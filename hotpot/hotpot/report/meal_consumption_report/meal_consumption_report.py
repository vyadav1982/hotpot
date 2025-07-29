# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

from hotpot.utils.utc_time import *


def get_star_rating(rating):
	"""Convert a float rating to a star string."""
	if not rating:
		return "-"
	return "⭐" * round(rating)


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
		{"label": "Meal Title", "fieldname": "meal_title", "fieldtype": "Data", "width": 200},
		# {"label": "Meal Date", "fieldname": "meal_date", "fieldtype": "Date", "width": 120},
		{"label": "Meal Rate", "fieldname": "meal_weight", "fieldtype": "float", "width": 120},
		# {"label": "Vendor Id", "fieldname": "vendor_id", "fieldtype": "Data", "width": 120},
		{"label": "Vendor Name", "fieldname": "vendor_name", "fieldtype": "Data", "width": 150},
		{"label": "Coupon Count", "fieldname": "coupon_count", "fieldtype": "Data", "width": 120},
		{"label": "Total Price", "fieldname": "total_weight", "fieldtype": "Data", "width": 120},
		{"label": "Average Rating", "fieldname": "avg_rating", "fieldtype": "float", "width": 120},
		# {"label": "Feedback's", "fieldname": "feedback_list", "fieldtype": "Data", "width": 150},
	]
	user_timezone = get_user_timezone() or "Asia/Kolkata"

	query = """
	   SELECT
			hm.name AS meal_id,
			hm.meal_title AS meal_title,
			hm.meal_date AS meal_date,
			MAX(hm.actual_meal_rate)  AS meal_weight,
			vendor.employee_id AS vendor_id,
			vendor.full_name AS vendor_name,
			COUNT(hc.name) AS coupon_count,
			(MAX(hm.actual_meal_rate) * COUNT(hc.name)) AS total_weight,
			IFNULL(AVG(hr.rating), 0) AS avg_rating,
			JSON_ARRAYAGG(COALESCE(hr.feedback, '')) AS feedback_list
		FROM
			`tabHotpot Meal` AS hm
		LEFT JOIN
			`tabHotpot Coupons` AS hc ON hm.name = hc.parent
		LEFT JOIN
			`tabHotpot User` AS vendor ON vendor.name = hm.vendor_id
		LEFT JOIN
			`tabHotpot Meal Rating` AS hr ON hr.parent = hm.name
		WHERE
			hc.coupon_status !=2 AND hc.coupon_status != 1 AND DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %s)) BETWEEN %s AND %s
	"""

	params = [user_timezone, start_date, end_date]

	if vendor_id:
		query += "		AND hm.vendor_id = %s"
		params.append(vendor_id)

	query += """
		GROUP BY
			hm.name, hm.meal_title, vendor.employee_id, vendor.full_name
		ORDER BY
			hc.coupon_date DESC;
	"""

	data = frappe.db.sql(query, params, as_dict=True)
	for row in data:
		row["avg_rating"] = get_star_rating(row["avg_rating"])
		row["total_weight"] = f"₹{row['total_weight']:.2f}"

	return columns, data
