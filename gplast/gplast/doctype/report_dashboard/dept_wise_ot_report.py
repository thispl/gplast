import frappe
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from io import BytesIO
from openpyxl.utils import get_column_letter
from datetime import timedelta


@frappe.whitelist()
def download(from_date, to_date, unit=None):

    from_date = frappe.utils.getdate(from_date)
    to_date = frappe.utils.getdate(to_date)

    departments = frappe.get_all(
        "Department",
        filters={"disabled": 0 , "name": ["!=", "All Departments"]},
        fields=["name"],
        order_by="name"
    )

    ot_records = frappe.db.sql("""
        SELECT 
            ot.department,
            ot.ot_date,
            ot.overtime_hours
        FROM `tabOver Time` ot
        WHERE ot.ot_date BETWEEN %s AND %s
        AND (%s IS NULL OR ot.unit = %s)
        AND ot.docstatus = 1
    """, (from_date, to_date, unit, unit), as_dict=True)

    data_map = {}
    c = from_date
    while c <= to_date:
        data_map[str(c)] = {}
        c += timedelta(days=1)

    for row in ot_records:
        date = str(row.ot_date)
        dep = row.department
        hrs = row.overtime_hours or 0
        data_map[date][dep] = data_map[date].get(dep, 0) + hrs

    wb = Workbook()
    ws = wb.active

    total_columns = 1 + len(departments) + 2   
    last_col_letter = get_column_letter(total_columns)

    ws.merge_cells(f"A1:{last_col_letter}1")
    cell = ws["A1"]
    cell.value = "OVERTIME REPORT"
    cell.font = Font(size=16, bold=True)
    cell.alignment = Alignment(horizontal="center", vertical="center")

    ws.merge_cells(f"A2:{last_col_letter}2")
    cell = ws["A2"]
    cell.value = f"{unit or 'All Units'} | {from_date.strftime('%d-%m-%Y')} to {to_date.strftime('%d-%m-%Y')}"
    cell.font = Font(size=12, bold=True)
    cell.alignment = Alignment(horizontal="center", vertical="center")

    ws["A3"] = "Date"
    ws["A3"].font = Font(bold=True)
    ws["A3"].alignment = Alignment(horizontal="center")

    col_index = 2
    dep_list = []

    for dep in departments:
        col_letter = get_column_letter(col_index)
        ws[f"{col_letter}3"] = dep.name
        ws[f"{col_letter}3"].font = Font(bold=True)
        ws[f"{col_letter}3"].alignment = Alignment(horizontal="center")
        dep_list.append(dep.name)
        ws.column_dimensions[col_letter].width = 20
        col_index += 1

    total_col = get_column_letter(col_index)
    ws[f"{total_col}3"] = "Total Hrs"
    ws[f"{total_col}3"].font = Font(bold=True , color="FF0000")
    ws[f"{total_col}3"].alignment = Alignment(horizontal="center")
    col_index += 1

    manpower_col = get_column_letter(col_index)
    ws[f"{manpower_col}3"] = "Manpower Count"
    ws[f"{manpower_col}3"].font = Font(bold=True , color="0000FF")   
    ws[f"{manpower_col}3"].alignment = Alignment(horizontal="center")

    ws.column_dimensions["A"].width = 15
    ws.column_dimensions[manpower_col].width = 20

    thin = Side(style="thin")
    border = Border(top=thin, bottom=thin, left=thin, right=thin)

    row_no = 4

    for dt, dep_data in data_map.items():

        ws[f"A{row_no}"] = frappe.utils.getdate(dt).strftime("%d-%m-%Y")
        ws[f"A{row_no}"].alignment = Alignment(horizontal="center")

        total_hrs = 0

        col_index = 2
        for dep in dep_list:
            col_letter = get_column_letter(col_index)
            value = dep_data.get(dep, 0)

            ws[f"{col_letter}{row_no}"] = value
            ws[f"{col_letter}{row_no}"].alignment = Alignment(horizontal="center")
            ws[f"{col_letter}{row_no}"].border = border

            total_hrs += value
            col_index += 1

        ws[f"{total_col}{row_no}"] = total_hrs
        ws[f"{total_col}{row_no}"].alignment = Alignment(horizontal="center")
        ws[f"{total_col}{row_no}"].border = border
        ws[f"{total_col}{row_no}"].font = Font(bold=False, color="FF0000")

        ws[f"{manpower_col}{row_no}"] = round(total_hrs / 8, 2)
        ws[f"{manpower_col}{row_no}"].alignment = Alignment(horizontal="center")
        ws[f"{manpower_col}{row_no}"].border = border
        ws[f"{manpower_col}{row_no}"].font = Font(bold=False, color="0000FF")

        ws[f"A{row_no}"].border = border

        row_no += 1
    border_style = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )

    last_row = ws.max_row
    last_col = ws.max_column

    for r in range(1, last_row + 1):
        for c in range(1, last_col + 1):
            ws.cell(row=r, column=c).border = border_style

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    frappe.local.response.filename = "Overtime_Report.xlsx"
    frappe.local.response.filecontent = output.read()
    frappe.local.response.type = "download"
