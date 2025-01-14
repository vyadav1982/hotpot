# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HotpotMenu(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		active: DF.Check
		breakfast: DF.Data | None
		breakfast_special: DF.Check
		day: DF.Data | None
		dinner: DF.Data | None
		dinner_special: DF.Check
		luch: DF.Data | None
		lunch_special: DF.Check
		snacks: DF.Data | None
		snacks_special: DF.Check
		special: DF.Check
	# end: auto-generated types
	pass
