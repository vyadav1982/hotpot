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
		if self.is_active == 1 and self.request_type == "Guest Coupon Generation" and self.approval_status=="Approved":
			try:
				res = generate_guest_coupon(self, from_hook=True)
				if res:
					indicator_color = "green" if res.get("status") == "success" else "red"
					frappe.msgprint(_(res.get("msg")), indicator=indicator_color)
				else:
					frappe.msgprint(_("Coupon generation failed"))
				self.is_active = 0
				return
			except Exception as e:
				print(e)
				frappe.log_error(str(e), "on_update error")
				frappe.msgprint(_("An error occurred while generating coupon."))

		elif self.is_active == 1 and self.request_type == "Meal Delete" and self.approval_status=="Approved":
			try:
				meal_doc = frappe.get_doc("Hotpot Meal",self.meal_id)
				meal_doc.is_deleted=1
				coupons = meal_doc.coupons
				for coupon in coupons:
					if coupon.coupon_status == '1':
						user_doc  = frappe.get_doc("Hotpot User",coupon.get("employee_id"))
						if not coupon.birthday_coupon and not coupon.joining_day and not coupon.guest_of:
							user_doc.coupon_count= user_doc.coupon_count + meal_doc.meal_weight
							transaction_doc = frappe.new_doc("Hotpot Transaction History")
							transaction_doc.update(
								{
									"employee_id": user_doc.get("name"),
									"type": "Credit",
									"message": f"{meal_doc.meal_weight} tokens credited to your wallet for '{meal_doc.meal_title}' meal deletion.",
									"title": "Meal Cost Refund",
									"amount": meal_doc.meal_weight
								}
							)
							transaction_doc.insert()
					coupon.coupon_status = 2
				meal_doc.save()
				frappe.db.commit()
				frappe.msgprint(_("Meal deleted successfully!."),indicator="green")
			except Exception as e:
				print(e)
				frappe.log_error(str(e), "on_update error")
				frappe.msgprint(_("An error occurred while deleting meal."))
	# def before_save(self):
	# 	print(self.to_dict())
	# 	if self.approval_status != "Pending":
	# 		self.is_active = 0
		# self.is_active = 0
		# self.save()
		# frappe.db.commit()
