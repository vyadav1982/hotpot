from datetime import datetime,timedelta

import frappe
import json

from hotpot.utils.utc_time import *
from hotpot.utils.email import *

import re

from frappe.utils import now_datetime

@frappe.whitelist(methods=["GET"])
def get_current_user():
	return frappe.get_cached_doc("User", frappe.session.user)


@frappe.whitelist(methods=["GET"])
def get_list():
	return frappe.db.get_list(
		"Hotpot User",
		fields=["name", "employee_id", "employee_name"],
		filters=[
			["is_active", "=", 1],
			["is_guest", "=", 0],
		],
	)


@frappe.whitelist()
def update_coupon_count(params):
	params = frappe.parse_json(params)
	employee_id = params.get("userId")
	coupon_count = params.get("token")
	coupon = params.get("coupon")
	doc = frappe.get_doc("Hotpot User", employee_id)
	doc.coupon_count = int(coupon_count)
	doc.save()
	frappe.db.commit()
	doc = frappe.new_doc("Hotpot Coupons History")
	doc.employee_id = employee_id
	doc.type = "Cancellation"
	doc.message = f"You Cancelled a coupon for {coupon['title']} ({coupon['coupon_date']})"
	doc.insert()
	return {"message": "Coupon count updated successfully"}


def set_response(http_status_code, status, message, data=None):
	frappe.local.response["http_status_code"] = http_status_code
	frappe.response["status"] = status
	frappe.response["message"] = message
	frappe.response["data"] = data


@frappe.whitelist()
def get_coupons_history(page=1,limit=10):
	try:
		if frappe.request.method != "GET":
			set_response(405, False, "Only GET method is allowed")
			return

		user_doc = get_hotpot_user_by_email()

		if not user_doc:
			set_response(401, False, "User Not found")
			return

		if not user_doc.get("role") in ["Hotpot User","Hotpot Admin","Hotpot HR"]:
			set_response(403, False, "Not Permitted to access this resource")
			return
		employee_id = user_doc.get("employee_id")
		
		# end_date = get_utc_datetime_str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		# start_date = end_date - timedelta(days=30) 
		# page = int(page)
		# limit = int(limit)
		# start = (page - 1) * limit
		# result = []
		# employee_id = user_doc.get("name")
		# print("start date ",start_date,"end date ",end_date)
		# query = """ SELECT modified_by, data, docname, creation FROM tabVersion WHERE docname = %s AND ref_doctype LIKE '%%Hotpot%%' ORDER BY creation DESC LIMIT 10; """
		# result = frappe.db.sql(query, employee_id, as_dict=True)
		# result += frappe.db.get_list(
		# 	"Hotpot Coupons History",
		# 	fields=["employee_id", "type", "message", "creation"],
		# 	filters=[["employee_id", "=", employee_id],["modified",">=",start_date],["modified","<=",end_date]],
		# 	order_by="modified desc",
		# 	start=start,
		# )
		end_date = datetime.utcnow()+timedelta(days=2)
		start_date = end_date - timedelta(days=30)

		page = int(page)
		limit = int(limit)
		start = (page - 1) * limit

		employee_id = user_doc.get("name")

		query = """
			SELECT modified_by, data, docname, creation 
			FROM tabVersion 
			WHERE docname = %s 
			AND ref_doctype LIKE '%%Hotpot%%' 
			ORDER BY creation DESC ;
		"""

		result = frappe.db.sql(query, (employee_id), as_dict=True)
		user_timezone = get_user_timezone()
		query = """
			SELECT employee_id, type, message, creation 
			FROM `tabHotpot Coupons History`
			WHERE employee_id = %s
			AND modified BETWEEN %s AND %s
			ORDER BY modified DESC;
		"""
		params = (employee_id,start_date, end_date)
		result += frappe.db.sql(query,params,as_dict=True)
		# result += frappe.db.get_list(
		# 	"Hotpot Coupons History",
		# 	fields=["employee_id", "type", "message", "creation"],
		# 	filters=[
		# 		["employee_id", "=", employee_id],
		# 		["modified", ">=", start_date],
		# 		["modified", "<=", end_date]
		# 	],
		# 	order_by="modified desc",
		# 	start=start,
		# 	limit=limit
		# )
		set_response(200, True, "History fetched successfully", result)
	except Exception as e:
		frappe.db.rollback()
		print(frappe.get_traceback())
		frappe.log_error(frappe.get_traceback(), "History Error")
		return set_response(500, False, f"Server error: {str(e)}")


