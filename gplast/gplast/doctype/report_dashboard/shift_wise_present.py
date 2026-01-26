import frappe
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from frappe.utils import getdate
from six import BytesIO


@frappe.whitelist()
def download(from_date=None, to_date=None):

    FIRST_SHIFT_CODES = ["A", "G", "G1"]   
    SECOND_SHIFT_CODES = ["B"]
    THIRD_SHIFT_CODES = ["C"]

    CNC_DESIGNATION = "Cnc Machine Operator"
    CASTING_DESIGNATIONS = ["MACHINE OPERATOR DCD", "MACHINE OPERATOR PMD"]

    if from_date:
        from_date = getdate(from_date)
    if to_date:
        to_date = getdate(to_date)

    if not from_date or not to_date:
        frappe.throw("Please provide from_date and to_date")

    # from_text = from_date.strftime("%b'%Y")
    # to_text = to_date.strftime("%b'%Y")
    from_text = from_date.strftime("%d-%b-%Y")
    to_text = to_date.strftime("%d-%b-%Y")

    filename = "Shift Wise Present Count Report.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Shift Report"

    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin")
    )

    # ws.merge_cells("B2:F2")
    # ws["B2"] = "G PLAST PRIVATE LIMITED"
    # ws["B2"].font = Font(bold=True, size=14, underline="single")
    # ws["B2"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A3:E3")
    ws["A3"] = f"Shift Wise Present Count Report {from_text} To {to_text}"
    ws["A3"].font = Font(size=12, bold=True)
    ws["A3"].alignment = Alignment(horizontal="center")
    thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

    # Apply border to all merged cells
    for row in ws["A3:E3"]:
        for cell in row:
            cell.border = thin_border

    ws.column_dimensions["A"].width = 5
    ws.column_dimensions["B"].width = 17
    ws.column_dimensions["C"].width = 13
    ws.column_dimensions["D"].width = 13
    ws.column_dimensions["E"].width = 13


    def get_first_shift_available(designation_filter=None):
        params_a = ["A", to_date, from_date]
        designation_join = ""
        designation_condition = ""

        if designation_filter:
            designation_join = " JOIN `tabEmployee` e ON sa.employee = e.name "
            if isinstance(designation_filter, list):
                placeholders = ",".join(["%s"] * len(designation_filter))
                designation_condition = f" AND e.designation IN ({placeholders}) "
                params_a = ["A"] + designation_filter + [to_date, from_date]
            else:
                designation_condition = " AND e.designation = %s "
                params_a = ["A", designation_filter, to_date, from_date]

        sql_a = f"""
            SELECT COUNT(*) AS cnt
            FROM `tabShift Assignment` sa
            {designation_join}
            WHERE sa.shift_type = %s
            {designation_condition}
            AND sa.start_date <= %s
            AND sa.end_date >= %s
            AND sa.docstatus != 2
        """
        a_count = frappe.db.sql(sql_a, tuple(params_a), as_dict=True)[0].cnt

        # G and G1 FROM EMPLOYEE TABLE
        params_emp = ["G", "G1"]
        des_join = ""
        des_condition = ""

        if designation_filter:
            if isinstance(designation_filter, list):
                placeholders = ",".join(["%s"] * len(designation_filter))
                des_condition = f" AND designation IN ({placeholders}) "
                params_emp += designation_filter
            else:
                des_condition = " AND designation = %s "
                params_emp.append(designation_filter)

        sql_emp = f"""
            SELECT COUNT(*) AS cnt
            FROM `tabEmployee`
            WHERE default_shift IN (%s, %s)
            {des_condition}
        """

        g_g1_count = frappe.db.sql(sql_emp, tuple(params_emp), as_dict=True)[0].cnt

        return a_count + g_g1_count

    def count_shift_assignments(shift_codes, designation_filter=None):
        placeholders = ",".join(["%s"] * len(shift_codes))
        params = list(shift_codes)

        join_text = ""
        where_designation = ""

        if designation_filter:
            join_text = " JOIN `tabEmployee` e ON sa.employee = e.name "
            if isinstance(designation_filter, list):
                des_placeholders = ",".join(["%s"] * len(designation_filter))
                where_designation = f" AND e.designation IN ({des_placeholders}) "
                params += designation_filter
            else:
                where_designation = " AND e.designation = %s "
                params.append(designation_filter)

        params += [to_date, from_date]

        sql = f"""
            SELECT COUNT(*) as cnt
            FROM `tabShift Assignment` sa
            {join_text}
            WHERE sa.shift_type IN ({placeholders})
            {where_designation}
            AND sa.start_date <= %s
            AND sa.end_date >= %s
            AND sa.docstatus != 2
        """

        res = frappe.db.sql(sql, tuple(params), as_dict=True)
        return res[0].cnt if res else 0

    def count_attendance(shift_codes, status, designation_filter=None):
        placeholders = ",".join(["%s"] * len(shift_codes))
        params = list(shift_codes) + [status]

        join_text = ""
        where_designation = ""

        if designation_filter:
            join_text = " JOIN `tabEmployee` e ON a.employee = e.name "
            if isinstance(designation_filter, list):
                des_placeholders = ",".join(["%s"] * len(designation_filter))
                where_designation = f" AND e.designation IN ({des_placeholders}) "
                params += designation_filter
            else:
                where_designation = " AND e.designation = %s "
                params.append(designation_filter)

        params += [from_date, to_date]

        sql = f"""
            SELECT COUNT(*) as cnt
            FROM `tabAttendance` a
            {join_text}
            WHERE a.shift IN ({placeholders})
            AND a.status = %s
            {where_designation}
            AND a.attendance_date BETWEEN %s AND %s
            AND a.docstatus != 2
        """

        res = frappe.db.sql(sql, tuple(params), as_dict=True)
        return res[0].cnt if res else 0


    def build_section(start_row, title, designation_filter=None):

        ws.merge_cells(start_row=start_row, start_column=1, end_row=start_row, end_column=5)
        main_cell = ws.cell(row=start_row, column=1, value=title)
        main_cell.font = Font(bold=True)
        main_cell.alignment = Alignment(horizontal="center")

        for col in range(1, 6):
            border_cell = ws.cell(row=start_row, column=col)
            border_cell.border = thin_border


        

        header_row = start_row + 1
        headers = ["Sl.No", "Shift", "Available", "Present", "Absent"]

        col = 1
        for h in headers:
            ws.merge_cells(start_row=header_row, start_column=col,
                           end_row=header_row, end_column=col)
            hc = ws.cell(row=header_row, column=col, value=h)
            hc.font = Font(bold=True)
            hc.alignment = Alignment(horizontal="center")
            hc.border = thin_border
            col += 1

        data_row = header_row + 1
        serial = 1
        
        ws.cell(row=data_row, column=1, value=serial).border = thin_border
        ws.cell(row=data_row, column=2, value="1st Shift").border = thin_border
        

        ws.cell(row=data_row, column=3,
                value=get_first_shift_available(designation_filter)).border = thin_border

        ws.cell(row=data_row, column=4,
                value=count_attendance(FIRST_SHIFT_CODES, "Present", designation_filter)).border = thin_border

        ws.cell(row=data_row, column=5,
                value=count_attendance(FIRST_SHIFT_CODES, "Absent", designation_filter)).border = thin_border

        data_row += 1
        serial += 1
        ws.cell(row=data_row, column=1, value=serial).border = thin_border
        ws.cell(row=data_row, column=2, value="2nd Shift").border = thin_border

        ws.cell(row=data_row, column=3,
                value=count_shift_assignments(SECOND_SHIFT_CODES, designation_filter)).border = thin_border

        ws.cell(row=data_row, column=4,
                value=count_attendance(SECOND_SHIFT_CODES, "Present", designation_filter)).border = thin_border

        ws.cell(row=data_row, column=5,
                value=count_attendance(SECOND_SHIFT_CODES, "Absent", designation_filter)).border = thin_border

        data_row += 1
        serial += 1

        ws.cell(row=data_row, column=1, value=serial).border = thin_border
        ws.cell(row=data_row, column=2, value="3rd Shift").border = thin_border

        ws.cell(row=data_row, column=3,
                value=count_shift_assignments(THIRD_SHIFT_CODES, designation_filter)).border = thin_border

        ws.cell(row=data_row, column=4,
                value=count_attendance(THIRD_SHIFT_CODES, "Present", designation_filter)).border = thin_border

        ws.cell(row=data_row, column=5,
                value=count_attendance(THIRD_SHIFT_CODES, "Absent", designation_filter)).border = thin_border

        return data_row + 2

    row = 5
    row = build_section(row, "Over All", designation_filter=None)
    row = build_section(row, "CNC Machine Operator", designation_filter=CNC_DESIGNATION)
    row = build_section(row, "Machine Operator PMD & Machine Operator DCD", designation_filter=CASTING_DESIGNATIONS)

    xlsx_file = BytesIO()
    wb.save(xlsx_file)
    xlsx_file.seek(0)

    frappe.response["filename"] = filename
    frappe.response["filecontent"] = xlsx_file.getvalue()
    frappe.response["type"] = "binary"



