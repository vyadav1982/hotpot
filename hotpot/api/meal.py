import json
import re
import traceback
from datetime import datetime, timedelta

import frappe
import pytz

from hotpot.utils.meal_utils import get_discount
from hotpot.utils.role_utils import has_any_of_role, has_role
from hotpot.utils.send_fcm import *
from hotpot.utils.utc_time import *

from ..api.users import *
from ..api.coupons import update_coupon_status


def set_response(http_status_code, status, message, data=None,hdata=None):
	frappe.local.response["http_status_code"] = http_status_code
	frappe.response["status"] = status
	frappe.response["message"] = message
	frappe.response["data"] = data
	frappe.response["holiday_data"] = hdata


@frappe.whitelist(methods=["POST"])
def give_feedback():
	try:
		"""
			Gets the Project Branch document with the organization and app name
		"""
		if frappe.request.method != "POST":
			set_response(405, False, "Only POST method is allowed")
			return

		user_data = get_hotpot_user_by_email()
		if not user_data:
			set_response(401, False, "User Not found")
			return
		if not has_any_of_role(["Hotpot User", "Hotpot Admin", "Hotpot HR"]):
			set_response(403, False, "Not Permitted to acess this resource")
			return
		data = json.loads(frappe.request.data or "{}")
		meal_doc = frappe.get_doc("Hotpot Meal", data["meal"])
		if not meal_doc:
			set_response(404, False, "Meal not found")
			return

		ratings = data.get("ratings", [])
		employee_id = user_data.get("name")
		meal = data.get("meal")
		coupon = data.get("coupon")
		coupon_doc = frappe.get_doc("Hotpot Coupons", coupon)
		if not coupon_doc:
			set_response(404, False, "Coupon not found")
			return
		if coupon_doc.coupon_status != "0":
			set_response(400, False, "You can only rate after using the coupon.")
			return
		already_rated_items = []
		for rating_entry in ratings:
			item_id = rating_entry.get("id")
			existing_ratings = frappe.get_all(
				"Hotpot Meal Menu Items Rating",
				filters={"meal_item": item_id, "employee": employee_id, "meal": meal, "coupon": coupon},
				pluck="meal_item",
			)
			if existing_ratings:
				already_rated_items.append(item_id)

		if already_rated_items:
			set_response(
				400, False, f"You've already rated item(s): {', '.join(already_rated_items)} in this meal."
			)
			return
		for rating_entry in ratings:
			rating_doc = frappe.get_doc(
				{
					"doctype": "Hotpot Meal Menu Items Rating",
					"employee": employee_id,
					"meal": meal,
					"meal_item": rating_entry.get("id"),
					"rating": int(rating_entry.get("rating")) / 5,
					"review": rating_entry.get("review"),
					"coupon": coupon,
				}
			)
			rating_doc.insert(ignore_permissions=True)
		# meal_doc.save()
		frappe.db.commit()
		set_response(200, True, "Ratings submitted successfully!")
		return

	except Exception as e:
		frappe.db.rollback()
		print(frappe.get_traceback())
		frappe.log_error(frappe.get_traceback(), "Cannot update feedback at this momemt.")
		return set_response(500, False, f"Server error: {str(e)}")


