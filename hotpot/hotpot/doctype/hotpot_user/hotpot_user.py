# Copyright (c) 2024, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import random
from datetime import datetime
import pytz

import frappe
from frappe.model.document import Document

from hotpot.utils.email import *
from hotpot.utils.utc_time import *
from hotpot.utils.role_utils import has_role
from frappe.core.doctype.version.version import get_diff
from frappe.utils import getdate, nowdate
from hotpot.api.meal import get_meals_internal
from hotpot.utils.send_fcm import *



class HotpotUser(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from hotpot.hotpot.doctype.discounted_meal_day.discounted_meal_day import DiscountedMealDay
		from hotpot.hotpot.doctype.hotpot_category_prices.hotpot_category_prices import HotpotCategoryPrices

		approval_id: DF.JSON | None
		category_prices: DF.Table[HotpotCategoryPrices]
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
	# end: auto-generated types

	def autoname(self):
		if self.is_employee:
			self.name = self.employee_id
		else:
			self.name = self.email

	def on_update(self):
		try:
			frappe_user = frappe.get_doc("User", {"email": self.email})
			emp_user = None
			if self.is_vendor:
				update_meals(self)
			if self.is_employee:
				emp_user = frappe.get_doc("Employee", {"employee_number": self.employee_id})
			if emp_user and emp_user.user_id is None:
				frappe.db.set_value("Employee", emp_user.name, "user_id", self.email)

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
			user.send_welcome_email = 0
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



def update_meals(self):
	# if the user is not a vendor stop here ✋
	if not self.is_vendor:
		return

	# get previous details
	old_doc = self.get_doc_before_save()

	# preparing the old data json 🙆🏻‍♂️
	old_data_map = {
		row.category: {
			"applicable_from": getdate(row.applicable_from) if row.applicable_from else None,
			"discounted_rate": row.discounted_rate
		}
		for row in getattr(old_doc, "category_prices", [])
	}

	today = getdate(nowdate())
	changed_categories = []

	for row in self.category_prices:
		category = row.category
		new_date = getdate(row.applicable_from) if row.applicable_from else None
		new_rate = row.discounted_rate

		old_data = old_data_map.get(category, {})
		old_date = old_data.get("applicable_from")
		old_rate = old_data.get("discounted_rate")

		date_changed = new_date != old_date
		rate_changed = new_rate != old_rate

		if (date_changed and new_date == today) or (new_date == today and rate_changed):
			changed_categories.append(category)

	if not changed_categories:
		return

	local_time_now = get_local_time_now()
	start_date = get_utc_datetime_obj(f"{today} {local_time_now}")

	# today_str = today.strftime("%Y-%m-%d")
	# todays_meal = get_meals_internal(today_str,self.name)
	# print()
	# todays_categories = set(meal.get("category") for meal in todays_meal)

	# categories_to_update = list(set(changed_categories) & todays_categories)
	# print("checkpoint111")
	# if not categories_to_update:
	# 	return

	# getting the meals of the vendor 🍝
	categories_sql = ', '.join(f"'{cat}'" for cat in changed_categories)

	query = f"""
		SELECT name, category, meal_title, meal_date
		FROM `tabHotpot Meal`
		WHERE vendor_id = %s
		AND is_active = 1
		AND category IN ({categories_sql})
		AND meal_date >= %s
	"""
	meals = frappe.db.sql(query, (self.name, start_date), as_dict=True)

	discounted_rate_map = {
		row.category: row.discounted_rate for row in self.category_prices
	}

	for idx, meal in enumerate(meals, 1):
		try:
			meal_doc = frappe.get_doc("Hotpot Meal", meal.name)
			meal_date = get_local_datetime_obj(meal_doc.meal_date)
			if getdate(meal_date)==today and get_local_datetime_obj(meal_doc.start_time).time() <= get_local_datetime_obj(datetime.utcnow().replace(tzinfo=None)).time():
				continue

			coupons = meal_doc.get("coupons")
			for coupon in coupons:
				coupon_doc = frappe.get_doc("Hotpot Coupons", coupon.name)
				if coupon_doc.coupon_status != "1":
					continue
				prev_weight = coupon_doc.coupon_weight
				if not prev_weight:
					continue
				new_weight = discounted_rate_map.get(meal.category)
				user_doc = frappe.get_doc("Hotpot User", coupon.employee_id)

				if prev_weight != new_weight:
					coupon_doc.coupon_weight = new_weight

					transaction_doc = frappe.new_doc("Hotpot Transaction History")

					#  if the meal price is dropped 🤑
					if prev_weight > new_weight:
						amount_changed = prev_weight - new_weight
						user_doc.coupon_count += amount_changed
						transaction_doc.update({
							"employee_id": user_doc.get("name"),
							"type": "Credit",
							"message": f"{amount_changed} tokens refunded as meal cost for '{meal_doc.meal_title}' dropped. 💸",
							"title": "Meal Cost Refund",
							"amount": amount_changed,
							"meal": meal_doc.name,
							"coupon": coupon.get("name"),
							"coupon_status": "1",
							"category": meal_doc.get("category"),
						})
						message = f"Sweet deal! 😄 '{meal_doc.meal_title}' just got cheaper!"
						message2 = f"Refund alert! 💸 You got back {amount_changed} tokens. Check your wallet!"

					#  if the meal price is increased 🥺
					else:
						amount_changed = new_weight - prev_weight
						user_doc.coupon_count -= amount_changed
						transaction_doc.update({
							"employee_id": user_doc.get("name"),
							"type": "Debit",
							"message": f"{amount_changed} tokens deducted as meal cost for '{meal_doc.meal_title}' increased. 💰",
							"title": "Meal Cost Update",
							"amount": amount_changed,
							"meal": meal_doc.name,
							"coupon": coupon.get("name"),
							"coupon_status": "1",
							"category": meal_doc.get("category"),
						})
						message = f"Price bump! 😕 '{meal_doc.meal_title}' costs a bit more now."
						message2 = f"{amount_changed} tokens deducted 💰. Check your wallet for updates!"

					transaction_doc.insert()
					coupon_doc.save(ignore_permissions=True)
					user_doc.save(ignore_permissions=True)

					# sending fcm notification 📲
					if user_doc.fcm_token:
						try:
							send_notification_by_token(
								user_doc.fcm_token,
								"Meal Update Alert",
								message,
								date=meal_doc.meal_date,
								doc_id=meal_doc.name,
								text="meals",
							)
							send_notification_by_token(
								user_doc.fcm_token,
								"Wallet Update 💼",
								message2,
								doc_id=transaction_doc.name,
								text="transactions",
							)
						except Exception:
								frappe.log_error(
									frappe.get_traceback(),
									f"Failed to send update notification to {user_doc.name}",
								)
			frappe.db.commit()
			for row in self.category_prices:
				if row.category == meal_doc.category :
					frappe.set_value("Hotpot Meal",meal_doc.name,'meal_weight',row.discounted_rate)
					frappe.set_value("Hotpot Meal",meal_doc.name,'actual_meal_rate',row.actual_rate)
					break
			frappe.db.commit()

			# displaying progress bar 🚀
			frappe.publish_progress(
				float(idx) * 100 / len(meals),
				title="Updating Meals",
				description=f"{idx}/{len(meals)} Meals Updated"
			)
		except Exception:
			frappe.log_error(frappe.get_traceback(), f"Failed to update meal {meal.name}")
