import frappe


def after_uninstall():
	remove_standard_navbar_items()


def remove_standard_navbar_items():
	frappe.db.delete(
		"Navbar Item",
		{"item_label": "Hotpot", "is_standard": 1, "item_type": "Route", "route": "/hotpot"},
	)
	# This will run in a post uninstall hook hence needs to be committed manually
	frappe.db.commit()  # nosemgrep
