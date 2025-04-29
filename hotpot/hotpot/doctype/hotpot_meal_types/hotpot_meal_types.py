# Copyright (c) 2025, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import re
from frappe.model.document import Document


class HotpotMealTypes(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		is_active: DF.Check
		type: DF.Data | None
	# end: auto-generated types
	
	def before_insert(self):
		if self.type:
			if not isinstance(self.type, str):
				self.type = str(self.type)

			cleaned_type = re.sub(r'\s+', ' ', self.type.strip()).lower()

			cleaned_type = re.sub(r'[^a-z0-9 _-]', '', cleaned_type)
			print(f"Cleaned type: {cleaned_type}")
			self.type = cleaned_type.strip()
