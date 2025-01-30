import json
from datetime import datetime, timedelta
import pytz
import frappe

from ..api.users import *

@frappe.whitelist(allow_guest=True)
def generate_coupon():
	try:
		if frappe.request.method != "POST":
			set_response(500, False, "Only POST method is allowed")
			return
		
		user_doc = get_hotpot_user_by_email()
		if not user_doc :
			set_response(404,False,"User Not found")
			return
		if not user_doc.get("role") == "Hotpot User":
			set_response(403,False,"Not Permitted to acess this resouce")
			return

		data = json.loads(frappe.request.data or "{}")
		required_fields = ["meal_id", "from_date", "to_date"]
		if missing := [field for field in required_fields if not data.get(field)]:
			return set_response(400, False, f"Missing required fields: {', '.join(missing)}")

		date_format = "%m/%d/%Y"
		try:
			from_date = datetime.strptime(data["from_date"], date_format).date()
			to_date = datetime.strptime(data["to_date"], date_format).date()
		except ValueError:
			return set_response(400, False, "Invalid date format. Use MM/DD/YYYY")

		try:
			meal_doc = frappe.get_doc("Hotpot Meal", data["meal_id"])
		except frappe.DoesNotExistError:
			return set_response(404, False, "Meal not found")

		current_datetime = datetime.now(pytz.timezone("Asia/Kolkata"))
		today = current_datetime.date()
		current_time_num = current_datetime.hour * 100 + current_datetime.minute
		output = []
		day_difference = (to_date - from_date).days + 1
		meal_title = meal_doc.meal_title
		user_coupon_count = user_doc.coupon_count
		meal_weight = 5
		is_buffer_time = False
		meal_buffer_count = meal_doc.buffer_coupon_count

		if user_coupon_count < meal_weight * day_difference:
			return set_response(400, False, "Insufficient coupons for selected date range")

		if int(meal_doc.start_time) <= current_time_num <= int(meal_doc.end_time):
			is_buffer_time = True
		buffer_used = 0


		for day in range(day_difference):
			current_date = from_date + timedelta(days=day)
			date_str = current_date.strftime("%Y-%m-%d")
			display_date = current_date.strftime("%d %b %Y")

			if current_date < today:
				output.append(f"Cannot create coupon for past date: {display_date}")
				continue

			is_today = current_date == today
			if is_today and is_buffer_time:
				if meal_buffer_count == 0:
					output.append(f"Not Enough Vendor Coupon for {display_date}")
					continue
				buffer_used += 1

			exists = frappe.db.exists("Hotpot Coupons", {
				"employee_id": user_doc.get("name"),
				"coupon_date": date_str,
				"title": meal_title
			})

			if exists:
				output.append(f"Already present {meal_title} on {display_date}")
				continue

			try:
				history_doc = frappe.new_doc("Hotpot Coupons History")
				history_doc.update({
					"employee_id": user_doc.get("name"),
					"type": "Creation",
					"message": f"Created coupon for {meal_title} ({display_date})"
				})
				history_doc.insert()

				meal_doc.append("coupons", {
					"employee_id": user_doc.get("name"),
					"coupon_date": date_str,
					"title": meal_title,
					"coupon_status": "1"
				})

				user_coupon_count -= meal_weight
				output.append(f"Created coupon for {meal_title} on {display_date}")

			except Exception as e:
				frappe.db.rollback()
				output.append(f"Failed to create coupon for {display_date}: {str(e)}")
				continue
		
		if is_buffer_time and buffer_used > 0:
			meal_doc.buffer_coupon_count = meal_buffer_count - buffer_used
			if meal_doc.buffer_coupon_count < 0:
				meal_doc.buffer_coupon_count = 0

		if meal_doc.has_value_changed():
			meal_doc.save()
		
		user_doc.coupon_count = user_coupon_count
		user_doc.save()
		frappe.db.commit()

		return set_response(200, True, "Processing completed", {
			"output": output,
			"remaining_coupons": user_coupon_count
		})

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Coupon Generation Error")
		return set_response(500, False, f"Server error: {str(e)}")

def set_response(code, success, message, data=None):
	frappe.response.update({
		"http_status_code": code,
		"success": success,
		"message": message,
		"data": data
	})