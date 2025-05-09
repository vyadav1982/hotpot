# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from hotpot.utils.utc_time import *



def is_frappe_ui_request():
	try:
		referer = frappe.get_request_header("Referer")
		csrf_token = frappe.get_request_header("X-Frappe-CSRF-Token")
		user_agent = frappe.get_request_header("User-Agent")

		if referer and "app" in referer:
			return True
		if csrf_token:
			return True
		if user_agent and "frappe" in user_agent.lower():
			return True
	except Exception:
		pass
	return False


def has_permission(doc, ptype="read", user=None):
	if not user:
		user = frappe.session.user

	print(">>>> Checking Permission <<<<")
	print("User:", user)
	print("Doc:", doc)
	print("Doc Type:", doc.doctype)
	print("Command:", frappe.form_dict.get("cmd"))
	print("Request Path:", frappe.request.path)

	# Restrict Hotpot HR on desk only
	if ptype == "read" and user != "Administrator":
		roles = frappe.get_roles(user)
		if "Hotpot HR" in roles:
			# Detect desk access
			cmd = frappe.form_dict.get("cmd")
			if cmd and cmd.startswith("frappe.desk"):
				print(">>> Desk UI access blocked")
				return False

			if frappe.request.path and "/api/method/frappe.desk." in frappe.request.path:
				print(">>> Desk UI access blocked via path")
				return False

	return True


class HotpotMeal(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from hotpot.hotpot.doctype.hotpot_coupons.hotpot_coupons import HotpotCoupons
		from hotpot.hotpot.doctype.hotpot_meal_rating.hotpot_meal_rating import HotpotMealRating

		approval_id: DF.Link | None
		buffer_coupon_count: DF.Int
		cancellation_time: DF.Int
		category: DF.Link
		coupons: DF.Table[HotpotCoupons]
		end_time: DF.Datetime | None
		is_active: DF.Check
		is_deleted: DF.Check
		is_special: DF.Check
		lead_time: DF.Int
		meal_date: DF.Datetime
		meal_items: DF.Data
		meal_title: DF.Data
		meal_weight: DF.Int
		ratings: DF.Table[HotpotMealRating]
		repeat_days: DF.Data | None
		repeat_type: DF.Literal["once", "daily", "specific_days"]
		start_time: DF.Datetime | None
		vendor_id: DF.Link | None
	# end: auto-generated types

	def validate(self):
		"""Validate that start and end times are on the same day and start is before end."""
		if self.start_time and self.end_time:
			if isinstance(self.start_time, str):
				self.start_time = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")

			if isinstance(self.end_time, str):
				self.end_time = datetime.strptime(self.end_time, "%Y-%m-%d %H:%M:%S")

			if self.start_time.date() != self.end_time.date():
				frappe.throw("Start time and End time must be on the same date.")
			if self.start_time >= self.end_time:
				frappe.throw("Start time must be before End time.")
	# def before_save(self):
	# 	roles = frappe.get_roles()
	# 	if "Hotpot Vendor" not in roles:
	# 		frappe.throw("Vendor Id is mandatory.")

	def before_insert(self):
		if is_frappe_ui_request() or frappe.flags.in_import:
			if self.start_time :
				if isinstance(self.start_time, datetime):
		   			self.start_time = self.start_time.strftime('%Y-%m-%d %H:%M:%S')
				self.start_time = get_utc_datetime_obj(self.start_time)
			if self.end_time :
				if isinstance(self.end_time, datetime):
		   			self.end_time = self.end_time.strftime('%Y-%m-%d %H:%M:%S')
				self.end_time = get_utc_datetime_obj(self.end_time)
			if not self.start_time and not self.end_time:
				category_doc = frappe.get_doc("Hotpot Meal Category", self.category)
				self.start_time =category_doc.start_time
				self.end_time = category_doc.end_time
				self.is_active = 1
				self.lead_time = category_doc.lead_time
				self.cancellation_time = category_doc.cancellation_time
				self.is_special = category_doc.is_special
				self.meal_weight = category_doc.meal_rate
			roles = frappe.get_roles()
			if "Hotpot Vendor" in roles:
				vendor_id = frappe.db.get_value("Hotpot User", {"email": frappe.session.user}, "name")
				self.vendor_id = vendor_id
