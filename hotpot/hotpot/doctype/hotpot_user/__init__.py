import frappe

@frappe.whitelist()
def get_all_vendor(doctype, txt, searchfield, start, page_len, filters):
    users = frappe.get_all(
        "Hotpot User",
        filters={"role": "Hotpot Vendor"},
        fields=["employee_id", "employee_name"],
    )
    return [[r["employee_id"], r["employee_name"]] for r in users]


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
        disabled_count+=1

    frappe.db.commit() 
    if disabled_count > 0:
        user_text = "user" if disabled_count == 1 else "users"
        frappe.msgprint(f"Successfully disabled {disabled_count} {user_text}.")
    else:
        frappe.msgprint("No users were disabled.")