import json

import frappe


@frappe.whitelist()
def set_menu(data):
	try:
		data = json.loads(data)

		for day, values in data.items():
			day_special = 1 if values.get("daySpecial", False) else 0

			meals = values.get("meals", {})
			breakfast = meals.get("breakfast", {})
			lunch = meals.get("lunch", {})
			snacks = meals.get("snacks", {})
			dinner = meals.get("dinner", {})

			menu_data = {
				"day": day,
				"special": day_special,
				"breakfast": breakfast.get("meal", ""),
				"breakfast_special": 1 if breakfast.get("special", False) else 0,
				"luch": lunch.get("meal", ""),
				"lunch_special": 1 if lunch.get("special", False) else 0,
				"snacks": snacks.get("meal", ""),
				"snacks_special": 1 if snacks.get("special", False) else 0,
				"dinner": dinner.get("meal", ""),
				"dinner_special": 1 if dinner.get("special", False) else 0,
				"active": 1,
			}

			if any(menu_data[field] for field in ["breakfast", "luch", "snacks", "dinner"]):
				existing_entry = frappe.db.exists("Hotpot Menu", {"day": day})

				if existing_entry:
					doc = frappe.get_doc("Hotpot Menu", existing_entry)
					for key, value in menu_data.items():
						setattr(doc, key, value)
					doc.save(ignore_permissions=True)
				else:
					frappe.get_doc(
						{
							"doctype": "Hotpot Menu",
							**menu_data,
						}
					).insert(ignore_permissions=True)

				frappe.db.commit()

		return {"status": "success", "message": "Menu updated successfully."}

	except json.JSONDecodeError:
		return {"status": "error", "message": "Invalid JSON data."}
	except Exception as e:
		frappe.log_error(message=str(e), title="Menu Update Error")
		return {"status": "error", "message": str(e)}
