# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MealMenuItems(Document):
	# begin: auto-generated types
	# ruff: noqa

	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		meal_item: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# ruff: noqa
	# end: auto-generated types

	pass