@frappe.whitelist()
def create_meal():
	try:
		if frappe.request.method != "POST":
			set_response(405, False, "Only POST method is allowed")
			return

		user_data = get_hotpot_user_by_email()
		if not user_data:
			set_response(401, False, "User Not found")
			return

		data = json.loads(frappe.request.data or "{}")

		meal_date = data.get("meal_date")
		start_time = data.get("start_time")
		end_time = data.get("end_time")
		category = data.get("category")

		vendor_id = None
		if has_role("Hotpot Vendor"):
			vendor_id = user_data.get("email")
		else:
			vendor_id = data.get("vendor_id")

		# for checking if there is any existing meal in the category
		output = check_valid_meal(meal_date, vendor_id, category)
		if output.get("status") == "error":
			return set_response(500, False, output.get("message"))

		start_time = f"{meal_date} {start_time}"
		end_time = f"{meal_date} {end_time}"
		local_time_now = get_local_time_now()

		if isinstance(meal_date, str):
			meal_date = f"{meal_date} {local_time_now}"
		meal_title = data.get("meal_title")
		day = get_utc_datetime_obj(meal_date).day

		meal_items = ",".join(data.get("meal_items", []))
		start_time = get_utc_datetime_obj(start_time)
		end_time = get_utc_datetime_obj(end_time)
		meal_date = get_utc_datetime_obj(meal_date)
		buffer_coupon_count = data.get("buffer_coupon_count")
		meal_weight = data.get("meal_weight")
		is_special = data.get("is_special")
		lead_time = data.get("lead_time")
		cancellation_time = data.get("cancellation_time")
		repeat_type = data.get("repeat_type", "once")
		repeat_days = ",".join(data.get("repeat_days", []))
		category = data.get("category", None)
		meal_item_ids = data.get("meal_item_ids", None)
		max_meal_count = data.get("max_meal_count", -1)

		required_fields = [
			"meal_title",
			"day",
			"meal_date",
			"start_time",
			"end_time",
			"meal_items",
			"meal_weight",
		]
		if missing := [field for field in required_fields if not data.get(field)]:
			set_response(400, False, f"Missing required fields: {', '.join(missing)}")
			return

		meal_doc = frappe.get_doc(
			{
				"doctype": "Hotpot Meal",
				"meal_title": meal_title,
				"day": day,
				"meal_date": meal_date,
				"vendor_id": vendor_id,
				"meal_items": meal_items,
				"start_time": start_time,
				"end_time": end_time,
				"buffer_coupon_count": buffer_coupon_count,
				"remaining_coupon_count": buffer_coupon_count,
				"meal_weight": meal_weight,
				"is_active": "1",
				"is_special": is_special,
				"lead_time": lead_time,
				"cancellation_time": cancellation_time,
				"repeat_type": repeat_type,
				"repeat_days": repeat_days,
				"category": category,
				"max_meal_count": max_meal_count,
			}
		)
		if meal_item_ids:
			for item_id in meal_item_ids:
				meal_doc.append(
					"menu_items",
					{
						"meal_item": item_id,
					},
				)
		try:
			meal_doc.insert()
			frappe.db.commit()

			set_response(
				201,
				True,
				"Meal created successfully",
				{"meal_id": meal_doc.name},
			)
			return
		except Exception as e:
			set_response(
				406,
				False,
				str(e)
			)
			return

	except Exception as e:
		frappe.db.rollback()
		error_message = f"Failed to create meal: {str(e)}"
		trace = traceback.format_exc()
		frappe.log_error(f"{error_message}\n{trace}", "Meal Creation Error")
		set_response(500, False, error_message)
		return


@frappe.whitelist()
def update_meal():
	try:
		if frappe.request.method != "PUT":
			set_response(405, False, "Only PUT method is allowed")
			return

		user_data = get_hotpot_user_by_email()
		if not user_data:
			set_response(401, False, "User Not found")
			return

		data = json.loads(frappe.request.data or "{}")
		meal_id = data.get("meal_id")

		if not meal_id:
			set_response(400, False, "Meal Id is required")
			return

		meal_doc = frappe.get_doc("Hotpot Meal", meal_id)
		if int(meal_doc.buffer_coupon_count or 0) != int(data.get("buffer_coupon_count") or 0):
			old_value = meal_doc.buffer_coupon_count
			meal_doc.buffer_coupon_count = data.get("buffer_coupon_count")
			coupons = meal_doc.coupons
			unique_emp_ids = {c.employee_id for c in coupons}

			for emp_id in unique_emp_ids:
				user_doc = frappe.get_doc("Hotpot User", emp_id)
				if user_doc.fcm_token:
					try:
						change_msgs = []
						change_msgs.append(f"🎟️ Buffer Coupons: {old_value} ➡️ {data.get("buffer_coupon_count")}")
						change_text = "\n".join(change_msgs) if change_msgs else "✨ Something got updated!"

						send_notification_by_token(
							user_doc.fcm_token,
							"🍴 Meal Plot Twist! 🔄",
							f"Guess what? '{meal_doc.meal_title}' just got an update! 🎉\n\n"
							f"Here’s what changed:\n{change_text}\n\n"
							"👉 Check it out now!",
							date=meal_doc.meal_date,
							doc_id=meal_doc.name,
							text="meals",
						)
					except Exception:
						frappe.log_error(
							frappe.get_traceback(),
							f"Failed to send plot twist notification to user {user_doc.name}",
						)
			meal_doc.save()
			frappe.db.commit()
			if data.get("only_buffer"):
				set_response(200,True, "Buffer coupon count updated successfully")
				return

		if not meal_doc:
			set_response(404, False, "Meal not found")
			return
		
		meal_doc.reload()

		upcoming_coupons = False
		coupons = meal_doc.coupons
		for coupon in coupons:
			if coupon.coupon_status == "1":
				upcoming_coupons = True
				break
		approval_id = meal_doc.approval_id
		status = False
		active_status = True
		if approval_id:
			approval_doc = frappe.get_doc("Hotpot Approvals", approval_id)
			if approval_doc.approval_status != "Pending":
				status = True
			if approval_doc.approval_status == "Approved" and approval_doc.is_active == 0:
				active_status = False
			if not status:
				set_response(400, False, "Your, Request is still pending.")
				return
			if not active_status:
				set_response(409, False, "You don't have any active requests.")
				return
		elif upcoming_coupons:
			set_response(409, False, "Approval is required to update the meal.")
			return
		if upcoming_coupons and not active_status:
			set_response(
				409,
				False,
				"Coupons are already generated for this meal. Need Admin Approval for this operation.",
			)
			return

		local_time = get_local_time_now()

		if data.get("start_time"):
			data["start_time"] = get_utc_datetime_obj(f"{data['meal_date']} {data['start_time']}")
		if data.get("end_time"):
			data["end_time"] = get_utc_datetime_obj(f"{data['meal_date']} {data['end_time']}")
		if data.get("meal_date"):
			data["meal_date"] = get_utc_datetime_obj(f"{data['meal_date']} {local_time}")

		for field in [
			"meal_title",
			"meal_date",
			"meal_items",
			"meal_item_ids",
			"buffer_coupon_count",
			"is_active",
			"is_special",
		]:
			if field in data:
				if field in ["meal_items", "repeat_days"] and isinstance(data[field], list):
					setattr(meal_doc, field, str(",".join(data[field])))

				elif field == "meal_item_ids":
					meal_doc.menu_items = []

					raw_items = data[field]
					if isinstance(raw_items, str):
						raw_items = raw_items.split(",")
					elif not isinstance(raw_items, list):
						raw_items = ",".join([str(item).strip() for item in raw_items if isinstance(item, str) and item.strip()])

					item_list = list(
						{item.strip().lower() for item in raw_items if isinstance(item, str) and item.strip()}
					)

					for item_name in item_list:
						menu_item = frappe.get_value(
							"Hotpot Meal Items", {"vendor_id": meal_doc.vendor_id, "name": item_name}, "name"
						)
						if menu_item:
							meal_doc.append("menu_items", {"meal_item": menu_item})
						else:
							frappe.throw(f"Meal Item '{item_name}' not found for vendor '{meal_doc.vendor_id}'.")

				else:
					setattr(meal_doc, field, data[field])


		if approval_id:
			approval_doc = frappe.get_doc("Hotpot Approvals", meal_doc.approval_id)
			approval_doc.is_active = 0
			meal_doc.approval_id = ""
			approval_doc.save()
		meal_doc.save()
		frappe.db.commit()
		# coupons = meal_doc.coupons
		# for coupon in coupons:
		# 	try:
		# 		user_doc = frappe.get_doc("Hotpot User", coupon.employee_id)
		# 		if user_doc.fcm_token and coupon.coupon_status == "1":
		# 			send_notification_by_token(
		# 				user_doc.fcm_token,
		# 				"Meal Plot Twist!",
		# 				f"Guess what? The vendor just spiced things up in '{meal_doc.meal_title}'. Go check it out!",
		# 				date=meal_doc.meal_date,
		# 				doc_id=meal_doc.name,
		# 				text="meals",
		# 			)
		# 	except Exception:
		# 		frappe.log_error(
		# 			frappe.get_traceback(), f"Notification failed for employee: {coupon.employee_id}"
		# 		)
		
		set_response(200, True, "Meal updated successfully", {"meal_id": meal_doc.name})
		return

	except Exception as e:
		frappe.db.rollback()
		set_response(500, False, f"Failed to update meal: {str(e)}")
		return


