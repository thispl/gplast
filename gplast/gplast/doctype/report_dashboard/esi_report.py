# import frappe
# from io import BytesIO
# import openpyxl
# from openpyxl.styles import Font, Alignment, Border, Side


# @frappe.whitelist()
# def download_esi_excel(from_date, to_date):
#     wb = openpyxl.Workbook()
#     ws = wb.active
#     ws.title = "ESI Report"

#     header_font = Font(bold=True)
#     center = Alignment(horizontal="center", vertical="center")
#     border = Border(
#         left=Side(style="thin"),
#         right=Side(style="thin"),
#         top=Side(style="thin"),
#         bottom=Side(style="thin")
#     )

#     headers = [
#         "IP Number",
#         "IP Name",
#         "No of Days for which wages paid/payable during the month",
#         "Total Monthly Wages",
#         "Reason Code for Zero working days",
#         "Last Working Day"
#     ]
    
#     for col, header in enumerate(headers, start=1):
#         cell = ws.cell(row=1, column=col, value=header)
#         cell.font = header_font
#         cell.alignment = center
#         cell.border = border

#     salary_slips = frappe.get_all("Salary Slip", filters={"docstatus":["!=",2],"start_date": ["<=", to_date],"end_date": [">=", from_date]},
#         fields=["name", "employee", "payment_days", "gross_pay"])
#     row = 2
#     for ss in salary_slips:
#         emp = frappe.db.get_value("Employee",ss.employee,["esi_number", "employee_name"],as_dict=True)
#         ws.cell(row=row, column=1, value=emp.esi_number)
#         ws.cell(row=row, column=2, value=emp.employee_name)
#         ws.cell(row=row, column=3, value=ss.payment_days)
#         ws.cell(row=row, column=4, value=round(ss.gross_pay, 2))
#         ws.cell(row=row, column=5, value="")  # Reason Code
#         ws.cell(row=row, column=6, value="")  # Last Working Day

#         for col in range(1, 7):
#             ws.cell(row=row, column=col).border = border
#         row += 1
#     for col in ws.columns:
#         ws.column_dimensions[col[0].column_letter].width = 25

#     file = BytesIO()
#     wb.save(file)

#     frappe.response["filename"] = "ESI_Wages_Report.xlsx"
#     frappe.response["filecontent"] = file.getvalue()
#     frappe.response["type"] = "binary"



import frappe
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from frappe.utils import getdate, add_months, get_last_day
from openpyxl.styles import Font, Alignment, PatternFill

@frappe.whitelist()
def download_esi_excel(from_date, to_date):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "ESI Report"

    border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )
    header_center = Alignment(horizontal="center", vertical="center", wrap_text=True)

    
    header_fill = PatternFill(
        start_color="CCFFFF",
        end_color="CCFFFF",
        fill_type="solid"
    )

    header_alignment = Alignment(
        horizontal="center",
        vertical="center",
        wrap_text=True
    )

    headers = [
        "IP Number\n(10 Digits)",
        "IP Name\n(Only alphabets and space)",
        "No of Days for which wages\npaid/payable during the month",
        "Total Monthly Wages",
        "Reason Code for Zero working days\n(numeric only; provide 0 for all\nother reasons. Click on\nthe link for reference)",
        "Last Working Day\n(Format DD/MM/YYYY\nor DD-MM-YYYY)"
    ]

    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=header)

        cell.font = Font(bold=True)
        cell.alignment = header_alignment
        cell.fill = header_fill
        cell.border = border

    # Header row height
    ws.row_dimensions[1].height = 80
    report_month_start = getdate(from_date).replace(day=1)
    prev_month_start = add_months(report_month_start, -1)

    # Employees with ESI > 0
    salary_slips = frappe.get_all( "Salary Slip", filters={"docstatus": ["!=", 2],  "start_date": ["<=", to_date], "end_date": [">=", from_date] },fields=["name", "employee", "payment_days", "gross_pay"] )

    filtered_slips = []
    for slip in salary_slips:
        esi_amount = frappe.db.get_value(  "Salary Detail", {"parent": slip.name, "salary_component": "Employee State Insurance"}, "amount")
        if esi_amount and esi_amount > 0:
            filtered_slips.append(slip)

    added_employees = set()
    row = 2

    for ss in filtered_slips:
        emp = frappe.db.get_value("Employee", ss.employee, ["esi_number", "employee_name"], as_dict=True)
        added_employees.add(ss.employee)

        ws.cell(row=row, column=1, value=emp.esi_number)
        ws.cell(row=row, column=2, value=emp.employee_name)
        ws.cell(row=row, column=3, value=ss.payment_days)
        ws.cell(row=row, column=4, value=round(ss.gross_pay, 2))
        ws.cell(row=row, column=5, value="")
        ws.cell(row=row, column=6, value="")

        for col in range(1, 7):
            ws.cell(row=row, column=col).border = border
        row += 1

    # Employees with relieving date or ESI end date in previous month
    employees = frappe.get_all(
        "Employee",
        filters={"esi_number": ["!=", ""]},
        fields=["name", "esi_number", "employee_name", "relieving_date", "esi_end_date"]
    )

    for emp in employees:
        if emp.name in added_employees:
            continue 

        last_working_day = None
        reason_code = ""

        # ESI end date in previous month
        if emp.esi_end_date:
            esi_end = getdate(emp.esi_end_date)
            if esi_end.year == prev_month_start.year and esi_end.month == prev_month_start.month:
                last_working_day = emp.esi_end_date
                reason_code = "4"

        # Relieving date in previous month
        elif emp.relieving_date:
            rel_date = getdate(emp.relieving_date)
            if rel_date.year == prev_month_start.year and rel_date.month == prev_month_start.month:
                last_working_day = emp.relieving_date
                reason_code = "2"

        if not last_working_day:
            continue

        ws.cell(row=row, column=1, value=emp.esi_number)
        ws.cell(row=row, column=2, value=emp.employee_name)
        ws.cell(row=row, column=3, value=0)
        ws.cell(row=row, column=4, value=0)
        ws.cell(row=row, column=5, value=reason_code)
        ws.cell(row=row, column=6, value=last_working_day)

        rc_cell = ws.cell(row=row, column=5, value=reason_code)
        rc_cell.alignment = Alignment(horizontal="right", vertical="center")

        for col in range(1, 7):
            ws.cell(row=row, column=col).border = border
        row += 1

    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 25

    file = BytesIO()
    wb.save(file)

    frappe.response["filename"] = "ESI_Wages_Report.xlsx"
    frappe.response["filecontent"] = file.getvalue()
    frappe.response["type"] = "binary"
