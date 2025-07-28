# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from hotpot.utils.role_utils import get_dominant_role_for_current_user, has_any_of_role
from hotpot.utils.utc_time import *


def is_frappe_ui_request():
	referer = frappe.get_request_header("Referer")
	csrf_token = frappe.get_request_header("X-Frappe-CSRF-Token")
	user_agent = frappe.get_request_header("User-Agent")

	# Heuristics to detect Frappe UI
	if referer and "app" in referer:
		return True
	if csrf_token:
		return True
	if user_agent and "frappe" in user_agent.lower():
		return True

	return False


class HotpotMealCategory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		cancellation_time: DF.Int
		end_time: DF.Datetime | None
		end_time_local: DF.Time
		is_active: DF.Check
		lead_time: DF.Int
		max_meal_count: DF.Int
		meal_rate: DF.Int
		sequence: DF.Int
		start_time: DF.Datetime | None
		start_time_local: DF.Time
		type: DF.Link
	# end: auto-generated types

	def validate_dates(self):
		"""Ensure start_time is before end_time, skip if either is missing."""

		def parse_datetime_safe(dt):
			if not dt:
				return None
			if isinstance(dt, str):
				try:
					return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
				except ValueError:
					frappe.throw(f"Invalid datetime format: {dt}. Expected format: YYYY-MM-DD HH:MM:SS")
			return dt  # Already a datetime object

		start = parse_datetime_safe(self.start_time)
		end = parse_datetime_safe(self.end_time)

		# If either time is missing, don't validate
		if not start or not end:
			return

		# Check that start is before end
		if start >= end:
			frappe.throw("Start time must be earlier than End time.")

	def before_save(self):
		role = get_dominant_role_for_current_user()
		if role == "Hotpot User":
			return
		old_doc = self.get_doc_before_save()
		if old_doc and old_doc.start_time != self.start_time:
			self.validate_dates()
			self.start_time = get_utc_datetime_obj_v2(self.start_time)
		if old_doc and old_doc.end_time != self.end_time:
			self.validate_dates()
			self.end_time = get_utc_datetime_obj_v2(self.end_time)

	def before_insert(self):
		role = get_dominant_role_for_current_user()
		if role == "Hotpot User":
			return
		self.validate_dates()
		if is_frappe_ui_request():
			self.start_time = get_utc_datetime_obj_v2(self.start_time)
			self.end_time = get_utc_datetime_obj_v2(self.end_time)
