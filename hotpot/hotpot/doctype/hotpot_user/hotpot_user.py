# Copyright (c) 2024, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import random
from datetime import datetime
import pytz

import frappe
from frappe.model.document import Document

from hotpot.utils.email import *
from hotpot.utils.role_utils import has_role


class HotpotUser(Document):
	# begin: auto-generated types
	# ruff: noqa

	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from hotpot.hotpot.doctype.discounted_meal_day.discounted_meal_day import DiscountedMealDay

		approval_id: DF.JSON | None
		coupon_count: DF.Int
		discount: DF.Percent
		discounted_meal_days: DF.Table[DiscountedMealDay]
		email: DF.Data | None
		employee: DF.Link | None
		employee_id: DF.Data | None
		fcm_token: DF.Text | None
		full_name: DF.Data
		guest_of: DF.Link | None
		is_active: DF.Check
		is_deleted: DF.Check
		is_employee: DF.Check
		is_guest: DF.Check
		is_server: DF.Check
		is_vendor: DF.Check
		latitude: DF.Float
		location: DF.Link
		longitude: DF.Float
		mobile_no: DF.Phone | None
		tag_id: DF.Data | None
		user: DF.Link | None
	# ruff: noqa
	# end: auto-generated types

	def autoname(self):
		if self.is_employee:
			self.name = self.employee_id
		else:
			self.name = self.email

	def on_update(self):
		try:
			frappe_user = frappe.get_doc("User", {"email": self.email})
			emp_user = frappe.get_doc("Employee", {"employee_number": self.employee_id})
			if emp_user and emp_user.user_id is None:
				emp_user.user_id = self.email
				emp_user.save(ignore_permissions=True)
				frappe.db.commit()

			if frappe_user and not frappe.flags.in_import:
				# names = self.full_name.split(" ", 1) if self.full_name else ["", ""]
				frappe_user.enabled = 1 if self.is_active == 1 and self.is_deleted == 0 else 0
				# frappe_user.first_name = names[0] if names[0] else frappe_user.first_name
				# frappe_user.last_name = names[1] if len(names) > 1 else frappe_user.last_name
				# frappe_user.username = self.employee_id if self.employee_id else frappe_user.username

				frappe_user.save()

				# frappe_user.flags.ignore_permissions = True
				# frappe_user.flags.update_from_hotpot = True
				# frappe_user.save()
				frappe.db.commit()
			# print("No Need for Updating user in Frappe")

		except frappe.DoesNotExistError:
			frappe.log_error(f"User with email {self.email} does not exist.")
			return {"status": "error", "message": f"User {self.email} not found in Frappe"}
		except Exception:
			frappe.log_error(frappe.get_traceback(), "Unexpected error during user update")
			return {"status": "error", "message": "An unexpected error occurred during user update."}


def send_password_email(to_email, user_doc, password):
	email_subject = f"Congrats, {user_doc.full_name}! You’re Now Part of the Hotpot Club 🍽️"
	context = {
		"user_data": user_doc,
		"password": password,
		# "login_url": frappe.utils.get_url('app/login')
		"login_url": "https://hotpot.bytepanda.in/app",
	}
	send_email("initial_password", to_email, context, email_subject)


def set_user_password(site, user, password, user_doc, logout_all_sessions=False):
	from frappe.utils.password import update_password

	if not password:
		raise ValueError("Password cannot be empty.")
	try:
		if not frappe.db.exists("User", user):
			# frappe.throw(f"User {user} does not exist")
			return

		update_password(user=user, pwd=password, logout_all_sessions=logout_all_sessions)
		frappe.db.commit()
		send_password_email(user, user_doc, password)
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Error setting password")
		frappe.db.rollback()
		frappe.throw(str(e))


def add_user_to_hotpot(doc, method):
	# check if the hotpot user already exists
	# if not add to hotpot user
	pass


def validate_employee(doc, method):
	doc.create_user_permission = 0


import frappe


def validate_user(doc, method):
	user_roles = [d.role for d in doc.roles]

	if any(role.startswith("Hotpot ") for role in user_roles) and not has_role("Administrator"):
		doc.document_follow_notify = 0
		doc.follow_liked_documents = 0
		doc.search_bar = 0
		doc.notifications = 0
		doc.list_sidebar = 0
		doc.bulk_action = 0
		doc.view_switcher = 0
		doc.form_sidebar = 0
		doc.timeline = 0
		doc.dashboard = 0
		doc.bulk_actions = 0