def reset_coupon_count():
	users = frappe.db.get_list(
		"Hotpot User",
		filters=[["is_active", "=", 1], ["is_guest", "=", 0]],
		pluck="name",
	)

	for name in users:
		doc = frappe.get_doc("Hotpot User", name)
		doc.coupon_count = 60
		doc.save()
	frappe.db.commit()


@frappe.whitelist(methods=["POST"])
def get_hotpot_user_by_employee_id(employee_id):
	return frappe.get_doc("Hotpot User", employee_id)


@frappe.whitelist(allow_guest=True)
def get_hotpot_user_by_tag_id(tag_id):
	try:
		if not tag_id:
			set_response(400, False, "Tag ID is required")
			return

		user = frappe.db.get_list(
			"Hotpot User",
			filters=[["tag_id", "=", tag_id], ["is_active", "=", 1]],
			fields=[
				"name",
				"employee_name",
				"employee_id",
				"email",
				"mobile_no",
				"is_active",
				"role",
				"is_guest",
				"guest_of",
				"coupon_count",
				"approval_id",
				"date_of_birth",
				"date_of_joining",
				"department",
				"location",
				"latitude",
				"longitude"
			],
		)
		if user:
			return user[0]
		return None
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Get Hotpot User by Tag Id Error")
		return None

@frappe.whitelist()
def get_hotpot_user_by_email():
	try:
		email = frappe.session.user
		if not email:
			set_response(401, False, "No auth token found")
			return

		if not frappe.has_permission("Hotpot User", "read"):
			set_response(401, False, "No auth token found")
			return
		user = frappe.db.get_list(
			"Hotpot User",
			filters=[["email", "=", email],["is_active", "=", 1]],
			fields=[
				"name",
				"employee_name",
				"employee_id",
				"email",
				"mobile_no",
				"is_active",
				"role",
				"is_guest",
				"guest_of",
				"coupon_count",
				"approval_id",
				"date_of_birth",
				"date_of_joining",
				"department",
				"location",
				"latitude",
				"longitude"
			],
		)
		if user:
			return user[0]

		return None

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Get Hotpot User by Email Error")
		return None


@frappe.whitelist()
def get_hotpot_loggedin_user():
	try:
		user = get_hotpot_user_by_email()
		if user:
			set_response(200, True, "Data fetched successfully", user)
			return

		set_response(401, False, "No user found with the given email")
		return
	except frappe.PermissionError:
		set_response(403, False, "You do not have permission to access this resource")
		return

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Hotpot User by Email Error")
		set_response(500, False, f"An error occurred: {str(e)}")
		return


