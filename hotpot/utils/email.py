import base64
import io
import json
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import frappe
from frappe.utils.file_manager import save_file
from frappe.utils.jinja import render_template


@frappe.whitelist()
def send_email(template_name, to_email, context, subject, qr_code_base64=None):
	try:
		context = json.loads(context) if isinstance(context, str) else context
		if not isinstance(context, dict):
			raise ValueError("Context must be a dictionary")

		attachments = []
		if template_name == "qr_email":
			qr_code_base64 = clean_and_decode_base64(qr_code_base64)
			if not qr_code_base64:
				frappe.log_error("Base64 decoding returned None", "Email Sending Error")
				raise ValueError("Failed to decode QR code Base64 string")

			attachments.append(
				{
					"fname": "qr_code.png",
					"fcontent": qr_code_base64,
				}
			)
		email_body = render_template(f"templates/email/{template_name}.html", context)
		try:
			print("sending email")
			# frappe.enqueue(
			# 	queue="long",
			# 	method=frappe.sendmail,
			# 	recipients=to_email,
			# 	subject=subject,
			# 	content=email_body,
			# 	attachments=attachments if attachments else None,
			# 	now=True,
			# )
			frappe.sendmail(
				recipients=to_email,
				subject=subject,
				content=email_body,
				attachments=attachments if attachments else None,
				now=True,
			)
			frappe.logger().info(f"Email sent successfully to {to_email}")
			print("mail send successfully")
		except Exception as e:
			print("------------------------> ",e)
	except Exception as e:
		print("---------->", e)
		frappe.log_error(frappe.get_traceback(), "Email Sending Error")
		# frappe.throw(f"Failed to send email: {str(e)}")


def clean_and_decode_base64(base64_string):
	if not base64_string:
		frappe.log_error("Empty Base64 string provided", "Base64 Decoding Error")
		return None
	if base64_string.startswith('"') and base64_string.endswith('"'):
		base64_string = base64_string[1:-1]
	if base64_string.startswith("data:image/png;base64,"):
		base64_string = base64_string.split(",", 1)[1]

	try:
		decoded = base64.b64decode(base64_string)
		if not decoded:
			frappe.log_error("Decoded Base64 resulted in empty bytes", "Base64 Decoding Error")
		return decoded
	except Exception as e:
		frappe.log_error(f"Base64 Decoding Failed: {str(e)}", "Base64 Decoding Error")
		return None