@frappe.whitelist()
def delete_meal():
	try:
		if frappe.request.method != "DELETE":
			set_response(405, False, "Only DELETE method is allowed")
			return
		user_data = get_hotpot_user_by_email()
		if not user_data:
			set_response(401, False, "User Not found")
			return

		data = json.loads(frappe.request.data or "{}")
		meal_id = data.get("meal_id")
		if not meal_id:
			set_response(400, False, "Meal ID is required")
			return

		try:
			meal_doc = frappe.get_doc("Hotpot Meal", meal_id)
		except frappe.DoesNotExistError:
			return set_response(404, False, "Meal not found")
		upcoming_coupons = False
		coupons = meal_doc.coupons
		for coupon in coupons:
			if coupon.coupon_status == "1":
				upcoming_coupons = True
				break
		approval_id = meal_doc.approval_id
		status = False
		active_status = True
		if approval_id:
			approval_doc = frappe.get_doc("Hotpot Approvals", approval_id)
			if approval_doc.approval_status != "Pending":
				status = True
			if not status:
				set_response(400, False, "Your, Request in still pending.")
				return
			if approval_doc.approval_status == "Approved" and approval_doc.is_active == 0:
				active_status = False
			if not active_status:
				set_response(400, False, "You don't have any active requests.")
				return
		if upcoming_coupons:
			set_response(
				409,
				False,
				"Coupons are already generated for this meal. Need Admin Approval for this operation.",
			)
			return
		if approval_id:
			approval_doc = frappe.get_doc("Hotpot Approvals", meal_doc.approval_id)
			approval_doc.is_active = 0
			meal_doc.approval_id = ""
			approval_doc.save()
		meal_doc.is_deleted = 1
		meal_doc.is_active = 0
		meal_doc.save()
		frappe.db.commit()

		set_response(200, True, "Meal deleted successfully")
		return
	except Exception as e:
		set_response(500, False, f"Failed to delete meal: {str(e)}")
		return


