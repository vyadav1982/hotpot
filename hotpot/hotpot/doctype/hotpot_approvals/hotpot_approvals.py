# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _ 
from hotpot.utils.guest_coupon_generate import *


class HotpotApprovals(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		approval_remarks: DF.SmallText | None
		approval_status: DF.Literal["Pending", "Approved", "Rejected"]
		attachments: DF.Attach | None
		coupon_count: DF.Int
		date: DF.Datetime | None
		descrption: DF.SmallText | None
		guest_mobile_no: DF.Phone | None
		guest_name: DF.Data | None
		is_active: DF.Check
		meal_id: DF.Link | None
		purpose_of_visiting: DF.Data | None
		request_type: DF.Literal["Guest Coupon Generation", "Meal Edit", "Meal Delete"]
		requested_by: DF.Link | None
	# end: auto-generated types
	


	def on_update(self):
		if self.is_active == 1:
			try:
				res = generate_guest_coupon(self, from_hook=True)

				# Only mark approved if coupon generation succeeded
				if res:
					self.approval_status = "Approved"
					self.is_active = 0
					self.save()
				else:
					frappe.msgprint(_("Coupon generation failed: {0}").format(res.get("msg", "Unknown error")))

				print(res)
				return
			except Exception as e:
				frappe.log_error(str(e), "on_update error")
				frappe.msgprint(_("An error occurred while generating coupon."))
