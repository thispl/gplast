import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from io import BytesIO
import frappe

@frappe.whitelist()
def generate_shift_excel(from_date=None, to_date=None, department=None):

    # Shift Status Mapping
    shift_map = {
        "1": ["A", "G", "G1"],   # 1st Shift
        "2": ["B"],              # 2nd Shift
        "3": ["C"]               # 3rd Shift
    }

    # Department filter
    dept_filters = {}
    if department:
        dept_filters["name"] = department

    # Fetch all departments
    departments = frappe.get_all(
        "Department",
        fields=["name"],
        filters=dept_filters,
        order_by="name asc"
    )

    # Prepare Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Department & Shift Wise Present Report"

    headers = ["Sl.No", "Department", "1st Shift & General", "2nd Shift", "3rd Shift"]
    bold = Font(bold=True)
    center = Alignment(horizontal="center", vertical="center")
    border = Border(left=Side(style="thin"), right=Side(style="thin"),
                    top=Side(style="thin"), bottom=Side(style="thin"))

    # Header row
    for col, title in enumerate(headers, start=1):
        c = ws.cell(row=2, column=col, value=title)
        c.font = bold
        c.alignment = center
        c.border = border

    # Sub Filters For Attendance
    att_filters = {}
    if from_date and to_date:
        att_filters["attendance_date"] = ["between",[from_date,to_date]]

    # Fill Dept Rows
    row = 3
    for idx, dept in enumerate(departments, start=1):

        # Sl.No
        ws.cell(row=row, column=1, value=idx).alignment = center
        ws.cell(row=row, column=1).border = border

        # Department Name
        ws.cell(row=row, column=2, value=dept.name).border = border

        # Shift 1 Count → A,G,G1
        shift1_count = frappe.db.count(
            "Attendance",
            filters={
                "department": dept.name,
                "shift": ["in", shift_map["1"]],
                "status":"Present",
                "docstatus":["!=","2"],
                **att_filters
            }
        )

        # Shift 2 Count → B
        shift2_count = frappe.db.count(
            "Attendance",
            filters={
                "department": dept.name,
                "shift": ["in", shift_map["2"]],
                "status":"Present",
                "docstatus":["!=","2"],
                **att_filters
            }
        )

        # Shift 3 Count → C
        shift3_count = frappe.db.count(
            "Attendance",
            filters={
                "department": dept.name,
                "shift": ["in", shift_map["3"]],
                "status":"Present",
                "docstatus":["!=","2"],
                **att_filters
            }
        )

        # Write to Excel
        ws.cell(row=row, column=3, value=shift1_count).alignment = center
        ws.cell(row=row, column=3).border = border

        ws.cell(row=row, column=4, value=shift2_count).alignment = center
        ws.cell(row=row, column=4).border = border

        ws.cell(row=row, column=5, value=shift3_count).alignment = center
        ws.cell(row=row, column=5).border = border

        row += 1

    # Column width
    for i, w in enumerate([10, 25, 15, 15, 15], start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # Output file
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return frappe.response.update({
        "type": "binary",
        "filename": "Dept & Shift Wise Report.xlsx",
        "filecontent": output.getvalue()
    })
