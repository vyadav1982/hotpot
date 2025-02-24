import frappe
from hotpot.utils.utc_time import *
from ..api.users import *
import json
from frappe.utils.file_manager import save_file
from hotpot.utils.utc_time import *




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

		fields = ["name", "request_type","meal_id", "descrption", "approval_status", "attachments", "approval_remarks"]

		if user_data.get("role") == "Hotpot User":
			fields += ["guest_name", "guest_mobile_no", "purpose_of_visiting", "date"]

		approvals = frappe.db.get_list(
			"Hotpot Approvals",
			fields=fields,
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
			return set_response(405, False, "Only POST method is allowed")

		user_data = get_hotpot_user_by_email()
		if not user_data:
			return set_response(404, False, "User not found")

		data = json.loads(frappe.request.data or "{}")
		required_fields = ["request_type", "description", "meal_id"]
		
		if user_data.get("role") == "Hotpot User":
			required_fields += ["guest_name", "guest_mobile_no", "purpose_of_visiting", "date"]

		missing_fields = [field for field in required_fields if not data.get(field)]
		if missing_fields:
			return set_response(400, False, f"Missing required fields: {', '.join(missing_fields)}")

		if user_data.get("role") == "Hotpot User":
			existing_approval = frappe.get_all(
				"Hotpot Approvals",
				filters={"guest_mobile_no": data.get("guest_mobile_no"), "approval_status": "Pending"},
				limit=1
			)
		if existing_approval:
			return set_response(400, False, "Pending approval already exists for this mobile number.")


		date = get_utc_datetime_obj(f"{data.get('date')} {get_local_time_now()}") if "date" in data else None

		approval_data = {
			"doctype": "Hotpot Approvals",
			"request_type": data["request_type"],
			"requested_by": user_data.get("name"),
			"descrption": data.get("description"),
			"meal_id": data.get("meal_id"),
			"attachments": json.dumps(data.get("attachments", [])),
			"approval_status": "Pending",
			"is_active": 1,
		}
		if user_data.get("role") == "Hotpot User":
			approval_data.update({
				"purpose_of_visiting": data.get("purpose_of_visiting"),
				"guest_name": data.get("guest_name"),
				"guest_mobile_no" : data.get("guest_mobile_no", "").strip(),
				"date": date,
			})

		approval = frappe.get_doc(approval_data)

		if user_data.get("role") in ["Hotpot Vendor", "Hotpot Server"]:
			meal_doc = frappe.get_doc("Hotpot Meal", data.get("meal_id"))
			if not meal_doc:
				return set_response(404, False, "Meal not found")

			if meal_doc.get("approval_id"):
				return set_response(400, False, "Pending approval already exists for this meal.")

			meal_doc.approval_id = approval.name
			meal_doc.save()

		approval.insert()
		existing_approvals = frappe.db.get_value("Hotpot User", user_data.get("name"), "approval_id")
		print(existing_approvals)
		approval_list = json.loads(existing_approvals) if existing_approvals and isinstance(existing_approvals, str) else []
		if not isinstance(approval_list, list):
			approval_list = []

		approval_list.append(approval.name)

		frappe.db.set_value("Hotpot User", user_data.get("name"), "approval_id", json.dumps(approval_list))
		frappe.db.commit()

		return set_response(200, True, "Approval created successfully", approval.name)

	except Exception as e:
		frappe.log_error(f"Error creating approval: {str(e)}")
		return set_response(500, False, f"Server error: {str(e)}")

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
