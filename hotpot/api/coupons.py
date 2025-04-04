import json
from datetime import datetime, timedelta

import frappe
import pytz
import re

from ..api.users import *
from hotpot.utils.utc_time import *



@frappe.whitelist()
def get_coupon_count(start_date, end_date,user=False):
	try:
		if frappe.request.method != "GET":
			set_response(405, False, "Only GET method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(404, False, "User Not found")
			return

		if not user and  user_doc.get("role") == "Hotpot User":
			set_response(403, False, "Not Permitted to access this resource")
			return
		start_date = f"{start_date} 00:00:00"
		start_date = get_utc_datetime_obj(start_date)
		end_date = f"{end_date} 23:59:59"
		end_date = get_utc_datetime_obj(end_date)
		start_date = get_local_datetime_obj(start_date).date()
		end_date = get_local_datetime_obj(end_date).date()
		
		
		user_timezone = get_user_timezone() or "Asia/Kolkata"

		if user_doc.get("role") =="Hotpot User":
			coupon_query = """
				SELECT hc.coupon_status, 
					COUNT(hc.name) AS coupon_count
				FROM `tabHotpot Coupons` AS hc
				WHERE hc.employee_id = %(user_name)s
					AND DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %(user_timezone)s)) 
					BETWEEN %(start_date)s AND %(end_date)s
				GROUP BY hc.coupon_status
				ORDER BY hc.coupon_status ASC;
			"""

			coupon_data = frappe.db.sql(coupon_query,{
				"user_name": user_doc.get("name"),
				"user_timezone": user_timezone,
				"start_date": start_date,
				"end_date": end_date
			},as_dict=True)
			set_response(200,True,"Coupon data fetched successfully",coupon_data)
			return


		coupon_query = """
			SELECT DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %(user_timezone)s)) AS coupon_date, 
				COUNT(hc.name) AS coupon_count
			FROM `tabHotpot Coupons` AS hc
			INNER JOIN `tabHotpot Meal` AS hm ON hm.name = hc.parent
			WHERE hm.vendor_id = %(vendor_name)s 
			AND DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %(user_timezone)s)) BETWEEN %(start_date)s AND %(end_date)s
			GROUP BY DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %(user_timezone)s))
			ORDER BY DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %(user_timezone)s)) ASC;
		"""

	
		feedback_query = """
			SELECT COUNT(hr.name) AS total_feedback
			FROM `tabHotpot Meal Rating` AS hr
			INNER JOIN `tabHotpot Meal` AS hm ON hm.name = hr.parent
			WHERE hm.vendor_id = %(vendor_name)s 
			AND DATE(CONVERT_TZ(hr.creation, 'UTC', %(user_timezone)s)) BETWEEN %(start_date)s AND %(end_date)s;
		"""

		
		# params = {"vendor_name": user_doc.get("guest_of"), "start_date": start_date, "end_date": end_date}

		# day_wise_data = frappe.db.sql(coupon_query, params, as_dict=True)
		day_wise_data=frappe.db.sql(coupon_query, {
			"vendor_name": user_doc.get("guest_of"),
			"start_date": start_date,
			"end_date": end_date,
			"user_timezone": user_timezone
		},as_dict=True)
		# total_feedback = frappe.db.sql(feedback_query, params, as_dict=True)[0].get("total_feedback", 0)
		total_feedback=frappe.db.sql(feedback_query, {
			"vendor_name": user_doc.get("guest_of"),
			"start_date": start_date,
			"end_date": end_date,
			"user_timezone": user_timezone
		}, as_dict=True)[0].get("total_feedback", 0)

		response = {
			"total_feedback": total_feedback,
			"day_wise_consumption": day_wise_data
		}

		if not response:
			set_response(200, True, "No Data Available")
			return

		set_response(200, True, "Data Fetched successfully", response)
		return

	except Exception as e:
		set_response(500, False, "ERROR: " + str(e))
@frappe.whitelist()
def get_report(start_date,end_date):
	try:
		if frappe.request.method != "GET":
			set_response(405, False, "Only GET method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(404, False, "User Not found")
			return

		if user_doc.get("role") == "Hotpot User":
			set_response(403, False, "Not Permitted to access this resource")
			return
		start_date = f"{start_date} 00:00:00"
		start_date = get_utc_datetime_obj(start_date)
		end_date = f"{end_date} 23:59:59"
		end_date = get_utc_datetime_obj(end_date)
		start_date = get_local_datetime_obj(start_date).date()
		end_date = get_local_datetime_obj(end_date).date()
		
		
		user_timezone = get_user_timezone() or "Asia/Kolkata"
		coupon_query = """
			SELECT 
				hm.meal_title AS meal_name,
				hm.meal_weight AS meal_weight,
				DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %(user_timezone)s)) AS coupon_date,
				COUNT(hc.name) AS total_coupons,
				CAST(SUM(CASE WHEN hc.coupon_status = 1 THEN 1 ELSE 0 END) AS SIGNED) AS Upcoming,
				CAST(SUM(CASE WHEN hc.coupon_status = -1 THEN 1 ELSE 0 END) AS SIGNED) AS Expired,
				CAST(SUM(CASE WHEN hc.coupon_status = 0 THEN 1 ELSE 0 END) AS SIGNED) AS Consumed,
				CAST(SUM(CASE WHEN hc.coupon_status = 2 THEN 1 ELSE 0 END) AS SIGNED) AS Cancelled,
				(SELECT COUNT(hf.name) FROM `tabHotpot Meal Rating` AS hf WHERE hf.parent = hm.name) AS total_feedback
			FROM `tabHotpot Coupons` AS hc
			INNER JOIN `tabHotpot Meal` AS hm ON hm.name = hc.parent
			WHERE hm.vendor_id = %(vendor_name)s 
			AND DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %(user_timezone)s)) 
				BETWEEN %(start_date)s AND %(end_date)s
			GROUP BY hm.name, coupon_date
			ORDER BY coupon_date ASC;
		"""
		data = frappe.db.sql(coupon_query, {
			"vendor_name": user_doc.get("guest_of"),
			"start_date": start_date,
			"end_date": end_date,
			"user_timezone": user_timezone
		}, as_dict=True)

		set_response(200,True,"Data Fetched successfully",data)
		return

		
	except Exception as e:
		set_response(500, False, "ERROR: " + str(e))

@frappe.whitelist()
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
		if meal_doc.is_deleted:
			set_response(400, False, "Oops! The vendor deleted the meal!😢")  
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
		if(diff<0):
			# set_response(400, False, "Nice try! But instead of canceling, why not enjoy the meal? Sorry, your coupon is staying right where it is! 😜🍽️")
			set_response(400, False, "Cannot cancel a coupon during meal time.")

		if cancel :
			# set_response(400, False, f"Oops! You’re too late! Coupons turn into pumpkins {meal_doc.cancellation_time} hours before the meal starts. No take-backs now! 🎃⏳🍽️")
			set_response(400, False, f"Cannot cancel a coupon during cancellation time.")
			return


		if coupon_found.coupon_status == "2":
			set_response(409, False, "Coupon already Cancelled")
			# set_response(409, False, "Too late! Coupon’s already gone! ❌")
			return

		query = """
			UPDATE `tabHotpot Coupons` AS hc
			INNER JOIN `tabHotpot Meal` AS hm ON hm.name = hc.parent
			SET hc.coupon_status = 2
			WHERE hm.name=%(meal_id)s AND hc.name=%(coupon_id)s
			"""
		user_doc = frappe.get_doc("Hotpot User",coupon_found.employee_id)
		if not coupon_found.birthday_coupon and not coupon_found.joining_day and not coupon_found.guest_of:
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
		set_response(200, True, "Coupon cancelled successfully")
		# set_response(200, True, "Poof! Gone. 🎩🐇")  
		return

	except Exception as e:
		set_response(500, False, "ERROR: " + str(e))
		return

@frappe.whitelist()
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

@frappe.whitelist()
def scan_coupon():
	try:
		if frappe.request.method != "PUT":
			set_response(405, False, "Only PUT method is allowed")
			return

		data = json.loads(frappe.request.data or "{}")
		data = json.loads(frappe.request.data or "{}")
		meal_id = data.get("meal_id")
		coupon_id = data.get("coupon_id")
		user_id = data.get("user_id")
		vendor_id = data.get("vendor_id")

		if not meal_id or not user_id or not vendor_id:
			set_response(400, False, "Missing required field")
			return

		user_doc = get_hotpot_user_by_email()
		emp_doc=None
		# try:
		# 	emp_doc = frappe.get_doc("Hotpot User", user_id)
		# except frappe.DoesNotExistError:
		# 	emp_doc = get_hotpot_user_by_tag_id(user_id)
		if frappe.db.exists("Hotpot User", user_id):
			emp_doc = frappe.get_doc("Hotpot User", user_id)
		else:
			emp_doc = get_hotpot_user_by_tag_id(user_id)

		if not emp_doc:
			set_response(404, False, "Employee not found")
			return
		if not user_doc:
			set_response(404, False, "User Not Found")
			return
		if not (user_doc.get("role") == "Hotpot Server" or user_doc.get("role") == "Hotpot Vendor"):
			set_response(403, False, "Not Permitted to access this resource")
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
		if not coupons:
			set_response(400, False, "ERROR: No Coupons found for this meal.")
			return

		if not coupon_id:
			for coupon in coupons:
				if get_local_datetime_obj(coupon.coupon_date).date() == get_local_datetime_obj(datetime.utcnow()).date() and coupon.employee_id == emp_doc.name:
					coupon_found=coupon
					break
		else:
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
				"employee_id": emp_doc.get("employee_id"),
				"employee_name": emp_doc.get("employee_name"),
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


@frappe.whitelist()
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
		start_date = get_local_datetime_obj(start_date).date()
		end_date = get_local_datetime_obj(end_date).date()
		user_timezone = get_user_timezone() or "Asia/Kolkata"
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
				and DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %(user_timezone)s)) BETWEEN %(start_date)s AND %(end_date)s
			ORDER BY
				hc.modified DESC
			;
		"""
		params = {
			"user_timezone":user_timezone,
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


@frappe.whitelist()
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


@frappe.whitelist()
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
		start_date = get_local_datetime_obj(start_date).date()
		end_date = get_local_datetime_obj(end_date).date()
		
		user_timezone = get_user_timezone() or "Asia/Kolkata"
		

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
					AND DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %(user_timezone)s)) BETWEEN %(start_date)s AND %(end_date)s
				LIMIT %(start)s, %(limit)s;
				"""

			params = {
				"vendor_name": user_doc.get("guest_of"),
				"user_timezone":user_timezone,
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
				"user_timezone":user_timezone,
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
					DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %(user_timezone)s)) BETWEEN %(start_date)s AND %(end_date)s
					AND hc.employee_id = %(user_name)s
					AND hc.guest_of IS NULL
				LIMIT %(start)s, %(limit)s;
			""", params, as_dict=True)


			for coupon in coupons:
				rating = frappe.db.sql("""
					SELECT 
						rating, feedback
					FROM `tabHotpot Meal Rating`
					WHERE parent = %(meal_id)s AND employee_id = %(employee_id)s
				""", {"meal_id": coupon["meal_id"],"employee_id":user_doc.get("name")}, as_dict=True)
				
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
				WHERE DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %(user_timezone)s)) BETWEEN %(start_date)s AND %(end_date)s
				ORDER BY creation DESC
				LIMIT  %(start)s, %(limit)s;
				)
			"""
			params = {"user_timezone":user_timezone,"start_date": start_date, "end_date": end_date, "start": start, "limit": limit}
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

		data = json.loads(frappe.request.data or "{}")
		tagId = data.get("tag_id")
		user_doc = get_hotpot_user_by_tag_id(tagId) if tagId else get_hotpot_user_by_email()
		if not user_doc:
			set_response(404, False, "User Not Found")
			return
		role = user_doc.get("role")
		if role not in ["Hotpot Admin", "Hotpot HR", "Hotpot User"]:
			set_response(403, False, "Not Permitted to access this resource")
			return
		hotpot_config = frappe.get_single("Hotpot Configurations")
		required_fields = ["meal_id", "date"]
		for_guest = data.get('guest', False) 
		if for_guest and role=="Hotpot User":
			required_fields.append("approval_id")
		missing = [field for field in required_fields if not data.get(field)]
		if missing:
			return set_response(400, False, f"Missing required fields: {', '.join(missing)}")
		
		meal_ids = data.get("meal_id")
		date = data.get("date")
		qty = data.get("qty",1)
		if not isinstance(meal_ids, list):
			meal_ids = [meal_ids]
		meal_docs = {}
		temp_docs = []
		total_coupons_consumed=0
		for j in range(int(qty)):
			for i in range(len(meal_ids)):
				meal_id = meal_ids[i]
				local_time_now = get_local_time_now()
				start_date = get_utc_datetime_obj(f"{date} {local_time_now}")
				from_date = start_date.date()

				if role=="Hotpot User" and  for_guest and hotpot_config.get("can_generate_for_guest") == 0:
					return set_response(400, False, "Not allowed to generate coupon for guest")
				
				approval_id = data.get('approval_id', None)
				approval_doc = None
				
				dob = user_doc.get("date_of_birth")
				start = get_local_datetime_obj(start_date).date()
				is_birthday = False
				if role=="Hotpot User" and dob:
					is_birthday = (
						hotpot_config.get("free_birthday_meal") == 1
						and dob.month == start.month
						and dob.day == start.day
					)
				is_joining_day = False
				if role=="Hotpot User" and user_doc.get("joining_date"):
					is_joining_day = hotpot_config.get("free_joining_day_meal") == 1 and user_doc.get("date_of_joining") == get_local_datetime_obj(start_date).date()

				try:
					meal_doc = frappe.get_doc("Hotpot Meal", meal_id)
				except frappe.DoesNotExistError:
					return set_response(404, False, "Meal not found")
				
				if approval_id:
					approval_doc = frappe.get_doc("Hotpot Approvals", approval_id)
					if approval_doc.approval_status != "Approved":
						set_response(400, False, "Approval is not approved")
						return
					if approval_doc.is_active == 0:
						set_response(400, False, "Approval is already used")
						return
					if approval_doc.meal_id != meal_id:
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

				if get_local_datetime_obj(start_date).date()< get_local_datetime_obj(datetime.utcnow().replace(tzinfo=None)).date():
					set_response(400, False, f"Cannot create coupon for past date: {from_date.strftime('%d %b %Y')}",start_date)
					return
				
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

				params = (user_doc.get("name"), meal_id, str(user_tz), get_local_datetime_obj(start_date).date())
				exists = frappe.db.sql(query, params)


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
					if for_guest and role=="Hotpot User":
						history_doc.update(
							{
								"employee_id": user_doc.get("name"),
								"type": "Guest Creation",
								"message": f"Generated coupon for {approval_doc.guest_name}{(approval_doc.guest_mobile_no)} for meal {meal_title} on {from_date.strftime('%d %b %Y')}",
								"meal_id": meal_id,
							}
						)
					else:
						history_doc.update(
							{
								"employee_id": user_doc.get("name"),
								"type": "Creation",
								"message": f"Created coupon for {meal_title} {start_date}",
								"meal_id": meal_id,
							}
						)
					
					temp_docs.append(history_doc)

					# Append created coupon in meal
					meal_doc.append(
						"coupons",
						{
							"employee_id": user_doc.get("name"),
							"coupon_date": start_date,
							"title": meal_title,
							"coupon_status": "1",
							**({"guest_of": user_doc.get("name")} if for_guest else {}),
							**({"birthday_coupon": 1} if is_birthday and not for_guest else {}),
							**({"joining_day": 1} if is_joining_day and not for_guest else {}),
							**({"approval_id": approval_id} if (for_guest and role=="Hotpot User") else {}),
						},
					)

					if not for_guest and not is_birthday and not is_joining_day:
						user_coupon_count -= meal_weight
						total_coupons_consumed+=meal_weight
					

				except Exception as e:
					frappe.db.rollback()
					frappe.log_error(frappe.get_traceback(), "Coupon Generation Error")
					set_response(500, False, f"Failed to create coupon: {str(e)}")
					return

				# Update meal buffer count if buffer time
				if is_buffer_time and buffer_used > 0:
					meal_doc.buffer_coupon_count = max(0, meal_buffer_count - buffer_used)
				if for_guest and role=="Hotpot User":
					approval_doc.is_active = 0
				if role=="Hotpot User":
					meal_docs[meal_id] = meal_doc
				else:
					meal_doc.save()

		if approval_doc :
			approval_doc.save()
		for meal_doc in meal_docs.values():
			meal_doc.save()
		frappe.db.set_value(
				"Hotpot User",
				user_doc.get("name"),
				{
					"coupon_count": user_doc.coupon_count-total_coupons_consumed,
				},
			)
		for doc in temp_docs:
			doc.insert()
		frappe.db.commit()
		message = f"Generated coupon for {from_date.strftime('%d %b %Y')}."
		if for_guest and role=="Hotpot User":
			message = f"Welcome, {approval_doc.guest_name}! Your meal coupon for {from_date.strftime('%d %b %Y')} has been generated."
		elif is_birthday and role=="Hotpot User":
			if start.month == get_local_datetime_obj(datetime.utcnow()).month and start.day == get_local_datetime_obj(datetime.utcnow()).day:
				message = f"🎉 Happy Birthday {user_doc.employee_name}! 🎂 Enjoy your special day—your meal is on us!"
			else:
				message = f"🎉 Early Birthday Treat! 🎂 {user_doc.employee_name}, we’re celebrating you in advance! Your birthday meal coupon is ready for {start.strftime('%d %b %Y')}!"
			# message = f"🎉 Happy Birthday {user_doc.employee_name}! 🎂 Enjoy your special day—your meal is on us!"
		elif is_joining_day and role=="Hotpot User":
			message = f"🎊 Welcome aboard {user_doc.employee_name}! 🎉 As a warm gesture, your meal is on us today. Enjoy!"
			
		return set_response(200, True,message, {"remaining_coupons": user_doc.coupon_count-total_coupons_consumed,"start_date":start_date})

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Coupon Generation Error")
		set_response(500, False, f"Server error: {str(e)}")
		return

