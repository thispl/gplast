# import frappe
# import os
# from datetime import datetime
# from openpyxl import Workbook
# from openpyxl.styles import Font, Alignment, Border, Side


# @frappe.whitelist()
# def download(from_date, to_date, contractor_name):

#     from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")
#     month_name = from_date_obj.strftime("%B").upper()   
#     year = from_date_obj.strftime("%Y")                 

#     wb = Workbook()
#     ws = wb.active
#     ws.title = "Contract Bill"

#     header_font = Font(bold=True, size=10)
#     title_font = Font(bold=True, size=12)
#     center_align = Alignment(horizontal="center", vertical="center")
#     wrap_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

#     thin_border = Border(
#         left=Side(style="thin"),
#         right=Side(style="thin"),
#         top=Side(style="thin"),
#         bottom=Side(style="thin")
#     )

#     ws.append([])

#     heading = (
#         f"{contractor_name} Contract Bill Details "
#         f"for the month of {month_name} {year}"
#     )

#     ws.merge_cells(start_row=2, start_column=2, end_row=2, end_column=13)
#     cell = ws.cell(row=2, column=2)
#     cell.value = heading
#     cell.font = title_font
#     cell.alignment = Alignment(horizontal="left", vertical="center")
#     cell.border = thin_border

#     ws.row_dimensions[2].height = 30
#     headers = [
#         "Total Days", "S.No", "Emp No", "Name", "Cost Center", "Gender",
#         "Department", "Nature of Work", "Days Worked", "OT Hours", "OT Days",
#         "Wages", "Basic", "Other Allowance", "Heat Allowance", "PF Wages",
#         "Gross Wages", "OT Wages", "Attendance Incentive", "Total Gross Wages",
#         "PF", "ESI", "LWF Employee", "Emp PF", "Emp ESI", "LWF Employer",
#         "Canteen", "Late", "Net Wages", "Canteen Management Contribution",
#         "Absent", "Absent %", "8.33 % Service Tax", "Total", "Deduction"
#     ]

#     row_no = 4
#     col_no = 2  

#     for header in headers:
#         cell = ws.cell(row=row_no, column=col_no)
#         cell.value = header
#         cell.font = header_font
#         cell.alignment = wrap_align
#         cell.border = thin_border

#         ws.column_dimensions[cell.column_letter].width = 18
#         col_no += 1

#     ws.row_dimensions[4].height = 45

#     file_name = f"Contract_Bill_{contractor_name}_{month_name}_{year}.xlsx"
#     file_path = os.path.join(
#         frappe.get_site_path("private", "files"),
#         file_name
#     )

#     wb.save(file_path)
#     frappe.response.filename = file_name
#     frappe.response.filecontent = open(file_path, "rb").read()
#     frappe.response.type = "binary" 


import frappe
import os
from io import BytesIO
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
import math


