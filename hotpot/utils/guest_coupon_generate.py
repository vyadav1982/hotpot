import frappe
from frappe import _

from hotpot.api.coupons import generate_coupon_guest
from hotpot.utils.utc_time import get_local_datetime_obj


@frappe.whitelist()
def generate_guest_coupon(data, from_hook=False):
	if from_hook:
		if data.approval_status == "Approved" and data.is_active == 1:
			try:
				user = frappe.get_doc("Hotpot User", data.requested_by)
				if user:
					response = generate_coupon_guest(
						data.requested_by,
						data.name,
						data.meal_id,
						get_local_datetime_obj(data.date).strftime("%Y-%m-%d"),
						data.coupon_count,
					)
					if isinstance(response, dict):
						return response
					else:
						frappe.msgprint(_("Invalid response format."))

			except Exception as e:
				frappe.log_error(str(e), "on_update error")

	else:
		try:
			user = frappe.get_doc("Hotpot User", data.requested_by)
			if user:
				response = generate_coupon_guest(
					data.requested_by, data.name, data.meal_id, data.date, data.coupon_count
				)

				if isinstance(response, dict):
					return response
				else:
					frappe.msgprint(_("Invalid response format."))

		except Exception as e:
			frappe.log_error(str(e), "on_update error")
