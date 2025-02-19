# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HotpotBanner(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		created_by: DF.Link | None
		description: DF.SmallText | None
		end_date: DF.Date | None
		image: DF.Attach | None
		intent: DF.Literal["LinkClickable", "OpenModal", "NotClickable"]
		is_active: DF.Check
		link: DF.Data | None
		priority: DF.Int
		start_date: DF.Datetime | None
		text: DF.Data | None
		title: DF.Data | None
	# end: auto-generated types
	pass
