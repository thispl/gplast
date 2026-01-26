import frappe
import datetime
from frappe.utils import cstr, add_days, date_diff, getdate, format_date
from frappe import _, bold,msgprint
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
from frappe.utils.file_manager import get_file
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from datetime import date, timedelta, datetime
import openpyxl
from openpyxl import Workbook
import openpyxl
import xlrd
import re
from frappe.utils import  formatdate,get_last_day, get_first_day, add_days
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import GradientFill, PatternFill
from six import BytesIO, string_types
from openpyxl.styles.numbers import FORMAT_PERCENTAGE
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,format_date,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from datetime import datetime

@frappe.whitelist()
def download():
	filename = 'Monthly Salary Register'
	test = build_xlsx_response(filename)
	

def make_xlsx(data, sheet_name=None, wb=None, column_widths=None):
	args = frappe.local.form_dict
	column_widths = column_widths or []
	if wb is None:
		wb = openpyxl.Workbook()
	ws = wb.create_sheet(sheet_name, 0)
	ws.append([ _("S.No"),
		_("EMPLOYEE") ,		
		 _("EMPLOYEE NAME") ,
		_("DESIGNATION") ,
		_("DATE OF BIRTH") ,
		_("DATE OF JOINING") ,
		_("DEPARTMENT") ,
		_("FROM DATE"),
		_("TO DATE"),
		_("MONTH DAYS"),
		_("ABSENT DAYS"),
		_("PAID DAYS") ,
		_("BASIC") ,
		_("CCA") ,
		_("HRA") ,
		_("SPECIL ALLOWANCE") ,
		_("SHIFT ALLOWANCE") ,
		_("TA"),
		_("CA"),
		_("EDUCATION ALLOWANCE"),
		_("FVO"),
		_("HELP ALLOWANCE"),
		_("MAGAZINE ALLOWANCE"),
		_("MEDICAL ALLOWANCE"),
		_("UNIFORM ALLOWANCE"),
		_("ACCOMM.ALL"),
		_("OTHER ALLOWANCE") ,
		_("GROSS") ,
		_("EARNED BASIC") ,
		_("EARNED CCA") ,
		_("EARNED HRA") ,
		_("EARNED SPL ALL") ,
		_("EARNED SHIFT ALLOWANCE") ,
		_("EARNED TA"),
		_("EARNED CA"),
		_("EARNED EDU.ALL"),
		_("EARNED FVO"),
		_("EARNED HELP ALLOWANCE"),
		_("EARNED MAGAZINE ALLOWANCE"),
		_("EARNED MEDICAL ALLOWANCE"),
		_("EARNED UNIFORM ALLOWANCE"),
		_("EARNED ACCOMM.ALL"),
		_("EARNED OTHER ALLOWANCE"),
		_("EARNED TOTAL"),
		_("EARNED OVER TIME") ,
		_("EARNED TIFFIN ALLO") ,
		_("EARNED ATTENDANCE BONUS") ,
		_("EARNED SHIFT ALLO") ,
		_("BASIC ARR") ,
		_("HRA ARR") ,
		_("HEAT ALLOWANCE ") ,
		_("OTHER ADD") ,
		_("EARNED TOTAL ARR"),
		_("EARNED PF ELIG W") ,
		_("EARNED ESI ELIG W") ,
		_("EARNED PF") ,
		_("EARNED ESI") ,
		_("ILWA") ,
		_("TDS") ,
		_("RENT") ,
		_("CANTEEN") ,
		_("PROFESSIONAL TAX") ,
		_("LATE/OD"),
		_("LWF"),
		_("DEDUCTION TOTAL") ,
		_("NET PAY") 
	])
	
	for header in ws.iter_rows(min_row=1, max_row=1, min_col=1, max_col=65):
		for cell in header:
			cell.font = Font(bold=True)
	data = get_data(args)
	for d in data:
		ws.append(d)

	if data:
		totals = []
		for col_idx in range(len(data[0])):
			try:
				col_sum = sum(float(row[col_idx] or 0) for row in data)
				totals.append(round(col_sum, 2))
			except Exception:	
				totals.append('')  

		last_row = ws.max_row + 1  
		ws.merge_cells(start_row=last_row, start_column=1, end_row=last_row, end_column=9)
		cell = ws.cell(row=last_row, column=1, value="TOTAL")
		cell.alignment = Alignment(horizontal="center", vertical="center")
		cell.font = Font(bold=True)

		for idx, val in enumerate(totals[9:], start=10):  
			ws.cell(row=last_row, column=idx, value=val)

	
	thin_border = Border(
		left=Side(style='thin'),
		right=Side(style='thin'),
		top=Side(style='thin'),
		bottom=Side(style='thin')
	)

	for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
		for cell in row:
			cell.border = thin_border
			
	xlsx_file = BytesIO()
	wb.save(xlsx_file)
	return xlsx_file

