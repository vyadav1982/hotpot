# Copyright (c) 2024, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HotpotCoupon(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		coupon_date: DF.Date | None
		coupon_time: DF.Time | None
		emoji_reaction: DF.Data | None
		employee_id: DF.Link
		feedback: DF.Data | None
		served_by: DF.Link | None
		status: DF.Literal["Upcoming", "Expired", "Consumed"]
		title: DF.Literal["Breakfast", "Lunch", "Evening Snack", "Dinner"]
	# end: auto-generated types

	pass
