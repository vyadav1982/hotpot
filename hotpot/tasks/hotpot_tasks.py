import frappe

def load_balance():
	try:
        print("running taks hoorayy!!!!!!!!!")
        frappe.logger().info(f"it works!!!!!!!!!.")
        return
        frappe.
		employees = frappe.get_all(
			"Hotpot User",
			filters={"is_employee": 1},
			fields=["name", "coupon_count"]
		)

		for emp in employees:
			frappe.db.set_value("Hotpot User", emp.name, "coupon_count", 1000)

		frappe.db.commit()
		frappe.logger().info(f"Loaded 1000 coupon_count for {len(employees)} employees.")

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Load Balance Error")
		frappe.db.rollback()
