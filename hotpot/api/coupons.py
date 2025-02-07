import json
from datetime import datetime, timedelta
import pytz
import frappe

from ..api.users import *


@frappe.whitelist(allow_guest=True)
def get_coupon_count(start_date=datetime.today().strftime("%Y-%m-%d"),end_date=datetime.today().strftime("%Y-%m-%d")):
	try:
		if frappe.request.method != "GET":
			set_response(500, False, "Only GET method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(404, False, "User Not found")
			return

		if not user_doc.get("role") == "Hotpot Server":
			set_response(403, False, "Not Permitted to access this resource")
			return
		query = """ 
				SELECT 
					hm.meal_title, 
					COUNT(hc.name) AS coupon_count
				FROM 
					`tabHotpot Coupons` AS hc
				INNER JOIN 
					`tabHotpot Meal` AS hm ON hm.name = hc.parent
				WHERE 
					hm.vendor_id = %(vendor_name)s
					AND hm.meal_date BETWEEN %(start_date)s AND %(end_date)s
				GROUP BY 
					hm.meal_title
			"""
		params = {
			"vendor_name": user_doc.get("name"),
			"start_date": start_date,
			"end_date": end_date,
		}
		data = frappe.db.sql(query,params,as_dict=True)

		if not data :
			set_response(200,True,"No Coupons Available")
			return
		
		set_response(200,True,"Coupon Count Fetched successfully",data)
		return

	except Exception as e:
		set_response(500, False, "ERROR: " + str(e))

@frappe.whitelist(allow_guest=True)
def cancel_coupon():
	try:
		if frappe.request.method != "PUT":
			set_response(500, False, "Only PUT method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(404, False, "User Not found")
			return
		if not user_doc.get("role") == "Hotpot User":
			set_response(403, False, "Not Permitted to access this resource")
			return

		data = json.loads(frappe.request.data or "{}")
		meal_id = data.get("meal_id")
		coupon_id = data.get("coupon_id")

		if not meal_id or not coupon_id:
			set_response(400,False,"Required neccessary field")
			return

		today_str = datetime.today().strftime("%Y-%m-%d")
		current_datetime = datetime.now(pytz.timezone("Asia/Kolkata"))
		today = current_datetime.date()
		current_time_num = current_datetime.hour * 100 + current_datetime.minute
		meal_doc = frappe.get_doc("Hotpot Meal",meal_id)
		if not meal_doc:
			set_response(404,False,"Meal not found")
			return
		coupons = meal_doc.get("coupons")
		
		coupon_found = None
		for coupon in coupons:
			if coupon.name == coupon_id:
				coupon_found = coupon
				break

		if not coupon_found:
			set_response(400, False, "ERROR: Coupon Not Found")
			return
		if coupon_found.coupon_status =="-1" or coupon_found.coupon_status=="0":
			set_response(400,False,"Cannot cancel a redeemed or expired coupon")
			return
		if meal_doc.meal_date==datetime.strptime(datetime.today().strftime("%Y-%m-%d"), "%Y-%m-%d").date() and int(meal_doc.start_time) <= current_time_num:
			set_response(400,False,"Cannot Cancel at this moment")
			return
		if coupon_found.coupon_status=="2":
			set_response(409,False,"Coupon already Cancelled")
			return

		query="""
			UPDATE `tabHotpot Coupons` AS hc
			INNER JOIN `tabHotpot Meal` AS hm ON hm.name = hc.parent
			SET hc.coupon_status = 2
			WHERE hm.name=%(meal_id)s AND hc.name=%(coupon_id)s
			"""
		params = {
			"meal_id":meal_id,
			"coupon_id":coupon_id
		}
		frappe.db.sql(query,params)
		frappe.db.commit()
		set_response(200,True,"Cancelled successfully")
		return

	except Exception as e:
		set_response(500, False, "ERROR: " + str(e))
		return

@frappe.whitelist(allow_guest=True)
def scan_coupon():
	try:
		if frappe.request.method != "PUT":
			set_response(500, False, "Only PUT method is allowed")
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
		user_id = data.get("user_id")

		if not meal_id or not coupon_id or not user_id:
			set_response(400, False, "Missing required field")
			return
		
		user_doc = frappe.get_doc("Hotpot User", user_id)
		if not user_doc:
			set_response(404, False, "User Not Found")
			return
		meal_doc = frappe.get_doc("Hotpot Meal", meal_id)
		if not meal_doc:
			set_response(404, False, "Meal Not Found")
			return
		if not user_doc.get("name") == meal_doc.get("vendor_id"):
			set_response(403, False, "You are not authorised to scan this coupon.")
			return
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

		print(coupon_found,meal_id,current_time_num)

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
		coupon_found.served_by = user_doc.get("name")
		meal_doc.save()
		frappe.db.commit()

		data=[]
		data.append({
			"meal_title": meal_doc.get("meal_title"),
			"meal_date": meal_doc.get("meal_date"),
			"meal_time": f"{meal_doc.get('start_time')} - {meal_doc.get('end_time')}",
			"employee_id": user_doc.get("employee_id"),
			"employee_name": user_doc.get("employee_name"),
			"coupon_id": coupon_found.get("name"),
			"coupon_status": coupon_found.get("coupon_status"),
			"coupon_date": coupon_found.get("coupon_date"),
			"coupon_title": coupon_found.get("title"),
		})

		set_response(200, True, "SUCCESS: Meal Ready to Be Served", data)

	except Exception as e:
		set_response(500, False, "ERROR: " + str(e))
		return

@frappe.whitelist(allow_guest=True)
def get_scanned_coupons(start_date=datetime.today().strftime("%Y-%m-%d"),end_date=datetime.today().strftime("%Y-%m-%d"),page=1,limit=10):
	try:
		if frappe.request.method != "GET":
			set_response(500, False, "Only GET method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(404, False, "User Not found")
			return

		if not user_doc.get("role") == "Hotpot Server":
			set_response(403, False, "Not Permitted to access this resource")
			return

		query = """
			SELECT 
				hm.meal_title, 
				hc.coupon_status, 
				hc.coupon_date, 
				hm.start_time, 
				hm.end_time, 
				hc.name AS coupon_id, 
				hc.title AS coupon_title, 
				hc.employee_id, 
				hc.served_by
			FROM 
				`tabHotpot Coupons` AS hc
			INNER JOIN 
				`tabHotpot Meal` AS hm ON hm.name = hc.parent
			WHERE 
				hc.coupon_status = 0 and hm.meal_date BETWEEN %(start_date)s AND %(end_date)s
			ORDER BY 
				hc.modified DESC
			;
		"""
		params={
			"start_date": start_date,
			"end_date": end_date
		}
		data = frappe.db.sql(query,params, as_dict=True)
		if not data:
			set_response(200, False, "No Scanned Coupons Found")
			return

		set_response(200, True, "Scanned Coupons Fetched successfully", data)
		return

	except Exception as e:
		set_response(500, False, "ERROR: " + str(e))
		return


@frappe.whitelist(allow_guest=True)
def update_coupon_status():
	try:
		user_doc = get_hotpot_user_by_email()
		if not user_doc :
			set_response(404,False,"User Not found")
			return

		query="""
			UPDATE `tabHotpot Coupons` AS hc
			INNER JOIN `tabHotpot Meal` AS hm ON hm.name = hc.parent
			SET hc.coupon_status = "-1"
			WHERE hc.coupon_status = "1" 
			AND (
				hm.meal_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 3 DAY) AND DATE_SUB(CURDATE(), INTERVAL 1 DAY)
				OR (
					hm.meal_date = CURDATE() 
					AND CAST(LPAD(hm.end_time, 4, '0') AS UNSIGNED) < 
						CAST(DATE_FORMAT(CONVERT_TZ(NOW(), 'UTC', 'Asia/Kolkata'), '%H%i') AS UNSIGNED)
				)
			);
			"""
		data = frappe.db.sql(query)
		frappe.db.commit()
		return
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Failed to update status")
		set_response(500, False, f"Server error: {str(e)}")
		return



@frappe.whitelist(allow_guest=True)
def get_all_coupons(start_date=datetime.today().strftime("%Y-%m-%d"),end_date=datetime.today().strftime("%Y-%m-%d"),page=1,limit=10):
	try:
		if frappe.request.method != "GET":
			set_response(500, False, "Only GET method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc :
			set_response(404,False,"User Not found")
			return

		if not page or not limit or not end_date or not start_date:
			set_response(400,False,"Please provide all fields")
			return

		update_coupon_status()
		
		page = int(page)
		limit = int(limit)
		start = (page - 1) * limit
		if user_doc.get("role") == "Hotpot Server":
			query = """
				SELECT
					hm.start_time AS start_time,
					hm.end_time AS end_time,
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
				"start_date": start_date,
				"end_date": end_date,
				"start": start,
				"limit": limit
			}


			ans = frappe.db.sql(query, params, as_dict=True)
			if not ans :
				set_response(200,True,"No Coupon found",[])
				return
			set_response(200,True,"Coupons fetched successfully",ans)
			return
		
		elif user_doc.get("role") == "Hotpot User":
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
				"start_date": start_date,
				"end_date": end_date,
			}
			meals = frappe.db.sql(query,params,as_dict=True)
			query = """
			(
			SELECT
				'coupon' AS record_type,
				hc.name,
				hc.title AS title,
				hc.coupon_status,
				hc.coupon_date,
				hm.start_time AS start_time,
				hm.end_time AS end_time,
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
				"start_date": start_date,
				"end_date": end_date,
				"start": start,
				"limit": limit
			}
			
			ans = frappe.db.sql(query, params, as_dict=True)
			if not ans :
				set_response(200,True,"No Coupon found",[])
				return
			set_response(200,True,"Coupons fetched successfully",ans)
			return

		elif user_doc.get("role") == "Hotpot Admin":
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
				"start_date": start_date,
				"end_date": end_date,
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
		set_response(500, False, f"Server error: {str(e)}")
		return

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
		required_fields = ["meal_id"]
		if missing := [field for field in required_fields if not data.get(field)]:
			return set_response(400, False, f"Missing required fields: {', '.join(missing)}")

		if "from_date" not in data:
			data["from_date"] = datetime.today().strftime("%Y-%m-%d")
		if "to_date" not in data:
			data["to_date"] = datetime.today().strftime("%Y-%m-%d")

		from_date=data["from_date"] = datetime.strptime(data["from_date"], "%Y-%m-%d").date()
		to_date=data["to_date"] = datetime.strptime(data["to_date"], "%Y-%m-%d").date()

		try:
			meal_doc = frappe.get_doc("Hotpot Meal", data["meal_id"])
		except frappe.DoesNotExistError:
			return set_response(404, False, "Meal not found")

		print(type(from_date),type(to_date))
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
		set_response(500, False, f"Server error: {str(e)}")
		return

def set_response(http_status_code, status, message, data=None):
	frappe.local.response["http_status_code"] = http_status_code
	frappe.response["status"] = status
	frappe.response["message"] = message
	frappe.response["data"] = data