@frappe.whitelist()
def get_all_vendor():
	try:
		if frappe.request.method != "GET":
			set_response(500, False, "Only GET method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(401, False, "User Not found")
			return
		if not user_doc.get("role") in ["Hotpot User","Hotpot Admin","Hotpot HR"]:
			set_response(403, False, "Not Permitted to access this resource")
			return
		user_list = frappe.db.get_list(
			"Hotpot User",
			filters=[["role", "=", "Hotpot Vendor"],["is_active","=",1],["is_deleted","=",0]],
			fields=["name", "employee_name"],
		)
		if not user_list:
			set_response(200, False, "No Vendor found")
			return
		set_response(200, True, "Vendors fetched successfully", user_list)
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Vendor Error")
		return set_response(500, False, f"Server error: {str(e)}")
	

@frappe.whitelist()
def update_user_timezone():
	try:
		if frappe.request.method != "PUT":
			set_response(405, False, "Only PUT method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(401, False, "User Not found")
			return

		if not user_doc.get("role") in ["Hotpot User","Hotpot Admin","Hotpot HR"]:
			set_response(403, False, "Not Permitted to access this resource")
			return
		data = json.loads(frappe.request.data or "{}")
		timezone = data.get("timezone")
		if not timezone:
			set_response(400, False, "Timezone is required")
			return
		doc = frappe.get_doc("Hotpot User", user_doc.name)
		doc.time_zone = timezone
		doc.save(ignore_permissions=True)
		
		set_response(200, True, "Timezone updated successfully")
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Timezone Error")
		return set_response(500, False, f"Server error: {str(e)}")
	
@frappe.whitelist()
def update_latlong():
	try:
		if frappe.request.method != "PUT":
			set_response(405, False, "Only PUT method is allowed")
			return

		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(401, False, "User Not found")
			return

		data = json.loads(frappe.request.data or "{}")
		latitude = data.get("latitude")
		longitude = data.get("longitude")
		if not latitude or not longitude:
			set_response(400, False, "Latitude and Longitude are required")
			return
		doc = frappe.get_doc("Hotpot User", user_doc.name)
		doc.latitude = latitude
		doc.longitude = longitude
		doc.save(ignore_permissions=True)
		set_response(200, True, "Latitude and Longitude updated successfully")
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Latitude and Longitude Error")
		return set_response(500, False, f"Server error: {str(e)}")
	
@frappe.whitelist()
def get_config():
	try:
		if frappe.request.method!= "GET":
			set_response(405, False, "Only GET method is allowed")
			return
		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(401, False, "User Not found")
			return
		config_doc = frappe.get_doc("Hotpot Configurations")
		meta = frappe.get_meta("Hotpot Configurations")
		system_fields = {"name", "owner", "modified", "modified_by", "docstatus","idx","doctype"}

		user_created_fields = {
			field.fieldname: getattr(config_doc, field.fieldname)
			for field in meta.fields
			if field.fieldname not in system_fields
		}
		if not config_doc:
			set_response(404, False, "Configuration not found")
			return
		set_response(200, True, "Data fetched successfully", user_created_fields)
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Configuration Error")
		return set_response(500, False, f"Server error: {str(e)}")
	
@frappe.whitelist()
def email_wrapper():
	try:
		if frappe.request.method!= "POST":
			set_response(405, False, "Only POST method is allowed")
			return
		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(401, False, "User Not found")
			return
		data = json.loads(frappe.request.data or "{}")
		template_name = data.get("template_name")
		to_email = data.get("to_email")
		context = data.get("context")
		subject = data.get("subject")
		qr_code_base64 = data.get("qr_code_base64", None)

		if not all([template_name, to_email, context, subject]):
			return set_response(404, False, "Missing mandatory fields")
		
		try:
			send_email(template_name, to_email, context, subject,qr_code_base64)
			return set_response(200, True, "Email sent successfully")
		
		except Exception as e:
			frappe.log_error(frappe.get_traceback(), f"Email Error: {str(e)}")
			return set_response(500, False, f"Failed to send email: {str(e)}")
		
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Configuration Error")
		return set_response(500, False, f"Server error: {str(e)}")
	
@frappe.whitelist()
def get_dashboard_data():
	try:
		if frappe.request.method!= "GET":
			set_response(405, False, "Only GET method is allowed")
			return
		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(401, False, "User Not found")
			return
		if not user_doc.get("role") in ["Hotpot Finance","Hotpot Admin","Hotpot HR"]:
			set_response(403, False, "Not Permitted to access this resource")
			return
		user_timezone = get_user_timezone() or "Asia/Kolkata"
		user_timezone = str(user_timezone)
		today_str = now_datetime().replace(tzinfo=pytz.utc).astimezone(pytz.timezone(user_timezone)).strftime("%Y-%m-%d")
		start_date = f"{today_str} 00:00:00"
		end_date = f"{today_str} 23:59:59"
		start_date = get_utc_datetime_obj(start_date)
		end_date = get_utc_datetime_obj(end_date)

		start_date = get_local_datetime_obj(start_date).date()
		end_date = get_local_datetime_obj(end_date).date()
		meals = get_meals_dashboard(today_str)
		user_data = frappe.db.sql("""
			SELECT COUNT(*) AS total_user_count
			FROM `tabHotpot User`
			WHERE is_deleted = 0 AND role ="Hotpot User"
		""", as_dict=True)
		vendor_data = frappe.db.sql("""
			SELECT COUNT(*) AS total_vendor_count
			FROM `tabHotpot User`
			WHERE is_deleted = 0 AND role ="Hotpot Vendor"
		""", as_dict=True)

		# meal_data = frappe.db.sql("""
		# 	SELECT vendor_id, COUNT(*) AS meal_count
		# 	FROM `tabHotpot Meal`
		# 	WHERE is_active = 1
		# 	GROUP BY vendor_id
		# """, as_dict=True)

		total_service_requests = frappe.db.sql("""
			SELECT  COUNT(*) AS total_service_requests
			FROM `tabHotpot Approvals`
		""", as_dict=True)

		guest_coupon_data = frappe.db.sql("""
			SELECT COUNT(*) AS guest_coupon_count
			FROM `tabHotpot Coupons` as hc
			WHERE hc.guest_of IS NOT NULL AND DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %s)) BETWEEN %s AND %s
		""",(user_timezone,start_date,end_date), as_dict=True)
		
		meal_data = []

		for meal in meals:
			meal_count = frappe.db.count(
				"Hotpot Coupons",
				filters={
					"parent": meal["name"],
					"coupon_status": ["!=", 2]
				}
			)
			
			meal_data.append({
				"vendor_name": meal.get("vendor_name"),
				"meal_title": meal.get("meal_title"),
				"start_time": meal.get("start_time"),
				"end_time": meal.get("end_time"),
				"meal_count": meal_count
			})



		set_response(200, True, "Data fetched successfully", {
			**user_data[0],
			**vendor_data[0],
			**total_service_requests[0],
			**guest_coupon_data[0],
			"meal_data": meal_data,
		})


	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Dashboard Error")
		return set_response(500, False, f"Server error: {str(e)}")
	

@frappe.whitelist()
def get_meals_dashboard(date):
	try:
		
		local_time = get_local_time_now()
		date_param_utc = get_utc_datetime_obj(f"{date} {local_time}").date()
		utc_now = datetime.utcnow().replace(tzinfo=None)
		update_coupon_status()
		start_date = get_utc_datetime_obj(f"{date} 00:00:00")
		end_date = get_utc_datetime_obj(f"{date} 23:59:59")

		base_fields = [
			"name", "meal_title", "day", "meal_items", "start_time", "end_time",
			"buffer_coupon_count", "meal_weight", "meal_date", "is_special","is_active",
			"vendor_id", "repeat_type", "repeat_days","lead_time","cancellation_time"
		]

		filters = [
			["is_active", "=", 1],
			["is_deleted","=",0]
		]
		

		meals = frappe.db.get_list(
			"Hotpot Meal",
			fields=base_fields,
			filters=filters,
			# start=start,
			# limit=limit,
		)
		meals = [
			meal for meal in meals if meal["meal_date"] <= end_date
		]
		processed_meals = []
		for meal in meals:
			meal_date = meal["meal_date"]
			repeat_type = meal.get("repeat_type", "once")
			repeat_days = [d.strip() for d in meal.get("repeat_days", "").split(",") if d]
			valid = False
			if repeat_type == "once":
				valid = (meal_date >= start_date and meal_date <= end_date)
			elif repeat_type == "daily":
				valid = meal_date <= end_date
			elif repeat_type == "specific_days":
				weekday = date_param_utc.strftime("%A").upper()
				valid = meal_date <= end_date and weekday in repeat_days

			if not valid:
				continue

			if start_date<=utc_now and utc_now<=end_date:
				if get_local_datetime_obj(meal["end_time"]).time()<=get_local_datetime_obj(datetime.utcnow().replace(tzinfo=None)).time():
					continue

			vendor = frappe.db.get_value("Hotpot User", meal["vendor_id"], "employee_name")
			meal["vendor_name"] = vendor
			meal_doc = frappe.get_doc("Hotpot Meal", meal["name"])
			
			meal["coupon"] = [
				{"id": c.name, "status": c.coupon_status, "date": c.coupon_date}
				for c in meal_doc.coupons if c.coupon_date.date() == date_param_utc
			]

			meal_doc = frappe.get_doc("Hotpot Meal", meal["name"])
			meal["meal_id"] = meal_doc.name
			
			processed_meals.append(meal)

		return processed_meals

	except Exception as e:
		f"Failed to get meal: {str(e)}"
		raise 

def update_coupon_status():
	try:
		user_doc = get_hotpot_user_by_email()
		if not user_doc:
			set_response(401, False, "User Not found")
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
def bulk_insert_employee():
	import json
	if frappe.request.method!= "POST":
			set_response(405, False, "Only POST method is allowed")
			return
	user_doc = get_hotpot_user_by_email()
	if not user_doc:
		set_response(401, False, "User Not found")
		return
	if not user_doc.get("role") in ["Hotpot Admin"]:
		set_response(403, False, "Not Permitted to access this resource")
		return
	bliss_doc = frappe.get_doc("Hotpot Locations",{"location":"Bliss HQ"})
	try:
		data = json.loads(frappe.request.data or "{}")
		fields = data.get("fields", [])
		values = data.get("values", [])

		status_report = []

		for row in values:
			record = dict(zip(fields, row))
			email = record.get("email", "").strip()
			empid = record.get("employee_id","").strip()
			name = record.get("employee_name", "").strip()
			mobile = record.get("mobile_no", "").strip()
			coupon_count = record.get("coupon_count", 0)
			dob = record.get("date_of_birth")
			doj = record.get("date_of_joining")

			if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
				status_report.append({ "email": email, "status": "failed", "reason": "Invalid email format" })
				continue

			if not re.match(r"^\+91- \d{10}$", mobile):
				status_report.append({ "email": email, "status": "failed", "reason": "Mobile number must be +91- XXXXXXXXXX" })
				continue

			if not name.replace(" ", "").isalpha():
				status_report.append({ "email": email, "status": "failed", "reason": "Name must contain only letters and spaces" })
				continue

			try:
				coupon_count = int(coupon_count)
				if coupon_count < 0:
					raise ValueError()
			except:
				status_report.append({ "email": email, "status": "failed", "reason": "Coupon count must be a number >= 0" })
				continue

			date_pattern = r"^\d{4}-\d{2}-\d{2}$"

			if dob and not re.match(date_pattern, dob):
				status_report.append({ "email": email, "status": "failed", "reason": "Invalid DOB format (expected YYYY-MM-DD)" })
				continue

			if doj and not re.match(date_pattern, doj):
				status_report.append({ "email": email, "status": "failed", "reason": "Invalid DOJ format (expected YYYY-MM-DD)" })
				continue

			if frappe.db.exists("Hotpot User", {"email": email}):
				status_report.append({ "email": email, "status": "failed", "reason": "Email already exists" })
				continue
			if frappe.db.exists("Hotpot User", {"employee_id": empid}):
				status_report.append({ "email": email, "status": "failed", "reason": "Email already exists" })
				continue

			try:
				doc = frappe.get_doc({
					"doctype": "Hotpot User",
					**record,
					"is_active":1,
					"latitude":bliss_doc.latitude,
					"longitude":bliss_doc.longitude,
					"role":"Hotpot User",
				})
				doc.insert(ignore_permissions=True)
				status_report.append({ "email": email, "status": "success", "reason": "Inserted successfully" })
			except Exception as e:
				status_report.append({ "email": email, "status": "failed", "reason": f"Insertion error: {str(e)}" })

		return set_response(200,True,{ "status_report": status_report })

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "bulk_insert_employee")
		return set_response(500,False,{ "error": "Something went wrong", "details": str(e) })
		

@frappe.whitelist()
def get_hotpot_history(start_date,end_date):
	if frappe.request.method!= "GET":
			set_response(405, False, "Only GET method is allowed")
			return
	user_doc = get_hotpot_user_by_email()
	if not user_doc:
		set_response(401, False, "User Not found")
		return
	if not user_doc.get("role") in ["Hotpot User","Hotpot Admin","Hotpot HR"]:
		set_response(403, False, "Not Permitted to access this resource")
		return
	
	start_date = f"{start_date} 00:00:00"
	start_date = get_utc_datetime_obj(start_date)
	end_date = f"{end_date} 23:59:59"
	end_date = get_utc_datetime_obj(end_date)
	start_date = get_local_datetime_obj(start_date).date()
	end_date = get_local_datetime_obj(end_date).date()

	user_timezone = get_user_timezone() or "Asia/Kolkata"
	try:
		query="""
			SELECT 
				CONVERT_TZ(hc.coupon_date, 'UTC', %(timezone)s) AS date,
				hm.meal_title,
				hm.meal_weight,
				hm.start_time,
				hm.end_time
			FROM 
				`tabHotpot Coupons` AS hc
			JOIN 
				`tabHotpot Meal` AS hm
				ON hc.parent = hm.name
			WHERE
				hc.employee_id = %(user_name)s 
				AND DATE(CONVERT_TZ(hc.coupon_date, 'UTC', %(timezone)s)) BETWEEN %(start_date)s AND %(end_date)s
			ORDER BY 
				hc.modified DESC
		"""

		data = frappe.db.sql(query,{
					"user_name": user_doc.get("name"),
					"timezone": user_timezone,
					"timezone": user_timezone,
					"start_date": start_date,
					"end_date": end_date
				},as_dict=True)
		set_response(200,True,"Coupon data fetched successfully",data)
		return
	except Exception as e:
		set_response(500, False, "ERROR: " + str(e))


	