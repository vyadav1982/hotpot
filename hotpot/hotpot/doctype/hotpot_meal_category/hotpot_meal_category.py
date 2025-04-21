# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HotpotMealCategory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		cancellation_time: DF.Int
		end_time: DF.Datetime | None
		is_active: DF.Check
		lead_time: DF.Int
		order: DF.Int
		start_time: DF.Datetime | None
		type: DF.Link | None
	# end: auto-generated types
	pass