is_valid_email = lambda email: bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email))
@frappe.whitelist()
def search_coupon(start_date,end_date,identifier):
	try:
		if not start_date or not end_date:
			return set_response(400, False, "Missing required field")

		vendor_doc = get_hotpot_user_by_email()
		if not vendor_doc:
			return set_response(404, False, "User Not found")

		if not vendor_doc.get("role") in ["Hotpot Server", "Hotpot Vendor"]:
			return set_response(403, False, "Not Permitted to access this resource")
		# date = get_utc_datetime_obj(date)

		identifier_field = "email" if is_valid_email(identifier) else "employee_id"

		user_doc = frappe.db.sql(
			f"SELECT name FROM `tabHotpot User` WHERE {identifier_field} = %s AND role = 'Hotpot User' LIMIT 1;",
			(identifier,), as_dict=True
		)

		if not user_doc:
			return set_response(404, False, "User Not found")
		start_date = get_local_datetime_obj(start_date).date()
		end_date = get_local_datetime_obj(end_date).date()
		user_timezone = get_user_timezone() or "Asia/Kolkata"
		coupon_data = frappe.db.sql(
			"""
			SELECT hc.*, hm.*
			FROM `tabHotpot Coupons` hc
			JOIN `tabHotpot Meal` hm ON hc.parent = hm.name
			WHERE employee_id = %s AND DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %(user_timezone)s)) BETWEEN %s AND %s
			ORDER BY coupon_date DESC;
			""",
			(user_doc[0]["name"],user_timezone, start_date,end_date), as_dict=True
		)

		if not coupon_data:
			return set_response(404, False, "No coupon found for this user on this date")

		return set_response(200, True, "Coupon Data fetched successfully", coupon_data)

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Coupon Search Error")
		return set_response(500, False, f"Server error: {str(e)}")
	

