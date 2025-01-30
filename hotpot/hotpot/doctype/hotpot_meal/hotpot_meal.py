# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HotpotMeal(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from hotpot.hotpot.doctype.hotpot_coupons.hotpot_coupons import HotpotCoupons
		from hotpot.hotpot.doctype.hotpot_meal_rating.hotpot_meal_rating import HotpotMealRating

		buffer_coupon_count: DF.Int
		coupons: DF.Table[HotpotCoupons]
		day: DF.Data | None
		end_time: DF.Data | None
		is_active: DF.Check
		meal_date: DF.Date | None
		meal_items: DF.Data | None
		meal_title: DF.Data | None
		ratings: DF.Table[HotpotMealRating]
		start_time: DF.Data | None
		vendor_id: DF.Data | None
	# end: auto-generated types
	pass
