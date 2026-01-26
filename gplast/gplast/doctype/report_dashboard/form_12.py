import frappe
import io
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from datetime import datetime
from openpyxl.styles import Border, Side
from openpyxl.styles import Alignment, Font, Border, Side
from datetime import datetime
from datetime import timedelta


def get_full_url(path):
	if path.startswith("http"):
		return path
	else:
		site_url = frappe.utils.get_url()  
		return f"{site_url}{path}"
	
	

@frappe.whitelist()
def download_form12_excel(company=None):
	wb = Workbook()
	ws = wb.active
	ws.title = "Form 12"
	
	if company :
		employee_records = frappe.db.get_all("Employee",filters={"company":company,"status":"Active"},fields=["employee_name","name","gender","father_name","date_of_birth","current_address","permanent_address","employee_aadhar_number","date_of_joining","designation","_uan_no","esi_number","bank_ac_no","bank_name","photo_attachment","cell_number","company_email","signature_attachment","relieving_date","relieving_reason"])
		
	thin_border = Border(
		left=Side(style='thin'),
		right=Side(style='thin'),
		top=Side(style='thin'),
		bottom=Side(style='thin')
	)
	border = Border(
		left=Side(style='medium'),
		right=Side(style='medium'),
		top=Side(style='medium'),
		bottom=Side(style='medium')
	)
 
 
	for row in ws.iter_rows(min_row=1, max_row=3, min_col=1, max_col=23):
		for cell in row:
			cell.border = thin_border
 
	# for cell in ws[3]:
	# 	cell.border = border 
	
	ws.merge_cells("A1:W1")
	ws["A1"]="Form No.12 (Prescribed under rules 80, 86)"
	ws["A1"].font=Font(size=12)
	ws["A1"].alignment= Alignment(horizontal="center")
	
	
	
	ws.merge_cells("A2:W2")
	ws["A2"]="REGISTER OF ADULT WORKERS AND YOUNG PERSONS"
	ws["A2"].font=Font(size=16)
	ws["A2"].alignment= Alignment(horizontal="center")
	
	
	ws.merge_cells("A3:H3")
	ws["A3"]="Name and Address of the Factory:"
	ws["A3"].font=Font(size=12)
	
	
	ws.merge_cells("I3:W3")
	ws["I3"]="Registration No:"
	ws["I3"].font=Font(size=12)
	
	
 
 
	
	ws["A4"]="SI.No"
	ws["A4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["A4"].font=Font(size=12)
 
	ws["B4"]="Name of the worker"
	ws["B4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["B4"].font=Font(size=12)
 
	ws["C4"]="Worker Identity No."
	ws["C4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["C4"].font=Font(size=12)
 
	ws["D4"]="Gender"
	ws["D4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["D4"].font=Font(size=12)
 
	ws["E4"]="Father/Spouse Name"
	ws["E4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["E4"].font=Font(size=12)
 
	ws["F4"]="Date of Birth"
	ws["F4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["F4"].font=Font(size=12)
 
	ws["G4"]="Present Address"
	ws["G4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["G4"].font=Font(size=12)
 
	ws["H4"]="Permanent Address"
	ws["H4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["H4"].font=Font(size=12)
 
	ws["I4"]="Aadhaar No."
	ws["I4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["I4"].font=Font(size=12)
 
	ws["J4"]="Date of entry into service"
	ws["J4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["J4"].font=Font(size=12)
 
	ws["K4"]="Designation/Nature of work"
	ws["K4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["K4"].font=Font(size=12)
 
	ws["L4"]="EPF No./UAN No."
	ws["L4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["L4"].font=Font(size=12)
 
	ws["M4"]="ESIC No."
	ws["M4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["M4"].font=Font(size=12)
 
	ws["N4"]="Date on which completion of 480 days of service"
	ws["N4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["N4"].font=Font(size=12)
 
	ws["O4"]="Date on which made permanent"
	ws["O4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["O4"].font=Font(size=12)
 
	ws["P4"]="Period of suspension if any"
	ws["P4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["P4"].font=Font(size=12)
 
	ws["Q4"]="Bank A/C No.   Name of Bank"
	ws["Q4"].font=Font(size=12)
	ws["Q4"].alignment = Alignment(horizontal="center", wrap_text=True,vertical="center")
 
	ws["R4"]="Photo"
	ws["R4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["R4"].font=Font(size=12)
 
	ws["S4"]="Mobile Number"
	ws["S4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["S4"].font=Font(size=12)
 
	ws["T4"]="E-mail ID"
	ws["T4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["T4"].font=Font(size=12)
 
	ws["U4"]="Signature"
	ws["U4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["U4"].font=Font(size=12)
 
	ws["V4"]="Date of Exit"
	ws["V4"].alignment= Alignment(horizontal="center",vertical="center")
	ws["V4"].font=Font(size=12)
 
	ws["W4"]="Reason for Exit"
	ws["W4"].font=Font(size=12)
	ws["W4"].alignment = Alignment(horizontal="center", wrap_text=True,vertical="center")
 
	column_widths = {
		"A": 10, "B": 25, "C": 25, "D": 10, "E": 25, "F": 18, "G": 100, "H": 100,
		"I": 20, "J": 40, "K": 40, "L": 20, "M": 20, "N": 50, "O": 40, "P": 40,
		"Q": 20, "R": 15, "S": 20, "T": 20, "U": 15, "V": 15, "W": 25 
	}

	
	for col, width in column_widths.items():
		ws.column_dimensions[col].width = width
	
	
	
	
	if company and employee_records:
		for idx, emp in enumerate(employee_records, start=1):
	  
	  
			bank_details = ""
			if emp.bank_ac_no:
				bank_details += str(emp.bank_ac_no)
			if emp.bank_name:
				if bank_details:  
					bank_details += "\n"
				bank_details += emp.bank_name
	  
	
			row = [
				idx,
				emp.employee_name,
				emp.name,
				emp.gender,
				emp.father_name,
				emp.date_of_birth.strftime("%d-%m-%Y") if emp.date_of_birth else "",
				emp.current_address,
				emp.permanent_address,
				emp.employee_aadhar_number,
				emp.date_of_joining.strftime("%d-%m-%Y") if emp.date_of_joining else "",
				emp.designation,
				emp._uan_no,
				emp.esi_number,
				"", "", "",  
				bank_details,
				emp.photo_attachment,
				emp.cell_number,
				emp.company_email,
				emp.signature_attachment,
				emp.relieving_date.strftime("%d-%m-%Y") if emp.relieving_date else "",
				emp.relieving_reason
			]
			ws.append(row)
   
			current_row = ws.max_row
			ws.cell(row=current_row, column=17).alignment = Alignment(wrap_text=True)

			
			if emp.photo_attachment:
				photo_url = get_full_url(emp.photo_attachment)
				ws.cell(row=current_row, column=18).value = "View Photo"
				ws.cell(row=current_row, column=18).hyperlink = photo_url
				ws.cell(row=current_row, column=18).font = Font(color="0000FF", underline="single")

			
			if emp.signature_attachment:
				sig_url = get_full_url(emp.signature_attachment)
				ws.cell(row=current_row, column=21).value = "View Signature"
				ws.cell(row=current_row, column=21).hyperlink = sig_url
				ws.cell(row=current_row, column=21).font = Font(color="0000FF", underline="single")
	
	for row in ws.iter_rows(min_row=4, max_row=ws.max_row, min_col=1, max_col=23):
		for cell in row:
			cell.border = thin_border
	
	
	
	xls_file = io.BytesIO()
	wb.save(xls_file)
	xls_file.seek(0)

	
	frappe.local.response["filename"] = "Form 12.xlsx"
	frappe.local.response["filecontent"] = xls_file.getvalue()
	frappe.local.response["type"] = "download"
	