@frappe.whitelist()
def get_admin_guest_coupon(date, qty=None, page=0, limit=10):
	try:
		if frappe.request and frappe.request.method != "GET":
			return set_response(405, False, "Only GET method is allowed")

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			return set_response(404, False, "User Not found")

		if user_doc.get("role") not in ["Hotpot User", "Hotpot Admin"]:
			return set_response(403, False, "Not Permitted to access this resource")

		if not date:
			return set_response(400, False, "Please provide date")

		start_date = get_local_datetime_obj(get_utc_datetime_obj(f"{date} 00:00:00")).date()
		end_date = get_local_datetime_obj(get_utc_datetime_obj(f"{date} 23:59:59")).date()
		user_timezone = get_user_timezone() or "Asia/Kolkata"

		try:
			page = int(page)
			limit = int(qty) if qty else int(limit)
			if page < 0 or limit <= 0:
				return set_response(400, False, "Page must be >= 0 and Limit must be > 0")
		except ValueError:
			return set_response(400, False, "Invalid pagination values")
		if page==0:
			page=1
		start = (page - 1) * limit
		params = [user_timezone, start_date, end_date, start, limit]

		query = f"""
			SELECT 
				hc.name AS coupon_id,
				hc.modified,
				hm.meal_title,
				U.employee_name,
				hc.coupon_date,
				hc.coupon_status
			FROM 
				`tabHotpot Coupons` AS hc
			LEFT JOIN 
				`tabHotpot Meal` AS hm ON hm.name = hc.parent
			INNER JOIN
				`tabHotpot User` AS U ON hm.vendor_id = U.name
			WHERE DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %s)) BETWEEN %s AND %s
			ORDER BY hc.modified DESC
			LIMIT %s, %s
		"""

		coupons_data = frappe.db.sql(query, tuple(params), as_dict=True)

		if not coupons_data:
			return set_response(200, False, "No guest coupon found.", [])

		return set_response(200, True, "Guest coupons fetched successfully", coupons_data)

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Coupon Search Error")
		return set_response(500, False, f"Server error: {str(e)}")

