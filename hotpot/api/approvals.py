import frappe
from hotpot.utils.utc_time import *
from ..api.users import *
import json
from frappe.utils.file_manager import save_file
from hotpot.utils.utc_time import *
from hotpot.utils.email import *
from hotpot.utils.guest_coupon_generate import *




def send_approval_request_email(to_email, user_data, request_data, doc,meal_name):
	email_subject = f"Approval Request from {user_data.employee_name} ({user_data.employee_id}) for {request_data['request_type']}"
	context = {
		"user_data": user_data,
		"request_data": request_data,
		"meal_name": meal_name,
		"get_approval_link": "https://hotpot-admin.vercel.app/service-requests"
	}
	send_email("approval_email", to_email, context, email_subject)

def get_approval_link(doc):
	# return f"http://shashi.localhost:8000/app/hotpot-approvals/{doc}"
	return f"{frappe.utils.get_url()}/app/hotpot-approvals/{doc}"


def set_response(http_status_code, status, message, data=None):
	frappe.local.response["http_status_code"] = http_status_code
	frappe.response["status"] = status
	frappe.response["message"] = message
	frappe.response["data"] = data

@frappe.whitelist()
def get_approvals():
	try:
		if frappe.request.method != "GET":
			set_response(405, False, "Only GET method is allowed")
			return
		user_data = get_hotpot_user_by_email()
		if not user_data:
			set_response(404, False, "User not found")
			return

		fields = ["name", "request_type","meal_id", "descrption", "approval_status", "attachments", "approval_remarks","is_active"]

		if user_data.get("role") in ["Hotpot User","Hotpot Admin","Hotpot HR"]:
			fields += ["guest_name", "guest_mobile_no", "purpose_of_visiting", "date","coupon_count"]

		approvals = frappe.db.get_list(
			"Hotpot Approvals",
			fields=fields,
			filters=[["requested_by", "=", user_data.get("name")]],
		)

		if not approvals:
			set_response(200, False, "No approvals found")
			return
		meal_fields = [
			"name", "owner", "creation", "modified", "modified_by", "docstatus", "idx",
			"meal_title", "meal_items", "start_time", "end_time", "buffer_coupon_count",
			"vendor_id", "is_active", "meal_date", "meal_weight", "is_special",
			"lead_time", "cancellation_time", "repeat_type", "repeat_days", "approval_id"
		]

		# Append filtered meal details for each approval
		for approval in approvals:
			meal_id = approval.get("meal_id")
			if meal_id:
				try:
					meal_data = frappe.db.get_value("Hotpot Meal", meal_id, meal_fields, as_dict=True)
					approval["meal_details"] = meal_data  # Attach only selected fields
				except frappe.DoesNotExistError:
					approval["meal_details"] = None  # Handle missing meal data gracefully


		set_response(200, True, "Approvals fetched successfully", approvals)
		return

	except Exception as e:
		frappe.log_error(f"Error fetching approvals: {str(e)}")
		set_response(500, False, f"Server error: {str(e)}")

@frappe.whitelist()
def create_approval():
	try:
		if frappe.request.method != "POST":
			return set_response(405, False, "Only POST method is allowed")

		user_data = get_hotpot_user_by_email()
		if not user_data:
			return set_response(404, False, "User not found")

		data = json.loads(frappe.request.data or "{}")
		required_fields = ["request_type", "description", "meal_id"]
		
		if user_data.get("role") in ["Hotpot User","Hotpot Admin","Hotpot HR"]:
			required_fields += ["guest_name", "guest_mobile_no", "purpose_of_visiting", "date","country_code","coupon_count"]

		missing_fields = [field for field in required_fields if not data.get(field)]
		if missing_fields:
			return set_response(400, False, f"Missing required fields: {', '.join(missing_fields)}")
		if user_data.get("role") in ["Hotpot User","Hotpot Admin","Hotpot HR"]:
			if data.get("guest_mobile_no") and not data.get("guest_mobile_no").strip().isdigit():
				return set_response(400, False, "Mobile number should contain only digits")
			if data.get("guest_mobile_no") and len(data.get("guest_mobile_no").strip()) != 10:
				return set_response(400, False, "Mobile number should contain 10 digits")
		
		if user_data.get("role") in ["Hotpot User","Hotpot Admin","Hotpot HR"]:
			mobile_no = data.get("country_code")+"- "+data.get("guest_mobile_no")
		existing_approval = None
		if user_data.get("role") in ["Hotpot User","Hotpot Admin","Hotpot HR"]:
			existing_approval = frappe.get_all(
				"Hotpot Approvals",
				filters={"guest_mobile_no": mobile_no, "approval_status": "Pending"},
				limit=1
			)
		if existing_approval and user_data.get("role")!="Hotpot Admin":
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
			"is_active": 1
		}
		if user_data.get("role") in ["Hotpot User","Hotpot Admin","Hotpot HR"]:
			approval_data.update({
				"purpose_of_visiting": data.get("purpose_of_visiting"),
				"guest_name": data.get("guest_name"),
				"guest_mobile_no" : mobile_no,
				"date": date,
				"coupon_count":data.get("coupon_count")
			})

		approval = frappe.get_doc(approval_data)
		meal_doc = frappe.get_doc("Hotpot Meal", data.get("meal_id"))
		if user_data.get("role") in ["Hotpot Vendor", "Hotpot Server"]:
			if not meal_doc:
				return set_response(404, False, "Meal not found")

			if meal_doc.get("approval_id"):
				return set_response(400, False, "Pending approval already exists for this meal.")

		approval.insert()
		existing_approvals = frappe.db.get_value("Hotpot User", user_data.get("name"), "approval_id")
		approval_list = json.loads(existing_approvals) if existing_approvals and isinstance(existing_approvals, str) else []
		if not isinstance(approval_list, list):
			approval_list = []
		if user_data.get("role") in ["Hotpot Vendor", "Hotpot Server"]:
			meal_doc.approval_id = approval.name
			meal_doc.save()

		approval_list.append(approval.name)
		if user_data.get("role")!="Hotpot Admin":
			send_approval_request_email("sashikant12rao@gmail.com",user_data,data,approval.name,meal_doc.meal_title)


		frappe.db.set_value("Hotpot User", user_data.get("name"), "approval_id", json.dumps(approval_list))
		frappe.db.commit()
		if user_data.get("role") == "Hotpot Admin":
			approval_doc = frappe.get_doc("Hotpot Approvals",approval.name)
			approval_doc.approval_status="Approved"
			approval_doc.is_active=0
			approval_doc.save()
			res = generate_guest_coupon(approval_doc)
			frappe.db.commit()
			return set_response(200, res.get("status") == "success", res.get("msg"))

			

		return set_response(200, True, "Request created successfully", approval.name)

	except Exception as e:
		frappe.rollback()
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

		allowed_extensions = {"jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "tiff"}
		allowed_mime_types = {
			"image/jpeg", "image/png", "image/gif", "image/bmp",
			"image/webp", "image/svg+xml", "image/tiff"
		}

		filename = uploaded_file.filename.lower()
		file_ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
		file_mime_type = uploaded_file.content_type

		if file_ext not in allowed_extensions or file_mime_type not in allowed_mime_types:
			return {"success": False, "message": "Only image files are allowed"}

		doctype = "Hotpot User"
		docname = user_data.get("name")

		file_doc = save_file(filename, uploaded_file.read(), doctype, docname, is_private=0)

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
