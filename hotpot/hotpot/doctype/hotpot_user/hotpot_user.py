# Copyright (c) 2024, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import random

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
			self.name = self.employee
		else:
			self.name = self.email

	def after_insert(self):
		try:
			if self.is_guest:
				return

			user = frappe.db.exists("User", {"email": self.email})
			if not user or user.enabled == 0:
				names = self.full_name.split(" ", 1)
				new_user = frappe.new_doc("User")
				user_type = "System User" if not self.is_guest else "Website User"
				new_user.update(
					{
						"email": self.email,
						"first_name": names[0],
						"username": self.employee_id,
						"last_name": names[1] if len(names) > 1 else "",
						"enabled": 1,
						"document_follow_notify": 0,
						"follow_liked_documents": 0,
						"send_welcome_email": 0,
						"user_type": user_type,
						"search_bar": 0,
						"notifications": 0,
						"list_sidebar": 0,
						"bulk_action": 0,
						"view_switcher": 0,
						"form_sidebar": 0,
						"timeline": 0,
						"dashboard": 0,
						"roles": [{"role": "Hotpot User"}],
						"default_app": "hotpot",
					}
				)

				try:
					new_user.append_roles("Hotpot User")
					new_user.flags.ignore_permissions = True
					new_user.flags.ignore_if_duplicate = True
					new_user.insert(ignore_permissions=True)
					new_user.reload()
				except Exception as e:
					print("🔥 Error during user insert:", e)
					frappe.log_error(frappe.get_traceback(), "User Creation Failed")
				try:
					user_name = frappe.get_value("Hotpot User", {"email": self.email}, "name")
				except Exception as e:
					print(e)
				user_doc = None
				if user_name:
					user_doc = frappe.get_doc("Hotpot User", user_name)

					if has_role("Hotpot Vendor"):
						user_doc.guest_of = user_doc.name
						user_doc.save(ignore_permissions=True)
						frappe.db.commit()
					if has_role("Hotpot User"):
						transaction_doc = frappe.new_doc("Hotpot Transaction History")
						transaction_doc.update(
							{
								"employee_id": user_doc.get("name"),
								"type": "Credit",
								"message": f"{self.coupon_count} tokens have been credited to your wallet",
								"title": "Token added by Admin",
								"amount": self.coupon_count,
							}
						)
						transaction_doc.insert()
				password = frappe.generate_hash(length=8)
				set_user_password(frappe.local.site, self.email, password, user_doc)
				frappe.db.commit()
			else:
				return {"status": "error", "message": "Duplicate user"}

		except frappe.ValidationError as e:
			frappe.log_error(f"User creation error: {e}")
			return {"status": "error", "message": "Failed to create user in Frappe"}

		except Exception:
			frappe.log_error(frappe.get_traceback(), "Unexpected error during user creation")
			return {"status": "error", "message": "An unexpected error occurred."}

	def on_update(self):
		try:
			frappe_user = frappe.get_doc("User", {"email": self.email})
			if frappe_user:
				names = self.full_name.split(" ", 1) if self.full_name else ["", ""]
				frappe_user.enabled = 1 if self.is_active == 1 and self.is_deleted == 0 else 0
				frappe_user.first_name = names[0] if names[0] else frappe_user.first_name
				frappe_user.last_name = names[1] if len(names) > 1 else frappe_user.last_name
				frappe_user.username = self.employee_id if self.employee_id else frappe_user.username

				frappe_user.roles = []
				frappe_user.save()
				frappe_user.append_roles(self.role)

				frappe_user.flags.ignore_permissions = True
				frappe_user.save()
				frappe.db.commit()

		except frappe.DoesNotExistError:
			frappe.log_error(f"User with email {self.email} does not exist.")
			return {"status": "error", "message": f"User {self.email} not found in Frappe"}
		except Exception:
			frappe.log_error(frappe.get_traceback(), "Unexpected error during user update")
			return {"status": "error", "message": "An unexpected error occurred during user update."}

	def on_trash(self):
		try:
			frappe_user = frappe.get_doc("User", {"email": self.email})
			if frappe_user:
				frappe_user.enabled = 0
				frappe_user.save(ignore_permissions=True)
				frappe.db.commit()
		except frappe.DoesNotExistError:
			frappe.log_error(f"User with email {self.email} does not exist.")
			return {"status": "error", "message": f"User {self.email} not found in Frappe"}
		except Exception:
			frappe.log_error(frappe.get_traceback(), "Unexpected error during user deletion")
			return {"status": "error", "message": "An unexpected error occurred during user deletion."}


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
			frappe.throw(f"User {user} does not exist")
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


def update_employee_to_hotpot(doc, method):
	if frappe.db.exists("Hotpot User", doc.name):
		hp_user = frappe.get_doc("Hotpot User", doc.name)
		hp_user.employee_id = doc.employee_number
		hp_user.full_name = doc.full_name
		hp_user.mobile_no = doc.cell_number if doc.cell_number else hp_user.mobile_no
		hp_user.email = doc.company_email if doc.company_email else hp_user.email
		hp_user.is_active = 1 if doc.status == "Active" else 0
		hp_user.is_deleted = 0 if doc.status == "Active" else 1
		hp_user.is_guest = 0
		hp_user.is_vendor = 0
		hp_user.is_server = 0
		hp_user.tag_id = doc.attendance_device_id
		hp_user.user = doc.user_id
		hp_user.location = doc.branch if doc.branch else hp_user.location
		hp_user.save(ignore_permissions=True)
	else:
		hp_user = frappe.new_doc("Hotpot User")
		hp_user.employee_id = doc.employee_number
		hp_user.full_name = doc.full_name
		hp_user.mobile_no = doc.cell_number
		hp_user.email = doc.company_email
		hp_user.is_active = 1 if doc.status == "Active" else 0
		hp_user.is_deleted = 0 if doc.status == "Active" else 1
		hp_user.is_guest = 0
		hp_user.is_vendor = 0
		hp_user.is_server = 0
		hp_user.tag_id = doc.attendance_device_id
		hp_user.user = doc.user_id
		hp_user.location = doc.branch
		hp_user.insert(ignore_permissions=True)


def remove_employee_from_hotpot(doc, method):
	if frappe.db.exists("Hotpot User", {"user": doc.name}):
		hp_user = frappe.get_doc("Hotpot User", {"user": doc.name})
		hp_user.is_deleted = 1
		hp_user.is_active = 0
		hp_user.save(ignore_permissions=True)
