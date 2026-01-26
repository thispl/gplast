# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

class AbsentIntimation(Document):
    def on_submit(self):
        recipients = frappe.db.get_value("Employee", {'name': self.employee}, 'user_id')

        frappe.sendmail(
            recipients=[recipients],   
            subject="Warning Letter",
            message=f"""
                <p style="font-family:Calibri, sans-serif;">Dear {self.employee_name},</p>
                <p style="font-family:Calibri, sans-serif;">
                    Kindly find the attached document of Warning Letter for your reference.
                </p>
            """,
            now=True,
            attachments=[
                frappe.attach_print(
                    "Absent Intimation",
                    self.name,
                    file_name="Absent-Intimation.pdf",
                    print_format="Absent Intimation"
                )
            ]
        )
        frappe.msgprint(f"Warning Letter has been sent to {self.employee}")
    def validate(self):
        recipients = frappe.db.get_value("Employee", {'name': self.employee}, 'user_id')
        if not recipients:
            frappe.throw(f"User ID is not set for Employee {self.employee_name}")


            