# @frappe.whitelist()
# def get_admin_guest_coupon(date, qty=None):
# 	try:
# 		if frappe.request and frappe.request.method != "GET":
# 			return set_response(405, False, "Only GET method is allowed")

# 		user_doc = get_hotpot_user_by_email()
# 		if not user_doc:
# 			return set_response(404, False, "User Not found")

# 		if user_doc.get("role") not in ["Hotpot User", "Hotpot Admin"]:
# 			return set_response(403, False, "Not Permitted to access this resource")

# 		if not date:
# 			return set_response(400, False, "Please provide date")

# 		start_date = f"{date} 00:00:00"
# 		end_date = f"{date} 23:59:59"
# 		start_date = get_utc_datetime_obj(start_date)
# 		end_date = get_utc_datetime_obj(end_date)

# 		start_date = get_local_datetime_obj(start_date).date()
# 		end_date = get_local_datetime_obj(end_date).date()
				
# 		user_timezone = get_user_timezone() or "Asia/Kolkata"

# 		limit_clause = ""
# 		params = [user_timezone, start_date, end_date]
		
# 		if qty:
# 			try:
# 				qty = int(qty)
# 				if qty <= 0:
# 					return set_response(400, False, "Quantity must be greater than 0")
# 				limit_clause = "LIMIT %s"
# 				params.append(qty)
# 			except ValueError:
# 				return set_response(400, False, "Invalid quantity value")
		
