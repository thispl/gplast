from openpyxl import Workbook
from openpyxl.styles import Border, Side, Alignment, Font
from openpyxl.utils import column_index_from_string, get_column_letter
from io import BytesIO
import frappe
import math
from openpyxl.styles import numbers
from datetime import datetime

@frappe.whitelist()
def download(from_date=None, to_date=None):

    if from_date:
        from_date = datetime.strptime(from_date, "%Y-%m-%d").date()

    if to_date:
        to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
    filename = "EPF_Report.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "EPF Report"

    headers = [
        "S.No", "Employee ID", "UAN No", "Name",
        "Gross Wages", "EPF Wages", "EPS Wages", "EDLI Wages",
        "EPF Contribution", "EPF Contri. Remit",
        "EPS Contribution", "EPS Contri. Remit",
        "Diff EPS and EPF", "Diff EPS and EPF Remit",
        "NCP Days", "Refund of Advance",
        "Arrear EPF Wages", "Arrear EPF EE Share",
        "Arrear EPF ER Share", "Arrear EPS",
        "Father/Husband Name", "Relationship with Member",
        "Date of Birth", "Gender",
        "Date of Joining EPF", "Date of Joining EPS",
        "Date of Exit EPF", "Date of Exit EPS",
        "Reason for Leaving"
    ]

    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )

    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col)
        cell.value = header
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 22
    ws.column_dimensions["D"].width = 25

    for col_idx in range(
        column_index_from_string("E"),
        column_index_from_string("AC") + 1
    ):
        ws.column_dimensions[get_column_letter(col_idx)].width = 22

    GROSS_COMPONENTS = [
        "Basic","City Compensatory Allowance","Special Allowance",
        "Other Allowance","House Rent Allowance","Shift Allowance",
        "Basic ARR","HRA ARR"
    ]

    EPF_COMPONENTS = [
        "Basic","City Compensatory Allowance","Special Allowance",
        "Basic ARR","HRA ARR","Special Arrear"
    ]

    ARREAR_COMPONENTS = ["Basic ARR", "HRA ARR", "Special Arrear"]

    salary_slips = frappe.db.sql(
        """
        SELECT employee, employee_name, name,
               absent_days, leave_without_pay
        FROM `tabSalary Slip`
        WHERE docstatus = 0
          AND start_date >= %s
          AND end_date <= %s
        """,
        (from_date, to_date),
        as_dict=True
    )

    row = 2
    sno = 1

    for ss in salary_slips:
        emp = ss.employee

        emp_doc = frappe.get_doc("Employee", emp)

        gross_wages = epf_wages = arrear_epf = arr_epf_ee = arr_epf_er = 0

        earnings = frappe.get_all(
            "Salary Detail",
            filters={
                "parent": ss.name,
                "parenttype": "Salary Slip",
                "parentfield": "earnings"
            },
            fields=["salary_component", "amount"]
        )

        for e in earnings:
            if e.salary_component in GROSS_COMPONENTS:
                gross_wages += e.amount or 0

            if e.salary_component in EPF_COMPONENTS:
                epf_wages += e.amount or 0

            if e.salary_component in ARREAR_COMPONENTS:
                arrear_epf += e.amount or 0

        eps_wages = 15000 if epf_wages > 15000 else epf_wages
        edli = eps_wages

        epf_con = round((epf_wages / 100) * 12)
        eps_con = round((eps_wages / 100) * 8.33)

        diff_eps_epf = epf_con - eps_con
        
        ncp_days = (ss.absent_days or 0) + (ss.leave_without_pay or 0)

        arr_epf_ee = round((arrear_epf/100)*12)
        arr_epf_er = round((arrear_epf/100)*12)

        relieving_date = frappe.db.get_value("Employee", emp, "relieving_date")

        exit_epf = exit_eps = None
        if relieving_date and from_date and to_date:
            if from_date <= relieving_date <= to_date:
                exit_epf = relieving_date
                exit_eps = relieving_date

        reason = ""

        if frappe.db.exists("Resignation Form", emp):
            res_doc = frappe.get_doc("Resignation Form", emp)

            if res_doc.workflow_state == "Approved":
                reason = res_doc.reason


        values = {
            1: sno,
            2: emp,
            3: emp_doc.get("_uan_no"),
            4: ss.employee_name,
            5: gross_wages,
            6: epf_wages,
            7: eps_wages,
            8: edli,
            9: epf_con,
            10: epf_con,
            11: eps_con,
            12: eps_con,
            13: diff_eps_epf,
            14: diff_eps_epf,
            15: ncp_days,
            16: 0,
            17: arrear_epf,
            18: arr_epf_ee,
            19: arr_epf_er,
            20: 0,
            21: emp_doc.get("father_name"),
            22: "Father",
            23: emp_doc.get("date_of_birth"),
            24: emp_doc.get("gender"),
            25: emp_doc.get("date_of_joining"),
            26: emp_doc.get("date_of_joining"),
            27: exit_epf,
            28: exit_eps,
            29: reason
        }

        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=row, column=col)
            cell.value = values.get(col, "")
            cell.border = thin_border

            if col in (23, 25, 26, 27, 28) and cell.value:
                cell.number_format = "DD-MM-YYYY"

            if col in (2, 3, 4, 21):
                cell.alignment = Alignment(horizontal="left", vertical="center")
            else:
                cell.alignment = Alignment(vertical="center")

        
        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=row, column=col)
            cell.value = values.get(col, "")
            cell.border = thin_border

            if col in (2, 3, 4, 21):
                cell.alignment = Alignment(horizontal="left", vertical="center")
            else:
                cell.alignment = Alignment(vertical="center")

        sno += 1
        row += 1

    xlsx_file = BytesIO()
    wb.save(xlsx_file)
    xlsx_file.seek(0)

    frappe.response["filename"] = filename
    frappe.response["filecontent"] = xlsx_file.getvalue()
    frappe.response["type"] = "binary"
