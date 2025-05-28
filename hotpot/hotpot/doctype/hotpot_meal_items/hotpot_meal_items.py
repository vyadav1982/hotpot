# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


def is_frappe_ui_request():
	try:
		referer = frappe.get_request_header("Referer")
		csrf_token = frappe.get_request_header("X-Frappe-CSRF-Token")
		user_agent = frappe.get_request_header("User-Agent")

		if referer and "app" in referer:
			return True
		if csrf_token:
			return True
		if user_agent and "frappe" in user_agent.lower():
			return True
	except Exception:
		pass
	return False


class HotpotMealItems(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		is_active: DF.Check
		is_deleted: DF.Check
		item_name: DF.Data | None
		vendor_id: DF.Link | None
	# end: auto-generated types

	def before_insert(self):
		self.item_name = self.item_name.strip().lower()
		if is_frappe_ui_request() or frappe.flags.in_import:
			roles = frappe.get_roles()
			if "Administrator" in roles:
				return
			if "Hotpot Vendor" in roles:
				vendor_id = frappe.db.get_value("Hotpot User", {"email": frappe.session.user}, "name")
				self.vendor_id = vendor_id
			exists = frappe.db.exists(
				"Hotpot Meal Items",
				{"item_name": self.item_name, "vendor_id": self.vendor_id},
			)
			if exists:
				frappe.throw(
					_("Meal Item {0} already exists for vendor {1}.").format(self.item_name, self.vendor_id)
				)
