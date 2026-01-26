# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TrainingEventsType(Document):
    def validate(self):
        self.month_mandatory()

    def month_mandatory(self):
        if self.effectiveness == "Yes":
            if not self.month or self.month <= 0:
                frappe.throw("Month must be more than '0'.")