@frappe.whitelist()
def get_meals(date, vendor_id=None, page=1, limit=10, for_kiosk=False):
	try:
		if frappe.request.method != "GET":
			set_response(405, False, "Only GET method is allowed")
			return

		if not date:
			set_response(400, False, "Required date")
			return

		user_data = get_hotpot_user_by_email()
		if not user_data:
			set_response(401, False, "User Not Found")
			return

		hotpot_config = frappe.get_single("Hotpot Configurations")

		if has_any_of_role(["Hotpot User", "Hotpot Admin", "Hotpot HR"]):
			vendor_doc = None
			if vendor_id:
				vendor_doc = frappe.db.get("Hotpot User", vendor_id)

			filters = {"date": date, "is_active": 1}
			if vendor_doc:
				filters["location"] = vendor_doc.get("location")

			holiday_doc = frappe.db.get_value("Hotpot Holidays", filters, ["name", "title", "tag_line", "holiday_image"], as_dict=True)
			if holiday_doc:
				return set_response(200, False, f"Oops! Today is a holiday - {holiday_doc.get('title', 'Holiday')} in your location.",[], {
					"type": "holiday",
					"title": holiday_doc.get('title'),
					"tagline": holiday_doc.get('tag_line'),
					"holidayImage": holiday_doc.get('holiday_image'),
				})

			# Check for Sunday
			if (datetime.strptime(date, "%Y-%m-%d").date().weekday() == 6
				and not int(hotpot_config.get("allow_meal_on_sunday", 0))):
				return set_response(200, False, "Oops! Meals are not available on Sundays.", [],{
					"type": "sunday"
				})

		local_time = get_local_time_now()
		date_param_utc = get_utc_datetime_obj(f"{date} {local_time}").date()
		utc_now = datetime.utcnow().replace(tzinfo=None)
		update_coupon_status()
		start_date = get_utc_datetime_obj(f"{date} 00:00:00")
		end_date = get_utc_datetime_obj(f"{date} 23:59:59")

		base_fields = [
			"name",
			"meal_title",
			"day",
			"meal_items",
			"start_time",
			"end_time",
			"buffer_coupon_count",
			"remaining_coupon_count",
			"meal_weight",
			"meal_date",
			"is_special",
			"is_active",
			"vendor_id",
			"repeat_type",
			"lead_time",
			"cancellation_time",
			"category",
			"max_meal_count",
			"surplus_scan_time"
		]

		# start = (page - 1) * limit
		if has_any_of_role(["Hotpot Server", "Hotpot Vendor"]):
			filters = [["vendor_id", "=", user_data.get("email")], ["is_deleted", "=", 0]]

			meals = frappe.db.get_list(
				"Hotpot Meal",
				fields=base_fields,
				filters=filters,
				order_by="creation desc",
				# start=start,
				# limit=limit,
			)

		else:
			filters = [["is_active", "=", 1], ["is_deleted", "=", 0]]
			if vendor_id:
				filters.append(["vendor_id", "=", vendor_id])

			meals = frappe.db.get_list(
				"Hotpot Meal",
				fields=base_fields,
				filters=filters,
				# start=start,
				# limit=limit,
			)
		meals = [meal for meal in meals if meal["meal_date"] <= end_date]
		processed_meals = []
		for meal in meals:
			meal_date = meal["meal_date"]
			repeat_type = meal.get("repeat_type", "once")
			repeat_days = [d.strip() for d in meal.get("repeat_days", "").split(",") if d]

			valid = False
			if repeat_type == "once":
				valid = meal_date >= start_date and meal_date <= end_date
			elif repeat_type == "daily":
				valid = meal_date <= end_date
			elif repeat_type == "specific_days":
				weekday = date_param_utc.strftime("%A").upper()
				valid = meal_date <= end_date and weekday in repeat_days

			if not valid:
				continue

			if (
				start_date <= utc_now
				and utc_now <= end_date
				and has_any_of_role(["Hotpot User", "Hotpot Admin", "Hotpot HR"])
			):
				if (
					get_local_datetime_obj(meal["end_time"]).time()
					<= get_local_datetime_obj(datetime.utcnow().replace(tzinfo=None)).time()
				):
					continue

			vendor = frappe.db.get_value("Hotpot User", meal["vendor_id"], "full_name")
			meal["vendor_name"] = vendor

			meal_doc = frappe.get_doc("Hotpot Meal", meal["name"])
			vendor = frappe.get_doc("Hotpot User", meal_doc.vendor_id)
			# if not has_any_of_role(["Hotpot Server", "Hotpot Vendor"]):
			# 	meal["meal_weight"] = (
			# 		meal["meal_weight"] * (100 - (get_discount(user_data, vendor) or 0)) * 0.01
			# 	)
			meal_doc = frappe.get_doc("Hotpot Meal", meal["name"])
			meal["total_coupons"] = 0
			if has_any_of_role(["Hotpot User", "Hotpot Admin", "Hotpot HR"]):
				meal["coupon"] = [
					{"id": c.name, "status": c.coupon_status, "date": c.coupon_date}
					for c in meal_doc.coupons
					if c.employee_id == user_data.name and get_local_datetime_obj((c.coupon_date.strftime("%Y-%m-%d %H:%M:%S"))).date() == datetime.strptime(f"{date} {local_time}", "%Y-%m-%d %H:%M:%S").date() and not c.guest_of 
				]
			else:
				# meal["coupon"] = [
				# 	{"id": c.name, "status": c.coupon_status, "date": c.coupon_date}
				# 	for c in meal_doc.coupons
				# 	if get_local_datetime_obj(c.coupon_date.strftime("%Y-%m-%d %H:%M:%S")).date() == datetime.strptime(f"{date} {local_time}", "%Y-%m-%d %H:%M:%S").date() and c.coupon_status != "2" and (not c.approval_id or c.status == "Approved")
				# ]
				meal["coupon"] = []
			for coupon in meal_doc.coupons:
				if coupon.coupon_status != "2" and (not coupon.approval_id or coupon.status == "Approved"):
						meal["total_coupons"] += 1
			meal["redeemed_coupons"]=0
			for coupon in meal_doc.coupons:
				if coupon.coupon_status == "0" and (not coupon.approval_id or coupon.status == "Approved"):
					meal["redeemed_coupons"] += 1

			# all_ratings = frappe.get_all(
			# 	"Hotpot Meal Menu Items Rating",
			# 	filters={"meal": meal["name"]},
			# 	fields=["name", "employee", "meal_item", "rating", "review"],
			# )

			# rating_values = [
			# 	float(r["rating"]) if isinstance(r["rating"], str) else r["rating"]
			# 	for r in all_ratings
			# 	if r["rating"] is not None
			# ]

			items_rating=[]

			total_rating = 0
			total_count = 0
			for meal_item in meal_doc.menu_items:
				item_detail = frappe.get_doc("Hotpot Meal Items",meal_item.meal_item)
				all_ratings = frappe.get_all(
					"Hotpot Meal Menu Items Rating",
					filters={"meal_item": meal_item.meal_item},
					fields=["rating"],
				)
				item_rating=0
				item_count=0
				for r in all_ratings:
					if r["rating"] is not None:
						total_rating += float(r["rating"])
						item_rating += float(r["rating"])
						item_count += 1
						total_count += 1
				items_rating.append({"item_name":item_detail.item_name,"rating": round((item_rating / item_count) * 5, 1) if item_count else 0})


			meal["avg_rating"] = round((total_rating / total_count) * 5, 1) if total_count else 0
			meal["items_rating"] = items_rating

			meal["meal_id"] = meal_doc.name
			cat_type = (
				frappe.get_doc("Hotpot Meal Category", meal["category"]) if meal.get("category") else None
			)
			meal["category_name"] = (
				frappe.db.get_value("Hotpot Meal Types", cat_type.get("type"), "type") if cat_type else None
			)
			processed_meals.append(meal)

		processed_meals.sort(
			key=lambda x: (
				get_local_datetime_obj(x["start_time"]).time(),
				get_local_datetime_obj(x["end_time"]).time(),
			)
		)
		if for_kiosk:
			return processed_meals
		set_response(200, True, "Meals Fetched successfully", processed_meals)
		return

	except Exception as e:
		set_response(500, False, f"Failed to get meal: {str(e)}")
		return


