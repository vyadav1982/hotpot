# Copyright (c) 2024, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HotpotUser(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		breakfast: DF.Check
		dinner: DF.Check
		email: DF.Data | None
		employee_id: DF.Data
		employee_name: DF.Data | None
		evening_snack: DF.Check
		is_active: DF.Check
		lunch: DF.Check
		role: DF.Literal["Hotpot User", "Hotpot Server"]
	# end: auto-generated types

	pass
