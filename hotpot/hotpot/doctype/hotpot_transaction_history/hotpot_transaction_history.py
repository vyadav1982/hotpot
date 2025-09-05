# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HotpotTransactionHistory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Int
		category: DF.Data | None
		coupon: DF.Link | None
		coupon_status: DF.Data | None
		employee_id: DF.Link | None
		meal: DF.Link | None
		message: DF.Text | None
		title: DF.Data | None
		type: DF.Literal["Credit", "Debit"]
	# end: auto-generated types
	pass