@frappe.whitelist()
def get_meals_for_kiosk(date):
	try:
		meals = []
		date_obj = datetime.strptime(date, "%Y-%m-%d")
		new_date_str = (date_obj).strftime("%Y-%m-%d")
		meals = get_meals(new_date_str, for_kiosk=True)
		if not meals:
			set_response(200, True, "No meal found", [])
			return
		# filtered_meals = []
		# for meal in meals:
		# 	start_time = get_local_datetime_obj(meal["start_time"]).time()
		# 	end_time = get_local_datetime_obj(meal["end_time"]).time()
		# 	lead_time = timedelta(hours=meal["lead_time"])

		# 	current_time = get_local_datetime_obj(datetime.utcnow()).time()
		# 	if ( (datetime.combine(datetime.today().date(), start_time) - lead_time).time() >= current_time)) or (start_time<=current_time and end_time>=current_time):
		# 		filtered_meals.append(meal)

		set_response(200, True, "Fetched successfully", meals)
		return
	except Exception as e:
		set_response(500, False, f"Failed to get meal: {str(e)}")
		return


@frappe.whitelist()
def add_meal_items():
	try:
		if frappe.request.method != "POST":
			set_response(405, False, "Only POST method is allowed")
			return

		user_data = get_hotpot_user_by_email()
		if not user_data:
			set_response(401, False, "User Not found")
			return
		if user_data["role"] not in ["Hotpot Vendor", "Hotpot Admin"]:
			set_response(403, False, "Not Permitted to access this resource")
			return

		data = json.loads(frappe.request.data or "{}")
		item_name = data.get("item_name")
		item_name = item_name.strip().lower()
		if not re.fullmatch(r"^[a-zA-Z ]+$", item_name):
			set_response(409, False, "Item name must only contain letters.")
			return
		vendor_id = None
		if has_role("Hotpot Vendor"):
			vendor_id = user_data.get("email")
		else:
			vendor_id = data.get("vendor_id")
		existing_meal_item = frappe.get_list(
			"Hotpot Meal Items",
			fields=["name"],
			filters=[["item_name", "=", item_name], ["vendor_id", "=", vendor_id]],
		)
		if existing_meal_item:
			set_response(409, False, f"A meal item '{item_name}' already exists")
			return
		if not item_name:
			set_response(400, False, "Item is required")
			return
		meal_item_doc = frappe.get_doc(
			{
				"doctype": "Hotpot Meal Items",
				"item_name": item_name,
				"vendor_id": vendor_id,
				"is_active": "1",
			}
		)
		meal_item_doc.insert()
		frappe.db.commit()
		set_response(201, True, "Item added successfully", {"item": meal_item_doc.name})
		return
	except Exception as e:
		set_response(500, False, f"Failed to add item: {str(e)}")
		return


