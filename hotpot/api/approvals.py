import frappe
from hotpot.utils.utc_time import *
from ..api.users import *
import json
from frappe.utils.file_manager import save_file



def set_response(http_status_code, status, message, data=None):
	frappe.local.response["http_status_code"] = http_status_code
	frappe.response["status"] = status
	frappe.response["message"] = message
	frappe.response["data"] = data

@frappe.whitelist(allow_guest=True)
def get_approvals():
	try:
		if frappe.request.method != "GET":
			set_response(405, False, "Only GET method is allowed")
			return
		user_data = get_hotpot_user_by_email()
		if not user_data:
			set_response(404, False, "User not found")
			return

		approvals = frappe.db.get_list(
			"Hotpot Approvals",
			fields=["name", "request_type","descrption", "approval_status", "attachments","approval_remarks"],
			filters=[["requested_by", "=", user_data.get("name")]],
		)
		if not approvals:
			set_response(200, False, "No approvals found")
			return

		set_response(200, True, "Approvals fetched successfully", approvals)
		return

	except Exception as e:
		frappe.log_error(f"Error fetching approvals: {str(e)}")
		set_response(500, False, f"Server error: {str(e)}")


@frappe.whitelist(allow_guest=True)
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
			"doctype": "Hotpot Approvals",
			"request_type": data["request_type"],
			"requested_by": user_data.get("name"),
			"descrption": data.get("description"),
			"attachments": json.dumps(data.get("attachments", [])),
			"approval_status": "Pending",
		})

		if(user_data.get("role") == "Hotpot Vendor" or user_data.get("role") == "Hotpot Server"):
			if not data.get("meal_id"):
				set_response(400, False, "Meal ID is required for Vendor and Server")
				return
			if not meal_doc:
				set_response(404, False, "Meal not found")
				return
			meal_doc = frappe.get_doc("Hotpot Meal",data.get("meal_id"))
			approval_id = meal_doc.get("approval_id")
			if approval_id:
				set_response(400, False, "Approval already exists for this meal")
				return
			approval.meal_id = data.get("meal_id")
			meal_doc.approval_id = approval.name
			meal_doc.save()
		
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

@frappe.whitelist(allow_guest=False)
def upload_attachment():
    try:
        if frappe.request.method != "POST":
            return {"success": False, "message": "Only POST method is allowed"}

        user_data = get_hotpot_user_by_email()
        if not user_data:
            return {"success": False, "message": "User not found"}

        uploaded_file = frappe.request.files.get("file")
        if not uploaded_file:
            return {"success": False, "message": "No file uploaded"}

        doctype = "Hotpot User"
        docname = user_data.get("name")

        file_doc = save_file(uploaded_file.filename, uploaded_file.read(), doctype, docname, is_private=0)

        return {
            "success": True,
            "message": "File uploaded successfully",
            "file_url": file_doc.file_url,
            "file_name": file_doc.file_name,
            "file_id": file_doc.name,
        }

    except Exception as e:
        frappe.log_error(f"Error in file upload: {str(e)}")
        return {"success": False, "message": f"Error: {str(e)}"}
