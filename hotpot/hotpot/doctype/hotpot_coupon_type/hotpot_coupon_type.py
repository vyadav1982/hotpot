# Copyright (c) 2024, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HotpotCouponType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		end_hour: DF.Int
		is_active: DF.Check
		start_hour: DF.Int
		title: DF.Data
	# end: auto-generated types

	def validate(self):
		if self.start_hour > 2359:
			frappe.throw("Start hour cannot be greater than 2359.")
		elif self.end_hour <= self.start_hour:
			frappe.throw("End hour cannot be less than or equal to start hour.")
		elif self.end_hour > 2359:
			frappe.throw("End hour cannot be greater than 2359.")
		elif self.start_hour % 100 > 59 or self.end_hour % 100 > 59:
			frappe.throw("Minutes cannot be greater than 59")
