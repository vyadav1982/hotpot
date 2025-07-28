from datetime import datetime

import frappe
import pytz

from hotpot.utils.send_fcm import *


def load_balance():
	try:
		india = pytz.timezone("Asia/Kolkata")
		now = datetime.now(india)

		hotpot_config = frappe.get_single("Hotpot Configurations")
		monthly_credit_amount = hotpot_config.get("initial_tokens")

		if now.day == 1:
			frappe.logger().info("Starting load_balance scheduled task...")
			print("Starting load_balance scheduled task...")

			employees = frappe.get_all(
				"Hotpot User",
				filters={"is_employee": 1, "is_active": 1},
				fields=["name", "employee_id", "fcm_token"],
			)

			for emp in employees:
				current_count = frappe.db.get_value("Hotpot User", emp.name, "coupon_count") or 0
				new_count = monthly_credit_amount

				frappe.db.set_value("Hotpot User", emp.name, "coupon_count", new_count)

				transaction_doc = frappe.new_doc("Hotpot Transaction History")
				transaction_doc.update(
					{
						"employee_id": emp.employee_id,
						"type": "Credit",
						"message": f"🎉 You've received your monthly credit of {monthly_credit_amount} tokens on {now.strftime('%d %b %Y')} by the Admin.",
						"title": "Monthly Credit",
						"amount": monthly_credit_amount,
						"meal": None,
						"coupon": None,
					}
				)
				transaction_doc.insert(ignore_permissions=True)

				if emp.fcm_token:
					from hotpot.utils.send_fcm import send_notification_by_token

					try:
						send_notification_by_token(
							emp.fcm_token,
							"💰 Wallet Getting Heavier!",
							f"🎉 Great news! Admin just added ₹{monthly_credit_amount} to your wallet. New balance: ₹{new_count}.",
							doc_id=transaction_doc.name,
							text="transaction",
						)
					except Exception:
						frappe.log_error(
							frappe.get_traceback(),
							f"Failed to send wallet credit notification to user {emp.name}",
						)

			frappe.db.commit()
			frappe.logger().info(f"✅ Successfully updated coupon_count for {len(employees)} employee(s).")
			print(f"✅ Successfully updated coupon_count for {len(employees)} employee(s).")

	except Exception:
		frappe.log_error(frappe.get_traceback(), "❌ Load Balance Error")
		frappe.db.rollback()
