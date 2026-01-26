# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from collections import defaultdict
position_counters = defaultdict(int)
class DesignationApproval(Document):
	def before_save(self):
		if not self.designation_code:
			title = (self.designation or "").strip()
			if not title:
				frappe.throw("Designation Name is required to generate Designation Code.")

			parts = title.split()
			if len(parts) == 1:
				code = parts[0][:2].upper()
			else:
				code = "".join(part[0].upper() for part in parts[:3])
			# frappe.errprint(code)
			length = len (code)
			existing_count = frappe.db.count(
				self.doctype,
				{ "designation_code": ["like", f"{code}%"] }
			)
			seq = existing_count + 1
			# frappe.errprint(seq)
			if length == 2:
				self.designation_code = f"{code}{seq:03}"
			elif length == 3:
				self.designation_code = f"{code}{seq:02}"

