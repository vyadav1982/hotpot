import frappe
import json

from datetime import datetime,timedelta
from frappe.utils import today

from ..api.users import *

def set_response(http_status_code, status, message, data=None):
	frappe.local.response["http_status_code"] = http_status_code
	frappe.response["status"] = status
	frappe.response["message"] = message
	frappe.response["data"] = data

@frappe.whitelist(allow_guest=True)
def give_feedback():
	try:
		if frappe.request.method != "POST":
			set_response(500, False, "Only POST method is allowed")
			return

			
		user_data = get_hotpot_user_by_email()
		if user_data.get("role") != "Hotpot User":
			set_response(403,False,"Not Permitted to acess this resouce")
			return
		if not user_data :
			set_response(404,False,"User Not found")
			return
		data = json.loads(frappe.request.data or "{}")

		meal_doc = frappe.get_doc("Hotpot Meal",data["meal_id"])
		if not meal_doc:
			set_response(404,False,"Meal Not found")
			return
		meal_doc.append("ratings",{
			"employee_id":user_data.get("name"),
			"feedback" : data["feedback"],
			"meal_id": meal_doc.get("name"),
			"rating": data["rating"]
		})
		meal_doc.save()
		frappe.db.commit()
		set_response(200,True,"feedback updated successfully.")
		return

	except Exception as e:
		frappe.db.rollback()
		print(frappe.get_traceback())
		frappe.log_error(frappe.get_traceback(), "Cannot update feedback at this momemt.")
		return set_response(500, False, f"Server error: {str(e)}")

@frappe.whitelist(allow_guest=True)
def create_meal():
	try:
		if frappe.request.method != "POST":
			set_response(500, False, "Only POST method is allowed")
			return

		user_data = get_hotpot_user_by_email()
		if not user_data :
			set_response(404,False,"User Not found")
			return
		data = json.loads(frappe.request.data or "{}")


		meal_title = data.get("meal_title")
		day = data.get("day")
		meal_date = data.get("meal_date")
		vendor_id = user_data.get("name")
		meal_items = ",".join(data.get("meal_items", []))
		start_time = data.get("start_time")
		end_time = data.get("end_time")
		buffer_coupon_count = data.get("buffer_coupon_count")
		meal_weight = data.get("meal_weight")
		is_special = data.get("is_special")

		required_fields = ["meal_title", "day", "meal_date", "vendor_id", 
						 "start_time", "end_time", "meal_items","meal_weight"]
		if missing := [field for field in required_fields if not data.get(field)]:
			set_response(400, False, f"Missing required fields: {', '.join(missing)}")
			return

		existing_meal = frappe.db.exists("Hotpot Meal", {
			"meal_title": meal_title,
			"day": day,
			"meal_date": meal_date,
			"vendor_id": vendor_id
		})

		if existing_meal:
			set_response(409, False, 
				f"Meal '{meal_title}' already exists for vendor {vendor_id} on {day} ({meal_date})")
			return

		meal_doc = frappe.get_doc({
			"doctype": "Hotpot Meal",
			"meal_title": meal_title,
			"day": day,
			"meal_date": meal_date,
			"vendor_id": vendor_id,
			"meal_items": meal_items,
			"start_time": start_time,
			"end_time": end_time,
			"buffer_coupon_count": buffer_coupon_count,
			"meal_weight" : meal_weight,
			"is_active": "1",
			"is_special" : is_special
		})

		meal_doc.insert()
		frappe.db.commit()

		set_response(201, True, "Meal created successfully", {
			"meal_id": meal_doc.name,
			"unique_identifier": f"{vendor_id}|{meal_title}|{day}|{meal_date}"
		})
		return

	except Exception as e:
		frappe.db.rollback()
		set_response(500, False, f"Failed to create meal: {str(e)}")
		return

@frappe.whitelist(allow_guest=True)
def update_meal():
	try:
		if frappe.request.method != "PUT":
			set_response(500, False, "Only PUT method is allowed")
			return
		
		user_data = get_hotpot_user_by_email()
		if not user_data :
			set_response(404,False,"User Not found")
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

		for field in ["meal_title", "day", "meal_date", "meal_items", "start_time", "end_time", "buffer_coupon_count","meal_weight","is_active","is_special"]:
			if field in data:
				setattr(meal_doc, field, ",".join(data[field]) if field == "meal_items" else data[field])

		meal_doc.save()
		frappe.db.commit()

		set_response(200, True, "Meal updated successfully", {"meal_id": meal_doc.name})
		return

	except Exception as e:
		frappe.db.rollback()
		set_response(500, False, f"Failed to update meal: {str(e)}")
		return

