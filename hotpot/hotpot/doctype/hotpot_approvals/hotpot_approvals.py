# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from hotpot.api.coupons import generate_coupon_guest 
from frappe import _ 


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
		if self.approval_status == "Approved" and self.is_active == 1:
			try:
				user = frappe.get_doc("Hotpot User", self.requested_by)
				if user:
					response = generate_coupon_guest(
						self.requested_by,
						self.name,
						self.meal_id,
						self.date,
						self.coupon_count
					)

					if isinstance(response, dict):
						status = response.get("status")
						message = response.get("msg", "No message received")

						if status == "success":
							self.is_active = 0
							frappe.msgprint(
								title=_("Success"),
								message=_(message),
								indicator="green"
							)
						elif status == "error":
							frappe.msgprint(
								message=_(message),
								title=_("Error"),
								indicator="red"
							)
						else:
							frappe.msgprint(_("Unknown response status."))
					else:
						frappe.msgprint(_("Invalid response format."))

			except Exception as e:
				frappe.log_error(str(e), "on_update error")
				# frappe.msgprint(
				# 	message=_("An error occurred: {0}").format(str(e)),
				# 	title=_("Exception"),
				# 	indicator="red"
				# )
