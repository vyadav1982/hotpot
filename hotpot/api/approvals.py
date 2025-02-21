import frappe
from hotpot.utils.utc_time import *
from ..api.users import *
import json



def set_response(http_status_code, status, message, data=None):
	frappe.local.response["http_status_code"] = http_status_code
	frappe.response["status"] = status
	frappe.response["message"] = message
	frappe.response["data"] = data


def create_approval():
    try:
        if frappe.request.method != "POST":
            set_response(405, False, "Only POST method is allowed")
            return
        
        user_data = get_hotpot_user_by_email()
        if not user_data:
            set_response(404, False, "User not found")
            return
        
        data = json.loads(frappe.request.data or "{}")
        required_fields = ["request_type", "requested_by", "description"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            set_response(400, False, f"Missing required fields: {', '.join(missing_fields)}")
            return

        approval = frappe.get_doc({
            "doctype": "Hotpot Approval",
            "request_type": data["request_type"],
            "requested_by": user_data.get("name"),
            "descrption": data.get("description"),
            "attachments": json.dumps(data.get("attachments", [])),
            "approval_status": "Pending",
        })

        if(user_data.get("role") == "Hotpot Vendor" or user_data.get("role") == "Hotpot Server"):
             approval.meal_id = data.get("meal_id")
        
        approval.insert()
        frappe.db.commit()

        approvals_id = user_data.get("approval_id")
        approvals_id.append(approval.name)
        frappe.db.set_value("Hotpot User", user_data.get("name"), "approval_id", json.dumps(approvals_id))
        frappe.db.commit()

        set_response(200, True, "Approval created successfully", approval.name)
        return
    
    except Exception as e:
        frappe.log_error(f"Error creating approval: {str(e)}")
        set_response(500, False, f"Server error: {str(e)}")