import frappe
from frappe import _


@frappe.whitelist(methods=["POST"])
def load_balance(**args):
	employee_id = args.get("selected_employee")
	if not employee_id:
		frappe.throw("Employee ID is required")

	loading_amount = args.get("loading_amount")
	if not loading_amount or float(loading_amount) <= 0:
		frappe.throw("Loading amount is required")

	employee = frappe.get_doc("Hotpot User", employee_id)
	print(employee.__dict__)
	if not employee:
		frappe.throw("Employee Id is not Valid")

	employee_balance = employee.coupon_count

	if employee_balance is None or employee_balance == "":
		employee_balance = 0.0
	else:
		employee_balance = float(employee_balance) + float(loading_amount)

	frappe.db.set_value("Hotpot User", employee_id, "coupon_count", employee_balance)
	# update the document history for the changes made
	new_transaction = frappe.get_doc(
		{
			"doctype": "Hotpot Transaction History",
			"employee_id": employee_id,
			"amount": loading_amount,
			"type": "Debit",
			"title": "Balance Loaded",
			"message": f"Balance loaded successfully. New balance: {employee_balance}",
		}
	)

	new_transaction.insert(ignore_permissions=True)

	frappe.db.commit()

	return {
		"status": "success",
		"message": "Balance loaded successfully",
	}
