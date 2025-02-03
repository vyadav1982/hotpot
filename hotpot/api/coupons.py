import json
from datetime import datetime, timedelta
import pytz
import frappe

from ..api.users import *


@frappe.whitelist(allow_guest=True)
def scan_coupon():
	try:
		if frappe.request.method != "POST":
			set_response(500, False, "Only POST method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(404, False, "User Not found")
			return

		if not user_doc.get("role") == "Hotpot Server":
			set_response(403, False, "Not Permitted to access this resource")
			return

		data = json.loads(frappe.request.data or "{}")
		meal_id = data.get("meal_id")
		coupon_id = data.get("coupon_id")

		if not meal_id or not coupon_id:
			set_response(400, False, "Missing required field")
			return
		
		meal_doc = frappe.get_doc("Hotpot Meal", meal_id)
		coupons = meal_doc.get("coupons")
		
		coupon_found = None
		for coupon in coupons:
			if coupon.name == coupon_id:
				coupon_found = coupon
				break

		if not coupon_found:
			set_response(400, False, "ERROR: Coupon Not Found")
			return

		today_str = datetime.today().strftime("%Y-%m-%d")
		current_datetime = datetime.now(pytz.timezone("Asia/Kolkata"))
		today = current_datetime.date()
		current_time_num = current_datetime.hour * 100 + current_datetime.minute

		if coupon_found.get("coupon_date").strftime("%Y-%m-%d") != today_str:
			set_response(400, False, "NOTICE: Coupon Not Valid for Today")
			return

		start_time = meal_doc.get("start_time")
		if start_time:
			if current_time_num < int(start_time):
				set_response(400, False, "NOTICE: Too Early to Serve")
				return

		end_time = meal_doc.get("end_time")
		if end_time:
			if current_time_num > int(end_time):
				set_response(400, False, "ERROR: Meal Serving Time Passed")
				return

		if int(coupon_found.get("coupon_status")) == 0:
			set_response(400, False, "ERROR: Coupon Already Consumed")
			return

		coupon_found.coupon_status = 0
		meal_doc.save()
		frappe.db.commit()

		set_response(200, True, "SUCCESS: Meal Ready to Be Served", coupon_found)

	except Exception as e:
		set_response(500, False, "ERROR: " + str(e))


@frappe.whitelist(allow_guest=True)
def get_all_coupons(page,limit,start_date,end_date):
	try:
		if frappe.request.method != "GET":
			set_response(500, False, "Only GET method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc :
			set_response(404,False,"User Not found")
			return
		print(user_doc.get("name"))


		if not page or not limit or not end_date or not start_date:
			set_response(400,False,"Please provide all fields")
			return
		
		page = int(page)
		limit = int(limit)
		start = (page - 1) * limit
		if user_doc.get("role") == "Hotpot Server":
			# meal_data = frappe.db.get_list(
			# 	"Hotpot Meal",
			# 	fields=["name"],
			# 	filters=[
			# 		["vendor_id", "=", user_doc.get("name")],
			# 		["meal_date", ">=", datetime.today().strftime("%Y-%m-%d")],
			# 		["meal_date", "<=", datetime.today().strftime("%Y-%m-%d")]
			# 	]
			# )
			# ans=[]
			# for id in meal_data:
			# 	meal_doc = frappe.get_doc("Hotpot Meal",id)
			# 	ans.append(meal_doc.coupons)
			query = """
				SELECT
					hc.*
				FROM
					`tabHotpot Coupons` AS hc
				INNER JOIN
					`tabHotpot Meal` AS hm ON hm.name = hc.parent
				WHERE
					hm.vendor_id = %(vendor_name)s
					AND hm.meal_date BETWEEN %(start_date)s AND %(end_date)s
				LIMIT %(start)s, %(limit)s;
				"""

			params = {
				"vendor_name": user_doc.get("name"),
				"start_date": start_date or datetime.today().strftime("%Y-%m-%d"),
				"end_date": end_date or datetime.today().strftime("%Y-%m-%d"),
				"start": start,
				"limit": limit
			}

			ans = frappe.db.sql(query, params, as_dict=True)
			if not ans :
				set_response(404,False,"No Coupon found")
				return
			set_response(200,True,"Coupons fetched successfully",ans)
			return
		
		elif user_doc.get("role") == "Hotpot User":
			# meal_data = frappe.db.get_list(
			# 	"Hotpot Meal",
			# 	fields = ["name"],
			# 	filters = [
			# 		["meal_date", ">=", datetime.today().strftime("%Y-%m-%d")],
			# 		["meal_date", "<=", datetime.today().strftime("%Y-%m-%d")]
			# 	]
			# )
			# ans =[]
			# for meal in meal_data:
			# 	meal_doc = frappe.get_doc("Hotpot Meal", meal["name"])

			# 	user_coupons=[]
			# 	for coupon in meal_doc.coupons:
			# 		if coupon.employee_id == user_doc.get("name"):
			# 			user_coupons.append({
			# 				"id":coupon.name,
			# 				"coupon status": coupon.coupon_status,
			# 				"coupon_date":coupon.coupon_date
			# 			})

			# 	user_ratings=[]
			# 	for coupon in meal_doc.ratings:
			# 		if coupon.employee_id ==user_doc.get("name"):
			# 			user_ratings.append({
			# 				"id":coupon.name,
			# 				"rating": coupon.rating,
			# 				"feedback":coupon.feedback
			# 			})
			query= """
				(
				SELECT 
					name 
				FROM 
					`tabHotpot Meal`
				WHERE
					meal_date BETWEEN %(start_date)s AND %(end_date)s
				)
			"""
			params = {
				"start_date": start_date or datetime.today().strftime("%Y-%m-%d"),
				"end_date": end_date or datetime.today().strftime("%Y-%m-%d"),
			}
			meals = frappe.db.sql(query,params,as_dict=True)
			print("{{{{}}}}",meals)
			query = """
			(
			SELECT
				'coupon' AS record_type,
				hc.name AS id,
				hc.title AS title,
				hc.coupon_status AS status,
				hc.coupon_date AS coupon_date,
				hm.name AS meal_id
			FROM
				`tabHotpot Coupons` AS hc
			INNER JOIN
				`tabHotpot Meal` AS hm ON hm.name = hc.parent
			WHERE
				hc.coupon_date BETWEEN %(start_date)s AND %(end_date)s
				AND hc.employee_id = %(user_name)s
			)
			LIMIT %(start)s, %(limit)s;
			"""

			params = {
				"user_name": user_doc.get("name"),
				"start_date": start_date or datetime.today().strftime("%Y-%m-%d"),
				"end_date": end_date or datetime.today().strftime("%Y-%m-%d"),
				"start": start,
				"limit": limit
			}
			
			ans = frappe.db.sql(query, params, as_dict=True)
			if not ans :
				set_response(404,False,"No Coupon found")
				return
			set_response(200,True,"Coupons fetched successfully",ans)
			return

		elif user_doc.get("role") == "Hotpot Admin":
			# coupons = frappe.get_list(
			# 	"Hotpot Coupons",
			# 	filters = [["employee_id", "=" ,user_doc.get("name")]],
			# 	fields=["*"],
			# 	start=start,
			# 	page_length=limit,
			# 	order_by="creation desc"
			# )
			query = f"""
				(
				SELECT *
				FROM `tabHotpot Coupons`
				WHERE coupon_date BETWEEN %(start_date)s AND %(end_date)s
				ORDER BY creation DESC
				LIMIT  %(start)s, %(limit)s;
				)
			"""
			params = {
				"start_date": start_date or  datetime.today().strftime("%Y-%m-%d"),
				"end_date": end_date or datetime.today().strftime("%Y-%m-%d"),
				"start": start,
				"limit": limit
			}
			ans = frappe.db.sql(query, params, as_dict=True)
			if not ans :
				set_response(404,False,"No Coupon found")
				return
			set_response(200,True,"Coupons fetched successfully",ans)
			return
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Coupon Generation Error")
		return set_response(500, False, f"Server error: {str(e)}")

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
		day_difference = abs(to_date - from_date).days + 1
		meal_title = meal_doc.meal_title
		user_coupon_count = user_doc.coupon_count
		meal_weight = meal_doc.get("meal_weight")
		is_buffer_time = False
		meal_buffer_count = meal_doc.buffer_coupon_count

		# Check if required amount of coupon are present or not
		if user_coupon_count < meal_weight * day_difference:
			return set_response(400, False, "Insufficient coupons for selected date range")

		if int(meal_doc.start_time) <= current_time_num <= int(meal_doc.end_time):
			is_buffer_time = True
		buffer_used = 0


		for day in range(day_difference):
			current_date = from_date + timedelta(days=day)
			date_str = current_date.strftime("%Y-%m-%d")
			display_date = current_date.strftime("%d %b %Y")

			# Cannot create coupon for past
			if current_date < today:
				set_response(500,False,f"Cannot create coupon for past date: {display_date}")
				return

			# If buffer time then check for vendor coupons
			is_today = current_date == today
			if is_today and is_buffer_time:
				if meal_buffer_count == 0:
					set_response(500,False,f"Not Enough Vendor Coupon for {display_date}")
					return
				buffer_used += 1
			
			# Check for duplicate coupon
			exists = frappe.db.exists("Hotpot Coupons", {
				"employee_id": user_doc.get("name"),
				"coupon_date": date_str,
				"title": meal_title
			})

			if exists:
				set_response(409,False,f"Already present {meal_title} on {display_date}")
				return

			try:
				# History used for user transactions
				history_doc = frappe.new_doc("Hotpot Coupons History")
				history_doc.update({
					"employee_id": user_doc.get("name"),
					"type": "Creation",
					"message": f"Created coupon for {meal_title} ({display_date})"
				})
				history_doc.insert()

				# Append created coupon in meal
				meal_doc.append("coupons", {
					"employee_id": user_doc.get("name"),
					"coupon_date": date_str,
					"title": meal_title,
					"coupon_status": "1"
				})

				user_coupon_count -= meal_weight
				# output.append(f"Created coupon for {meal_title} on {display_date}")

			except Exception as e:
				frappe.db.rollback()
				# output.append(f"Failed to create coupon for {display_date}: {str(e)}")
				set_response(500,False,f"Failed to create coupon for {display_date}: {str(e)}")
				return
		
		# Decide whether we need to chnange coupon count or not
		if is_buffer_time and buffer_used > 0:
			meal_doc.buffer_coupon_count = meal_buffer_count - buffer_used
			if meal_doc.buffer_coupon_count < 0:
				meal_doc.buffer_coupon_count = 0

		meal_doc.save()
		frappe.db.set_value("Hotpot User", user_doc.get("name"), {
			"coupon_count" : user_coupon_count,
		})
		frappe.db.commit()

		return set_response(200, True, "Processing completed", {
			"remaining_coupons": user_coupon_count
		})

	except Exception as e:
		frappe.db.rollback()
		print(frappe.get_traceback())
		frappe.log_error(frappe.get_traceback(), "Coupon Generation Error")
		return set_response(500, False, f"Server error: {str(e)}")

def set_response(http_status_code, status, message, data=None):
	frappe.local.response["http_status_code"] = http_status_code
	frappe.response["status"] = status
	frappe.response["message"] = message
	frappe.response["data"] = data