@frappe.whitelist(allow_guest=True)
def delete_meal():
	try:
		if frappe.request.method != "DELETE":
			set_response(500, False, "Only DELETE method is allowed")
			return
		user_data = get_hotpot_user_by_email()
		if not user_data :
			set_response(404,False,"User Not found")
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

		meal_doc.delete()
		frappe.db.commit()

		set_response(200, True, "Meal deleted successfully")
		return
	except Exception as e:
		set_response(500, False, f"Failed to delete meal: {str(e)}")
		return

@frappe.whitelist(allow_guest=True)
def get_meals():
	try:
		if frappe.request.method != "GET":
			set_response(500, False, "Only GET method is allowed")
			return

		user_data = get_hotpot_user_by_email()
		if not user_data:
			set_response(404, False, "User Not Found")
			return

		user_id = user_data.get("name")

		if user_data.get("role") == "Hotpot Server":
			data = frappe.db.get_list(
				"Hotpot Meal",
				fields=["*"],
				filters={"vendor_id": user_id}
			)

		elif user_data.get("role") == "Hotpot User":
			today_date = today()
			meal_data = frappe.db.get_list(
				"Hotpot Meal",
				fields=["name", "meal_title", "day", "meal_items", "start_time", "end_time", "buffer_coupon_count", "meal_weight","coupons"],
				filters={"meal_date": today_date, "is_active": 1}
			)
			if not meal_data:
				set_response(404,False,"No meal found for today")
				return

			data = []
			for meal in meal_data:
				meal_doc = frappe.get_doc("Hotpot Meal", meal["name"])

				user_coupons=[]
				for coupon in meal_doc.coupons:
					if coupon.employee_id == user_data.name:
						user_coupons.append({
							"id":coupon.name,
							"coupon status": coupon.coupon_status,
							"coupon_date":coupon.coupon_date
						})

				user_ratings=[]
				for coupon in meal_doc.ratings:
					if coupon.employee_id == user_data.name:
						user_ratings.append({
							"id":coupon.name,
							"rating": coupon.rating,
							"feedback":coupon.feedback
						})


				print(user_coupons)
				data.append({
					"meal_title": meal_doc.meal_title,
					"meal_id": meal_doc.name,
					"day": meal_doc.day,
					"meal_items": meal_doc.meal_items,
					"start_time": meal_doc.start_time,
					"end_time": meal_doc.end_time,
					"buffer_coupon_count": meal_doc.buffer_coupon_count,
					"meal_weight": meal_doc.meal_weight,
					"coupon": user_coupons,
					"ratings": user_ratings
				})

		else:
			data = frappe.db.get_list("Hotpot Meal", fields=["*"])

		if not data:
			set_response(404, False, "No meal found")
			return

		set_response(200, True, "Fetched successfully", data)
		return

	except Exception as e:
		set_response(500, False, f"Failed to get meal: {str(e)}")
		return


@frappe.whitelist(allow_guest=True)
def add_meal_items():
	try:
		if frappe.request.method != "POST":
			set_response(500, False, "Only POST method is allowed")
			return

		user_data = get_hotpot_user_by_email()
		if not user_data :
			set_response(404,False,"User Not found")
			return

		data = json.loads(frappe.request.data or "{}")
		item_name = data.get("item_name")
		item_name = item_name.lower()
		existing_meal = frappe.db.exists("Hotpot Meal Items", f"{item_name}")
		if existing_meal:
			set_response(409, False, f"A meal item '{item_name}' already exists")
			return
		if not item_name:
			set_response(400, False, "Item is required")
			return
		meal_item_doc = frappe.get_doc({
			"doctype": "Hotpot Meal Items",
			"item_name": item_name,
			"vendor_id" : user_data.get("name"),
			"is_active":"1"
		})
		meal_item_doc.insert()
		frappe.db.commit()
		set_response(201, True, "Item added successfully", {"item": meal_item_doc.name})
		return
	except Exception as e:
		set_response(500, False, f"Failed to add item: {str(e)}")
		return

@frappe.whitelist(allow_guest=True)
def get_meal_items():
	try:
		if frappe.request.method != "GET":
			set_response(500, False, "Only GET method is allowed")
			return

		user_data = get_hotpot_user_by_email()
		if not user_data :
			set_response(404,False,"User Not found")
			return

		data = frappe.db.get_list("Hotpot Meal Items", fields=["*"],filters=[["vendor_id", "=", user_data.get("name")]])

		if not data:
			set_response(404, False, "No meal item found")
			return

		set_response(200, True, "Fetched successfully", data)
		return
	except Exception as e:
		set_response(500, False, f"Failed to get meal items: {str(e)}")
		return