@frappe.whitelist()
def update_meal_items():
	try:
		if frappe.request.method != "PUT":
			return set_response(405, False, "Only PUT method is allowed")

		user_data = get_hotpot_user_by_email()
		if not user_data:
			return set_response(401, False, "User not found")

		if user_data["role"] not in ["Hotpot Vendor", "Hotpot Admin"]:
			return set_response(403, False, "Not permitted to access this resource")

		data = json.loads(frappe.request.data or "{}")
		item_id = data.get("item_id")
		item_name = (data.get("item_name") or "").strip().lower()

		if not item_id or not item_name:
			return set_response(400, False, "Item ID and Item name are required")

		if not frappe.db.exists("Hotpot Meal Items", item_id):
			return set_response(409, False, f"Meal item '{item_name}' does not exist")

		vendor_id = user_data.get("email") if user_data["role"] == "Hotpot Vendor" else data.get("vendor_id")
		if not frappe.db.get_value("Hotpot Meal Items", {"name": item_id, "vendor_id": vendor_id}):
			set_response(409, False, f"Meal item '{item_name}' does not exist for the vendor")
			return

		meal_item_doc = frappe.get_doc("Hotpot Meal Items", item_id)

		if "is_active" in data:
			meal_item_doc.is_active = data["is_active"]

		if "item_name" in data:
			meal_item_doc.item_name = data["item_name"]

		meal_item_doc.save()
		frappe.db.commit()

		return set_response(200, True, "Item updated successfully", {"item": meal_item_doc.name})

	except Exception as e:
		return set_response(500, False, f"Failed to update item: {str(e)}")


@frappe.whitelist()
def get_meal_items():
	try:
		if frappe.request.method != "GET":
			set_response(500, False, "Only GET method is allowed")
			return

		user_data = get_hotpot_user_by_email()
		if not user_data:
			set_response(401, False, "User Not found")
			return
		if not user_data["role"] == "Hotpot Vendor":
			set_response(403, False, "Not Permitted to acess this resource")
			return

		data = frappe.db.get_list(
			"Hotpot Meal Items",
			fields=["*"],
			filters={"vendor_id": user_data.get("email"), "is_active": 1, "is_deleted": 0},
			order_by="item_name asc",
		)

		if not data:
			set_response(200, True, "No meal item found", [])
			return

		set_response(200, True, "Fetched successfully", data)
		return
	except Exception as e:
		set_response(500, False, f"Failed to get meal items: {str(e)}")
		return


@frappe.whitelist()
def update_meal_admin():
	try:
		if frappe.request.method != "PUT":
			set_response(405, False, "Only PUT method is allowed")
			return

		user_data = get_hotpot_user_by_email()
		if not user_data:
			set_response(401, False, "User Not found")
			return

		data = json.loads(frappe.request.data or "{}")
		meal_id = data.get("meal_id")

		if not meal_id:
			set_response(400, False, "Meal Id is required")
			return

		meal_doc = frappe.get_doc("Hotpot Meal", meal_id)

		if not meal_doc:
			set_response(404, False, "Meal not found")
			return

		local_time = get_local_time_now()

		if data.get("start_time"):
			data["start_time"] = get_utc_datetime_obj(f"{data['meal_date']} {data['start_time']}")
		if data.get("end_time"):
			data["end_time"] = get_utc_datetime_obj(f"{data['meal_date']} {data['end_time']}")
		if data.get("meal_date"):
			data["meal_date"] = get_utc_datetime_obj(f"{data['meal_date']} {local_time}")

		for field in [
			"meal_title",
			"meal_date",
			"meal_items",
			"start_time",
			"end_time",
			"buffer_coupon_count",
			"meal_weight",
			"is_active",
			"is_special",
			"is_deleted",
			"cancellation_time",
			"repeat_type",
			"repeat_days",
			"lead_time",
		]:
			if field in data:
				if field in ["meal_items", "repeat_days"] and isinstance(data[field], list):
					setattr(meal_doc, field, str(",".join(data[field])))
				else:
					setattr(meal_doc, field, data[field])

		meal_doc.save()
		frappe.db.commit()

		set_response(200, True, "Meal updated successfully", {"meal_id": meal_doc.name})
		return

	except Exception as e:
		frappe.db.rollback()
		set_response(500, False, f"Failed to update meal: {str(e)}")
		return


