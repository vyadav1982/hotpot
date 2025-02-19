import frappe
from hotpot.utils.utc_time import *
from ..api.users import *
import json



def set_response(http_status_code, status, message, data=None):
    frappe.local.response["http_status_code"] = http_status_code
    frappe.response["status"] = status
    frappe.response["message"] = message
    frappe.response["data"] = data


@frappe.whitelist(allow_guest=True)
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

        if not data.get("intent") or not data.get("start_date") or not data.get("end_date") or not data.get("title") or not data.get("text"):
            set_response(400,False,"Intent is required")
            return

        if data["intent"] not in ["LinkClickable", "OpenModal", "NotClickable"]:
            set_response(400,False,"Invalid intent type")

        if data["intent"] == "LinkClickable" and not data.get("link"):
            set_response(400,False,"Link is required for LinkClickable intent")
        if data["intent"] == "OpenModal" and not data.get("description"):
            set_response(400,False,"Description is required for OpenModal intent")

        if data.get("start_date") and not data.get("end_date"):
            set_response(400,False,"Either pass both or none")
            return
        if data.get("end_date") and not data.get("start_date"):
            set_response(400,False,"Either pass both date or none")
            return
        if data.get("start_date") and data.get("end_date"):
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
            "start_date": data.get("start_date"),
            "end_date": data.get("end_date"),
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

@frappe.whitelist(allow_guest=True)
def get_active_banners():
    try:
        if frappe.request.method != "GET":
            set_response(405, False, "Only GET method is allowed")
            return

        user_data = get_hotpot_user_by_email()
        if not user_data:
            set_response(404, False, "User Not found")
            return
        if user_data.get("role") == "Hotpot User":
            set_response(403, False, "Not Permitted to acess this resouce")
            return
        
        today = datetime.utcnow().replace(tzinfo=None)
        banners = frappe.get_all(
            "Hotpot Banner",
            filters={
                "is_active": 1,
                "created_by": user_data.get("name"),
                # "start_date": ["<=", today, "OR start_date IS NULL"],
                # "end_date": [">=", today, "OR end_date IS NULL"],
            },
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

