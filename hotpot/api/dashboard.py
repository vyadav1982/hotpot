from datetime import datetime, timedelta

import frappe
import frappe.utils
from frappe import _
import pytz


@frappe.whitelist(allow_guest=True)
def get_coupon_type_list():
	coupon_type_list = frappe.db.get_list(
		"Hotpot Coupon Type",
		filters=["isActive", "=","1"],
		fields=["name", "start_hour", "end_hour", "buffer_time"],
		order_by="start_hour",
	)
	return coupon_type_list

@frappe.whitelist(allow_guest=True)
def update_coupon_status(employee_id, meal_types, to_date, from_date):
    if isinstance(from_date, str):
        from_date = datetime.strptime(from_date, "%Y-%m-%d")
    if isinstance(to_date, str):
        to_date = datetime.strptime(to_date, "%Y-%m-%d")

    current_time = int(datetime.now().astimezone(pytz.timezone("Asia/Kolkata")).strftime("%H%M"))
    today = datetime.now().astimezone(pytz.timezone("Asia/Kolkata")).date()

    date = from_date
    while date <= to_date:
        coupons_to_update = frappe.get_all(
            "Hotpot Coupon",
            filters={"employee_id": employee_id, "status": ["=", "Upcoming"], "coupon_date": ["=", date]},
            fields=["name", "title", "status"],
        )

        for coupon in coupons_to_update:
            meal_end_hour = int(meal_types.get(coupon["title"]))
            
            if date.date() == today:  # Check only for today's date
                if current_time >= meal_end_hour:
                    doc = frappe.get_doc("Hotpot Coupon", coupon["name"])
                    doc.status = "Expired"
                    doc.save()
                    frappe.db.commit()
            else:  # For future dates, directly update status
                doc = frappe.get_doc("Hotpot Coupon", coupon["name"])
                doc.status = "Expired"
                doc.save()
                frappe.db.commit()

        date += timedelta(days=1)

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
	query = """
		select title,end_hour
		from `tabHotpot Coupon Type`
	"""
	if len(users) == 0:
		return []
	user_Id = []
	for user in users:
		user_Id.append(user.get("employee_id"))
	meal_types = {row["title"]: row["end_hour"] for row in frappe.db.sql(query, as_dict=True)}
	print("(())"*10,user_Id)
	for user in user_Id:
		update_coupon_status(user,meal_types,to_date,from_date)
	placeholders = ", ".join(["%s"] * len(user_Id))
	query = f"""
		SELECT
			a.employee_id,
			a.title,
			b.employee_name,
			a.coupon_date,
			a.coupon_time,
			a.served_by,
			a.status
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
