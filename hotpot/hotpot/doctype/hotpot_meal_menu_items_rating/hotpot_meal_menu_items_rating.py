# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HotpotMealMenuItemsRating(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		coupon: DF.Link
		employee: DF.Link
		meal: DF.Link
		meal_item: DF.Link
		rating: DF.Rating
		review: DF.SmallText | None
	# end: auto-generated types
	pass
