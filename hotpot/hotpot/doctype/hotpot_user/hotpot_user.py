# Copyright (c) 2024, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import random
from hotpot.utils.email import * 

def send_password_email(to_email, user_doc, password):
	email_subject = f"Congrats, { user_doc.employee_name }! You’re Now Part of the Hotpot Club 🍽️"
	context = {
		"user_data": user_doc,
		"password": password,
		# "login_url": frappe.utils.get_url('app/login')
		"login_url": "https://hotpot.bytepanda.in/app"
	}
	send_email("initial_password", to_email, context, email_subject)
def set_user_password(site, user, password,user_doc, logout_all_sessions=False):
	from frappe.utils.password import update_password

	if not password:
		raise ValueError("Password cannot be empty.")
	try:
		if not frappe.db.exists("User", user):
			frappe.throw(f"User {user} does not exist")
			return

		update_password(user=user, pwd=password, logout_all_sessions=logout_all_sessions)
		frappe.db.commit()
		send_password_email(user,user_doc,password)
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Error setting password")
		frappe.db.rollback()
		frappe.throw(str(e))


class HotpotUser(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		approval_id: DF.JSON | None
		coupon_count: DF.Int
		date_of_birth: DF.Date | None
		date_of_joining: DF.Date | None
		department: DF.Data | None
		email: DF.Data
		employee_id: DF.Data
		employee_name: DF.Data | None
		fcm_token: DF.Text | None
		guest_of: DF.Link | None
		is_active: DF.Check
		is_deleted: DF.Check
		is_guest: DF.Check
		is_server: DF.Check
		is_vendor: DF.Check
		latitude: DF.Data | None
		location: DF.Data | None
		longitude: DF.Data | None
		mobile_no: DF.Phone
		password: DF.Data | None
		role: DF.Link | None
		tag_id: DF.Data | None
		timezone: DF.Data | None
	# end: auto-generated types


	def before_save(self):
		if self.role=="Hotpot Server" and self.guest_of=="":
			frappe.throw("The field 'guest_of' is mandatory for Hotpot Server.")

	def before_insert(self):
		if self.role == "Hotpot Vendor":
			self.is_vendor = 1
		if self.role == "Hotpot Server":
			self.is_server = 1

	def after_insert(self):
		try:
			user = frappe.db.exists("User", {"email": self.email})
			if not user or user.enabled==0:
				names = self.employee_name.split(" ", 1)
				new_user = frappe.new_doc("User")
				role = self.role
				user_type = "System User" if role in ["Hotpot HR", "Hotpot Finance", "Hotpot Admin","Hotpot Vendor"] else "Website User"
				new_user.update({
					"email": self.email,
					"first_name": names[0],
					"username": self.employee_id,
					"last_name": names[1] if len(names) > 1 else "",
					"enabled": 1,
					"document_follow_notify": 0,
					"follow_liked_documents": 0,
					"send_welcome_email": 0,
					"user_type":user_type,
					"search_bar":0,
					"notifications":0,
					"list_sidebar":0,
					"bulk_action":0,
					"view_switcher":0,
					"form_sidebar":0,
					"timeline":0,
					"dashboard":0,
					"module_profile": "Hotpot",
					"roles": [{"role": self.role}],
					"default_app": "hotpot",
				})
				if role == "Hotpot Admin":
					new_user.update({
				# 		"notifications": 1,
				# 		"list_sidebar": 1,
				# 		"bulk_action": 1,
				# 		"view_switcher": 1,
				# 		"form_sidebar": 1,
						"timeline": 1,
				# 		"dashboard": 1,
					})
				if not frappe.db.exists("Role", self.role):
					raise ValueError(f"Role {self.role} does not exist.")
				try: 
					new_user.append_roles(self.role)
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
				user_doc=None
				if user_name:
					user_doc = frappe.get_doc("Hotpot User", user_name)

					if user_doc.get("role") == "Hotpot Vendor":
						user_doc.guest_of = user_doc.name
						user_doc.save(ignore_permissions=True)

						# meals = ["Pasta", "Burger", "Sushi", "Tacos", "Pizza", "Salad", "Biryani", "Steak", "Sandwich", "Noodles",
						# 		"Soup", "Dosa", "Pancakes", "Omelette", "Grilled Chicken", "Shawarma", "Fried Rice", "Ramen", "BBQ Ribs",
						# 		"Curry", "Lasagna", "Burrito", "Fish and Chips", "Momo", "Dim Sum"]
						# meal_items = random.sample(meals, 5)

						# for meal in meal_items:
						# 	meal_doc = frappe.get_doc({
						# 		"doctype": "Hotpot Meal Items",
						# 		"item_name": meal,
						# 		"vendor_id": user_doc.get("name")
						# 	})
						# 	meal_doc.insert(ignore_permissions=True)

						frappe.db.commit()
					if user_doc.get("role") == "Hotpot User":
						transaction_doc = frappe.new_doc("Hotpot Transaction History")
						transaction_doc.update(
							{
								"employee_id": user_doc.get("name"),
								"type": "Credit",
								"message": f"{self.coupon_count} tokens have been credited to your wallet",
								"title": "Token added by Admin",
								"amount": self.coupon_count
							}
						)
						transaction_doc.insert()
				password = frappe.generate_hash(length=8)
				set_user_password(frappe.local.site, self.email,password,user_doc)
				frappe.db.commit()	
			else:
				return {
					"status": "error",
					"message": "Duplicate user"
				}

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
				names = self.employee_name.split(" ", 1) if self.employee_name else ["", ""]
				frappe_user.enabled = 1 if self.is_active == 1 and self.is_deleted == 0 else 0
				frappe_user.first_name = names[0] if names[0] else frappe_user.first_name
				frappe_user.last_name = names[1] if len(names) > 1 else frappe_user.last_name
				frappe_user.username = self.employee_id if self.employee_id else frappe_user.username

				# frappe_user.module_profile = "Hotpot Admin" if self.role == "Hotpot Admin" else "Hotpot"
				frappe_user.module_profile = "Hotpot"
				frappe_user.roles = []  
				frappe_user.save()
				frappe_user.append_roles(self.role)

				if self.role == "Hotpot Admin":
					frappe_user.update({
						"bulk_action": 0,
						"timeline": 1,
					})

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


