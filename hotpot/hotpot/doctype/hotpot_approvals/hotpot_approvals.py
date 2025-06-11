# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from hotpot.utils.guest_coupon_generate import *
from hotpot.utils.send_fcm import *
from hotpot.utils.email import *
import json

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
		description: DF.SmallText | None
		draft_meal: DF.Link | None
		guest_mobile_no: DF.Phone | None
		guest_name: DF.Data | None
		is_active: DF.Check
		meal_id: DF.Link | None
		purpose_of_visiting: DF.Data | None
		request_type: DF.Literal["Guest Coupon Generation", "Meal Edit", "Meal Delete"]
		requested_by: DF.Link | None
	# end: auto-generated types


	def after_insert(self):
		if is_frappe_ui_request() and self.meal_id:
			meal_id = self.meal_id
			meal_doc = frappe.get_doc("Hotpot Meal",meal_id)
			user_data = frappe.get_doc("Hotpot User",self.requested_by)
			approval_doc = frappe.get_doc("Hotpot Approvals",self.name)
			meal_doc.approval_id = self.name
			meal_doc.save()
			frappe.db.commit()
			send_approval_request_email(
				"sashikant12rao@gmail.com", user_data, approval_doc, self.name, meal_doc.meal_title
			)

 

	def on_update(self):
		if (
			self.is_active == 1
			and self.request_type == "Guest Coupon Generation"
			and self.approval_status == "Rejected"
		):
			user_doc = frappe.get_doc("Hotpot User", self.requested_by)
			self.is_active = 0
			if user_doc.fcm_token:
				send_notification_by_token(
					user_doc.fcm_token,
					"Guest Coupon Request ❌",
					"Oops! 😢 Your guest coupon request was rejected by the admin. Maybe next time!",
				)
			self.save()
			frappe.db.commit()

		elif (
			self.is_active == 1
			and self.request_type == "Guest Coupon Generation"
			and self.approval_status == "Approved"
		):
			try:
				res = generate_guest_coupon(self, from_hook=True)
				user_doc = frappe.get_doc("Hotpot User", self.requested_by)
				if res:
					indicator_color = "green" if res.get("status") == "success" else "red"
					frappe.msgprint(_(res.get("msg")), indicator=indicator_color)
					if res.get("status") == "success" and user_doc.fcm_token:
						send_notification_by_token(
							user_doc.fcm_token,
							"Guest Coupon Request ✅",
							"Hurray! 😁 Your guest coupons have been successfully generated. Enjoy the treat!",
						)

					elif user_doc.fcm_token:
						send_notification_by_token(
							user_doc.fcm_token,
							"Guest Coupon Request Failed ⚠️",
							f"😢 Couldn't generate your guest coupons. Reason: {res.get('msg')}",
						)
					self.approval_remarks = res.get("msg")

				else:
					frappe.msgprint(_("Coupon generation failed"))
				self.is_active = 0
				self.save()
				frappe.db.commit()
				return
			except Exception as e:
				frappe.log_error(str(e), "on_update error")
				frappe.msgprint(_("An error occurred while generating coupon."))

		elif (
			self.is_active == 1 and self.request_type == "Meal Delete" and self.approval_status == "Approved"
		):
			try:
				meal_doc = frappe.get_doc("Hotpot Meal", self.meal_id)
				meal_doc.is_deleted = 1
				coupons = meal_doc.coupons
				user_doc = frappe.get_doc("Hotpot User", self.requested_by)
				if user_doc.fcm_token:
					send_notification_by_token(
						user_doc.fcm_token,
						"Meal Deleted Successfully ✅",
						f"Woohoo! 🎉 Your request was approved by the admin and the {meal_doc.meal_title} meal has been deleted.",
					)

				for coupon in coupons:
					if coupon.coupon_status == "1":
						user_doc = frappe.get_doc("Hotpot User", coupon.get("employee_id"))
						if user_doc.fcm_token:
							send_notification_by_token(
								user_doc.fcm_token,
								"Meal Vanished! 🥲",
								f"Oops! '{meal_doc.meal_title}' has been deleted by your vendor. It's gone... but never forgotten.",
							)
						if not coupon.birthday_coupon and not coupon.joining_day and not coupon.guest_of:
							user_doc.coupon_count = user_doc.coupon_count + meal_doc.meal_weight
							transaction_doc = frappe.new_doc("Hotpot Transaction History")
							transaction_doc.update(
								{
									"employee_id": user_doc.get("name"),
									"type": "Credit",
									"message": f"{int(coupon.coupon_weight)} tokens credited to your wallet for '{meal_doc.meal_title}' meal deletion.",
									"title": "Meal Cost Refund",
									"amount": coupon.coupon_weight,
									"meal": self.meal_id,
									"coupon": coupon.get("name"),
									"coupon_status": "2",
									"category": meal_doc.get("category"),
								}
							)
							transaction_doc.insert()
							if user_doc.fcm_token:
								send_notification_by_token(
									user_doc.fcm_token,
									"Refund Incoming! 💸",
									f"You've been credited {coupon.coupon_weight} tokens for the deleted meal '{meal_doc.meal_title}'. Your wallet just got heavier!",
								)

					coupon.coupon_status = 2
				self.is_active = 0
				self.save()
				meal_doc.save()
				frappe.db.commit()
				frappe.msgprint(_("Meal deleted successfully!."), indicator="green")

			except Exception as e:
				frappe.log_error(str(e), "on_update error")
				frappe.msgprint(_("An error occurred while deleting meal."))

		elif (
			self.is_active == 1 and self.request_type == "Meal Delete" and self.approval_status == "Rejected"
		):
			meal_doc = frappe.get_doc("Hotpot Meal", self.meal_id)
			user_doc = frappe.get_doc("Hotpot User", self.requested_by)
			self.is_active = 0
			if user_doc.fcm_token:
				send_notification_by_token(
					user_doc.fcm_token,
					"Meal Deletion Request ❌",
					f"Oops! 😢 Your {meal_doc.meal_title} meal delete request was rejected by the admin. Maybe next time!",
				)
			self.save()
			frappe.db.commit()
		elif self.is_active == 1 and self.request_type == "Meal Edit" and self.approval_status == "Rejected":
			meal_doc = frappe.get_doc("Hotpot Meal", self.meal_id)
			user_doc = frappe.get_doc("Hotpot User", self.requested_by)
			self.is_active = 0
			if user_doc.fcm_token:
				send_notification_by_token(
					user_doc.fcm_token,
					"Meal Edit Request ❌",
					f"Oops! 😢 Your {meal_doc.meal_title} meal edit request was rejected by the admin. Maybe next time!",
				)
			self.save()
			frappe.db.commit()
		elif self.is_active == 1 and self.request_type == "Meal Edit" and self.approval_status == "Approved":
			meal_doc = frappe.get_doc("Hotpot Meal", self.meal_id)
			user_doc = frappe.get_doc("Hotpot User", self.requested_by)

			draft_name = frappe.db.get_value("Hotpot Draft Meal", {
				"meal": self.meal_id,
				"approval": self.name
			})

			if not draft_name:
				frappe.throw("Draft Meal not found.")

			draft_doc = frappe.get_doc("Hotpot Draft Meal", draft_name)
			draft_values = json.loads(draft_doc.new_values)

			for field, value in draft_values.items():
				if hasattr(meal_doc, field):
					try:
						if field == "meal_items" and isinstance(value, list):
							value = ", ".join([str(i).strip() for i in value if i])
						setattr(meal_doc, field, value)
					except Exception as e:
						frappe.throw(f"Error setting value for '{field}': {e}")
				else:
					frappe.throw(f"Field '{field}' does not exist in Hotpot Meal.")

			meal_doc.save()

			# if user_doc.fcm_token:
				# send_notification_by_token(
				# 	user_doc.fcm_token,
				# 	"Meal Edit Approved ✏️",
				# 	f"Good news! ✅ Your request was approved — changes will now reflect on your {meal_doc.meal_title} meal.",
				# )
			coupons = meal_doc.coupons
			for coupon in coupons:
				user_doc = frappe.get_doc("Hotpot User", coupon.employee_id)
				# if user_doc.fcm_token:
					# send_notification_by_token(
					# 	user_doc.fcm_token,
					# 	"Meal Plot Twist!",
					# 	f"Guess what? The vendor just spiced things up in '{meal_doc.meal_title}'. Go check it out!",
					# )
			self.is_active=0


def is_frappe_ui_request():
	try:
		referer = frappe.get_request_header("Referer")
		csrf_token = frappe.get_request_header("X-Frappe-CSRF-Token")
		user_agent = frappe.get_request_header("User-Agent")

		if referer and "app" in referer:
			return True
		if csrf_token:
			return True
		if user_agent and "frappe" in user_agent.lower():
			return True
	except Exception:
		pass
	return False


def send_approval_request_email(to_email, user_data, request_data, doc, meal_name):
	email_subject = (
		f"Approval Request from {user_data.full_name} ({user_data.name}) for {request_data.get('request_type')}"
	)
	context = {
		"user_data": user_data,
		"request_data": request_data,
		"meal_name": meal_name,
		"get_approval_link": "https://hotpot.bytepanda.in/app/hotpot-approvals/view/list?approval_status=Pending",
	}
	send_email("approval_email", to_email, context, email_subject)
