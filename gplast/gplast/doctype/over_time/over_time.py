# Copyright (c) 2023, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
from frappe.utils import today,flt,add_days,date_diff,getdate,cint,formatdate
from frappe import _
from frappe.utils import formatdate

class OverTime(Document):
	def after_insert(self):
		user_roles = frappe.get_roles(frappe.session.user)
		hr = "Miss Punch Role" in user_roles
        # admin = "Administrator" in user_roles
		if (not hr):
			allowed_days = 1
			current_date = today()
			if isinstance(current_date, str):
				current_date = datetime.strptime(current_date, "%Y-%m-%d").date()

			def is_working_day(check_date):
				return not check_holiday(check_date, self.employee)

			days_count = 0
			earliest_allowed = current_date
			while days_count < allowed_days:
				earliest_allowed = add_days(earliest_allowed, -1)
				if is_working_day(earliest_allowed):
					days_count += 1

			if not self.ot_date:
				return

			if isinstance(self.ot_date, str):
				miss_date = datetime.strptime(self.ot_date, "%Y-%m-%d").date()
			else:
				miss_date = self.ot_date

			if miss_date < earliest_allowed:
				frappe.throw(
					_("Overtime applications are allowed only for up to the previous {0} working days.")
					.format(allowed_days)
				)

	def validate(self):
		doctype = self.doctype
		old_state = frappe.db.get_value(doctype, self.name, "workflow_state")

		if old_state and old_state != self.workflow_state:
			self.previous_approval_date = today()
		overtime_hours =frappe.db.get_value('Attendance',{'employee':self.employee,'attendance_date':self.ot_date,'docstatus':['!=',2]},'overtime_hours')
		if frappe.db.exists('Over Time',{'name':['!=',self.name],'employee':self.employee,"ot_date": self.ot_date,'docstatus':['!=',2]}):
			formatted_date = formatdate(self.ot_date, "dd-mm-yyyy")
			frappe.throw(f'Over Time Request for employee {self.employee} has already been recorded for the date {formatted_date}.')
		if float(self.overtime_hours) == 0:
			frappe.throw(f"Employee {self.employee} must have Overtime hours greater than 0 to apply for OT.")
		if overtime_hours:
			if float(overtime_hours) < float(self.overtime_hours):
				frappe.throw('Not Allowed to update the OT hours more than the Actual OT Hours')


# 		if self.outtime and self.in_time:
# 			try:
# 				in_time = datetime.strptime(self.in_time, "%H:%M:%S")
# 				out_time = datetime.strptime(self.outtime, "%H:%M:%S")
# 				total_hour = datetime.strptime(self.total_hours, "%H:%M:%S")


# 				if out_time < in_time:
# 					frappe.throw("Out time cannot be earlier than in time.")

# 				# Calculate overtime hours
# 				overtime = out_time - in_time
# 				total_hour = overtime.total_seconds() / 3600
# 				frappe.errprint(total_hours)

# 				# Update ot_hours field
# 				self.total_hours = total_hour

# 			except ValueError:
# 				frappe.throw("Invalid time format. Please use HH:MM:SS format.")

# @frappe.whitelist()
# def validate(self):
# 	if self.outtime and self.in_time:
# 		in_time = datetime.strptime(self.in_time, "%H:%M:%S")
# 		outtime = datetime.strptime(self.outtime, "%H:%M:%S")

# 		# Calculate overtime hours
# 		overtime = outtime - in_time
# 		ot_hours = overtime.total_seconds() / 3600

# 		# Update ot_hours field
# 		self.ot_hours = ot_hours

@frappe.whitelist()
def get_total_ot_hours(employee,ot_date):
	datalist =[]
	data ={}
	if frappe.db.exists('Attendance',{'employee':employee,'attendance_date':ot_date,'docstatus':['!=',2]}):
		overtime_hours =frappe.db.get_value('Attendance',{'employee':employee,'attendance_date':ot_date,'docstatus':['!=',2]},'overtime_hours')
		ot_hours = frappe.db.get_value('Attendance',{'employee':employee,'attendance_date':ot_date,'docstatus':['!=',2]},'ot_hours')
		shift = frappe.db.get_value('Attendance',{'employee':employee,'attendance_date':ot_date,'docstatus':['!=',2]},'shift')
		data.update({
			'overtime_hours':overtime_hours,
			'ot_hours':ot_hours,
			'shift':shift
		})
		datalist.append(data.copy())
	return datalist



@frappe.whitelist()  
def check_holiday(date,emp):
	holiday_list = frappe.db.get_value('Employee',emp,'holiday_list')
	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
	if holiday:
		if holiday[0].weekly_off == 1:
			return "WW"
		else:
			return "HH"