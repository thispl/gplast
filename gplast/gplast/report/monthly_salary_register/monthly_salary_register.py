# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils import flt
import erpnext
from openpyxl import Workbook
from openpyxl.styles import Font

# Create a new Excel workbook
wb = Workbook()
ws = wb.active
from frappe.utils.data import add_days, today
from frappe.utils import  formatdate,get_last_day, get_first_day, add_days
from frappe.utils import format_datetime
from frappe.utils import (
	add_days,
	cint,
	cstr,
	date_diff,
	flt,
	formatdate,
	get_first_day,
	get_link_to_form,
	getdate,
	money_in_words,
	rounded,
)


def execute(filters=None):
	if not filters:
		filters = {}
	currency = None
	if filters.get("currency"):
		currency = filters.get("currency")
	company_currency = erpnext.get_company_currency(filters.get("company"))
	salary_slips = get_salary_slips(filters, company_currency)
	if not salary_slips:
		return [], []

	columns = get_columns()

	data = []
	for ss in salary_slips:
		dob = frappe.db.get_value('Employee', ss.employee, 'date_of_birth') or ""
		doj=frappe.db.get_value('Employee',ss.employee,'date_of_joining') or "",
		row = [
			ss.employee,
			ss.employee_name,
			 formatdate(dob, "dd-MM-yyyy") if dob else "", 
			 formatdate(doj, "dd-MM-yyyy") if doj else "",
			 frappe.db.get_value('Employee',ss.employee,'department') or "", 
			 frappe.db.get_value('Employee',ss.employee,'designation') or "",
			 formatdate(ss.start_date, "dd-MM-yyyy"),
			 formatdate(ss.end_date, "dd-MM-YYY"),
			 ss.payment_days or 0,
			 frappe.db.get_value('Employee',ss.employee,'basic') or 0,
			 frappe.db.get_value('Employee',ss.employee,'cca') or 0,
			 frappe.db.get_value('Employee',ss.employee,'house_rent_allowance') or 0,
			 frappe.db.get_value('Employee',ss.employee,'special_allowance') or 0,
			 frappe.db.get_value('Employee',ss.employee,'shift_allowance') or 0,
			 frappe.db.get_value('Employee',ss.employee,'other_allowance') or 0,
			 (int(frappe.db.get_value('Employee',ss.employee,'basic') or 0)+
			 int(frappe.db.get_value('Employee',ss.employee,'cca') or 0)+
			 int(frappe.db.get_value('Employee',ss.employee,'house_rent_allowance') or 0)+
			 int(frappe.db.get_value('Employee',ss.employee,'special_allowance') or 0)+
			 int(frappe.db.get_value('Employee',ss.employee,'shift_allowance') or 0)+
			 int(frappe.db.get_value('Employee',ss.employee,'other_allowance') or 0)) or 0,
			 int(frappe.get_value('Salary Detail',{'salary_component':"Basic",'parent':ss.name},["amount"]) or 0),
			 int(frappe.get_value('Salary Detail',{'salary_component':"City Compensatory Allowance",'parent':ss.name},["amount"]) or 0),
			 int(frappe.get_value('Salary Detail',{'salary_component':"House Rent Allowance",'parent':ss.name},["amount"]) or 0),
			 int(frappe.get_value('Salary Detail',{'salary_component':"Special Allowance",'parent':ss.name},["amount"]) or 0),
			 int(frappe.get_value('Salary Detail',{'salary_component':"Shift Allowance",'parent':ss.name},["amount"]) or 0),
			 int(frappe.get_value('Salary Detail',{'salary_component':"Other Allowance",'parent':ss.name},["amount"]) or 0),
			 int(frappe.get_value('Salary Detail',{'salary_component':"Overtime",'parent':ss.name},["amount"]) or 0),
			 int(frappe.get_value('Salary Detail',{'salary_component':"ERND ARR",'parent':ss.name},["amount"]) or 0),
			 int(frappe.get_value('Salary Detail',{'salary_component':"Basic ARR",'parent':ss.name},["amount"]) or 0),
			 int(frappe.get_value('Salary Detail',{'salary_component':"HRA ARR",'parent':ss.name},["amount"]) or 0),
			 int(frappe.get_value('Salary Detail',{'salary_component':"Heat Allowance",'parent':ss.name},["amount"]) or 0),
			 int(frappe.get_value('Salary Detail',{'salary_component':"Other",'parent':ss.name},["amount"]) or 0),
			 ss.gross_pay,
			 int(frappe.get_value('Salary Detail',{'salary_component':"Provident Fund",'parent':ss.name},["amount"]) or 0),
			 int(frappe.get_value('Salary Detail',{'salary_component':"Employee State Insurance",'parent':ss.name},["amount"]) or 0),
			 int(frappe.get_value('Salary Detail',{'salary_component':"ILWA",'parent':ss.name},["amount"]) or 0),
			 int(frappe.get_value('Salary Detail',{'salary_component':"Tax Deducted AT Source",'parent':ss.name},["amount"]) or 0),
			 int(frappe.get_value('Salary Detail',{'salary_component':"Rent",'parent':ss.name},["amount"]) or 0),
			 int(frappe.get_value('Salary Detail',{'salary_component':"Canteen",'parent':ss.name},["amount"]) or 0),
			 int(frappe.get_value('Salary Detail',{'salary_component':"Professional Tax",'parent':ss.name},["amount"]) or 0),
			 ss.total_deduction or 0,
			 ss.net_pay or 0 
			]
		data.append(row)

	return columns, data

