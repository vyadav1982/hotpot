# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HotpotCoupons(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		coupon_date: DF.Date | None
		coupon_status: DF.Literal["-1", "0", "1"]
		employee_id: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		served_by: DF.Data | None
		title: DF.Data | None
	# end: auto-generated types
	pass
