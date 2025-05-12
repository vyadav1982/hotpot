import frappe


@frappe.whitelist()
def get_all_vendor(doctype, txt, searchfield, start, page_len, filters):
	filters = {"role": "Hotpot Vendor"}

	roles = frappe.get_roles()
	if "Hotpot HR" in roles and "Administrator" not in roles:
		filters["is_active"] = 1
		filters["is_deleted"] = 0

	users = frappe.get_all(
		"Hotpot User",
		filters=filters,
		fields=["employee_id", "full_name"],
		or_filters=[["employee_id", "like", f"%{txt}%"], ["full_name", "like", f"%{txt}%"]],
	)

	return [[u["employee_id"], u["full_name"]] for u in users]


@frappe.whitelist()
def disable_users(user_list):
	if not user_list:
		frappe.throw("User list cannot be empty")
	if isinstance(user_list, str):
		user_list = frappe.parse_json(user_list)
	disabled_count = 0
	for user in user_list:
		user_doc = frappe.get_doc("Hotpot User", user)
		user_doc.is_active = 0
		user_doc.save()
		disabled_count += 1

	frappe.db.commit()
	if disabled_count > 0:
		user_text = "user" if disabled_count == 1 else "users"
		frappe.msgprint(f"Successfully disabled {disabled_count} {user_text}.")
	else:
		frappe.msgprint("No users were disabled.")
