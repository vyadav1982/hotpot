import json
from datetime import datetime, timedelta

import frappe
import pytz

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
		start_date = get_utc_datetime_str(start_date)
		end_date = f"{end_date} 23:59:59"
		end_date = get_utc_datetime_str(end_date)
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
		
		current_datetime = datetime.utcnow()
		current_time = get_utc_time(current_datetime)
		utc_date = get_utc_date(current_datetime)

		if (
			get_utc_date(meal_doc.meal_date) == utc_date
			and get_utc_time(meal_doc.start_time) <= current_time
		):
			set_response(400, False, "Cannot Cancel at this moment")
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
		params = {"meal_id": meal_id, "coupon_id": coupon_id}
		frappe.db.sql(query, params)
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

		current_datetime = datetime.utcnow()
		current_time = get_utc_time(current_datetime)
		utc_date = get_utc_date(current_datetime)

		# print(coupon_found, meal_id, current_time_num)

		if get_utc_date(coupon_found.get("coupon_date")) != utc_date:
			set_response(400, False, "NOTICE: Coupon Not Valid for Today")
			return

		start_time = meal_doc.get("start_time")
		if start_time:
			if current_time < get_utc_time(start_time):
				set_response(400, False, "NOTICE: Too Early to Serve")
				return

		end_time = meal_doc.get("end_time")
		if end_time:
			if current_time > get_utc_time(end_time):
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
		start_date = get_utc_datetime_str(start_date)
		end_date = f"{end_date} 23:59:59"
		end_date = get_utc_datetime_str(end_date)

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
				and hm.meal_date BETWEEN %(start_date)s AND %(end_date)s
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

		query = """
			UPDATE `tabHotpot Coupons` AS hc
			INNER JOIN `tabHotpot Meal` AS hm ON hm.name = hc.parent
			SET hc.coupon_status = "-1"
			WHERE hc.coupon_status = "1"
			AND DATE(hm.meal_date) = UTC_DATE()
			AND TIME(hm.end_time) < TIME(UTC_TIMESTAMP());
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
def get_all_coupons(
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

		if not page or not limit or not end_date or not start_date:
			set_response(400, False, "Please provide all fields")
			return

		update_coupon_status()
		local_time_now = get_local_time_now()
		start_date = f"{start_date} {local_time_now}"
		start_date = get_utc_datetime_str(start_date)
		end_date = f"{end_date} 23:59:59"
		end_date = get_utc_datetime_str(end_date)

		page = int(page)
		limit = int(limit)
		start = (page - 1) * limit


		if user_doc.get("role") == "Hotpot Server" or user_doc.get("role") == "Hotpot Vendor":
			start_date=get_utc_date(start_date)
			end_date=get_utc_date(end_date)
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
					AND DATE(hm.meal_date) BETWEEN %(start_date)s AND %(end_date)s
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
			set_response(200, True, "Coupons fetched successfully", ans)
			return

		elif user_doc.get("role") == "Hotpot User":
			start_date=get_utc_date(start_date)
			end_date=get_utc_date(end_date)
			query = """
			(
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
				`tabHotpot User` as U on hm.vendor_id = U.name
			WHERE
				DATE(hc.coupon_date) BETWEEN %(start_date)s AND %(end_date)s
				AND hc.employee_id = %(user_name)s
			)
			LIMIT %(start)s, %(limit)s;
			"""

			params = {
				"user_name": user_doc.get("name"),
				"start_date": start_date,
				"end_date": end_date,
				"start": start,
				"limit": limit,
			}

			ans = frappe.db.sql(query, params, as_dict=True)
			if not ans:
				set_response(200, True, "No Coupon found", [])
				return
			set_response(200, True, "Coupons fetched successfully", ans)
			return

		elif user_doc.get("role") == "Hotpot Admin":
			query = """
				(
				SELECT *
				FROM `tabHotpot Coupons`
				WHERE DATE(coupon_date) BETWEEN %(start_date)s AND %(end_date)s
				ORDER BY creation DESC
				LIMIT  %(start)s, %(limit)s;
				)
			"""
			params = {"start_date": start_date, "end_date": end_date, "start": start, "limit": limit}
			ans = frappe.db.sql(query, params, as_dict=True)
			if not ans:
				set_response(404, False, "No Coupon found")
				return
			set_response(200, True, "Coupons fetched successfully", ans)
			return
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Coupon Generation Error")
		set_response(500, False, f"Server error: {str(e)}")
		return


# @frappe.whitelist(allow_guest=True)
# def generate_coupon():
# 	try:
# 		if frappe.request.method != "POST":
# 			set_response(500, False, "Only POST method is allowed")
# 			return

# 		user_doc = get_hotpot_user_by_email()
# 		if not user_doc:
# 			set_response(404, False, "User Not found")
# 			return
# 		if not user_doc.get("role") == "Hotpot User":
# 			set_response(403, False, "Not Permitted to acess this resouce")
# 			return

# 		data = json.loads(frappe.request.data or "{}")
# 		required_fields = ["meal_id","date"]
# 		if missing := [field for field in required_fields if not data.get(field)]:
# 			return set_response(400, False, f"Missing required fields: {', '.join(missing)}")
		
# 		date = data.get("date")
# 		local_time_now = datetime.now().time().strftime("%H:%M:%S")
# 		start_date = f"{date} {local_time_now}"
# 		start_date = get_utc_datetime_str(start_date)
# 		# end_date = f"{date} {local_time_now}"
# 		# end_date = get_utc_datetime_str(end_date)


# 		from_date = get_utc_date(start_date)
# 		# to_date = get_utc_date(end_date)

# 		try:
# 			meal_doc = frappe.get_doc("Hotpot Meal", data["meal_id"])
# 		except frappe.DoesNotExistError:
# 			return set_response(404, False, "Meal not found")

# 		current_datetime_utc = datetime.utcnow()
# 		utc_date_today = current_datetime_utc.date()
# 		current_time = current_datetime_utc.time()
# 		print("currnte time ",current_time," utc date ",utc_date_today,"utc time formua", datetime.utcnow().time() )
# 		# day_difference = abs(datetime.strptime(to_date, "%Y-%m-%d") - datetime.strptime(from_date, "%Y-%m-%d")).days + 1
# 		meal_title = meal_doc.meal_title
# 		# print("days difference",day_difference)
# 		user_coupon_count = user_doc.coupon_count
# 		meal_weight = meal_doc.get("meal_weight")
# 		is_buffer_time = False
# 		meal_buffer_count = meal_doc.buffer_coupon_count

# 		# hours,remainder = divmod(abs(datetime.strptime(get_utc_time(meal_doc.start_time), "%H:%M:%S") - datetime.strptime(current_time, "%H:%M:%S")).seconds,3600)
# 		# if  hours <= meal_doc.lead_time(0):
# 		# 	set_response(400,False,"Cannot create coupon in meal preparation time")
# 		# 	return

# 		# Check if required amount of coupon are present or not
# 		if user_coupon_count < meal_weight :
# 			return set_response(400, False, "Insufficient currency to create coupon")

# 		if get_utc_time(meal_doc.start_time) <= current_time <= get_utc_time(meal_doc.end_time):
# 			is_buffer_time = True
# 		buffer_used = 0
# 		# utc_today = get_utc_date(get_utc_datetime_str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

	
# 		current_date = datetime.strptime(from_date, "%Y-%m-%d")
# 		# print(type(current_date))
# 		# print("current date", current_date)
# 		# print("database date ",get_utc_date(get_utc_datetime_str(current_date.strftime("%Y-%m-%d %H:%M:%S"))))
# 		display_date = current_date.strftime("%d %b %Y")

# 		# Cannot create coupon for past
# 		if current_date.strftime("%Y-%m-%d") < get_utc_date(meal_doc.get("meal_date")):
# 			set_response(500, False, f"Cannot create coupon for past date: {display_date}")
# 			return

# 		# If buffer time then check for vendor coupons
# 		is_today = current_date == utc_date_today
# 		if is_today and is_buffer_time:
# 			if meal_buffer_count == 0:
# 				set_response(500, False, f"Not Enough Vendor Coupon for {display_date}")
# 				return
# 			buffer_used += 1

# 		# Check for duplicate coupon
# 		exists = frappe.db.exists(
# 			"Hotpot Coupons",
# 			{
# 				"employee_id": user_doc.get("name"),
# 				"parent": data["meal_id"],
# 			},
# 		)

# 		if exists:
# 			set_response(409, False, f"Already present {meal_title} on {display_date}")
# 			return

# 		try:
# 			# History used for user transactions
# 			history_doc = frappe.new_doc("Hotpot Coupons History")
# 			history_doc.update(
# 				{
# 					"employee_id": user_doc.get("name"),
# 					"type": "Creation",
# 					"message": f"Created coupon for {meal_title} ({display_date})",
# 					"meal_id": data["meal_id"],
# 				}
# 			)
# 			history_doc.insert()

# 			# Append created coupon in meal

# 			meal_doc.append(
# 				"coupons",
# 				{
# 					"employee_id": user_doc.get("name"),
# 					"coupon_date": start_date,
# 					"title": meal_title,
# 					"coupon_status": "1",
# 				},
# 			)

# 			user_coupon_count -= meal_weight
# 			# output.append(f"Created coupon for {meal_title} on {display_date}")

# 		except Exception as e:
# 			frappe.db.rollback()
# 			# output.append(f"Failed to create coupon for {display_date}: {str(e)}")
# 			set_response(500, False, f"Failed to create coupon for {display_date}: {str(e)}")
# 			return

# 		# Decide whether we need to chnange coupon count or not
# 		if is_buffer_time and buffer_used > 0:
# 			meal_doc.buffer_coupon_count = meal_buffer_count - buffer_used
# 			if meal_doc.buffer_coupon_count < 0:
# 				meal_doc.buffer_coupon_count = 0

# 		meal_doc.save()
# 		frappe.db.set_value(
# 			"Hotpot User",
# 			user_doc.get("name"),
# 			{
# 				"coupon_count": user_coupon_count,
# 			},
# 		)
# 		frappe.db.commit()

# 		return set_response(200, True, "Processing completed", {"remaining_coupons": user_coupon_count})

# 	except Exception as e:
# 		frappe.db.rollback()
# 		print(frappe.get_traceback())
# 		frappe.log_error(frappe.get_traceback(), "Coupon Generation Error")
# 		set_response(500, False, f"Server error: {str(e)}")
# 		return

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

		data = json.loads(frappe.request.data or "{}")
		required_fields = ["meal_id", "date"]
		missing = [field for field in required_fields if not data.get(field)]
		if missing:
			return set_response(400, False, f"Missing required fields: {', '.join(missing)}")

		date = data.get("date")
		local_time_now = get_local_time_now()
		start_date = f"{date} {local_time_now}"
		start_date = get_utc_datetime_str(start_date)
		from_date = start_date.date()

		try:
			meal_doc = frappe.get_doc("Hotpot Meal", data["meal_id"])
		except frappe.DoesNotExistError:
			return set_response(404, False, "Meal not found")

		current_datetime_utc = datetime.utcnow()
		utc_date_today = get_utc_date(current_datetime_utc)
		current_time = get_utc_time(current_datetime_utc)

		first =((datetime.strptime(get_utc_time(meal_doc.start_time), "%H:%M:%S") - datetime.strptime(current_time, "%H:%M:%S")).seconds)>0
		second = ((datetime.strptime(get_utc_time(meal_doc.start_time), "%H:%M:%S") - datetime.strptime(current_time, "%H:%M:%S")).seconds)<= (meal_doc.lead_time)*60*60

		meal_title = meal_doc.meal_title
		user_coupon_count = user_doc.coupon_count
		meal_weight = meal_doc.get("meal_weight")
		meal_buffer_count = meal_doc.buffer_coupon_count

		if from_date < meal_doc.meal_date.date():
			set_response(400, False, f"Cannot create coupon for past date: {from_date.strftime('%d %b %Y')}")
			return

		if (first and second):
			set_response(400,False,"Cannot create coupon in meal preparation time")
			return
		
		# Check if required amount of coupons are available
		if user_coupon_count < meal_weight:
			return set_response(400, False, "Insufficient currency to create coupon")
		is_buffer_time = get_utc_time(meal_doc.start_time) <= current_time <= get_utc_time(meal_doc.end_time)
		buffer_used = 0

		# If buffer time then check for vendor coupons
		if from_date.strftime("%Y-%m-%d") == utc_date_today and is_buffer_time:
			if meal_buffer_count == 0:
				set_response(400, False, f"Not Enough Vendor Coupons for {from_date.strftime('%d %b %Y')}")
				return
			buffer_used += 1

		if get_utc_time(start_date) >= datetime.utcnow().strftime("%H:%M:%S"):
			set_response(400, False, "Meal time already passed.")
			return

		# Check for duplicate coupon
		exists = frappe.db.exists(
			"Hotpot Coupons",
			{
				"employee_id": user_doc.get("name"),
				"parent": data["meal_id"],
				"coupon_status": ["!=", "2"],
			},
		)

		if exists:
			set_response(409, False, f"Already present {meal_title} on {from_date.strftime('%d %b %Y')}")
			return
		print(f"Created coupon for {meal_title} {start_date}")
		try:
			# History for user transactions
			history_doc = frappe.new_doc("Hotpot Coupons History")
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
				},
			)

			user_coupon_count -= meal_weight

		except Exception as e:
			frappe.db.rollback()
			frappe.log_error(frappe.get_traceback(), "Coupon Generation Error")
			set_response(500, False, f"Failed to create coupon: {str(e)}")
			return

		# Update meal buffer count if buffer time
		if is_buffer_time and buffer_used > 0:
			meal_doc.buffer_coupon_count = max(0, meal_buffer_count - buffer_used)

		meal_doc.save()
		frappe.db.set_value(
			"Hotpot User",
			user_doc.get("name"),
			{
				"coupon_count": user_coupon_count,
			},
		)
		frappe.db.commit()

		return set_response(200, True, "Processing completed", {"remaining_coupons": user_coupon_count})

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
