from hotpot.api.coupons import * 

@frappe.whitelist()
def generate_guest_coupon(data,from_hook=False):
	if from_hook==True :
		if data.approval_status == "Approved" and data.is_active == 1:
			print("((((()))))")
			print(from_hook)
			try:
				user = frappe.get_doc("Hotpot User", data.requested_by)
				if user:
					response = generate_coupon_guest(
						data.requested_by,
						data.name,
						data.meal_id,
						data.date,
						data.coupon_count
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
						data.requested_by,
						data.name,
						data.meal_id,
						data.date,
						data.coupon_count
					)

					if isinstance(response, dict):
						return response
					else:
						frappe.msgprint(_("Invalid response format."))

		except Exception as e:
			frappe.log_error(str(e), "on_update error")

		
				