def get_columns():
	
	columns = [
         _("EMPLOYEE") + "::120",		
		 _("EMPLOYEE NAME") + "::150",
		_("DATE OF BIRTH") + ":Data:120",
		_("DATE OF JOINING") + ":Data:120",
		_("DEPARTMENT") + ":Data:100",
		_("DESIGNATION") + ":Data:100",
		_("FROM DATE") + ":Data:110",
		_("TO DATE") + ":Data:100",
		_("PAID DAYS") + ":Data:100",
		_("FIXED BASIC") + ":Data:150",
		_("FIXED CCA") + ":Data:150",
		_("FIXED HOUSE RENT ALLOWANCE") + ":Data:150",
		_("FIXED SPECIL ALLOWANCE") + ":Data:150",
		_("FIXED SHIFT ALLOWANCE") + ":Data:150",
		_("FIXED OTHER ALLOWANCE") + ":Data:150",
		_("FIXED GROSS") + ":Data:150",
		_("EARNED BASIC") + ":Data:150",
		_("EARNED CCA") + ":Data:150",
		_("EARNED HOUSE RENT ALLOWANCE") + ":Data:150",
		_("EARNED SPECIAL ALLOWANCE") + ":Data:150",
		_("EARNED SHIFT ALLOWANCE") + ":Data:150",
		_("EARNED OTHER ALLOWANCE") + ":Data:150",
		_("EARNED OVER TIME") + ":Data:150",
		_("EARNED ATTRIBUTE") + ":Data:150",
		_("BASIC ARR") + ":Data:150",
		_("HOUSE RENT ALLOWNCE ARR") + ":Data:150",
		_("HEAT ALLOWNCE ") + ":Data:150",
		_("OTHER ADD") + ":Data:150",
		_("EARNED TOTAL") + ":Data:150",
		_("EARNED PF") + ":Data:150",
		_("EARNED ESI") + ":Data:150",
		_("ILWA") + ":Data:100",
		_("TDS") + ":Data:100",
		_("RENT") + ":Data:150",
		_("CANTEEN") + ":Data:100",
		_("PROFESSIONAL TAX") + ":Data:150",
		_("DEDUCTION TOTAL") + ":Data:150",
		_("NET PAY") + ":Data:150"
	]
	bold_font = Font(bold=True)
	for col_num, column_name in enumerate(columns, 1):
		cell = ws.cell(row=1, column=col_num)
		cell.value = column_name
		cell.font = bold_font
	return columns
	

def get_salary_slips(filters, company_currency):
	filters.update({"from_date": filters.get("from_date"), 
	"to_date": filters.get("to_date")
	})
	conditions, filters = get_conditions(filters, company_currency)
	salary_slips = frappe.db.sql(
		"""select * from `tabSalary Slip` where docstatus != 2 and %s order by employee"""% conditions,
		filters,
		as_dict=1,
	)
	return salary_slips or []

def get_conditions(filters, company_currency):
	conditions = ""
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
	if filters.get("docstatus"):
		conditions += "docstatus = {0}".format(doc_status[filters.get("docstatus")])
	if filters.get("from_date"):
		conditions += " and start_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " and end_date <= %(to_date)s"
	if filters.get("company"):
		conditions += " and company = %(company)s"
	if filters.get("currency") and filters.get("currency") != company_currency:
		conditions += " and currency = %(currency)s"

	user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if not ("System Manager" in user_roles):
		emp = frappe.db.get_value("Employee", {"user_id": user}, "name")
		if emp:
			conditions += " and employee = %(employee)s"
			filters["employee"] = emp
	


	return conditions, filters

def get_employee_doj_map():
	return frappe._dict(frappe.db.sql("""SELECT employee,date_of_joining FROM `tabEmployee` """))

@frappe.whitelist()
def get_to_date(from_date):
	return get_last_day(from_date)