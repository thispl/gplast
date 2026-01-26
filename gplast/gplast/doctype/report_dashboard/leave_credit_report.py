import frappe
import io
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from datetime import datetime
from openpyxl.styles import Border, Side
from openpyxl.styles import Alignment, Font, Border, Side
from datetime import datetime
from datetime import timedelta







@frappe.whitelist()
def download_leave_credit_excel(from_date, to_date, company=None, employee=None):
	wb = Workbook()
	ws = wb.active
	ws.title = "Leave Credit Report"


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
 
 
	for row in ws.iter_rows(min_row=1, max_row=2, min_col=1, max_col=11):
		for cell in row:
			cell.border = thin_border

	ws.merge_cells("A1:K1")
	ws["A1"]="Leave Credit Report"
	ws["A1"].font=Font(size=16)
	ws["A1"].alignment= Alignment(horizontal="center",vertical="center")


	ws["A2"]="SI.No."
	ws["A2"].alignment= Alignment(horizontal="center",vertical="center")
	ws["A2"].font=Font(size=12)
	ws["B2"]="EMP.No"
	ws["B2"].alignment= Alignment(horizontal="center",vertical="center")
	ws["B2"].font=Font(size=12)
	ws["C2"]="NAME"
	ws["C2"].alignment= Alignment(horizontal="center",vertical="center")
	ws["C2"].font=Font(size=12)
	ws["D2"]="DEPARTMENT"
	ws["D2"].alignment= Alignment(horizontal="center",vertical="center")
	ws["D2"].font=Font(size=12)
	ws["E2"]="COMPANY"
	ws["E2"].alignment= Alignment(horizontal="center" ,vertical="center")
	ws["E2"].font=Font(size=12)
	ws["F2"]="UNIT"
	ws["F2"].alignment= Alignment(horizontal="center", vertical="center")
	ws["F2"].font=Font(size=12)
	ws["G2"]="CREDIT DATE"
	ws["G2"].alignment= Alignment(horizontal="center",vertical="center")
	ws["G2"].font=Font(size=12)
	ws["H2"]="LEAVE TYPE"
	ws["H2"].alignment= Alignment(horizontal="center",vertical="center")
	ws["H2"].font=Font(size=12)
	ws["I2"]="CREDITED"
	ws["I2"].alignment= Alignment(horizontal="center",vertical="center")
	ws["I2"].font=Font(size=12)
	ws["J2"]="TAKEN THIS MONTH"
	ws["J2"].alignment= Alignment(horizontal="center",vertical="center")
	ws["J2"].font=Font(size=12)
	ws["K2"]="BALANCE"
	ws["K2"].alignment= Alignment(horizontal="center",vertical="center")
	ws["K2"].font=Font(size=12)
 
 
	column_widths = {
		"A": 10, "B": 25, "C": 25, "D": 20, "E": 25, "F": 18, "G": 20, "H": 20,
		"I": 20, "J": 20, "K": 20 
	}
 
	for col, width in column_widths.items():
		ws.column_dimensions[col].width = width
	
	
	
	
	filters = {"from_date": ["between", [from_date, to_date]]}

	if company:
		filters["company"] = company
	if employee:
		filters["employee"] = employee

	leave_allocations = frappe.db.get_all(
		"Leave Allocation",
		filters=filters,
		fields=[
			"from_date",
			"employee",
			"employee_name",
			"department",
			"company",
			"new_leaves_allocated",
			"leave_type",
		]
	)
  
  
  
  
  
	if leave_allocations:
		for idx, alloc in enumerate(leave_allocations, start=1):
		
			unit=frappe.db.get_value("Employee",{"name":alloc.employee},"unit") or ""
			# unit_str = str(unit)	
			
			leave_apps = frappe.db.sql("""
			SELECT from_date, to_date
			FROM `tabLeave Application`
			WHERE employee = %s
			  AND leave_type = %s
			  AND status = 'Approved'
              AND docstatus="1"
			  AND (
					(from_date BETWEEN %s AND %s) OR
					(to_date BETWEEN %s AND %s) OR
					(%s BETWEEN from_date AND to_date) OR
					(%s BETWEEN from_date AND to_date)
				  )
			""", (alloc.employee, alloc.leave_type,
				from_date, to_date, from_date, to_date,
				from_date, to_date), as_dict=True)

			leaves_taken = 0
			report_start = datetime.strptime(from_date, "%Y-%m-%d").date()
			report_end = datetime.strptime(to_date, "%Y-%m-%d").date()

			for app in leave_apps:
				leave_start = app.from_date
				leave_end = app.to_date

				overlap_start = max(report_start, leave_start)
				overlap_end = min(report_end, leave_end)

				if overlap_start <= overlap_end:
					leaves_taken += (overlap_end - overlap_start).days + 1

			
			balance = (alloc.new_leaves_allocated or 0) - leaves_taken
	
   
   
   
			row=[
	   			idx,
				alloc.employee,
				alloc.employee_name,
				alloc.department,
				alloc.company,
				unit,
				alloc.from_date.strftime("%d-%m-%Y") if alloc.from_date.strftime else "",
				alloc.leave_type,
				alloc.new_leaves_allocated,
				leaves_taken,
				balance
		  		]
			ws.append(row)
			
		 
	for row in ws.iter_rows(min_row=3, max_row=ws.max_row, min_col=1, max_col=11):
		for cell in row:
			cell.border = thin_border     
		 
		
 
 
	
 
 




	xls_file = io.BytesIO()
	wb.save(xls_file)
	xls_file.seek(0)


	frappe.local.response["filename"] = "Leave Credit Report.xlsx"
	frappe.local.response["filecontent"] = xls_file.getvalue()
	frappe.local.response["type"] = "download"