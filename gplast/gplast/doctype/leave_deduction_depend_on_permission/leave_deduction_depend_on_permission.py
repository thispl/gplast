# Copyright (c) 2023, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LeavedeductiondependonPermission(Document):
    def total_value(self):
        kl = 0
        hours = 0
        
        lp_lists = frappe.db.sql(
            """
            SELECT * FROM `tabAttendance Permission`
            WHERE employee = %s AND docstatus = 1 AND permission_date BETWEEN %s AND %s
            """,
            (self.employee, self.from_date, self.to_date),
            as_dict=True
        )
        for lp_list in lp_lists:
            kl = int(lp_list.get('permission_hour'))
            hours += kl  # Accumulate hours inside the loop

        self.permission_hours = hours
        if (self.permission_hours == 4 or self.permission_hours == 5):
            self.leave_days = 0.5
        elif (self.permission_hours == 6 or self.permission_hours == 7):
            self.leave_days = 1
        elif (self.permission_hours == 8 or self.permission_hours == 9):
            self.leave_days = 1.5
        elif (self.permission_hours == 10 or self.permission_hours == 11):
            self.leave_days = 2
        self.leave_balance=total_leave()
@frappe.whitelist()
def total_leave():
    
		data = ''
		data += '<table border="1" width="100%"><tr style="">'
		data += '<td style = "background-color:#e35310;color:white"><b>Leave Type</b></td>'
		data += '<td style = "background-color:#e35310;color:white"><b>Total Leave</b></td>'    
		# data += '<td style = "background-color:#e35310;color:white"><b>PCC Status</b></td>'    
		# data += '<td style = "background-color:#e35310;color:white"><b>Statmping Status</b></td></tr>'
		# if offer_letter and not sol:
		# 	data += '<td style = "color:orange"><b>Client Offer Letter</b></td>'
		# elif offer_letter and sol:
		# 	data += '<td style = "color:orange"><b>Signed Offer Letter</b></td>'
		# else:
		# 	data += '<td style = "color:orange"><b>Yet to be processed</b></td>'
		# if final_medical:
		# 	data += '<td style = "color:orange"><b>Final Medical</b></td>'
		# else:
		# 	data += '<td style = "color:orange"><b>Yet to be Processed</b></td>'
		# if pcc:    
		# 	data += '<td style = "color:orange"><b>PCC</b></td>'
		# elif pcc_not:
		# 	data += '<td style = "color:orange"><b>PCC not applicable</b></td>'
		# else:
		# 	data += '<td style = "color:orange"><b>Yet to be Processed</b></td>'
		# if visa_stamping:
		# 	data += '<td style = "color:orange"><b>Visa Stamped</b></td>'
		# else:
		# 	data += '<td style = "color:orange"><b>Yet to be Processed</b></td>'
		return data
