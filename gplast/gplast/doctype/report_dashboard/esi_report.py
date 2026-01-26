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


@frappe.whitelist()
def download_esi_excel(from_date, to_date):

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "ESI Report"

    header_font = Font(bold=True)
    center = Alignment(horizontal="center", vertical="center")
    border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )

    headers = [
        "IP Number",
        "IP Name",
        "No of Days for which wages paid/payable during the month",
        "Total Monthly Wages",
        "Reason Code for Zero working days",
        "Last Working Day"
    ]

    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.alignment = center
        cell.border = border

    report_month_start = getdate(from_date).replace(day=1)

    # -------------------------
    # 1️⃣ NORMAL SALARY SLIP EMPLOYEES (UNCHANGED)
    # -------------------------
    salary_slips = frappe.get_all(
        "Salary Slip",
        filters={
            "docstatus": ["!=", 2],
            "start_date": ["<=", to_date],
            "end_date": [">=", from_date]
        },
        fields=["employee", "payment_days", "gross_pay"]
    )

    added_employees = set()
    row = 2

    for ss in salary_slips:
        emp = frappe.db.get_value(
            "Employee",
            ss.employee,
            ["esi_number", "employee_name"],
            as_dict=True
        )
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

    # -------------------------
    # 2️⃣ EXTRA EMPLOYEES (NO SALARY SLIP)
    # -------------------------
    employees = frappe.get_all(
        "Employee",
        filters={
            "esi_number": ["!=", ""]
        },
        fields=[
            "name",
            "esi_number",
            "employee_name",
            "relieving_date",
            "esi_end_date"
        ]
    )

    for emp in employees:
        if emp.name in added_employees:
            continue

        last_working_day = None

        # 🔹 CONDITION 1: Relieved in previous month
        if emp.relieving_date:
            next_month = add_months(getdate(emp.relieving_date).replace(day=1), 1)
            if next_month == report_month_start:
                last_working_day = emp.relieving_date

        # 🔹 CONDITION 2: ESI ended previous month
        elif emp.esi_end_date:
            next_month = add_months(getdate(emp.esi_end_date).replace(day=1), 1)
            if next_month == report_month_start:
                last_working_day = get_last_day(emp.esi_end_date)

        if not last_working_day:
            continue

        ws.cell(row=row, column=1, value=emp.esi_number)
        ws.cell(row=row, column=2, value=emp.employee_name)
        ws.cell(row=row, column=3, value=0)
        ws.cell(row=row, column=4, value=0)
        ws.cell(row=row, column=5, value="")
        ws.cell(row=row, column=6, value=last_working_day)

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
