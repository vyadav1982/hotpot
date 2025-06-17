# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HotpotConfigurations(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		allow_free_meal_for_outer_location: DF.Check
		allow_meal_on_sunday: DF.Check
		can_generate_for_guest: DF.Check
		discount: DF.Percent
		free_birthday_meal: DF.Check
		free_joining_day_meal: DF.Check
		initial_tokens: DF.Int
	# end: auto-generated types

	pass
