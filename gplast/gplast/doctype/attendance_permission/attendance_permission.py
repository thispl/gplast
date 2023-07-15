# Copyright (c) 2023, Teampro and contributors
# For license information, please see license.txt


import frappe
from datetime import datetime
from frappe import _, msgprint
from urllib.request import ftpwrapper
from frappe.model.document import Document
from frappe.utils import get_first_day, get_last_day, format_datetime,get_url_to_form,today
from frappe.model.document import Document

class AttendancePermission(Document):
	@frappe.whitelist()
	def hour_res(self):
		data = []
		total = 0
		month_start = get_first_day(today())
		month_end = get_last_day(today())
		permission = frappe.db.get_all('Attendance Permission',{'employee':self.employee,"permission_date": ('between',(month_start,month_end))},['*'])    
		for per in permission:
			total_per_time = frappe.db.get_value('Attendance Permission',{'name':per.name},['total_time'])
			data.append(total_per_time)
		total = sum(map(int, [i for i in data if i.isdigit()]))
		total_hours = total + self.total_time
		frappe.errprint(total_hours)
		if total_hours > int(3):
			frappe.throw(_("Only 3 hours of permission is allowed for a Month"))
