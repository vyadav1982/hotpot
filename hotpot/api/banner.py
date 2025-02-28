import frappe
from hotpot.utils.utc_time import *
from ..api.users import *
import json



def set_response(http_status_code, status, message, data=None):
	frappe.local.response["http_status_code"] = http_status_code
	frappe.response["status"] = status
	frappe.response["message"] = message
	frappe.response["data"] = data


@frappe.whitelist()
def create_banner():
	try:
		if frappe.request.method != "POST":
			set_response(405, False, "Only POST method is allowed")
			return

		user_data = get_hotpot_user_by_email()
		if user_data.get("role") == "Hotpot User":
			set_response(403, False, "Not Permitted to acess this resouce")
			return
		
		if not user_data:
			set_response(404, False, "User Not found")
			return
		data = json.loads(frappe.request.data or "{}")
		required_fields = [
			"intent",
			"start_date",
			"end_date",
			"title",
			"text",
		]
		if missing := [field for field in required_fields if not data.get(field)]:
			set_response(400, False, f"Missing required fields: {', '.join(missing)}")
			return

		if data["intent"] not in ["LinkClickable", "OpenModal", "NotClickable"]:
			set_response(400,False,"Invalid intent type")
			return

		if data["intent"] == "LinkClickable" and not data.get("link"):
			set_response(400,False,"Link is required for LinkClickable intent")
			return
		if data["intent"] == "OpenModal" and not data.get("description"):
			set_response(400,False,"Description is required for OpenModal intent")
			return

		start_date = data.get("start_date")
		end_date = data.get("end_date")
		local_time = get_local_time_now()
		start_date = get_utc_datetime_obj(f"{start_date} {local_time}")
		end_date = get_utc_datetime_obj(f"{end_date} {local_time}")

		banner = frappe.get_doc({
			"doctype": "Hotpot Banner",
			"title": data.get("title"),
			"text": data.get("text"),
			"intent": data.get("intent"),
			"link": data.get("link"),
			"description": data.get("description"),
			"image": data.get("image"),
			"start_date": start_date,
			"end_date": end_date,
			"priority": data.get("priority"),
			"created_by": user_data.get("name"),
			"is_active":1
		})
		banner.insert()
		frappe.db.commit()
		set_response(200,True,"Banner created successfully",banner.name)
		return

	except Exception as e:
		frappe.log_error(f"Error creating banner: {str(e)}")
		set_response(500,False,f"Server error: {str(e)}")
		return

@frappe.whitelist()
def get_active_banners():
	try:
		if frappe.request.method != "GET":
			set_response(405, False, "Only GET method is allowed")
			return

		user_data = get_hotpot_user_by_email()
		if not user_data:
			set_response(404, False, "User Not found")
			return
		
		today = datetime.utcnow().replace(tzinfo=None)
		filters = {
			"is_active": 1,
			"start_date": ["<=", today],
			"end_date": [">=", today],
		}
		if not user_data.get("role") == "Hotpot User":
			filters["created_by"] = user_data.get("name")
		banners = frappe.get_all(
			"Hotpot Banner",
			filters=filters,
			fields=[
				"name", "title", "text", "intent", "link", "description", "image", "priority"
			],
			order_by="priority desc"
		)

		if not banners:
			set_response(200,True,"No active banners found")
			return
		set_response(200,True,"Banners Fetched successfully",banners)
		return

	except Exception as e:
		frappe.log_error(f"Error fetching banners: {str(e)}")
		set_response(500,False,f"Server error: {str(e)}")
		return


@frappe.whitelist()
def update_banner(banner_id, **kwargs):
	try:
		if frappe.request.method != "PUT":
			set_response(405, False, "Only PUT method is allowed")
			return

		user_data = get_hotpot_user_by_email()
		if user_data.get("role") == "Hotpot User":
			set_response(403, False, "Not Permitted to acess this resouce")
			return
		
		if not user_data:
			set_response(404, False, "User Not found")
			return
		banner = frappe.get_doc("Banner", banner_id)
		if not banner:
			set_response(404, False, "Banner not found")
			return

		for key, value in kwargs.items():
			if key in banner.as_dict():
				setattr(banner, key, value)

		banner.save()
		frappe.db.commit()
		set_response(200,True,"Banner updated successfully", banner.name)
		return

	except Exception as e:
		frappe.log_error(f"Error updating banner: {str(e)}")
		set_response(500,False,f"Server error: {str(e)}")
		return 


@frappe.whitelist()
def delete_banner(banner_id):
	try:
		if frappe.request.method != "DELETE":
			set_response(405, False, "Only DELETE method is allowed")
			return

		user_data = get_hotpot_user_by_email()
		if user_data.get("role") == "Hotpot User":
			set_response(403, False, "Not Permitted to acess this resouce")
			return
		
		if not user_data:
			set_response(404, False, "User Not found")
			return
		banner = frappe.get_doc("Hotpot Banner", banner_id)
		if not banner:
			set_response(404, False, "Banner not found")
			return
		frappe.delete_doc("Hotpot Banner", banner_id)
		frappe.db.commit()
		return {"status": "success", "message": "Banner deleted successfully"}

	except Exception as e:
		frappe.log_error(f"Error deleting banner: {str(e)}")
		return {"status": "error", "message": str(e)}

