# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from datetime import datetime, timedelta

import frappe
from frappe import _
from frappe.model.document import Document

from hotpot.utils.role_utils import get_dominant_role_for_current_user, has_any_of_role
from hotpot.utils.utc_time import *


class HotpotMeal(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from hotpot.hotpot.doctype.hotpot_coupons.hotpot_coupons import HotpotCoupons
		from hotpot.hotpot.doctype.hotpot_meal_menu_items.hotpot_meal_menu_items import HotpotMealMenuItems
		from hotpot.hotpot.doctype.hotpot_meal_rating.hotpot_meal_rating import HotpotMealRating

		actual_meal_rate: DF.Int
		approval_id: DF.Link | None
		buffer_count_enabled: DF.Check
		buffer_coupon_count: DF.Int
		cancellation_time: DF.Int
		category: DF.Link
		coupons: DF.Table[HotpotCoupons]
		end_time: DF.Datetime
		is_active: DF.Check
		is_deleted: DF.Check
		is_special: DF.Check
		lead_time: DF.Int
		max_meal_count: DF.Int
		meal_date: DF.Datetime
		meal_items: DF.Data
		meal_title: DF.Data
		meal_weight: DF.Int
		menu_items: DF.Table[HotpotMealMenuItems]
		ratings: DF.Table[HotpotMealRating]
		remaining_coupon_count: DF.Int
		repeat_days: DF.Data | None
		repeat_type: DF.Literal["once", "daily", "specific_days"]
		start_time: DF.Datetime
		vendor_id: DF.Link
	# end: auto-generated types

	def validate_dates(self):
		"""Validate that start and end times are on the same day and start is before end."""

		if not self.is_new():
			# Get the document state before the current save
			old_doc = self.get_doc_before_save()
			if old_doc.buffer_coupon_count > self.buffer_coupon_count:
				frappe.throw("Buffer coupon count cannot be decreased.")

		if self.start_time and self.end_time:
			if isinstance(self.start_time, str):
				self.start_time = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
			elif isinstance(self.start_time, timedelta):
				# Convert timedelta to datetime using today's date
				today = datetime.now().date()
				self.start_time = datetime.combine(today, (datetime.min + self.start_time).time())

			if isinstance(self.end_time, str):
				self.end_time = datetime.strptime(self.end_time, "%Y-%m-%d %H:%M:%S")
			elif isinstance(self.end_time, timedelta):
				# Convert timedelta to datetime using today's date
				today = datetime.now().date()
				self.end_time = datetime.combine(today, (datetime.min + self.end_time).time())

			if self.start_time.date() != self.end_time.date():
				frappe.throw("Start time and End time must be on the same date.")
			if self.start_time >= self.end_time:
				frappe.throw("Start time must be before End time.")

	def before_save(self):
		role = get_dominant_role_for_current_user()
		if role == "Hotpot User":
			return
		if self.meal_date and self.category:
			duplicate_exists = frappe.db.exists(
				"Hotpot Meal",
				{
					"meal_date": self.meal_date,
					"category": self.category,
					"name": ["!=", self.name],
					"vendor_id": self.vendor_id,
				},
			)
			if duplicate_exists:
				frappe.throw(f"A meal with category '{self.category}' already exists on {self.meal_date}.")
			
			child_record = frappe.get_list(
				"Hotpot Category Prices",
				filters={
					'parent': self.vendor_id,
					'parentfield': "category_prices",
					'category':self.category
				},
				fields=['name'],
			)
			prices = frappe.get_doc("Hotpot Category Prices", child_record[0].name) if child_record else None
			if prices:
				self.meal_weight = prices.discounted_rate
				self.actual_meal_rate = prices.actual_rate
			else:
				category_doc = frappe.get_doc("Hotpot Meal Category", self.category)
				self.meal_weight = category_doc.meal_rate
				self.actual_meal_rate = category_doc.meal_rate
		if is_frappe_ui_request() or frappe.flags.in_import:
			self.menu_items = []
			if self.meal_items:
				if isinstance(self.meal_items, str):
					raw_items = self.meal_items.split(",")
				elif isinstance(self.meal_items, list):
					raw_items = self.meal_items
				else:
					frappe.throw("meal_items must be a comma-separated string or a list of item names.")

				item_list = list(
					{item.strip().lower() for item in raw_items if isinstance(item, str) and item.strip()}
				)

				for item_name in item_list:
					menu_item = frappe.get_value(
						"Hotpot Meal Items", {"vendor_id": self.vendor_id, "item_name": item_name}, "name"
					)
					if menu_item:
						self.append("menu_items", {"meal_item": menu_item})
					else:
						frappe.throw(f"Meal Item '{item_name}' not found for vendor '{self.vendor_id}'.")

	def before_insert(self):
		role = get_dominant_role_for_current_user()
		if role == "Hotpot User":
			return
		self.validate_dates()
		existing = frappe.db.exists(
			"Hotpot Meal",
			{"meal_date": self.meal_date, "category": self.category, "vendor_id": self.vendor_id},
		)
		if existing:
			frappe.throw(
				_(
					"A meal for category '{0}' already exists on {1}. Only one entry per category per date is allowed."
				).format(self.category, self.meal_date)
			)
		vendor = None
		if is_frappe_ui_request() or frappe.flags.in_import:
			category_doc = frappe.get_doc("Hotpot Meal Category", self.category)
			self.start_time = category_doc.start_time
			self.end_time = category_doc.end_time
			self.is_active = 1
			self.remaining_coupon_count = self.buffer_coupon_count
			self.lead_time = category_doc.lead_time
			self.cancellation_time = category_doc.cancellation_time
			self.meal_weight = category_doc.meal_rate
			self.actual_meal_rate=category_doc.meal_rate
			self.max_meal_count = category_doc.max_meal_count
			roles = frappe.get_roles()
			if "Hotpot Vendor" in roles:
				vendor_id = frappe.db.get_value("Hotpot User", {"email": frappe.session.user}, "name")
				if self.vendor_id is None:
					self.vendor_id = vendor_id
					vendor = self.vendor_id
		child_record = frappe.get_list(
			"Hotpot Category Prices",
			filters={
				'parent': vendor,
				'parentfield': "category_prices",
				'category':self.category
			},
			fields=['name', 'actual_rate', 'discounted_rate'],
		)
		if child_record:
			self.meal_weight = child_record[0].discounted_rate
			self.actual_meal_rate = child_record[0].actual_rate

		meal_date = get_local_datetime_obj(self.meal_date)
		current_datetime = get_local_datetime_obj(datetime.utcnow())

		if meal_date.date() == current_datetime.date():
			local_time = get_local_datetime_obj(datetime.utcnow())

			lead_time_delta = timedelta(hours=float(self.lead_time))
			ready_time = local_time + lead_time_delta
			start_time_local = get_local_datetime_obj(self.start_time)
			start_time_today = datetime.combine(meal_date.date(), start_time_local.time())

			time_difference = (start_time_today - ready_time).total_seconds()

			if time_difference < 0:
				frappe.throw(
					_(
						"Meal ({0}) on {1} cannot be created. Lead time ({2} hours) results in time {3}, which is past the start time {4}."
					).format(
						self.meal_title,
						meal_date.strftime("%d %b").lstrip("0"),
						self.lead_time,
						ready_time.strftime("%I:%M %p"),
						(get_local_datetime_obj(self.start_time)).strftime("%I:%M %p"),
					)
				)


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

	# Restrict Hotpot HR on desk only
	if ptype == "read" and user != "Administrator":
		roles = frappe.get_roles(user)
		if "Hotpot HR" in roles:
			# Detect desk access
			cmd = frappe.form_dict.get("cmd")
			if cmd and cmd.startswith("frappe.desk"):
				return False

			if frappe.request.path and "/api/method/frappe.desk." in frappe.request.path:
				return False

	return True
