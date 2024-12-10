import frappe


@frappe.whitelist(methods=["GET"])
def get_current_user():
	return frappe.get_cached_doc("User", frappe.session.user)


@frappe.whitelist(methods=["GET"])
def get_list():
	return frappe.db.get_list(
		"Hotpot User",
		fields=["name","employee_id", "employee_name"],
		filters=[
			["is_active", "=", 1],
			["is_guest", "=", 0],
		],
	)


@frappe.whitelist(methods=["POST"])
def get_hotpot_user_by_employee_id(employee_id):
	return frappe.get_doc("Hotpot User", employee_id)