def build_xlsx_response(filename):
	xlsx_file = make_xlsx(filename)
	# write out response as a xlsx type
	frappe.response['filename'] = filename + '.xlsx'
	frappe.response['filecontent'] = xlsx_file.getvalue()
	frappe.response['type'] = 'binary'

@frappe.whitelist()
def get_data(args):
	data = []
	salary_slips = frappe.db.sql(
		"""
		SELECT * FROM `tabSalary Slip`
		WHERE start_date BETWEEN %s AND %s AND docstatus !=2 """ ,
		(args.from_date, args.to_date),
		as_dict=True
	)
	idx =0
	esi_elig = 0
	for ss in salary_slips:
		dob = frappe.db.get_value('Employee', ss.employee, 'date_of_birth') or ""
		doj=frappe.db.get_value('Employee',ss.employee,'date_of_joining') or ""
		idx+=1
		emp = frappe.db.get_value(
			"Employee",
			ss.employee,
			[
				"designation","date_of_birth","date_of_joining", "department","basic",
				"cca",
				"house_rent_allowance",
				"special_allowance",
				"shift_allowance",
				"ta_allowance",
				"conveyance_allowance",
				"education_allowance",
				"fvo_allowance",
				"help_allowance",
				"magazine_allowances",
				"medical_allowances",
				"uniform_allowance",
				"accommodation_allowance",
				"other_allowance",
				"salary_total"
			],
			as_dict=True
		) or {}

		total_allowance = sum(emp.get(f, 0) or 0 
			for f in [
				"ta_allowance",
				"conveyance_allowance",
				"education_allowance",
				"fvo_allowance",
				"help_allowance",
				"magazine_allowances",
				"medical_allowances",
				"uniform_allowance",
				"accommodation_allowance"
				
			]
		)
		
		total_fixed_gross = (
		(emp.basic or 0)
		+ (emp.cca or 0)
		+ (emp.house_rent_allowance or 0)
		+ (emp.special_allowance or 0)
		+ (emp.shift_allowance or 0)
		+ total_allowance
	)
	
		if emp.salary_total < 21000:
			esi_elig = ss.gross_pay + ((int(frappe.get_value('Salary Detail',{'salary_component':"Overtime",'parent':ss.name},["amount"]) or 0)
				+int(frappe.get_value('Salary Detail',{'salary_component':"ERND ARR",'parent':ss.name},["amount"]) or 0)
				+int(frappe.get_value('Salary Detail',{'salary_component':"Basic ARR",'parent':ss.name},["amount"]) or 0)
				+int(frappe.get_value('Salary Detail',{'salary_component':"HRA ARR",'parent':ss.name},["amount"]) or 0)
				+int(frappe.get_value('Salary Detail',{'salary_component':"Heat Allowance",'parent':ss.name},["amount"]) or 0)
				+int(frappe.get_value('Salary Detail',{'salary_component':"Other",'parent':ss.name},["amount"]) or 0)
				))
		else:
			esi_elig = 0

		# frappe.errprint(total_fixed_gross)
		# frappe.errprint(ss)
		row = [idx,ss.employee, ss.employee_name,
			#  frappe.db.get_value('Employee',ss.employee,'designation') or "",
			#  frappe.db.get_value('Employee',ss.employee,'date_of_birth') or "", 
			#  frappe.db.get_value('Employee',ss.employee,'date_of_birth') or "",
			#  frappe.db.get_value('Employee',ss.employee,'department') or "", 
			emp.get("designation", ""),
			formatdate(dob, "dd-MM-yyyy") if dob else "", 
			formatdate(doj, "dd-MM-yyyy") if doj else "",
			emp.get("department", ""),
			formatdate(ss.start_date, "dd-MM-yyyy"),
			formatdate(ss.end_date, "dd-MM-YYY"),
			ss.total_working_days or 0,
			ss.absent_days + ss.leave_without_pay or 0,
			ss.payment_days or 0,
			#  frappe.db.get_value('Employee',ss.employee,'basic') or 0,
			#  frappe.db.get_value('Employee',ss.employee,'cca') or 0,
			#  frappe.db.get_value('Employee',ss.employee,'house_rent_allowance') or 0,
			#  frappe.db.get_value('Employee',ss.employee,'special_allowance') or 0,
			#  frappe.db.get_value('Employee',ss.employee,'shift_allowance') or 0,
			#  frappe.db.get_value('Employee',ss.employee,'ta_allowance') or 0,
			#  frappe.db.get_value('Employee',ss.employee,'conveyance_allowance') or 0,
			#  frappe.db.get_value('Employee',ss.employee,'education_allowance') or 0,
			#  frappe.db.get_value('Employee',ss.employee,'fvo_allowance') or 0,
			#  frappe.db.get_value('Employee',ss.employee,'help_allowance') or 0,
			#  frappe.db.get_value('Employee',ss.employee,'magazine_allowances') or 0,
			#  frappe.db.get_value('Employee',ss.employee,'medical_allowances') or 0,
			#  frappe.db.get_value('Employee',ss.employee,'uniform_allowance') or 0,
			#  frappe.db.get_value('Employee',ss.employee,'accommodation_allowance') or 0,
			#  frappe.db.get_value('Employee',ss.employee,'other_allowance') or 0,
			emp.get("basic", 0),
			emp.get("cca", 0),
			emp.get("house_rent_allowance", 0),
			emp.get("special_allowance", 0),
			emp.get("shift_allowance", 0),
			emp.get("ta_allowance", 0),
			emp.get("conveyance_allowance", 0),
			emp.get("education_allowance", 0),
			emp.get("fvo_allowance", 0),
			emp.get("help_allowance", 0),
			emp.get("magazine_allowances", 0),
			emp.get("medical_allowances", 0),
			emp.get("uniform_allowance", 0),
			emp.get("accommodation_allowance", 0),
			# emp.get("other_allowance", 0),
			total_allowance,
			#  (int(frappe.db.get_value('Employee',ss.employee,'basic') or 0)+
			#  int(frappe.db.get_value('Employee',ss.employee,'cca') or 0)+
			#  int(frappe.db.get_value('Employee',ss.employee,'house_rent_allowance') or 0)+
			#  int(frappe.db.get_value('Employee',ss.employee,'special_allowance') or 0)+
			#  int(frappe.db.get_value('Employee',ss.employee,'shift_allowance') or 0)+
			#  int(frappe.db.get_value('Employee',ss.employee,'other_allowance') or 0)) or 0,
			total_fixed_gross,
				int(frappe.get_value('Salary Detail',{'salary_component':"Basic",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"City Compensatory Allowance",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"House Rent Allowance",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"Special Allowance",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"Shift Allowance",'parent':ss.name},["amount"]) or 0),
				round(((emp.get("ta_allowance", 0) or 0) / (ss.total_working_days or 1)) * (ss.payment_days or 0), 0),
				round(((emp.get("conveyance_allowance", 0) or 0) / (ss.total_working_days or 1)) * (ss.payment_days or 0), 0),
				round(((emp.get("education_allowance", 0) or 0) / (ss.total_working_days or 1)) * (ss.payment_days or 0), 0),
				round(((emp.get("fvo_allowance", 0) or 0) / (ss.total_working_days or 1)) * (ss.payment_days or 0), 0),
				round(((emp.get("help_allowance", 0) or 0) / (ss.total_working_days or 1)) * (ss.payment_days or 0), 0),
				round(((emp.get("magazine_allowances", 0) or 0) / (ss.total_working_days or 1)) * (ss.payment_days or 0), 0),
				round(((emp.get("medical_allowances", 0) or 0) / (ss.total_working_days or 1)) * (ss.payment_days or 0), 0),
				round(((emp.get("uniform_allowance", 0) or 0) / (ss.total_working_days or 1)) * (ss.payment_days or 0), 0),
				round(((emp.get("accommodation_allowance", 0) or 0) / (ss.total_working_days or 1)) * (ss.payment_days or 0), 0),
				round((total_allowance / (ss.total_working_days or 1)) * (ss.payment_days or 0), 0),
			# int(frappe.get_value('Salary Detail',{'salary_component':"Other Allowance",'parent':ss.name},["amount"]) or 0),
				ss.gross_pay,
				int(frappe.get_value('Salary Detail',{'salary_component':"Overtime",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"Tiffen Allowance",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"Attendance Bonus",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"Earn Shift Allowance",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"Basic ARR",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"HRA ARR",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"Heat Allowance",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"Other",'parent':ss.name},["amount"]) or 0),
				(int(frappe.get_value('Salary Detail',{'salary_component':"Overtime",'parent':ss.name},["amount"]) or 0)
				+int(frappe.get_value('Salary Detail',{'salary_component':"Tiffen Allowance",'parent':ss.name},["amount"]) or 0)
				+int(frappe.get_value('Salary Detail',{'salary_component':"Attendance Bonus",'parent':ss.name},["amount"]) or 0)
				+int(frappe.get_value('Salary Detail',{'salary_component':"Earn Shift Allowance",'parent':ss.name},["amount"]) or 0)
				+int(frappe.get_value('Salary Detail',{'salary_component':"Basic ARR",'parent':ss.name},["amount"]) or 0)
				+int(frappe.get_value('Salary Detail',{'salary_component':"HRA ARR",'parent':ss.name},["amount"]) or 0)
				+int(frappe.get_value('Salary Detail',{'salary_component':"Heat Allowance",'parent':ss.name},["amount"]) or 0)
				+int(frappe.get_value('Salary Detail',{'salary_component':"Other",'parent':ss.name},["amount"]) or 0)
				),
				(int(frappe.get_value('Salary Detail', {'salary_component': "Basic", 'parent': ss.name}, "amount") or 0)
				+ int(frappe.get_value('Salary Detail', {'salary_component': "City Compensatory Allowance", 'parent': ss.name}, "amount") or 0)
				+ int(frappe.get_value('Salary Detail', {'salary_component': "Special Allowance", 'parent': ss.name}, "amount") or 0)
				+ int(frappe.get_value('Salary Detail', {'salary_component': "Basic ARR", 'parent': ss.name}, "amount") or 0)),
				esi_elig,
				int(frappe.get_value('Salary Detail',{'salary_component':"Provident Fund",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"Employee State Insurance",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"ILWA",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"Tax Deducted AT Source",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"Rent",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"Canteen",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"Professional Tax",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"Late Penalty",'parent':ss.name},["amount"]) or 0), #late/od
				'' or 0, #lwf
				ss.total_deduction or 0,
				ss.net_pay or 0 
		]
		data.append(row)

	return data