@frappe.whitelist()
def download(from_date, to_date, contractor_name):

    from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")
    month_name = from_date_obj.strftime("%B").upper()
    year = from_date_obj.strftime("%Y")

    wb = Workbook()
    ws = wb.active
    ws.title = "Contract Bill"

    header_font = Font(bold=True, size=10)
    title_font = Font(bold=True, size=12)
    wrap_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align = Alignment(horizontal="left", vertical="center")
    center_align = Alignment(horizontal="center", vertical="center")

    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )

    ws.append([])

    heading = f"{contractor_name} Contract Bill Details for the month of {month_name} {year}"

    ws.merge_cells(start_row=2, start_column=2, end_row=2, end_column=8)
    hcell = ws.cell(row=2, column=2)
    hcell.value = heading
    hcell.font = title_font
    hcell.alignment = Alignment(horizontal="left", vertical="center")
    hcell.border = thin_border
    ws.row_dimensions[2].height = 30
    for col in range(2, 9):
        cell = ws.cell(row=2, column=col)
        cell.border = thin_border

    headers = [
        "Total Days", "S.No", "Emp No", "Name", "Cost Center", "Gender",
        "Department", "Nature of Work", "Days Worked", "OT Hours", "OT Days",
        "Wages", "Basic", "Other Allowance", "Heat Allowance", "PF Wages",
        "Gross Wages", "OT Wages", "Attendance Incentive", "Total Gross Wages",
        "PF", "ESI", "LWF Employee", "Emp PF", "Emp ESI", "LWF Employer",
        "Canteen", "Late", "Net Wages", "Canteen Management Contribution",
        "Absent", "Absent %", "8.33 % Service Tax", "Total", "Deduction" , "Total Wages" , "Total 18%"
    ]

    row = 4
    col = 2
    for h in headers:
        c = ws.cell(row=row, column=col, value=h)
        c.font = header_font
        c.alignment = wrap_align
        c.border = thin_border
        ws.column_dimensions[c.column_letter].width = 18
        col += 1

    ws.row_dimensions[4].height = 45

    slips = frappe.get_all(
        "Salary Slip",
        filters={
            "start_date": ("<=", from_date),
            "end_date": (">=", from_date),
            "employment_type": "Contract",
            "contractor_name": contractor_name,
            "docstatus": ["in", [0, 1]]
        },
        fields=[
            "name", "employee", "employee_name",
            "total_present_days_of_employee", "total_present_days_in_a_month",
            "ot_", "lwf"
        ]
    )

    data_row = 5
    sno = 1
    grand_totals = [0] * len(headers)
    for slip in slips:

        emp = frappe.get_doc("Employee", slip.employee)

        total_days = slip.total_present_days_in_a_month
        days_worked = slip.total_present_days_of_employee
        ot_hours = slip.ot_ or 0
        ot_days = ot_hours / 8

        wages = emp.salary_total
        basic = emp.basic
        other_allow = emp.other_allowance or 0

        pf_wages = basic * days_worked
        gross_wages = wages * days_worked
        ot_wages = math.ceil(ot_days * wages)

        attendance_incentive = 2000 if days_worked == total_days else 0

        total_gross = gross_wages + ot_wages + attendance_incentive

        pf = round(pf_wages * 0.12)
        esi = math.ceil(total_gross * 0.0075)

        emp_pf = round(pf_wages * 0.13)
        emp_esi = math.ceil(total_gross * 0.0325)

        lwf_emp = slip.lwf if emp.lwf_eligibility == "Yes" and emp.lwf_type == "Employee" else 0
        lwf_employer = slip.lwf if emp.lwf_eligibility == "Yes" and emp.lwf_type == "Employer" else 0

        deductions = frappe.get_all(
            "Salary Detail",
            filters={"parent": slip.name, "parentfield": "deductions"},
            fields=["salary_component", "amount"]
        )

        canteen = sum(d.amount for d in deductions if d.salary_component == "Canteen")
        late = sum(d.amount for d in deductions if d.salary_component == "Late Penalty")

        net_wages = total_gross - pf - esi - lwf_emp - canteen - late

        canteen_mgmt = (canteen / 21) * 43 if canteen else 0

        absent = total_days - days_worked
        absent_pct = (absent / total_days) * 100 if total_days else 0

        service_tax = gross_wages * 0.0833

        total = total_gross + emp_pf + emp_esi + lwf_employer + canteen_mgmt + service_tax
        total_deduction = pf + esi + lwf_emp + canteen + late
        total_wages = total - total_deduction
        total_18 = total * 0.18

        values = [
            total_days, sno, emp.employee, emp.employee_name,
            emp.payroll_cost_center, emp.gender, emp.department, emp.designation,
            days_worked, ot_hours, ot_days, wages, basic, other_allow, 0,
            pf_wages, gross_wages, ot_wages, attendance_incentive,
            total_gross, pf, esi, lwf_emp, emp_pf, emp_esi, lwf_employer,
            canteen, late, net_wages, canteen_mgmt,
            absent, absent_pct, service_tax, total, total_deduction ,
            total_wages , total_18
        ]
        for i, v in enumerate(values):
            if isinstance(v, (int, float)):
                grand_totals[i] += v

        col = 2
        for idx, v in enumerate(values, start=1):

            val = round(v, 2) if isinstance(v, (int, float)) else v
            c = ws.cell(row=data_row, column=col, value=val)
            c.border = thin_border

            if idx in [1, 2, 9, 10, 11]: 
                c.alignment = center_align

            elif idx in [3, 4, 5, 6, 7, 8]:  
                c.alignment = left_align

            else:
                c.alignment = center_align

            col += 1

        sno += 1
        data_row += 1

    total_row = data_row
    total_days_sum = sum(
        slip.total_present_days_in_a_month or 0 for slip in slips
    )
    td_cell = ws.cell(row=total_row, column=2, value=total_days_sum)
    td_cell.font = Font(bold=True)
    td_cell.alignment = center_align
    td_cell.border = thin_border


    start_col = 3
    end_col = 9

    ws.merge_cells(
        start_row=total_row,
        start_column=start_col,
        end_row=total_row,
        end_column=end_col
    )

    tcell = ws.cell(row=total_row, column=start_col)
    tcell.value = "TOTAL"
    tcell.font = Font(bold=True)
    tcell.alignment = center_align
    tcell.border = thin_border

    for c in range(start_col, end_col + 1):
        ws.cell(row=total_row, column=c).border = thin_border

    col = end_col + 1
    for val in grand_totals[end_col - 1:]:
        c = ws.cell(
            row=total_row,
            column=col,
            value=round(val, 2) if isinstance(val, (int, float)) else val
        )
        c.font = Font(bold=True)
        c.alignment = center_align
        c.border = thin_border
        col += 1

    file_name = f"Contract_Bill_{contractor_name}_{month_name}_{year}.xlsx"
    
    xlsx_file = BytesIO()
    wb.save(xlsx_file)
    xlsx_file.seek(0)

    frappe.response["filename"] = file_name
    frappe.response["filecontent"] = xlsx_file.getvalue()
    frappe.response["type"] = "binary"