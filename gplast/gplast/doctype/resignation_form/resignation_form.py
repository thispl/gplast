# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days
class ResignationForm(Document):
    def validate(self):
        if frappe.db.exists("Resignation Form",{"employee": self.employee,"docstatus": 1}):
            frappe.throw("Resignation has already been created for this employee.")

    def on_submit(self):
        if self.posting_date:
            notice_number_of_days = frappe.db.get_value('Employee',{'name':self.employee},['notice_number_of_days'])
            if notice_number_of_days:
                relieving_date =add_days(self.posting_date,notice_number_of_days)
            else:
                relieving_date = self.posting_date
            frappe.db.set_value('Employee',{'name':self.employee},'resignation_letter_date',self.posting_date)
            frappe.db.set_value('Employee',{'name':self.employee},'relieving_date',relieving_date)
            # frappe.db.set_value('Employee',{'name':self.employee},'status','Under Notice')
    def on_cancel(self):
        if self.posting_date:
            # notice_number_of_days = frappe.db.get_value('Employee',{'name':self.employee},['notice_number_of_days'])
            # if notice_number_of_days:
            #     relieving_date =add_days(self.posting_date,notice_number_of_days)
            # else:
            #     relieving_date = self.posting_date
            frappe.db.set_value('Employee',{'name':self.employee},'resignation_letter_date',None)
            frappe.db.set_value('Employee',{'name':self.employee},'relieving_date',None)

@frappe.whitelist()
def validate_the_interview_feedback_document(doc,method):
    if doc.reason_for_designation_change and len(doc.reason_for_designation_change) > 20:
        frappe.throw("Reason for Designation Change cannot exceed 20 characters.")


