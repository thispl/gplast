import frappe
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from frappe.utils import getdate
from six import BytesIO
from frappe.utils import getdate
from openpyxl.utils import get_column_letter
from datetime import timedelta
@frappe.whitelist()
def download(from_date=None, to_date=None):
    if from_date:
        from_date = getdate(from_date)
    if to_date:
        to_date = getdate(to_date)

    from_text = from_date.strftime("%b'%Y") 
    to_text = to_date.strftime("%b'%Y")
    month_year_text = from_date.strftime("%B - %Y").upper()
    filename = f"Bonus Report.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Bonus Report"  

    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )

    header_text = "G PLAST PRIVATE LIMITED"
    ws.merge_cells("B2:D2")   
    ws["B2"] = header_text
    ws["B2"].font = Font(bold=True, size=14, underline="single")
    ws["B2"].alignment = Alignment(horizontal="center", vertical="center")

    header_text = f"Bonus Earnings Details For The Period From {from_text} To {to_text}"
    ws.merge_cells("B3:E3")   
    ws["B3"] = header_text
    ws["B3"].font = Font(size=12)
    ws["B3"].alignment = Alignment(horizontal="center", vertical="center")

    fixed_headers = ["S. No", "Employee", "Name", "DOJ", "Unit"]
    start_row = 5
    col_start = 2

    for i, header in enumerate(fixed_headers):
        col = col_start + i
        ws.merge_cells(start_row=start_row, start_column=col, end_row=start_row+1, end_column=col)
        cell = ws.cell(row=start_row, column=col, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        for r in range(start_row, start_row+2):
            ws.cell(row=r, column=col).border = thin_border

    current_col = col_start + len(fixed_headers)
    current_date = from_date.replace(day=1)

    while current_date <= to_date:
        month_str = current_date.strftime("%b-%Y")
        ws.merge_cells(start_row=start_row, start_column=current_col, end_row=start_row, end_column=current_col+1)
        month_cell = ws.cell(row=start_row, column=current_col, value=month_str)
        month_cell.alignment = Alignment(horizontal="center", vertical="center")
        month_cell.font = Font(bold=True)
        month_cell.border = thin_border
        ws.cell(row=start_row, column=current_col+1).border = thin_border

        pd_cell = ws.cell(row=start_row+1, column=current_col, value="PD")
        pd_cell.alignment = Alignment(horizontal="center", vertical="center")
        pd_cell.font = Font(bold=True)
        pd_cell.border = thin_border
        ws.column_dimensions[get_column_letter(current_col)].width = 10 

        total_cell = ws.cell(row=start_row+1, column=current_col+1, value="Total Amount")
        total_cell.alignment = Alignment(horizontal="center", vertical="center")
        total_cell.font = Font(bold=True)
        total_cell.border = thin_border
        ws.column_dimensions[get_column_letter(current_col+1)].width = 18 

        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)

        current_col += 2

    extra_headers = [
        "Total Amount",
        "Leave Encahsment",
        "Total",
        "Diwali / Pongal Bonus",
        "Diwali / Pongal Amount"
    ]
    for header in extra_headers:
        ws.merge_cells(
            start_row=start_row,
            start_column=current_col,
            end_row=start_row+1,
            end_column=current_col
        )
        cell = ws.cell(row=start_row, column=current_col, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[get_column_letter(current_col)].width = 24
        for r in range(start_row, start_row+2):
            ws.cell(row=r, column=current_col).border = thin_border
        current_col += 1
    employees = frappe.db.sql("""
        SELECT 
            emp.name as employee,
            emp.employee_name as employee_name,
            emp.date_of_joining as doj,
            emp.unit as unit
        FROM `tabEmployee` emp
        WHERE emp.status = 'Active'
        ORDER BY emp.date_of_joining ASC
    """, as_dict=True)   

    selected_from = getdate(from_date)
    selected_to = getdate(to_date)

    bonus_docs = frappe.get_all(
        "Bonus",
        filters=[
            ["from_date", "<=", selected_to],
            ["to_date", ">=", selected_from]
        ],
        fields=["name", "from_date", "to_date", "exp_date","d_bonus","p_bonus",'category']
    )
    employees = frappe.get_all(
        "Employee",
        filters={"status": "Active"},
        fields=["name", "employee_name", "date_of_joining", "unit","employment_type"],
        order_by="date_of_joining DESC"
    )

    
    data_start_row = 7
    serial = 1

    for emp in employees:
        include_emp = False
        emp_category = emp.get('employment_type')
        for bonus in bonus_docs:
            if bonus.category:
                if emp_category != bonus.category:
                    continue
            if emp.date_of_joining and emp.date_of_joining <= bonus.exp_date:
                include_emp = True
                break

        if not include_emp:
            continue

        s_no_cell = ws.cell(row=data_start_row, column=2, value=serial)
        s_no_cell.alignment = Alignment(horizontal="center", vertical="center")
        s_no_cell.border = thin_border
        emp_cell = ws.cell(row=data_start_row, column=3, value=emp.name)
        emp_cell.alignment = Alignment(horizontal="left", vertical="center")
        emp_cell.border = thin_border
        name_cell = ws.cell(row=data_start_row, column=4, value=emp.employee_name)
        name_cell.alignment = Alignment(horizontal="left", vertical="center")
        name_cell.border = thin_border
        doj_value = emp.date_of_joining.strftime("%d-%m-%Y") if emp.date_of_joining else ""
        doj_cell = ws.cell(row=data_start_row, column=5, value=doj_value)
        doj_cell.alignment = Alignment(horizontal="center", vertical="center")
        doj_cell.border = thin_border
        unit_cell = ws.cell(row=data_start_row, column=6, value=emp.unit or "")
        unit_cell.alignment = Alignment(horizontal="center", vertical="center")
        unit_cell.border = thin_border
        ws.column_dimensions["B"].width = 8   
        ws.column_dimensions["C"].width = 18  
        ws.column_dimensions["D"].width = 28 
        ws.column_dimensions["E"].width = 15  
        ws.column_dimensions["F"].width = 18  

        month_col = 7
        current_date = from_date.replace(day=1)
        total_amount_sum = 0

        while current_date <= to_date:
            month_start = current_date
            if current_date.month == 12:
                month_end = current_date.replace(day=31)
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                next_month = current_date.replace(month=current_date.month + 1, day=1)
                month_end = next_month - timedelta(days=1)
                current_date = next_month

            slip = frappe.db.sql("""
                SELECT name, payment_days
                FROM `tabSalary Slip`
                WHERE employee=%s
                AND start_date >= %s AND end_date <= %s
                LIMIT 1
            """, (emp.name, month_start, month_end), as_dict=True)

            pd_value, total_amt = 0, 0
            if slip:
                pd_value = slip[0].payment_days or 0
                earnings = frappe.db.sql("""
                    SELECT amount
                    FROM `tabSalary Detail`
                    WHERE parent=%s AND parentfield='earnings'
                    AND salary_component IN (
                        'Basic', 'City Compensatory Allowance', 'Special Allowance', 
                        'CCA Arrear', 'Basic ARR', 'Special Arrear'
                    )
                """, (slip[0].name,), as_dict=True)
                total_amt = sum([e.amount for e in earnings]) if earnings else 0
            else:
                pd_value, total_amt = 0, 0

            total_amount_sum += total_amt

            pd_cell = ws.cell(row=data_start_row, column=month_col, value=pd_value)
            pd_cell.alignment = Alignment(horizontal="center", vertical="center")
            pd_cell.border = thin_border

            total_cell = ws.cell(row=data_start_row, column=month_col+1, value=total_amt)
            total_cell.alignment = Alignment(horizontal="center", vertical="center")
            total_cell.border = thin_border

            month_col += 2

        total_col = month_col  
        total_amount_cell = ws.cell(row=data_start_row, column=total_col, value=total_amount_sum)
        total_amount_cell.alignment = Alignment(horizontal="center", vertical="center")
        total_amount_cell.border = thin_border

        encashments = frappe.db.sql("""
            SELECT leave_period, encashment_amount
            FROM `tabLeave Encashment`
            WHERE employee=%s AND docstatus=1
        """, (emp.name,), as_dict=True)
        leave_encashment_amt = 0
        if encashments:
            for enc in encashments:
                lp = frappe.db.get_value("Leave Period", enc.leave_period,
                                        ["from_date", "to_date", "is_active"], as_dict=True)
                if lp and lp.is_active:
                    if lp.from_date <= selected_from <= lp.to_date:
                        leave_encashment_amt = enc.encashment_amount
                        break
        leave_col = total_col + 1 
        leave_cell = ws.cell(row=data_start_row, column=leave_col, value=leave_encashment_amt)
        leave_cell.alignment = Alignment(horizontal="center", vertical="center")
        leave_cell.border = thin_border
        
        grand_total_col = leave_col + 1
        grand_total = total_amount_sum + leave_encashment_amt

        grand_total_cell = ws.cell(row=data_start_row, column=grand_total_col, value=grand_total)
        grand_total_cell.alignment = Alignment(horizontal="center", vertical="center")
        grand_total_cell.border = thin_border

        bonus_percent = 0
        for bonus in bonus_docs:
            if emp.date_of_joining and emp.date_of_joining <= bonus.exp_date:
                bonus_percent = (bonus.d_bonus or 0) + (bonus.p_bonus or 0)
                break
        bonus_col = grand_total_col + 1
        bonus_cell = ws.cell(row=data_start_row, column=bonus_col, value=f"{bonus_percent}%")
        bonus_cell.alignment = Alignment(horizontal="center", vertical="center")
        bonus_cell.border = thin_border 

        bonus_amount = grand_total * (bonus_percent / 100)
        bonus_amt_col = bonus_col + 1
        bonus_amt_cell = ws.cell(row=data_start_row, column=bonus_amt_col, value=bonus_amount)
        bonus_amt_cell.alignment = Alignment(horizontal="center", vertical="center")
        bonus_amt_cell.border = thin_border
        serial += 1
        data_start_row += 1

    xlsx_file = BytesIO()
    wb.save(xlsx_file)
    xlsx_file.seek(0)

    frappe.response['filename'] = filename
    frappe.response['filecontent'] = xlsx_file.getvalue()
    frappe.response['type'] = 'binary'
