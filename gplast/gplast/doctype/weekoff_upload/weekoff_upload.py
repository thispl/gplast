# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
# from __future__ import unicode_literals
from csv import writer
from inspect import getfile
from unicodedata import name
from frappe.utils import cstr, add_days, date_diff, getdate
from frappe import _
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
from frappe.utils.file_manager import get_file, upload
from frappe.model.document import Document
from datetime import datetime,timedelta,date,time
from gplast.mark_attendance import get_dates
from frappe.utils import cint,today,flt,date_diff,add_days,add_months,date_diff,getdate,formatdate,cint,cstr
# from numpy import unicode_
from frappe.utils.background_jobs import enqueue
from frappe.model.document import Document
class Weekoffupload(Document):
	def on_submit(self): 
		if self.upload:
			args = {'upload':self.upload,'from_date':self.from_date,'to_date':self.to_date,'name':self.name}
			# create_shift_assignment(args)
			frappe.msgprint("Shift Assignment are creating in background.Kindly check after few minutes.")
			enqueue(create_shift_assignment, queue='default', timeout=6000, event='create_shift_assignment',args=args)
		else:
			frappe.throw("Kindly attach the file to submit the schedule")
	def on_cancel(self):
		if self.upload:
			args = {'attach':self.upload,'fdate':self.from_date,'tdate':self.to_date,'name':self.name}
			enqueue(cancel_shift_assignment, queue='default', timeout=6000, event='cancel_shift_assignment',args=args,name=self.name)
			# self.cancel_shift_assignment()
	def on_trash(self):
		sa=frappe.db.get_all("Shift Assignment", {'weekoff_upload':self.name},['name'])
		for s in sa:
			doc = frappe.get_doc('Shift Assignment', s.name)
			doc.delete()
			frappe.db.commit()

@frappe.whitelist()
def get_template():
	args = frappe.local.form_dict
	if getdate(args.from_date) > getdate(args.to_date):
		frappe.throw(_("To Date should be greater than From Date"))
	w = UnicodeWriter()
	w = add_header(w, args)
	w = add_data(w, args)
	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "Weekoff Assignment"

def add_header(w, args):
	base_header = ['Employee', 'Employee Name', 'Department','Designation','Employment Type','Sun','Mon','Tue','Wed','Thur','Fri','Sat']
	w.writerow(base_header)
	return w  

class UnicodeWriter:
	def __init__(self):
		import csv
		from io import StringIO
		self.stream = StringIO()
		self.writer = csv.writer(self.stream)
	def writerow(self, row):
		self.writer.writerow(row)
	def getvalue(self):
		return self.stream.getvalue()

def add_data(w, args):
	data = get_data(args)
	writedata(w, data)
	return w  

@frappe.whitelist()
def writedata(w, data):
	for row in data:
		w.writerow(row)

@frappe.whitelist()
def get_data(args):
	department=frappe.db.get_value('Weekoff upload',{"name":args.name},['department'])
	designation=frappe.db.get_value('Weekoff upload',{"name":args.name},['designation'])
	employment_type=frappe.db.get_value('Weekoff upload',{"name":args.name},['employment_type'])
	if department == 'All Departments' and designation:
		frappe.log_error('1')
		employees = frappe.db.get_all('Employee', {
			'status': 'Active',
			'designation': designation,
			'employment_type': employment_type
		}, ['*'])

	elif department and designation and employment_type:
		employees = frappe.db.get_all('Employee', {
			'status': 'Active',
			'department': department,
			'designation': designation,
			'employment_type': employment_type
		}, ['*'])

	elif department and employment_type: 
		employees = frappe.db.get_all('Employee', {
			'status': 'Active',
			'department': department,
			'employment_type': employment_type
		}, ['*'])

	elif department and designation:
		employees = frappe.db.get_all('Employee', {
			'status': 'Active',
			'department': department,
			'designation': designation
		}, ['*'])

	elif department and department != 'All Departments':
		employees = frappe.db.get_all('Employee', {
			'status': 'Active',
			'department': department
		}, ['*'])

	elif designation and employment_type:
		employees = frappe.db.get_all('Employee', {
			'status': 'Active',
			'designation': designation,
			'employment_type': employment_type
		}, ['*'])

	elif designation:
		employees = frappe.db.get_all('Employee', {
			'status': 'Active',
			'designation': designation
		}, ['*'])

	elif employment_type:
		employees = frappe.db.get_all('Employee', {
			'status': 'Active',
			'employment_type': employment_type
		}, ['*'])

	elif department == 'All Departments':
		employees = frappe.db.get_all('Employee', {'status': 'Active'}, ['*'])

	else:
		employees = frappe.db.get_all('Employee', {'status': 'Active'}, ['*'])


	data = []
	for emp in employees:
		e = "'" + str(emp.name)
		row = [
			e, emp.first_name, emp.department,emp.designation,emp.employment_type
		]
		data.append(row)
	return data

import datetime

@frappe.whitelist()
def create_shift_assignment(args):
	filepath = get_file(args['upload'])
	pps = read_csv_content(filepath[1])
	dates = get_dates(args['from_date'], args['to_date'])
	weekday_to_col_index = {
		6: 5,  # Sunday 
		0: 6,  # Monday 
		1: 7,  # Tuesday 
		2: 8,  # Wednesday 
		3: 9,  # Thursday
		4: 10,  # Friday 
		5: 11  # Saturday 
	}
	for pp in pps[1:]: 
		employee = pp[0]
		if employee.startswith("'"):
			employee = employee[1:]
		department = pp[2]
		schedule_name = args['name']
		for date in dates:
			frappe.log_error(date)
		for date in dates:
			weekday = datetime.datetime.strptime(date, "%Y-%m-%d").weekday()
			col_index = weekday_to_col_index.get(weekday)
			if col_index is not None and col_index < len(pp):
				if pp[col_index] == '1':
					shift = "WW"
				else:
					shift = ''
				if shift:
					if not frappe.db.exists("Shift Assignment", {
						'employee': employee,
						'start_date': date,
						# 'end_date': date,
						'docstatus': ['!=', 2]
					}):
						doc = frappe.new_doc('Shift Assignment')
						doc.employee = employee
						doc.shift_type = shift
						doc.department = department
						doc.weekoff_upload = schedule_name
						frappe.log_error(date)
						doc.start_date = date
						doc.end_date = date
						doc.save(ignore_permissions=True)
						doc.submit()
						frappe.db.commit()
					else:
						if  frappe.db.exists("Shift Assignment", {
							'employee': employee,
							'start_date': date,
							# 'end_date': date,
							'docstatus': ['!=', 2]}):
							sa=frappe.get_doc("Shift Assignment", {'employee': employee,'start_date': date,'docstatus': ['!=', 2]})
							if sa.docstatus==0:
								sa.delete()
							else:
								sa.cancel()
							doc = frappe.new_doc('Shift Assignment')
							doc.employee = employee
							doc.shift_type = shift
							doc.department = department
							doc.weekoff_upload = schedule_name
							frappe.log_error(date)
							doc.start_date = date
							doc.end_date = date
							doc.save(ignore_permissions=True)
							doc.submit()
							frappe.db.commit()



@frappe.whitelist()
def cancel_shift_assignment(args,name):
		sa=frappe.db.get_all("Shift Assignment", {'weekoff_upload':name,'docstatus':1},['name'])
		for s in sa:
			doc = frappe.get_doc('Shift Assignment', s.name)
			doc.cancel()
			frappe.db.commit()