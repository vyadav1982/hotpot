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

		approval_id: DF.Link | None
		buffer_coupon_count: DF.Int
		cancellation_time: DF.Int
		coupons: DF.Table[HotpotCoupons]
		end_time: DF.Datetime | None
		is_active: DF.Check
		is_special: DF.Check
		lead_time: DF.Int
		meal_date: DF.Datetime | None
		meal_items: DF.Data | None
		meal_title: DF.Data | None
		meal_weight: DF.Int
		ratings: DF.Table[HotpotMealRating]
		repeat_days: DF.Data | None
		repeat_type: DF.Literal["once", "daily", "specific_days"]
		start_time: DF.Datetime | None
		vendor_id: DF.Link | None
	# end: auto-generated types

	pass
