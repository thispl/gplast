# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from gplast.mark_attendance import check_holiday
from frappe.utils import today,flt,add_days,date_diff,getdate,cint,formatdate, getdate, get_link_to_form


class EmployeeBenefitsRegularization(Document):
	def on_submit(self):
		if self.benefits == 'COFF':
			work_end_date=add_days(self.date,30)
			if not frappe.db.exists('Compensatory Leave Request',{'employee':self.employee,'date':self.date,'docstatus':['!=',2]}):
				coff = frappe.new_doc("Compensatory Leave Request")
				coff.employee=self.employee
				coff.leave_type='Compensatory Off'
				coff.work_from_date=self.date
				frappe.errprint(work_end_date)
				coff.work_end_date=self.date
				# coff.new_leaves_allocated=self.comp_off_leave
				coff.save(ignore_permissions=True)
				frappe.db.commit()
				coff.submit()


@frappe.whitelist()
def calculate_ot_hours(employee,date):
	working_hours = 0
	frappe.errprint('att')
	att=frappe.db.get_all('Attendance',{"employee":employee,"attendance_date":date,'docstatus':['!=',2]},['employee','attendance_date','total_working_hours'])
	frappe.errprint(att)
	hh=check_holiday(date,employee)
	frappe.errprint(hh)
	if hh:
		count = frappe.db.count('Employee Benefits Regularization',{'employee':employee,'date':date,'docstatus':['!=',2]})
		frappe.errprint(count)
		if count <= 1 and not frappe.db.exists('Employee Benefits Regularization',{'employee':employee,'date':date,'docstatus':['!=',2]}):
			working_hours = att[0].get('total_working_hours')
			frappe.errprint(f"att.total_working_hours {att[0].get('total_working_hours')}")
		else:
			frappe.throw("Dublicate Entry")
	return working_hours

