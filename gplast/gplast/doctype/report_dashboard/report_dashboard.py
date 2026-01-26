# Copyright (c) 2023, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from bs4 import BeautifulSoup

class ReportDashboard(Document):
    def validate(self):
    
        if self.company1:
            raw_description = frappe.db.get_value("Company", self.company1, "company_description") or ""
            self.company_address = BeautifulSoup(raw_description, "html.parser").get_text()

