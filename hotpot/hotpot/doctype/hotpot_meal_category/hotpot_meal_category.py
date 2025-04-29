# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
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
		end_time: DF.Datetime
		is_active: DF.Check
		is_special: DF.Check
		lead_time: DF.Int
		meal_rate: DF.Int
		sequence: DF.Int
		start_time: DF.Datetime
		type: DF.Link
	# end: auto-generated types
	
	def validate(self):
		"""Validate that start and end times are on the same day and start is before end."""
		if self.start_time and self.end_time:
			if self.start_time.date() != self.end_time.date():
				frappe.throw("Start time and End time must be on the same date.")
			if self.start_time >= self.end_time:
				frappe.throw("Start time must be before End time.")


	

	def before_insert(self):
		if is_frappe_ui_request():
			self.start_time = get_utc_datetime_obj(self.start_time)
			self.end_time = get_utc_datetime_obj(self.end_time)
			
		
