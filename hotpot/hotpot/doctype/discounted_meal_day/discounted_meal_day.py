# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DiscountedMealDay(Document):
	# begin: auto-generated types
	# ruff: noqa

	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.Data
		discount: DF.Percent
		discount_date: DF.Date
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# ruff: noqa
	# end: auto-generated types

	pass
