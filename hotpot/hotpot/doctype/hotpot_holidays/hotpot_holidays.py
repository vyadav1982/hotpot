# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HotpotHolidays(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		date: DF.Date | None
		holiday_image: DF.AttachImage | None
		is_active: DF.Check
		location: DF.Link | None
		tag_line: DF.Data | None
		title: DF.Data | None
	# end: auto-generated types
	pass
