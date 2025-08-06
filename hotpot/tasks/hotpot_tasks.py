from datetime import datetime

import frappe
from frappe.utils import getdate, nowdate
from hotpot.utils.utc_time import get_local_time_now, get_utc_datetime_obj
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


def update_meals_future():
	try:
		today = getdate(nowdate())

		vendors = frappe.get_all(
			"Hotpot User",
			filters={"is_vendor": 1, "is_active": 1},
			fields=["name"]
		)

		for vendor in vendors:
			try:
				vendor_doc = frappe.get_doc("Hotpot User", vendor.name)

				categories = {
					row.category: row.discounted_rate
					for row in vendor_doc.category_prices
					if row.applicable_from and getdate(row.applicable_from) == today
				}


				if not categories:
					continue

				local_time_now = get_local_time_now()
				start_datetime_utc = get_utc_datetime_obj(f"{today} {local_time_now}")

				categories_sql = ', '.join(f"'{cat}'" for cat in categories)

				query = f"""
					SELECT name FROM `tabHotpot Meal`
					WHERE vendor_id = %s
					AND is_active = 1
					AND category IN ({categories_sql})
					AND meal_date >= %s
				"""

				meals = frappe.db.sql(query, (vendor.name, start_datetime_utc), as_dict=True)
				

				for meal in meals:
					try:
						meal_doc = frappe.get_doc("Hotpot Meal", meal.name)
						meal_doc.vendor_id = vendor.name


						coupons = meal_doc.get("coupons")
						for coupon in coupons:
							coupon_doc = frappe.get_doc("Hotpot Coupons", coupon.name)
							if coupon_doc.coupon_status != "1":
								continue
							prev_weight = coupon_doc.coupon_weight
							new_weight = categories.get(meal_doc.category)
							user_doc = frappe.get_doc("Hotpot User", coupon.employee_id)

							if prev_weight != new_weight:
								coupon_doc.coupon_weight = new_weight

								transaction_doc = frappe.new_doc("Hotpot Transaction History")

								if prev_weight > new_weight:
									amount_changed = prev_weight - new_weight
									user_doc.coupon_count += amount_changed
									transaction_doc.update({
										"employee_id": user_doc.get("name"),
										"type": "Credit",
										"message": f"{amount_changed} tokens refunded as meal cost for '{meal_doc.meal_title}' dropped. 💸",
										"title": "Meal Cost Refund",
										"amount": amount_changed,
										"meal": meal_doc.name,
										"coupon": coupon.get("name"),
										"coupon_status": "1",
										"category": meal_doc.get("category"),
									})
									message = f"Sweet deal! 😄 '{meal_doc.meal_title}' just got cheaper!"
									message2 = f"Refund alert! 💸 You got back {amount_changed} tokens. Check your wallet!"
								else:
									amount_changed = new_weight - prev_weight
									user_doc.coupon_count -= amount_changed
									transaction_doc.update({
										"employee_id": user_doc.get("name"),
										"type": "Debit",
										"message": f"{amount_changed} tokens deducted as meal cost for '{meal_doc.meal_title}' increased. 💰",
										"title": "Meal Cost Update",
										"amount": amount_changed,
										"meal": meal_doc.name,
										"coupon": coupon.get("name"),
										"coupon_status": "1",
										"category": meal_doc.get("category"),
									})
									message = f"Price bump! 😕 '{meal_doc.meal_title}' costs a bit more now."
									message2 = f"{amount_changed} tokens deducted 💰. Check your wallet for updates!"

								transaction_doc.insert()
								coupon_doc.save(ignore_permissions=True)
								user_doc.save(ignore_permissions=True)

								if user_doc.fcm_token:
									try:
										send_notification_by_token(
											user_doc.fcm_token,
											"Meal Update Alert",
											message,
											date=meal_doc.meal_date,
											doc_id=meal_doc.name,
											text="meals",
										)
										send_notification_by_token(
											user_doc.fcm_token,
											"Wallet Update 💼",
											message2,
											doc_id=transaction_doc.name,
											text="transactions",
										)
									except Exception:
											frappe.log_error(
												frappe.get_traceback(),
												f"Failed to send update notification to {user_doc.name}",
											)

						meal_doc.save(ignore_permissions=True)
						frappe.db.commit()
					except Exception as e:
						frappe.log_error(frappe.get_traceback(), f"[update_meals_future] Meal update failed for {meal.name}")

			except Exception as e:
				frappe.log_error(frappe.get_traceback(), f"[update_meals_future] Failed processing vendor {vendor.name}")

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "[update_meals_future] Fatal error")


def reset_todays_new_logins():
	"""Reset 'Today's New Login' count to 0 using Frappe ORM."""
	try:
		config = frappe.get_single("Hotpot Configurations")
		config.todays_new_login = 0
		config.save(ignore_permissions=True)
		frappe.db.commit()
		frappe.logger().info("✅ Reset today's new login count to 0.")
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "❌ Error resetting today's new logins")

