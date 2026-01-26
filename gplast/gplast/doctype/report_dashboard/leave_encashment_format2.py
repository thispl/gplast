import frappe
import io
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from datetime import datetime
from openpyxl.styles import Border, Side
from openpyxl.styles import Alignment, Font, Border, Side
from datetime import datetime
from datetime import timedelta
from datetime import date
from dateutil.relativedelta import relativedelta
import math


def get_full_url(path):
    if path.startswith("http"):
        return path
    else:
        site_url = frappe.utils.get_url()  
        return f"{site_url}{path}"
    
    

@frappe.whitelist()
def download_leave_encashment_format2_excel(employment_type):
    wb = Workbook()
    ws = wb.active
    ws.title = "Leave Encashment"


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
    
    
    ws.merge_cells("A1:U1")
    ws["A1"]="Leave Encashment"
    ws["A1"].alignment= Alignment(horizontal="center")
    ws["A1"].font=Font(bold=True,size=16)
    
    ws["A2"]="S.NO"
    ws["A2"].alignment= Alignment(horizontal="center")
    ws["A2"].font=Font(bold=True,size=12)
    ws["B2"]="E.CODE"
    ws["B2"].alignment= Alignment(horizontal="center")
    ws["B2"].font=Font(bold=True,size=12)
    ws["C2"]="NAME"
    ws["C2"].alignment= Alignment(horizontal="center")
    ws["C2"].font=Font(bold=True,size=12)
    ws["D2"]="GENDER"
    ws["D2"].alignment= Alignment(horizontal="center")
    ws["D2"].font=Font(bold=True,size=12)
    ws["E2"]="DESIGNATION"
    ws["E2"].alignment= Alignment(horizontal="center")
    ws["E2"].font=Font(bold=True,size=12)
    ws["F2"]="QUALIFICATION"
    ws["F2"].alignment= Alignment(horizontal="center")
    ws["F2"].font=Font(bold=True,size=12)
    ws["G2"]="DOJ"
    ws["G2"].alignment= Alignment(horizontal="center")
    ws["G2"].font=Font(bold=True,size=12)
    ws["H2"]="DOB"
    ws["H2"].alignment= Alignment(horizontal="center")
    ws["H2"].font=Font(bold=True,size=12)
    ws["I2"]="AGE"
    ws["I2"].alignment= Alignment(horizontal="center")
    ws["I2"].font=Font(bold=True,size=12)
    ws["J2"]="EXP IN"
    ws["J2"].alignment= Alignment(horizontal="center")
    ws["J2"].font=Font(bold=True,size=12)
    ws["K2"]="EXP OUT"
    ws["K2"].alignment= Alignment(horizontal="center")
    ws["K2"].font=Font(bold=True,size=12)
    ws["L2"]="EXP TOTAL"
    ws["L2"].alignment= Alignment(horizontal="center")
    ws["L2"].font=Font(bold=True,size=12)
    ws["M2"]="S/W"
    ws["M2"].alignment= Alignment(horizontal="center")
    ws["M2"].font=Font(bold=True,size=12)
    ws["N2"]="DEPT"
    ws["N2"].alignment= Alignment(horizontal="center")
    ws["N2"].font=Font(bold=True,size=12)
    ws["O2"]="COST CENTRE"
    ws["O2"].alignment= Alignment(horizontal="center")
    ws["O2"].font=Font(bold=True,size=12)
    ws["P2"]="EL CREDIT"
    ws["P2"].alignment= Alignment(horizontal="center")
    ws["P2"].font=Font(bold=True,size=12)
    ws["Q2"]="LEAVE TAKEN"
    ws["Q2"].alignment= Alignment(horizontal="center")
    ws["Q2"].font=Font(bold=True,size=12)
    ws["R2"]="BALANCE"
    ws["R2"].alignment= Alignment(horizontal="center")
    ws["R2"].font=Font(bold=True,size=12)
    ws["S2"]="FIXED BASIC"
    ws["S2"].alignment= Alignment(horizontal="center")
    ws["S2"].font=Font(bold=True,size=12)
    ws["T2"]="FIXED CCA"
    ws["T2"].alignment= Alignment(horizontal="center")
    ws["T2"].font=Font(bold=True,size=12)
    ws["U2"]="FIXED HRA"
    ws["U2"].alignment= Alignment(horizontal="center")
    ws["U2"].font=Font(bold=True,size=12)
    ws["V2"]="FIXED SPL"
    ws["V2"].alignment= Alignment(horizontal="center")
    ws["V2"].font=Font(bold=True,size=12)
    ws["W2"]="TOTAL"
    ws["W2"].alignment= Alignment(horizontal="center")
    ws["W2"].font=Font(bold=True,size=12)
    ws["X2"]="LEAVE ENCASHMENT"
    ws["X2"].alignment= Alignment(horizontal="center")
    ws["X2"].font=Font(bold=True,size=12)
    
    
    column_widths = {
        "A": 10, "B": 15, "C": 25, "D": 10, "E": 20, "F": 18, "G": 15, "H": 15,
        "I": 10, "J": 10, "K": 10, "L": 14, "M": 10, "N": 15, "O": 15, "P": 15,
        "Q": 15, "R": 15, "S": 15, "T": 15, "U": 15, "V": 15, "W": 15, "X": 20
    }

    
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width
    

    year = date.today().year

    first_date = date(year, 1, 1)
    last_date = date(year, 12, 31)
    
    first_date_str = first_date.strftime("%d-%m-%Y")
    last_date_str = last_date.strftime("%d-%m-%Y")
    
    frappe.log_error(message=first_date_str, title="first_date")
    frappe.log_error(message=last_date_str, title="last_date")
    frappe.log_error(message=year, title="year")
    
    
      
  
    leave_encashment = frappe.get_all("Leave Encashment",filters={"docstatus":"1"},fields=["name","leave_period","employee","encashable_days","leave_balance","encashment_amount"])
    
    for idx, i in enumerate(leave_encashment, start=1):
        frappe.log_error(message=i.name, title="LE")
        
        if not i.leave_period or not i.employee:
            continue

        
        leave_period_valid = frappe.get_value(
            "Leave Period",
            {
                "name": i.leave_period,
                "from_date": [">=", first_date],
                "to_date": ["<=", last_date]
                
            },
            "name"
        )

        if leave_period_valid:
            frappe.log_error(message= leave_period_valid , title="lp")	
            
            # emp_filters = {"name": i.employee}

            # if employment_type == "Apprentice":
            #     emp_filters["employment_type"] = "Apprentice"
            # elif employment_type == "Regular":
            #      emp_filters["employment_type"] =  ["!=", "Apprentice"]   
            
    
            # emps = frappe.get_all("Employee", filters=emp_filters, fields=["name","employee_name","gender","designation","date_of_joining","date_of_birth","employee_agent_id","previous_experience","department","payroll_cost_center","basic","bank_ac_no"])
            
            emp_filters = {"name": i.employee}
            fields=["name","employee_name","gender","designation","date_of_joining","date_of_birth","employee_agent_id","previous_experience","department","payroll_cost_center","basic","bank_ac_no","employee_category","cca","house_rent_allowance","special_allowance"]

            if employment_type :
                emp_filters["employment_type"] = employment_type
                emps = frappe.get_all("Employee", filters=emp_filters, fields=fields)
                
            # elif employment_type == "Regular":
                
            #     employees_with_type = frappe.get_all("Employee", filters={**emp_filters, "employment_type": ["!=", "Apprentice"]}, fields=fields)
            #     employees_null_type = frappe.get_all("Employee", filters={**emp_filters, "employment_type": ["=", None]}, fields=fields)

            #     emps = employees_with_type + employees_null_type
            # else:
                
            #     emps = frappe.get_all("Employee", filters=emp_filters, fields=fields)
            
            
            if emps:
                
                
                for e in emps:
                    
                #   doj = e.date_of_joining
                #   today = date.today()
                #   diff = relativedelta(today, doj)
                #   years = diff.years
                  
                #   exp_in = years
                #   exp_out = e.previous_experience
                #   exp_total = exp_in + exp_out 
                
                  doj = e.date_of_joining
                  today = date.today()

                  delta_days = (today - doj).days
                  exp_in = round(delta_days / 365.25, 2)  

                  exp_out = e.previous_experience or 0  
                  exp_total = round(exp_in + exp_out, 2)

                  
                  wd = frappe.db.count("Attendance",{"docstatus":"1","status":"Present","employee":e.name,"attendance_date":["between",[first_date,last_date]]})
                  
                  edu_qual = frappe.get_all("Employee Education", filters={"parent": e.name}, fields=["qualification"])
                  qualification = edu_qual[0].qualification if edu_qual else ""

                  el = round(i.encashable_days) - round(i.leave_balance)
                  sal_tot =e.basic+ e.cca + e.house_rent_allowance + e.special_allowance
                   
                  row=[
                      idx,
                      e.name,
                      e.employee_name,
                      "M" if e.gender == "Male" else "F",
                      e.designation,
                      qualification,
                      frappe.format(e.date_of_joining,{"fieldtype":"Date"}) or "",
                      frappe.format(e.date_of_birth,{"fieldtype":"Date"}) or "",
                      e.employee_agent_id,
                      exp_in,
                      e.previous_experience,
                      exp_total,
                      "W"  if e.employee_category=="Worker" else "S",
                      e.department,
                      e.payroll_cost_center,
                      round(i.encashable_days),
                      el,
                      i.leave_balance,
                      e.basic,
                      e.cca,
                      e.house_rent_allowance,
                      e.special_allowance,
                      sal_tot,
                      i.encashment_amount,
                                        
                    ]
                  ws.append(row)
                
                frappe.log_error(message=i.name, title="emp")
    
    
    
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=24):
        for cell in row:
            cell.border = thin_border
    
    for row in ws.iter_rows(min_row=3, max_row=ws.max_row, min_col=1, max_col=24):
        for idx, cell in enumerate(row, start=1):
            cell.border = thin_border
            if idx in [1, 2, 9, 10, 11,14,15,16, 12,19,20,21,22]:  # For numeric/id/exp fields
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif idx in [3, 5, 6]:  # For names, dept, designation
                cell.alignment = Alignment(horizontal="left", vertical="center")
            elif idx in [23,24]:  # For names, dept, designation
                cell.alignment = Alignment(horizontal="right", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="center", vertical="center")
        
    
    xls_file = io.BytesIO()
    wb.save(xls_file)
    xls_file.seek(0)


    frappe.local.response["filename"] = "Leave Encashment Report.xlsx"
    frappe.local.response["filecontent"] = xls_file.getvalue()
    frappe.local.response["type"] = "download"