def update_employee_to_hotpot(doc, method):
	if frappe.db.exists("Hotpot User", doc.name):
		hp_user = frappe.get_doc("Hotpot User", doc.name)
		hp_user.employee_id = doc.employee_number
		parts = [
			(doc.first_name or "").strip(),
			(doc.middle_name or "").strip(),
			(doc.last_name or "").strip(),
		]
		hp_user.full_name = " ".join(part for part in parts if part)
		hp_user.mobile_no = doc.cell_number if doc.cell_number else hp_user.mobile_no
		hp_user.email = doc.user_id if doc.user_id else doc.company_email
		hp_user.is_active = 1 if doc.status == "Active" else 0
		hp_user.is_deleted = 0 if doc.status == "Active" else 1
		hp_user.is_guest = 0
		hp_user.is_vendor = 0
		hp_user.is_server = 0
		hp_user.tag_id = doc.attendance_device_id
		hp_user.user = doc.company_email
		hp_user.location = doc.branch if doc.branch else hp_user.location
		hp_user.save(ignore_permissions=True)
		frappe.db.commit()
	else:
		create_user(doc)
		hp_user = frappe.new_doc("Hotpot User")
		hp_user.employee_id = doc.employee_number
		parts = [
			(doc.first_name or "").strip(),
			(doc.middle_name or "").strip(),
			(doc.last_name or "").strip(),
		]
		hp_user.full_name = " ".join(part for part in parts if part)
		hp_user.mobile_no = doc.cell_number
		hp_user.email = doc.company_email
		hp_user.is_active = 1 if doc.status == "Active" else 0
		hp_user.is_deleted = 0 if doc.status == "Active" else 1
		hp_user.is_guest = 0
		hp_user.is_vendor = 0
		hp_user.is_server = 0
		hp_user.tag_id = doc.attendance_device_id
		hp_user.user = doc.company_email
		hp_user.location = doc.branch
		hp_user.employee = doc.employee_number
		password = frappe.generate_hash(length=8)
		set_user_password(frappe.local.site, doc.company_email, password, hp_user)
		hotpot_config = frappe.get_single("Hotpot Configurations")
		hp_user.coupon_count = hotpot_config.get("initial_tokens")
		hp_user.insert(ignore_permissions=True)
		transaction_doc = frappe.new_doc("Hotpot Transaction History")
		india = pytz.timezone("Asia/Kolkata")
		now = datetime.now(india)
		transaction_doc.update(
			{
				"employee_id": doc.employee_number,
				"type": "Credit",
				"message": f"🎉 You've received your initial credit of {hotpot_config.get('initial_tokens')} tokens on {now.strftime('%d %b %Y')} by the Admin.",
				"title": "initial Credit",
				"amount": hotpot_config.get("initial_tokens"),
				"meal": None,
				"coupon": None,
			}
		)
		transaction_doc.insert(ignore_permissions=True)
		frappe.db.commit()


def remove_employee_from_hotpot(doc, method):
	if frappe.db.exists("Hotpot User", {"user": doc.name}):
		hp_user = frappe.get_doc("Hotpot User", {"user": doc.name})
		hp_user.is_deleted = 1
		hp_user.is_active = 0
		hp_user.save(ignore_permissions=True)
		frappe.db.commit()


def create_user(doc):
	try:
		if not doc.company_email:
			frappe.throw("Company email is missing.")

		if not frappe.db.exists("User", {"email": doc.company_email}):
			user = frappe.new_doc("User")
			user.email = doc.company_email
			user.first_name = doc.first_name or "First"
			user.last_name = doc.last_name or ""
			user.enabled = 1 if doc.status == "Active" else 0
			user.send_welcome_email = 1
			user.append("roles", {"role": "Hotpot User"})
			user.flags.ignore_permissions = True
			user.insert()
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Error in create_user")


# def update_employee(doc):
# 	if frappe.db.exists("Employee", doc.name):
# 		emp = frappe.get_doc("Employee", doc.name)
# 		emp.user_id = doc.company_email
# 		emp.save(ignore_permissions=True)
# 		frappe.db.commit()