# getting all existing meals
@frappe.whitelist()
def get_meals_internal(date, vendor_id=None):
	try:
		user_data = frappe.get_doc("Hotpot User", vendor_id)
		if not user_data:
			return

		local_time = get_local_time_now()
		date_param_utc = get_utc_datetime_obj(f"{date} {local_time}").date()
		utc_now = datetime.utcnow().replace(tzinfo=None)
		update_coupon_status()
		start_date = get_utc_datetime_obj(f"{date} 00:00:00")
		end_date = get_utc_datetime_obj(f"{date} 23:59:59")

		base_fields = [
			"name",
			"category",
			"meal_title",
			"day",
			"meal_items",
			"start_time",
			"end_time",
			"buffer_coupon_count",
			"meal_weight",
			"meal_date",
			"is_special",
			"is_active",
			"vendor_id",
			"repeat_type",
			"repeat_days",
			"lead_time",
			"cancellation_time",
		]
		if has_any_of_role(["Hotpot Server", "Hotpot Vendor"]):
			filters = [["vendor_id", "=", user_data.get("email")], ["is_deleted", "=", 0]]

			meals = frappe.db.get_list(
				"Hotpot Meal",
				fields=base_fields,
				filters=filters,
				order_by="creation desc",
			)

		else:
			filters = [
				["is_active", "=", 1],
			]
			if vendor_id:
				filters.append(["vendor_id", "=", vendor_id])

			meals = frappe.db.get_list(
				"Hotpot Meal",
				fields=base_fields,
				filters=filters,
			)
		meals = [meal for meal in meals if meal["meal_date"] <= end_date]
		processed_meals = []
		for meal in meals:
			meal_date = meal["meal_date"]
			repeat_type = meal.get("repeat_type", "once")
			repeat_days = [d.strip() for d in meal.get("repeat_days", "").split(",") if d]

			valid = False
			if repeat_type == "once":
				valid = meal_date >= start_date and meal_date <= end_date
			elif repeat_type == "daily":
				valid = meal_date <= end_date
			elif repeat_type == "specific_days":
				weekday = date_param_utc.strftime("%A").upper()
				valid = meal_date <= end_date and weekday in repeat_days

			if not valid:
				continue

			if (
				start_date <= utc_now
				and utc_now <= end_date
				and has_any_of_role(["Hotpot User", "Hotpot Admin", "Hotpot HR"])
			):
				if (
					get_local_datetime_obj(meal["end_time"]).time()
					<= get_local_datetime_obj(datetime.utcnow().replace(tzinfo=None)).time()
				):
					continue

			vendor = frappe.db.get_value("Hotpot User", meal["vendor_id"], "full_name")
			meal["vendor_name"] = vendor

			meal_doc = frappe.get_doc("Hotpot Meal", meal["name"])
			if has_any_of_role(["Hotpot User", "Hotpot Admin", "Hotpot HR"]):
				meal["coupon"] = [
					{"id": c.name, "status": c.coupon_status, "date": c.coupon_date}
					for c in meal_doc.coupons
					if c.employee_id == user_data.name and c.coupon_date.date() == date_param_utc and not c.guest_of 
				]
			else:
				meal["coupon"] = [
					{"id": c.name, "status": c.coupon_status, "date": c.coupon_date}
					for c in meal_doc.coupons
					if c.coupon_date.date() == date_param_utc
				]

			ratings = [
				float(r.rating) if isinstance(r.rating, str) else r.rating
				for r in meal_doc.ratings
				if r.rating is not None
			]
			meal["avg_rating"] = round(sum(ratings) / len(ratings), 2) if ratings else 0

			if has_any_of_role(["Hotpot User", "Hotpot Admin", "Hotpot HR"]):
				meal["rating"] = [
					{"id": r.name, "rating": r.rating, "feedback": r.feedback}
					for r in meal_doc.ratings
					if r.employee_id == user_data.name
				]
			else:
				meal["rating"] = [
					{"id": r.name, "rating": r.rating, "feedback": r.feedback} for r in meal_doc.ratings
				]
			meal["meal_id"] = meal_doc.name

			processed_meals.append(meal)

		processed_meals.sort(
			key=lambda x: (
				get_local_datetime_obj(x["start_time"]).time(),
				get_local_datetime_obj(x["end_time"]).time(),
			)
		)
		return processed_meals

	except Exception:
		return


