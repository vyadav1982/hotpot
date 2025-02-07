import json
import frappe
import frappe.utils
from frappe import _
from frappe.twofactor import two_factor_is_enabled
from frappe.utils.html_utils import get_icon_html
from frappe.utils.oauth import get_oauth2_authorize_url, get_oauth_keys
from frappe.utils.password import get_decrypted_password

import jwt
from datetime import datetime, timedelta
import random

# no_cache = True

def set_response(http_status_code, status, message, data=None):
	frappe.local.response["http_status_code"] = http_status_code
	frappe.response["status"] = status
	frappe.response["message"] = message
	frappe.response["data"] = data

@frappe.whitelist(allow_guest=True)
def get_context():
	redirect_to = frappe.local.request.args.get("redirect-to")
	context = {"provider_logins": []}
	providers = frappe.get_all(
		"Social Login Key",
		filters={"enable_social_login": 1},
		fields=["name", "client_id", "base_url", "provider_name", "icon", "redirect_url"],
		order_by="name",
	)

	for provider in providers:
		client_secret = get_decrypted_password("Social Login Key", provider.name, "client_secret")
		if not client_secret:
			continue

		icon = {"html": "", "src": "", "alt": ""}
		if provider.icon:
			if provider.provider_name == "Custom":
				icon["html"] = get_icon_html(provider.icon, small=True)
			else:
				icon["src"] = provider.icon
				icon["alt"] = provider.provider_name

		if provider.client_id and provider.base_url and get_oauth_keys(provider.name):
			context["provider_logins"].append(
				{
					"name": provider.name,
					"provider_name": provider.provider_name,
					"auth_url": get_oauth2_authorize_url(provider.name, redirect_to),
					"redirect_to": provider.redirect_url,
					"icon": icon,
				}
			)
			context["social_login"] = True

	login_label = [_("Email")]
	if frappe.utils.cint(frappe.get_system_settings("allow_login_using_mobile_number")):
		login_label.append(_("Mobile"))

	if frappe.utils.cint(frappe.get_system_settings("allow_login_using_user_name")):
		login_label.append(_("Username"))

	context["login_label"] = f" {_('/')} ".join(login_label)

	context["login_with_email_link"] = frappe.get_system_settings("login_with_email_link")
	context["two_factor_is_enabled"] = two_factor_is_enabled()
	context["disable_signup"] = frappe.get_website_settings("disable_signup")

	return context

JWT_SECRET = "boostIsMySecret"
@frappe.whitelist(allow_guest=True)
def user_login():
	try:
		if frappe.request.method != "POST":
			return {"status": "error", "message": "Only POST method is allowed"}
		
		data = json.loads(frappe.request.data or "{}")
		
		method = data.get("method")
		password = data.get("password")
		print("{{}}" * 10, password)
		
		if not method or not password:
			return {"status": "error", "message": "Method and password are required"}
		
		user_doc = None
		
		if method == "email":
			email = data.get("email")
			if not frappe.db.exists("Hotpot User", {"email": email}):
				return {"status": "error", "message": f"Email {email} doesn't exist."}
			user_doc = frappe.get_doc("Hotpot User", {"email": email})
		
		elif method == "emp_id":
			emp_id = data.get("empId")
			if not frappe.db.exists("Hotpot User", {"employee_id": emp_id}):
				return {"status": "error", "message": f"Employee ID {emp_id} doesn't exist."}
			user_doc = frappe.get_doc("Hotpot User", {"employee_id": emp_id})
		
		else:
			return {"status": "error", "message": "Invalid login method"}
		
		if not user_doc.password == password:
			return {"status": "error", "message": "Invalid password"}
		
		user_data = user_doc.as_dict()
		for key, value in user_data.items():
			if isinstance(value, datetime):
				user_data[key] = value.isoformat()
		
		payload = {
			"user": user_data,
			"exp": (datetime.now() + timedelta(days=30)).timestamp(),
			"iat": datetime.now().timestamp(),
		}
		
		token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
		
		return {
			"status": "success",
			"message": "Login successful",
			"token": token
		}
	
	except Exception as e:
		frappe.log_error(message=str(e), title="User Login Error")
		return {"status": "error", "message": f"Login failed: {str(e)}"}

@frappe.whitelist(allow_guest=True)
def user_signUp(data):
	try:
		data = json.loads(data)
		emp_id = data.get("empId")
		email = data.get("email")

		if frappe.db.exists("Hotpot User", {"employee_id": emp_id}):
			return {"status": "error", "message": f"Employee ID {emp_id} already exists."}

		if frappe.db.exists("Hotpot User", {"email": email}):
			return {"status": "error", "message": f"Email {email} already exists."}

		new_user = frappe.get_doc(
			{
				"doctype": "Hotpot User",
				"employee_id": emp_id,
				"employee_name": data.get("name"),
				"mobile_no": data.get("mobile"),
				"email": email,
				"password": data.get("password"),
				"coupon_count": 60,
			}
		)
		new_user.insert(ignore_permissions=True)
		frappe.db.commit()

		return {"status": "success", "message": "User created successfully.", "data": new_user.as_dict()}

	except json.JSONDecodeError:
		return {"status": "error", "message": "Invalid data format."}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "User Sign-Up Error")
		return {"status": "error", "message": f"An error occurred: {str(e)}"}


OTP_PREFIX = "otp:"

@frappe.whitelist(allow_guest=True)
def generate_otp(phone):
	if not phone.startswith("+"):
		phone = "+91- " + phone

	if not frappe.db.exists("Hotpot User", {"mobile_no": phone}):
		set_response(404, False, f"User with mobile number {phone} not found.")
		return

	otp = str(random.randint(100000, 999999))
	
	key = f"{OTP_PREFIX}{phone}"
	
	frappe.cache().set_value(key, otp, expires_in_sec=300)
	
	set_response(200, True, f"OTP({otp}) generated and sent to {phone}, valid for 5 minutes.")
	return

@frappe.whitelist(allow_guest=True)
def verify_otp(phone, submitted_otp):

	if not phone.startswith("+"):
		phone = "+91- " + phone

	key = f"{OTP_PREFIX}{phone}"
	

	stored_otp = frappe.cache().get_value(key)
	
	if not stored_otp:
		set_response(404, False, "OTP expired or not found.")
		return
	
	if stored_otp == submitted_otp:
		frappe.cache().delete_key(key)

		data = frappe.db.get_value("Hotpot User", {"mobile_no": phone}, ["name", "email","password"], as_dict=True)

		set_response(200, True, "OTP verified successfully.",data)
		return
	else:
		set_response(400, False, "Invalid OTP.")
		return