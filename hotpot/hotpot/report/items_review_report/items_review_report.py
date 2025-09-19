# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt




import frappe, json

def execute(filters=None):
	if not filters:
		filters = {}

	start_date = filters.get("from_date")
	end_date = filters.get("to_date")
	vendor_id = filters.get("vendor_id")
	employee = filters.get("employee")

	if not start_date or not end_date:
		frappe.throw("Please select both Start Date and End Date")

	columns = [
		{"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
		{"label": "Vendor", "fieldname": "vendor_id", "fieldtype": "Data", "width": 180},
		{"label": "Total Ratings", "fieldname": "ratings", "fieldtype": "Data", "width": 200},
		{"label": "Average Rating", "fieldname": "avg_rating", "fieldtype": "Data", "width": 150},
		{"label": "All Feedbacks", "fieldname": "all_feedbacks", "fieldtype": "HTML", "width": 500},
	]

	where_clause = "1=1"
	if vendor_id:
		where_clause += " AND hi.vendor_id = %(vendor_id)s"
	if employee:
		where_clause += " AND hr.employee = %(employee)s"

	frappe.db.sql("SET SESSION group_concat_max_len = 1000000")

	query = f"""
		SELECT
			COUNT(hr.rating ) AS ratings,
			hi.name AS item_id,
			hi.item_name,
			hi.vendor_id,
			COUNT(hi.name) AS total_feedback,
			ROUND(AVG(hr.rating) * 5, 1) AS avg_rating,
			GROUP_CONCAT(
				CONCAT(
					hu.full_name, ' (', hu.name, '): ',
					hr.review, ' (',
					FORMAT(hr.rating * 5, 1), ' ⭐',
					')'
				)
				SEPARATOR ' || '
			) AS all_reviews


		FROM `tabHotpot Meal Menu Items Rating` AS hr
		INNER JOIN `tabHotpot Meal Items` AS hi ON hi.name = hr.meal_item
		INNER JOIN `tabHotpot User` AS hu ON hu.name = hr.employee
		WHERE {where_clause}
		AND DATE(hr.creation) BETWEEN %(start_date)s AND %(end_date)s
		GROUP BY hi.name, hi.vendor_id
	"""

	data = frappe.db.sql(query, {"start_date": start_date, "end_date": end_date, "vendor_id": vendor_id, "employee":employee}, as_dict=True)

	result = []
	for d in data:
		stars = "⭐" * int(round(d.avg_rating or 0))

		feedbacks = []
		if d.all_reviews:
			for idx, review in enumerate(d.all_reviews.split("||"), start=1):
				review = review.strip()
				if review:  # skip empty ones
					feedbacks.append(f"<li>{review}</li>")

		feedbacks_html = "<ul style='margin:0; padding-left:16px;'>" + "".join(feedbacks) + "</ul>" if feedbacks else "No Feedback"

		result.append({
			"item_name": d.item_name,
			"vendor_id": d.vendor_id,
			 "ratings": d.ratings,
			"avg_rating": f"{d.avg_rating} ({stars})",
			"all_feedbacks": feedbacks_html
		})


	return columns, result
