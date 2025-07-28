# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HotpotDraftMeal(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		approval: DF.Link | None
		meal: DF.Link | None
		new_values: DF.Code | None
	# end: auto-generated types

	def after_insert(self):
		try:
			if not self.approval:
				frappe.throw("Approval ID is missing in the current document.")

			approval_doc = frappe.get_doc("Hotpot Approvals", self.approval)

			approval_doc.draft_meal = self.name
			approval_doc.save(ignore_permissions=True)

			frappe.db.commit()

		except frappe.DoesNotExistError:
			frappe.db.rollback()
			frappe.log_error(
				f"Approval document with ID {self.approval} not found.", "Draft Meal Insert Error"
			)
			frappe.throw("Approval document not found.")

		except Exception as e:
			frappe.db.rollback()
			frappe.log_error(frappe.get_traceback(), "Draft Meal Insert Error")
			frappe.throw(f"An unexpected error occurred while linking draft to approval: {str(e)}")
