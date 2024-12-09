# Copyright (c) 2024, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
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

	pass