# getting all meals and checking for existing category
@frappe.whitelist()
def check_valid_meal(meal_date, vendor_id, category):
	current_meals = get_meals_internal(meal_date, vendor_id)
	for meal in current_meals:
		if meal.category == category and meal.meal_date == meal_date and meal.vendor_id == vendor_id:
			return {
				"status": "error",
				"message": f"Meal timing conflicts with '{meal.meal_title}'. There is already a meal in {category}",
			}

	return {"status": "success", "message": "Valid meal timing. No conflict found."}


@frappe.whitelist()
def save_draft_meal():
	try:
		if frappe.request.method != "POST":
			set_response(405, False, "Only POST method is allowed")
			return

		user_data = get_hotpot_user_by_email()
		if not user_data:
			set_response(401, False, "User Not found")
			return

		data = json.loads(frappe.request.data or "{}")

		required_fields = [
			"meal_id",
			"approval_id",
			"old_doc",
		]
		if missing := [field for field in required_fields if not data.get(field)]:
			set_response(400, False, f"Missing required fields: {', '.join(missing)}")
			return

		old_doc = data.get("old_doc")

		if isinstance(old_doc, str):
			try:
				old_doc = json.loads(old_doc)
			except json.JSONDecodeError:
				set_response(400, False, "Invalid JSON format for Old doc")
				return

		elif not isinstance(old_doc, dict):
			set_response(400, False, "Old doc must be a dict or valid JSON string")
			return
		
		if "meal_items" in old_doc:
			old_doc["meal_items"] = list(set(old_doc.get("meal_items", [])))

		if "old_meal_items" in old_doc:
			old_doc["old_meal_items"] = list(set(old_doc.get("old_meal_items", [])))

		meal_draft_doc = frappe.get_doc(
			{
				"doctype": "Hotpot Draft Meal",
				"meal": data.get("meal_id"),
				"approval": data.get("approval_id"),
				"new_values": json.dumps(old_doc),
			}
		)

		meal_draft_doc.insert()
		frappe.db.commit()

		set_response(
			201,
			True,
			"Draft meal created successfully",
			{"meal_id": meal_draft_doc.name},
		)
		return

	except Exception as e:
		frappe.db.rollback()
		error_message = f"Failed to create draft meal: {str(e)}"
		trace = traceback.format_exc()
		frappe.log_error(f"{error_message}\n{trace}", "Draft Meal Creation Error")
		set_response(500, False, error_message)
		return


@frappe.whitelist()
def refresh_fetched_data(docname):
	meal_doc = frappe.get_doc("Hotpot Meal",docname)
	category_doc  = frappe.get_doc("Hotpot Meal Category",meal_doc.category)
	if meal_doc.start_time != category_doc.start_time or meal_doc.end_time != category_doc.end_time or meal_doc.surplus_scan_time != category_doc.extra_scan_time:
		meal_doc.start_time = category_doc.start_time
		meal_doc.end_time= category_doc.end_time
		meal_doc.surplus_scan_time=category_doc.extra_scan_time
		# meal_doc.lead_time=category_doc.lead_time
		# meal_doc.cancellation_time=category_doc.cancellation_time
		# meal_doc.actual_meal_rate=category_doc.meal_rate
		meal_doc.save(ignore_permissions=True)
		frappe.db.commit()

@frappe.whitelist()
def update_buffer_coupon_count():
	try:
		if frappe.request.method != "PUT":
			set_response(405, False, "Only PUT method is allowed")
			return

		user_data = get_hotpot_user_by_email()
		if not user_data:
			set_response(401, False, "User Not found")
			return
		if user_data["role"] not in ["Hotpot Vendor"]:
			set_response(403, False, "Not Permitted to access this resource")
			return

		data = json.loads(frappe.request.data or "{}")
		required_fields = [
			"meal_id",
			"buffer_coupon_count",
		]
		if missing := [field for field in required_fields if not data.get(field)]:
			set_response(400, False, f"Missing required fields: {', '.join(missing)}")
			return
		meal_doc = frappe.get_doc("Hotpot Meal", data["meal_id"])
		if not meal_doc:
			set_response(404, False, "Meal not found")
			return 

		current_datetime_local = get_local_datetime_obj(datetime.utcnow())
		current_time = current_datetime_local.time()
		
		is_buffer_time = (
			get_local_datetime_obj(meal_doc.start_time).time()
			<= current_time
			<= get_local_datetime_obj(meal_doc.end_time).time()
		)

		if not is_buffer_time:
			set_response(400, False, "Buffer coupon count can only be updated during meal time.")
			return

		if meal_doc.remaining_coupon_count != 0:
			set_response(400, False, "Buffer coupon count can only be updated when remaining coupon count is zero.")
			return
		meal_doc.buffer_coupon_count += int(data["buffer_coupon_count"])
		meal_doc.remaining_coupon_count = data["buffer_coupon_count"]
		meal_doc.save()
		frappe.db.commit()
		set_response(200, True, "Buffer coupon count updated successfully", {"meal_id": meal_doc.name})
		return
	except Exception as e:
		set_response(500, False, f"Failed to update buffer coupon count: {str(e)}")
		return

