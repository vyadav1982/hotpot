import json
from datetime import datetime, timedelta

import frappe
import pytz
import re

from ..api.users import *
from hotpot.utils.utc_time import *


@frappe.whitelist(allow_guest=True)
def get_coupon_count(start_date, end_date):
	try:
		if frappe.request.method != "GET":
			set_response(405, False, "Only GET method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(404, False, "User Not found")
			return

		if not user_doc.get("role") == "Hotpot Server":
			set_response(403, False, "Not Permitted to access this resource")
			return
		start_date = f"{start_date} 00:00:00"
		start_date = get_utc_datetime_obj(start_date)
		end_date = f"{end_date} 23:59:59"
		end_date = get_utc_datetime_obj(end_date)
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
					AND hc.coupon_date BETWEEN %(start_date)s AND %(end_date)s
				GROUP BY
					hm.meal_title
			"""
		params = {
			"vendor_name": user_doc.get("guest_of"),
			"start_date": start_date,
			"end_date": end_date,
		}
		data = frappe.db.sql(query, params, as_dict=True)

		if not data:
			set_response(200, True, "No Coupons Available")
			return

		set_response(200, True, "Coupon Count Fetched successfully", data)
		return

	except Exception as e:
		set_response(500, False, "ERROR: " + str(e))


@frappe.whitelist(allow_guest=True)
def cancel_coupon():
	try:
		if frappe.request.method != "PUT":
			set_response(405, False, "Only PUT method is allowed")
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
			set_response(400, False, "Required neccessary field")
			return

		meal_doc = frappe.get_doc("Hotpot Meal", meal_id)
		if not meal_doc:
			set_response(404, False, "Meal not found")
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
		if coupon_found.coupon_status == "-1" or coupon_found.coupon_status == "0":
			set_response(400, False, "Cannot cancel a redeemed or expired coupon")
			return
		

		# if (
		# 	get_utc_date(meal_doc.meal_date) == utc_date
		# 	and (get_utc_time(meal_doc.start_time) <= current_time)
		# ):
		# 	set_response(400, False, "Cannot Cancel at this moment")
		# 	return
		current_datetime =get_local_datetime_obj(datetime.utcnow().replace(tzinfo=None))
		current_time = current_datetime.time()

		meal_start_time = get_local_datetime_obj(meal_doc.start_time).time()

		diff = (datetime.combine(datetime.min, meal_start_time) - datetime.combine(datetime.min, current_time)).total_seconds()
		diff = int(diff)
		cancel = (diff < 0 or diff <= (meal_doc.cancellation_time) * 60 * 60)

		if cancel :
			set_response(400,False,"Cannot Cancel at this moment")
			return


		if coupon_found.coupon_status == "2":
			set_response(409, False, "Coupon already Cancelled")
			return

		query = """
			UPDATE `tabHotpot Coupons` AS hc
			INNER JOIN `tabHotpot Meal` AS hm ON hm.name = hc.parent
			SET hc.coupon_status = 2
			WHERE hm.name=%(meal_id)s AND hc.name=%(coupon_id)s
			"""
		user_doc = frappe.get_doc("Hotpot User",coupon_found.employee_id)
		if not coupon_found.birthday_coupon and not coupon_found.joining_day and coupon_found.is_guest == "":
			user_doc.coupon_count= user_doc.coupon_count + meal_doc.meal_weight
		params = {"meal_id": meal_id, "coupon_id": coupon_id}
		frappe.db.sql(query, params)
		history_doc = frappe.new_doc("Hotpot Coupons History")
		history_doc.update(
			{
				"employee_id": user_doc.get("name"),
				"type": "Cancellation",
				"message": f"Cancelled a coupon for {meal_doc.meal_title}",
				"meal_id": data["meal_id"],
			}
		)
		history_doc.insert()
		user_doc.save()
		frappe.db.commit()
		set_response(200, True, "Cancelled successfully")
		return

	except Exception as e:
		set_response(500, False, "ERROR: " + str(e))
		return

@frappe.whitelist(allow_guest=True)
def get_redeemed_coupon():
	try:
		if frappe.request.method!= "GET":
			set_response(405, False, "Only GET method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(404, False, "User Not found")
			return
		if not (user_doc.get("role") == "Hotpot Server" or user_doc.get("role") == "Hotpot Vendor"):
			set_response(403, False, "Not Permitted to access this resource")
			return
		data = json.loads(frappe.request.data or "{}")
		user_id = data.get("user_id")
		coupon_id=data.get("coupon_id")
		if not user_id or not coupon_id:
			set_response(400, False, "Missing required field")
			return
		query = """
			Select * from
				`tabHotpot Coupons` AS hc
			where hc.name = %(coupon_id)s
		"""
		params= {
			"coupon_id": coupon_id
		}
		coupon_data = frappe.db.sql(query,params,as_dict=True)

		if not coupon_data:
			set_response(404, False, "Coupon Not Found")
			return
		query = """
			Select employee_name,employee_id from `tabHotpot User` AS hu where hu.name = %(user_id)s
		"""
		params = {
			"user_id": user_id
		}
		user_data = frappe.db.sql(query,params,as_dict=True)
		if not user_data:
			set_response(404, False, "User Not Found")
			return
		merged_data = {**coupon_data[0], **user_data[0]}


		set_response(200, True, "Redeemed coupons detailed fetched successfully", merged_data)
		return

	except Exception as e:
		set_response(500, False, "ERROR: " + str(e))
		return

@frappe.whitelist(allow_guest=True)
def scan_coupon():
	try:
		if frappe.request.method != "PUT":
			set_response(405, False, "Only PUT method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(404, False, "User Not found")
			return

		if not (user_doc.get("role") == "Hotpot Server" or user_doc.get("role") == "Hotpot Vendor"):
			set_response(403, False, "Not Permitted to access this resource")
			return

		data = json.loads(frappe.request.data or "{}")
		meal_id = data.get("meal_id")
		coupon_id = data.get("coupon_id")
		user_id = data.get("user_id")
		vendor_id = data.get("vendor_id")

		if not meal_id or not coupon_id or not user_id or not vendor_id:
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
		if not vendor_id == meal_doc.get("vendor_id"):
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

		current_datetime = get_local_datetime_obj(datetime.utcnow())
		current_time = current_datetime.time()
		local_date = current_datetime.date()

		# print(coupon_found, meal_id, current_time_num)

		if get_local_datetime_obj(coupon_found.get("coupon_date")).date() != local_date:
			set_response(400, False, "NOTICE: Coupon Not Valid for Today")
			return

		start_time = get_local_datetime_obj(meal_doc.get("start_time")).time()
		if start_time:
			if current_time < start_time:
				set_response(400, False, "NOTICE: Too Early to Serve")
				return

		end_time = get_local_datetime_obj(meal_doc.get("end_time")).time()
		if end_time:
			if current_time >end_time:
				set_response(400, False, "ERROR: Meal Serving Time Passed")
				return

		if int(coupon_found.get("coupon_status")) == 0:
			set_response(400, False, "ERROR: Coupon Already Consumed")
			return

		coupon_found.coupon_status = 0
		coupon_found.served_by = user_doc.get("name")
		meal_doc.save()
		frappe.db.commit()

		data = []
		data.append(
			{
				"meal_title": meal_doc.get("meal_title"),
				"meal_date": meal_doc.get("meal_date"),
				"meal_time": f"{meal_doc.get('start_time')} - {meal_doc.get('end_time')}",
				"employee_id": user_doc.get("employee_id"),
				"employee_name": user_doc.get("employee_name"),
				"coupon_id": coupon_found.get("name"),
				"coupon_status": coupon_found.get("coupon_status"),
				"coupon_date": coupon_found.get("coupon_date"),
				"coupon_title": coupon_found.get("title"),
			}
		)

		set_response(200, True, "SUCCESS: Meal Ready to Be Served", data)

	except Exception as e:
		set_response(500, False, "ERROR: " + str(e))
		return


@frappe.whitelist(allow_guest=True)
def get_scanned_coupons(
	start_date,
	end_date,
	page=1,
	limit=10,
):
	try:
		if frappe.request.method != "GET":
			set_response(405, False, "Only GET method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(404, False, "User Not found")
			return

		if not (user_doc.get("role") == "Hotpot Server" or user_doc.get("role") == "Hotpot Vendor"):
			set_response(403, False, "Not Permitted to access this resource")
			return
		start_date = f"{start_date} 00:00:00"
		start_date = get_utc_datetime_obj(start_date)
		end_date = f"{end_date} 23:59:59"
		end_date = get_utc_datetime_obj(end_date)

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
				hc.served_by,
				U.employee_name AS vendor_name
			FROM
				`tabHotpot Coupons` AS hc
			INNER JOIN
				`tabHotpot Meal` AS hm ON hm.name = hc.parent
			INNER JOIN
				`tabHotpot User` as U on hm.vendor_id = U.name
			WHERE
				hc.coupon_status = 0
				and hm.vendor_id = %(vendor_id)s
				and hc.coupon_date BETWEEN %(start_date)s AND %(end_date)s
			ORDER BY
				hc.modified DESC
			;
		"""
		params = {
			"start_date": start_date,
			"end_date": end_date,
			"vendor_id": user_doc.get("guest_of"),
		}
		data = frappe.db.sql(query, params, as_dict=True)
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
		if not user_doc:
			set_response(404, False, "User Not found")
			return
		user_tz = get_user_timezone()
		now_local = get_local_datetime_obj(datetime.utcnow().replace(tzinfo=None))


		query = """
			UPDATE `tabHotpot Coupons` AS hc
			INNER JOIN `tabHotpot Meal` AS hm ON hm.name = hc.parent
			SET hc.coupon_status = "-1"
			WHERE hc.coupon_status = "1"
			AND (
				DATE(CONVERT_TZ(hc.coupon_date, '+00:00', %s)) < DATE(%s)
				OR (
					DATE(CONVERT_TZ(hc.coupon_date, '+00:00', %s)) = DATE(%s)
					AND TIME(CONVERT_TZ(hm.end_time, '+00:00', %s)) <= TIME(%s)
				)
			);
		"""
		params = (user_tz, now_local, user_tz, now_local,user_tz,now_local)
		frappe.db.sql(query,params)
		frappe.db.commit()
		return
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Failed to update status")
		set_response(500, False, f"Server error: {str(e)}")
		return


@frappe.whitelist(allow_guest=True)
def get_all_coupons(
	start_date,
	end_date,
	identifier=None,
	page=1,
	limit=10,
):
	try:
		if frappe.request.method != "GET":
			set_response(405, False, "Only GET method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(404, False, "User Not found")
			return

		if not page or not limit or not end_date or not start_date:
			set_response(400, False, "Please provide all fields")
			return

		update_coupon_status()

		start_date = f"{start_date} 00:00:00"
		end_date = f"{end_date} 23:59:59"
		start_date = get_utc_datetime_obj(start_date)
		end_date = get_utc_datetime_obj(end_date)

		if identifier:
			search_coupon(start_date,end_date,identifier)
			return
		

		page = int(page)
		limit = int(limit)
		start = (page - 1) * limit


		if user_doc.get("role") == "Hotpot Server" or user_doc.get("role") == "Hotpot Vendor":
			query = """
				SELECT
					hm.start_time AS start_time,
					hm.end_time AS end_time,
					U.employee_name AS vendor_name,
					hc.*
				FROM
					`tabHotpot Coupons` AS hc
				INNER JOIN
					`tabHotpot Meal` AS hm ON hm.name = hc.parent
				INNER JOIN
					`tabHotpot User` as U on hm.vendor_id = U.name
				WHERE
					hm.vendor_id = %(vendor_name)s
					AND hc.coupon_date BETWEEN %(start_date)s AND %(end_date)s
				LIMIT %(start)s, %(limit)s;
				"""

			params = {
				"vendor_name": user_doc.get("guest_of"),
				"start_date": start_date,
				"end_date": end_date,
				"start": start,
				"limit": limit,
			}
			ans = frappe.db.sql(query, params, as_dict=True)
			if not ans:
				set_response(200, True, "No Coupon found", [])
				return
			ans.sort(
				key=lambda x: (
					get_local_datetime_obj(x["start_time"]).time(),
					get_local_datetime_obj(x["end_time"]).time(),
					x["coupon_status"] != 1
				)
			)

			set_response(200, True, "Coupons fetched successfully", ans)
			return

		elif user_doc.get("role") == "Hotpot User":
			params = {
				"start_date": start_date,
				"end_date": end_date,
				"user_name": user_doc.get("name"),
				"start": start,
				"limit": limit,
			}
			coupons = frappe.db.sql(
				"""
				SELECT 
					'coupon' AS record_type,
					hc.name,
					hc.title AS title,
					hc.coupon_status,
					hc.coupon_date,
					hc.served_by,
					hm.vendor_id,
					hm.start_time AS start_time,
					hm.end_time AS end_time,
					hm.name AS meal_id,
					U.employee_name AS vendor_name
				FROM 
					`tabHotpot Coupons` AS hc
				INNER JOIN 
					`tabHotpot Meal` AS hm ON hm.name = hc.parent
				INNER JOIN 
					`tabHotpot User` AS U ON hm.vendor_id = U.name
				WHERE
					hc.coupon_date BETWEEN %(start_date)s AND %(end_date)s
					AND hc.employee_id = %(user_name)s
					AND hc.guest_of IS NULL
				LIMIT %(start)s, %(limit)s;
			""", params, as_dict=True)


			for coupon in coupons:
				rating = frappe.db.sql("""
					SELECT 
						rating, feedback
					FROM `tabHotpot Meal Rating`
					WHERE parent = %(meal_id)s
				""", {"meal_id": coupon["meal_id"]}, as_dict=True)
				
				coupon["rating"] = rating[0]["rating"] if rating else None
				coupon["feedback"] = rating[0]["feedback"] if rating else None
				
			if not coupons:
				set_response(200, True, "No Coupon found", [])
				return
			set_response(200, True, "Coupons fetched successfully", coupons)
			return

		elif user_doc.get("role") == "Hotpot Admin":
			query = """
				(
				SELECT *
				FROM `tabHotpot Coupons`
				WHERE coupon_date BETWEEN %(start_date)s AND %(end_date)s
				ORDER BY creation DESC
				LIMIT  %(start)s, %(limit)s;
				)
			"""
			params = {"start_date": start_date, "end_date": end_date, "start": start, "limit": limit}
			ans = frappe.db.sql(query, params, as_dict=True)
			if not ans:
				set_response(404, False, "No Coupon found")
				return
			ans.sort(
				key=lambda x: (
					get_local_datetime_obj(x["start_time"]).time(),
					get_local_datetime_obj(x["end_time"]).time(),
					x["coupon_status"] != 1
				)
			)
			set_response(200, True, "Coupons fetched successfully", ans)
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
			set_response(405, False, "Only POST method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(404, False, "User Not found")
			return
		if user_doc.get("role") != "Hotpot User":
			set_response(403, False, "Not Permitted to access this resource")
			return
		hotpot_config = frappe.get_single("Hotpot Configurations")
		data = json.loads(frappe.request.data or "{}")
		required_fields = ["meal_id", "date"]
		for_guest = data.get('guest', False) 
		if for_guest:
			required_fields.append("approval_id")
		missing = [field for field in required_fields if not data.get(field)]
		if missing:
			return set_response(400, False, f"Missing required fields: {', '.join(missing)}")
		
		date = data.get("date")
		local_time_now = get_local_time_now()
		start_date = f"{date} {local_time_now}"
		start_date = get_utc_datetime_obj(start_date)
		from_date = start_date.date()

		if for_guest and hotpot_config.get("can_generate_for_guest") == 0:
			return set_response(400, False, "Not allowed to generate coupon for guest")
		
		approval_id = data.get('approval_id', None)
		approval_doc = None

		is_birthday = hotpot_config.get("free_birthday_meal") == 1 and user_doc.get("date_of_birth") == get_local_datetime_obj(start_date).date()
		is_joining_day = hotpot_config.get("free_joining_day_meal") == 1 and user_doc.get("date_of_joining") == get_local_datetime_obj(start_date).date()

		try:
			meal_doc = frappe.get_doc("Hotpot Meal", data["meal_id"])
		except frappe.DoesNotExistError:
			return set_response(404, False, "Meal not found")
		
		if approval_id:
			approval_doc = frappe.get_doc("Hotpot Approvals", approval_id)
			print(approval_doc.date.date(),from_date)
			if approval_doc.approval_status != "Approved":
				set_response(400, False, "Approval is not approved")
				return
			if approval_doc.is_active == 0:
				set_response(400, False, "Approval is already used")
				return
			if approval_doc.meal_id != data["meal_id"]:
				set_response(400, False, "Approval is not for this meal")
				return
			if approval_doc.requested_by != user_doc.get("name"):
				set_response(400, False, "Approval is not for this user")
				return
			if approval_doc.date.date() != from_date:
				set_response(400, False, "Approval is not for this date")
				return


		current_datetime_local = get_local_datetime_obj(datetime.utcnow())
		local_date_today = current_datetime_local.date()
		current_time = current_datetime_local.time()

		# first =((datetime.strptime(get_local_datetime_obj(meal_doc.start_time).time(), "%H:%M:%S") - datetime.strptime(current_time, "%H:%M:%S")).seconds)>0
		# second = ((datetime.strptime(get_local_datetime_obj(meal_doc.start_time).time(), "%H:%M:%S") - datetime.strptime(current_time, "%H:%M:%S")).seconds)<= (meal_doc.lead_time)*60*60

		start_time_str = get_local_datetime_obj(meal_doc.start_time).time().strftime("%H:%M:%S")
		current_time_str = current_time.strftime("%H:%M:%S")
		start_time = datetime.strptime(start_time_str, "%H:%M:%S")
		current_time_dt = datetime.strptime(current_time_str, "%H:%M:%S")

		time_difference = (start_time - current_time_dt).seconds

		first = time_difference > 0
		second = time_difference <= (meal_doc.lead_time) * 60 * 60

		meal_title = meal_doc.meal_title
		user_coupon_count = user_doc.coupon_count
		meal_weight = meal_doc.get("meal_weight")
		meal_buffer_count = meal_doc.buffer_coupon_count

		if from_date < meal_doc.meal_date.date():
			set_response(400, False, f"Cannot create coupon for past date: {from_date.strftime('%d %b %Y')}",start_date)
			return
		print("Hello........................")
		
		if from_date==get_local_datetime_obj(datetime.utcnow()).date() and get_local_datetime_obj(meal_doc.get("end_time")).time() <= get_local_datetime_obj(datetime.utcnow()).time():
			set_response(400, False, "Meal time already passed.")
			return
		
		# Check if required amount of coupons are available
		if not for_guest and user_coupon_count < meal_weight:
			return set_response(400, False, "Insufficient currency to create coupon")
		is_buffer_time = get_local_datetime_obj(meal_doc.start_time).time() <= current_time <= get_local_datetime_obj(meal_doc.end_time).time()
		buffer_used = 0
		third = from_date==datetime.utcnow().date()
		user_tz = get_user_timezone()
		if (first and second and third):
			set_response(400,False,"Cannot create coupon in meal preparation time")
			return
		query = """
			SELECT 1 
			FROM `tabHotpot Coupons`
			WHERE `employee_id` = %s
			AND `parent` = %s
			AND `coupon_status` != '2'
			AND DATE(CONVERT_TZ(coupon_date, '+00:00', %s)) = %s
			LIMIT 1;
		"""

		params = (user_doc.get("name"), data["meal_id"], str(user_tz), get_local_datetime_obj(start_date).date())
		exists = frappe.db.sql(query, params)


		print(exists)
		if not for_guest and exists:
			set_response(409,False,f"Coupon for {meal_title} on {from_date.strftime('%d %b %Y')} is already generated !",start_date)
			return

		# If buffer time then check for vendor coupons
		if get_local_datetime_obj(start_date).date() == local_date_today and is_buffer_time:
			if meal_buffer_count == 0:
				set_response(400, False, f"Not Enough Vendor Coupons for {from_date.strftime('%d %b %Y')}",start_date)
				return
			buffer_used += 1


		try:
			# History for user transactions
			history_doc = frappe.new_doc("Hotpot Coupons History")
			if for_guest:
				history_doc.update(
                    {
                        "employee_id": user_doc.get("name"),
                        "type": "Guest Creation",
                        "message": f"Generated coupon for {approval_doc.guest_name}{(approval_doc.guest_mobile_no)} for meal {meal_title} on {from_date.strftime('%d %b %Y')}",
                        "meal_id": data["meal_id"],
                    }
                )
			else:
				history_doc.update(
					{
						"employee_id": user_doc.get("name"),
						"type": "Creation",
						"message": f"Created coupon for {meal_title} {start_date}",
						"meal_id": data["meal_id"],
					}
				)
			
			history_doc.insert()

			# Append created coupon in meal
			meal_doc.append(
				"coupons",
				{
					"employee_id": user_doc.get("name"),
					"coupon_date": start_date,
					"title": meal_title,
					"coupon_status": "1",
					**({"guest_of": user_doc.get("name")} if for_guest else {}),
					**({"birthday_coupon": 1} if is_birthday else {}),
					**({"joining_day": 1} if is_joining_day else {}),
				},
			)

			if not for_guest and not is_birthday and not is_joining_day:
				user_coupon_count -= meal_weight

		except Exception as e:
			frappe.db.rollback()
			frappe.log_error(frappe.get_traceback(), "Coupon Generation Error")
			set_response(500, False, f"Failed to create coupon: {str(e)}")
			return

		# Update meal buffer count if buffer time
		if is_buffer_time and buffer_used > 0:
			meal_doc.buffer_coupon_count = max(0, meal_buffer_count - buffer_used)
		if for_guest:
			approval_doc.is_active = 0
			approval_doc.save()
		meal_doc.save()
		frappe.db.set_value(
			"Hotpot User",
			user_doc.get("name"),
			{
				"coupon_count": user_coupon_count,
			},
		)
		frappe.db.commit()
		message = f"Generated coupon for {from_date.strftime('%d %b %Y')}."
		if for_guest:
			message = f"Welcome, {approval_doc.guest_name}! Your meal coupon for {from_date.strftime('%d %b %Y')} has been generated."
		elif is_birthday:
			message = f"🎉 Happy Birthday {user_doc.employee_name}! 🎂 Enjoy your special day—your meal is on us!"
		elif is_joining_day:
			message = f"🎊 Welcome aboard {user_doc.employee_name}! 🎉 As a warm gesture, your meal is on us today. Enjoy!"
			
		return set_response(200, True,message, {"remaining_coupons": user_coupon_count,"start_date":start_date})

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Coupon Generation Error")
		set_response(500, False, f"Server error: {str(e)}")
		return

is_valid_email = lambda email: bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email))
@frappe.whitelist(allow_guest=True)
def search_coupon(start_date,end_date,identifier):
	try:
		if not start_date or not end_date:
			return set_response(400, False, "Missing required field")

		vendor_doc = get_hotpot_user_by_email()
		if not vendor_doc:
			return set_response(404, False, "User Not found")

		if not vendor_doc.get("role") in ["Hotpot Server", "Hotpot Vendor"]:
			return set_response(403, False, "Not Permitted to access this resource")
		date = get_utc_datetime_obj(date)

		identifier_field = "email" if is_valid_email(identifier) else "employee_id"

		user_doc = frappe.db.sql(
			f"SELECT name FROM `tabHotpot User` WHERE {identifier_field} = %s AND role = 'Hotpot User' LIMIT 1;",
			(identifier,), as_dict=True
		)

		if not user_doc:
			return set_response(404, False, "User Not found")

		coupon_data = frappe.db.sql(
			"""
			SELECT hc.*, hm.*
			FROM `tabHotpot Coupons` hc
			JOIN `tabHotpot Meal` hm ON hc.parent = hm.name
			WHERE employee_id = %s AND coupon_date BETWEEN %s AND %s
			ORDER BY coupon_date DESC;
			""",
			(user_doc[0]["name"], start_date,end_date), as_dict=True
		)

		if not coupon_data:
			return set_response(404, False, "No coupon found for this user on this date")

		return set_response(200, True, "Coupon Data fetched successfully", coupon_data)

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Coupon Search Error")
		return set_response(500, False, f"Server error: {str(e)}")
	
@frappe.whitelist(allow_guest=True)
def get_guest_coupon(date):
	try:
		if frappe.request.method != "GET":
			set_response(405, False, "Only GET method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(404, False, "User Not found")
			return

		if not user_doc.get("role") == "Hotpot User":
			set_response(403, False, "Not Permitted to access this resource")
			return

		if not date:
			set_response(400, False, "Please provide date")
			return

		start_date = f"{date} 00:00:00"
		end_date = f"{date} 23:59:59"
		start_date = get_utc_datetime_obj(start_date)
		end_date = get_utc_datetime_obj(end_date)


		query = """
			Select * from
				`tabHotpot Coupons` AS hc
			where hc.guest_of = %s and hc.coupon_date between %s and %s
		"""
		params = [user_doc.get("name"),start_date,end_date]
		coupons_data = frappe.db.sql(query, params, as_dict=True)

		if not coupons_data:
			set_response(404, False, "No guest coupon")
			return

		set_response(200, True, "Guest coupons detailed fetched successfully", coupons_data)
		return

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Coupon Search Error")
		return set_response(500, False, f"Server error: {str(e)}")



def set_response(http_status_code, status, message, data=None):
	frappe.local.response["http_status_code"] = http_status_code
	frappe.response["status"] = status
	frappe.response["message"] = message
	frappe.response["data"] = data