# 		query = f"""
# 			SELECT 
# 				hc.name AS coupon_id,
# 				hc.modified,
# 				hm.meal_title,
# 				U.employee_name,
# 				hc.coupon_date,
# 				hc.coupon_status
# 			FROM 
# 				`tabHotpot Coupons` AS hc
# 			LEFT JOIN 
# 				`tabHotpot Meal` AS hm ON hm.name = hc.parent
# 			INNER JOIN
# 				`tabHotpot User` AS U ON hm.vendor_id = U.name
# 			WHERE DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %s)) BETWEEN %s AND %s
# 			ORDER BY hc.modified DESC
# 			{limit_clause}
# 		"""

# 		coupons_data = frappe.db.sql(query, tuple(params), as_dict=True)

# 		if not coupons_data:
# 			return set_response(200, False, "No guest coupon found.",[])

# 		return set_response(200, True, "Guest coupons fetched successfully", coupons_data)

# 	except Exception as e:
# 		frappe.db.rollback()
# 		frappe.log_error(frappe.get_traceback(), "Coupon Search Error")
# 		return set_response(500, False, f"Server error: {str(e)}")
@frappe.whitelist()
def get_guest_coupon(date):
	try:
		if frappe.request.method != "GET":
			set_response(405, False, "Only GET method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(404, False, "User Not found")
			return

		if not user_doc.get("role") in ["Hotpot User","Hotpot Admin"]:
			set_response(403, False, "Not Permitted to access this resource")
			return

		if not date:
			set_response(400, False, "Please provide date")
			return

		start_date = f"{date} 00:00:00"
		end_date = f"{date} 23:59:59"
		start_date = get_utc_datetime_obj(start_date)
		end_date = get_utc_datetime_obj(end_date)

		start_date = get_local_datetime_obj(start_date).date()
		end_date = get_local_datetime_obj(end_date).date()
		
		user_timezone = get_user_timezone() or "Asia/Kolkata"

		query = """
			SELECT 
				hc.name AS coupon_id,
				hc.parent AS meal_id,
				hc.title AS title,
				hc.coupon_status,
				hc.coupon_date,
				hc.served_by,
				hm.vendor_id,
				hm.start_time AS start_time,
				hm.end_time AS end_time,
				hm.name AS meal_id,
				U.employee_name AS vendor_name,
				ap.guest_name AS guest_name,
				ap.is_active AS approval_active

			FROM 
				`tabHotpot Coupons` AS hc
			LEFT JOIN 
				`tabHotpot Meal` AS hm ON hm.name = hc.parent
			INNER JOIN
				`tabHotpot Approvals` AS ap ON ap.name = hc.approval_id
			INNER JOIN
				`tabHotpot User` AS U ON hm.vendor_id = U.name
			WHERE 
				hc.guest_of = %s 
				AND DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %s)) BETWEEN %s AND %s
		"""

		params = [user_doc.get("name"),user_timezone,start_date,end_date]
		coupons_data = frappe.db.sql(query, params, as_dict=True)

		if not coupons_data:
			set_response(200, True, "No guest coupon",[])
			return

		set_response(200, True, "Guest coupons detailed fetched successfully", coupons_data)
		return

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Coupon Search Error")
		return set_response(500, False, f"Server error: {str(e)}")


@frappe.whitelist(allow_guest=True)
def generate_coupon_admin():
	try:
		if frappe.request.method != "POST":
			set_response(405, False, "Only POST method is allowed")
			return

		data = json.loads(frappe.request.data or "{}")
		tagId = data.get("tag_id")
		user_doc = get_hotpot_user_by_tag_id(tagId) if tagId else get_hotpot_user_by_email()
		if not user_doc:
			set_response(404, False, "User Not Found")
			return
		role = user_doc.get("role")
		if role not in ["Hotpot Admin", "Hotpot HR", "Hotpot User"]:
			set_response(403, False, "Not Permitted to access this resource")
			return
		hotpot_config = frappe.get_single("Hotpot Configurations")
		required_fields = ["meal_id", "date"]
		for_guest = data.get('guest', False) 
		if for_guest and role=="Hotpot User":
			required_fields.append("approval_id")
		missing = [field for field in required_fields if not data.get(field)]
		if missing:
			return set_response(400, False, f"Missing required fields: {', '.join(missing)}")
		
		meal_ids = data.get("meal_id")
		date = data.get("date")
		qty = data.get("qty",1)
		if not isinstance(meal_ids, list):
			meal_ids = [meal_ids]
		meal_docs = {}
		temp_docs = []
		coupon_id=[]
		total_coupons_consumed=0
		for j in range(int(qty)):
			for i in range(len(meal_ids)):
				meal_id = meal_ids[i]
				local_time_now = get_local_time_now()
				start_date = get_utc_datetime_obj(f"{date} {local_time_now}")
				from_date = start_date.date()

				if role=="Hotpot User" and  for_guest and hotpot_config.get("can_generate_for_guest") == 0:
					return set_response(400, False, "Not allowed to generate coupon for guest")
				
				approval_id = data.get('approval_id', None)
				approval_doc = None
				
				dob = user_doc.get("date_of_birth")
				start = get_local_datetime_obj(start_date).date()
				is_birthday = False
				if role=="Hotpot User" and dob:
					is_birthday = (
						hotpot_config.get("free_birthday_meal") == 1
						and dob.month == start.month
						and dob.day == start.day
					)
				is_joining_day = False
				if role=="Hotpot User" and user_doc.get("joining_date"):
					is_joining_day = hotpot_config.get("free_joining_day_meal") == 1 and user_doc.get("date_of_joining") == get_local_datetime_obj(start_date).date()

				try:
					meal_doc = frappe.get_doc("Hotpot Meal", meal_id)
				except frappe.DoesNotExistError:
					return set_response(404, False, "Meal not found")
				
				if approval_id:
					approval_doc = frappe.get_doc("Hotpot Approvals", approval_id)
					if approval_doc.approval_status != "Approved":
						set_response(400, False, "Approval is not approved")
						return
					if approval_doc.is_active == 0:
						set_response(400, False, "Approval is already used")
						return
					if approval_doc.meal_id != meal_id:
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

				if get_local_datetime_obj(start_date).date()< get_local_datetime_obj(datetime.utcnow().replace(tzinfo=None)).date():
					set_response(400, False, f"Cannot create coupon for past date: {from_date.strftime('%d %b %Y')}",start_date)
					return
				
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

				params = (user_doc.get("name"), meal_id, str(user_tz), get_local_datetime_obj(start_date).date())
				exists = frappe.db.sql(query, params)


				if not for_guest and exists:
					set_response(409,False,f"Coupon for {meal_title} on {from_date.strftime('%d %b %Y')} is already generated !",start_date)
					return

				# If buffer time then check for vendor coupons
				if get_local_datetime_obj(start_date).date() == local_date_today and is_buffer_time and meal_buffer_count<qty:
					if meal_buffer_count == 0:
						set_response(400, False, f"Not Enough Vendor Coupons for {from_date.strftime('%d %b %Y')}",start_date)
						return
					buffer_used += 1


				try:
					# History for user transactions
					history_doc = frappe.new_doc("Hotpot Coupons History")
					if for_guest and role=="Hotpot User":
						history_doc.update(
							{
								"employee_id": user_doc.get("name"),
								"type": "Guest Creation",
								"message": f"Generated coupon for {approval_doc.guest_name}{(approval_doc.guest_mobile_no)} for meal {meal_title} on {from_date.strftime('%d %b %Y')}",
								"meal_id": meal_id,
							}
						)
					else:
						history_doc.update(
							{
								"employee_id": user_doc.get("name"),
								"type": "Creation",
								"message": f"Created coupon for {meal_title} {start_date}",
								"meal_id": meal_id,
							}
						)
					
					temp_docs.append(history_doc)

					# Append created coupon in meal
					meal_doc.append(
						"coupons",
						{
							"employee_id": user_doc.get("name"),
							"coupon_date": start_date,
							"title": meal_title,
							"coupon_status": "1",
							**({"guest_of": user_doc.get("name")} if for_guest else {}),
							**({"birthday_coupon": 1} if is_birthday and not for_guest else {}),
							**({"joining_day": 1} if is_joining_day and not for_guest else {}),
							**({"approval_id": approval_id} if (for_guest and role=="Hotpot User") else {}),
						},
					)

					if not for_guest and not is_birthday and not is_joining_day:
						user_coupon_count -= meal_weight
						total_coupons_consumed+=meal_weight
					

				except Exception as e:
					frappe.db.rollback()
					frappe.log_error(frappe.get_traceback(), "Coupon Generation Error")
					set_response(500, False, f"Failed to create coupon: {str(e)}")
					return

				# Update meal buffer count if buffer time
				if is_buffer_time and buffer_used > 0:
					meal_doc.buffer_coupon_count = max(0, meal_buffer_count - buffer_used)
				if for_guest and role=="Hotpot User":
					approval_doc.is_active = 0
				if role=="Hotpot User":
					meal_docs[meal_id] = meal_doc
				else:
					meal_doc.save()
					coupon_id.append(meal_doc.coupons[-1].name)

		if approval_doc :
			approval_doc.save()
		for meal_doc in meal_docs.values():
			meal_doc.save()
		for doc in temp_docs:
			doc.insert()
		frappe.db.commit()
			
		return set_response(200, True,"Coupon generated successfully!",coupon_id)

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Coupon Generation Error")
		set_response(500, False, f"Server error: {str(e)}")
		return


def set_response(http_status_code, status, message, data=None):
	frappe.local.response["http_status_code"] = http_status_code
	frappe.response["status"] = status
	frappe.response["message"] = message
	frappe.response["data"] = data
