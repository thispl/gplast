import frappe
import io
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from datetime import datetime
from openpyxl.styles import Border, Side
from openpyxl.styles import Alignment, Font, Border, Side
from datetime import datetime
from datetime import timedelta
from openpyxl.utils import get_column_letter
# from gplast.gplast.report.attendance_register import attendance_register


# def get_status_map(from_date, to_date, company=None):
#     filters = frappe._dict({
#         "from_date": from_date,
#         "to_date": to_date,
#         "company": company
#     })
def get_status_map(from_date, to_date, company=None):
    attendance_records = frappe.get_all(
        "Attendance",
        filters={
            "attendance_date": ["between", [from_date, to_date]],
        },
        fields=["employee", "attendance_date", "shift", "status", "leave_type"]
    )

    status_map = {}
    lop_map = {}
    holiday_cache = {}  

    for rec in attendance_records:
        emp_map = status_map.setdefault(rec.employee, {})
        date_str = rec.attendance_date.strftime("%Y-%m-%d")
        emp_map[date_str] = rec.shift or ""

        holiday_list_name = frappe.db.get_value("Employee", rec.employee, "holiday_list")
        if not holiday_list_name and company:
            holiday_list_name = frappe.db.get_value("Company", company, "default_holiday_list")

        if holiday_list_name:
            if holiday_list_name not in holiday_cache:
                holidays = frappe.get_all(
                    "Holiday",
                    filters={
                        "parent": holiday_list_name,
                        "holiday_date": ["between", [from_date, to_date]],
                    },
                    fields=["holiday_date", "weekly_off", "national_holiday", "festival_holiday"]
                )
            
                holiday_cache[holiday_list_name] = {
                    h.holiday_date.strftime("%Y-%m-%d")
                    for h in holidays
                    if h.weekly_off or h.national_holiday or h.festival_holiday
                }

            holiday_dates = holiday_cache[holiday_list_name]
        else:
            holiday_dates = set()

        if date_str not in holiday_dates:
            if rec.status == "Absent" or rec.leave_type == "Leave Without Pay":
                lop_map[rec.employee] = lop_map.get(rec.employee, 0) + 1
            elif rec.status == "Half Day":
                lop_map[rec.employee] = lop_map.get(rec.employee, 0) + 0.5

    return status_map, lop_map




# def get_status_map(from_date, to_date, company=None):
#     # Returns dict { employee_id: { date1: shift, date2: shift, ... }, LOP count per employee }
#     attendance_records = frappe.get_all(
#         "Attendance",
#         filters={
#             "attendance_date": ["between", [from_date, to_date]],
#         },
#         fields=["employee", "attendance_date", "shift", "status"]
#     )
    
#     status_map = {}
#     lop_map = {}
    
#     for rec in attendance_records:
#         emp_map = status_map.setdefault(rec.employee, {})
#         emp_map[rec.attendance_date.strftime("%Y-%m-%d")] = rec.shift or ""
        
#         # Count LOP days
#         if rec.status == "Absent" or rec.leave_type == "Leave Without Pay" or rec.status=="Half Day":
#             lop_map[rec.employee] = lop_map.get(rec.employee, 0) + 1

    
#     return status_map, lop_map



@frappe.whitelist()
def download_form25_excel(from_date=None, to_date=None, company=None, company_address = None, employee=None):
    wb = Workbook()
    ws = wb.active
    ws.title = "Shift Register 1"

    if from_date and to_date:
        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_dt = datetime.strptime(to_date, "%Y-%m-%d")
        num_days = (to_dt - from_dt).days + 1  # inclusive
    else:
        from_dt = None
        to_dt = None
        num_days = 31
    

    def format_date(date_str):
        if not date_str:
            return "________"
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
        except:
            return date_str

    total_cols = 23 + num_days

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

  
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=total_cols)
    cell = ws.cell(row=1, column=1)
    cell.value = "Form No. 25 "
    cell.font = Font(bold=True, size=14)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=total_cols)
    cell = ws.cell(row=2, column=1)
    cell.value = "[Prescribed under rule 77(4), 103]"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center")


    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=total_cols)
    cell = ws.cell(row=3, column=1)
    cell.value = f"MUSTER ROLL AND REGISTER OF COMPENSATORY HOLIDAYS"
    cell.font = Font(size=12, bold=True)
    cell.alignment = Alignment(horizontal="center", vertical="center")


    ws.merge_cells(start_row=4, start_column=1, end_row=4, end_column=7)
    cell = ws.cell(row=4, column=1)
    cell.value = f"For the period from {format_date(from_date)} to {format_date(to_date)}"
    cell.font = Font(size=12, bold=True)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[4].height = 20

    
    ws.merge_cells(start_row=4, start_column=11, end_row=4, end_column=18)
    cell = ws.cell(row=4, column=11)
    cell.value = "Festival Holidays Approval Proceedings No. and Date:"
    cell.font = Font( size=12,bold=True)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[5].height = 20

    ws.merge_cells(start_row=8, start_column=1, end_row=8, end_column=7)
    cell = ws.cell(row=8, column=1)
    cell.value = "Registration No:"
    cell.font = Font( size=12,bold=True)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[5].height = 20
    for col in range(1, 8):  
        ws.cell(row=8, column=col).border = thin_border


    

    ws.merge_cells(start_row=5, start_column=1, end_row=5, end_column=7)
    cell = ws.cell(row=5, column=1)
    cell.value = "Name and Address of the Factory :"
    cell.font = Font( size=12,bold=True)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[5].height = 20

    ws.merge_cells(start_row=5, start_column=11, end_row=5, end_column=18)
    cell = ws.cell(row=5, column=11)
    cell.value = "Approved Festival Holidays:"
    cell.font = Font(size=12,bold=True)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[5].height = 20
    

 
    table_headers = [1, 2, 3, 4, 5, 6, 7]
    start_col = 11
    for i, val in enumerate(table_headers):
        col = start_col + i
        ws.cell(row=6, column=col, value=val)
        ws.cell(row=6, column=col).font = Font(size=12)
        ws.cell(row=6, column=col).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=6, column=col).border = border


    # for i in range(len(table_headers)):
    #     col = start_col + i
    #     ws.cell(row=7, column=col, value="") 
    #     ws.cell(row=7, column=col).border = border
    #     ws.cell(row=7, column=col).alignment = Alignment(horizontal="center", vertical="center")
    # ws.row_dimensions[6].height = 20  

    holiday_dates = []
    default_holiday_list = frappe.db.get_value("Company", company, "default_holiday_list")

    if default_holiday_list:
        holidays = frappe.get_all(
            "Holiday",
            filters={"parent": default_holiday_list,"holiday_date": ["between", [from_date, to_date]],},fields=["holiday_date", "description", "national_holiday", "festival_holiday"])
        for h in holidays:
            if h.national_holiday or h.festival_holiday:
                if h.national_holiday:
                    h_type = "NH"
                elif h.festival_holiday:
                    h_type = "FH"
                else:
                    continue
                holiday_dates.append((h.holiday_date.strftime("%Y-%m-%d"), h_type))
    holiday_dates = sorted(holiday_dates, key=lambda x: x[0])[:7]

    # write into row 7
    for idx in range(7):  
        col = 11 + idx
        if idx < len(holiday_dates):
            date_str, h_type = holiday_dates[idx]
            value = f"{datetime.strptime(date_str, '%Y-%m-%d').strftime('%d-%m-%Y')}\n({h_type})"
            font = Font( size=12)
        else:
            value = ""
            font = Font( size=12)
        cell = ws.cell(row=7, column=col, value=value)
        cell.border = border
        cell.font = font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.column_dimensions[cell.column_letter].width = 15

    ws.row_dimensions[7].height = 30

    ws.merge_cells(start_row=6, start_column=1, end_row=6, end_column=7)
    cell = ws.cell(row=6, column=1)
    cell.value = f"{company}\n{company_address}"  
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[6].height = 30  
    
    ws.row_dimensions[7].height = 15
    ws.row_dimensions[8].height = 15

    
    ws.row_dimensions[9].height = 60   
    ws.row_dimensions[10].height = 60  

    headers = [
        "Serial Number",
        "Serial Number\nin Register\nof adult workers",
        "Name of the worker",
        "Worker Identity Number",
        "Date of Joining",
        "Date of Exit",
        "Shift Group",
        "Scheme of Shifts"
    ]   
    

    for col_num, header in enumerate(headers, start=1):
        
        ws.merge_cells(start_row=9, start_column=col_num, end_row=10, end_column=col_num)
        
        
        cell = ws.cell(row=9, column=col_num)
        cell.value = header
        cell.font = Font(size=12)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        
        for row in range(9, 11):  
            merged_cell = ws.cell(row=row, column=col_num)
            merged_cell.border = thin_border

    
    start_col = 9
    end_col = start_col + num_days - 1  


    ws.merge_cells(start_row=9, start_column=start_col, end_row=9, end_column=end_col)
    cell = ws.cell(row=9, column=start_col)
    cell.value = "Daily Hours of work including overtime (if any)"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center")

    for i, col in enumerate(range(start_col, end_col + 1), start=1):
        cell = ws.cell(row=10, column=col)
        cell.value = i
        cell.font = Font(size=12)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    
    next_col = end_col + 1

    ws.merge_cells(start_row=9, start_column=next_col, end_row=10, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Shift I worked"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border

    next_col+=1

    ws.merge_cells(start_row=9, start_column=next_col, end_row=10, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Shift II Worked"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border
    next_col+=1

    ws.merge_cells(start_row=9, start_column=next_col, end_row=10, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Shift III Worked"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border
    next_col+=1

    ws.merge_cells(start_row=9, start_column=next_col, end_row=10, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "General Shift worked"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border
    next_col+=1

    ws.merge_cells(start_row=9, start_column=next_col, end_row=10, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "General Shift1 Worked"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border
    next_col+=1

    ws.merge_cells(start_row=9, start_column=next_col, end_row=10, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Point to Point shift Worked"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border
    next_col+=1

    ws.merge_cells(start_row=9, start_column=next_col, end_row=10, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "General Exemption Shift Worked"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border
    col_letter = get_column_letter(next_col)
    ws.column_dimensions[col_letter].width = 12
    next_col+=1

    
    ws.merge_cells(start_row=9, start_column=next_col, end_row=10, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Total Days Worked"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border

    next_col += 1
    ws.merge_cells(start_row=9, start_column=next_col, end_row=10, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Total Hours Worked"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border

    next_col += 1
    ws.merge_cells(start_row=9, start_column=next_col, end_row=10, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Number of days on Loss of Pay"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border

    next_col += 1
    ws.merge_cells(start_row=9, start_column=next_col, end_row=10, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Benefit availed for working on National Holiday"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border

    next_col += 1
    ws.merge_cells(start_row=9, start_column=next_col, end_row=10, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Benefit availed for working on Festival Holiday"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border

    next_col += 1
    ws.merge_cells(start_row=9, start_column=next_col, end_row=10, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Remarks"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border

    next_col += 1
    ws.merge_cells(start_row=9, start_column=next_col, end_row=10, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Total Approved OT Hours"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border
    col_letter = get_column_letter(next_col)
    ws.column_dimensions[col_letter].width = 13


    next_col += 1
    ws.merge_cells(start_row=9, start_column=next_col, end_row=10, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Total Approved OT Days"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border
    col_letter = get_column_letter(next_col)
    ws.column_dimensions[col_letter].width = 13
    
    
    
    for col in range(start_col, end_col + 1):
        ws.cell(row=9, column=col).border = thin_border


    for i, col in enumerate(range(start_col, end_col + 1), start=1):
        cell = ws.cell(row=10, column=col)
        cell.value = i
        cell.font = Font(size=12)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    # for col in range(start_col, end_col + 1):
    #     relay_cell = ws.cell(row=11, column=col)
    #     relay_cell.value = " "
    #     relay_cell.font = Font(size=12)
    #     relay_cell.alignment = Alignment(horizontal="center", vertical="center")
    #     relay_cell.border = thin_border

    # # Row 12 → Hours (separate cells, no merge)
    # for col in range(start_col, end_col + 1):
    #     hours_cell = ws.cell(row=12, column=col)
    #     hours_cell.value = " "
    #     hours_cell.font = Font(size=12)
    #     hours_cell.alignment = Alignment(horizontal="center", vertical="center")
    #     hours_cell.border = thin_border

    start_col = 1
    end_col = 10
    
    ws.merge_cells(start_row=12, start_column=7, end_row=13, end_column=7)
    relay_cell = ws.cell(row=12, column=7)
    relay_cell.value = "Staff / Worker"
    relay_cell.font = Font(size=12)
    relay_cell.alignment = Alignment(horizontal="center", vertical="center")

    for col in range(start_col, total_cols + 1):
        ws.cell(row=13, column=col).border = thin_border
    
    ws.merge_cells(start_row=12, start_column=8, end_row=12, end_column=8)
    hours_cell = ws.cell(row=12, column=8)
    hours_cell.value = "Relays"
    hours_cell.font = Font(size=12)
    hours_cell.alignment = Alignment(horizontal="center", vertical="center")

    ws.merge_cells(start_row=13, start_column=8, end_row=13, end_column=8)
    hours_cell = ws.cell(row=13, column=8)
    hours_cell.value = "Hours"
    hours_cell.font = Font(size=12)
    hours_cell.alignment = Alignment(horizontal="center", vertical="center")

    for col in range(start_col, total_cols + 1):
        ws.cell(row=12, column=col).border = thin_border    

    
    for col in range(1, total_cols+1): 
        ws.cell(row=1, column=col).border = thin_border


    for col in range(1, total_cols+1):
        ws.cell(row=2, column=col).border = thin_border

    for col in range(1, total_cols+1):
        ws.cell(row=3, column=col).border = thin_border

   
    for col in range(1, 8):
        ws.cell(row=4, column=col).border = thin_border


    for col in range(1, 8):
        ws.cell(row=5, column=col).border = thin_border


    for col in range(1, 8):
        ws.cell(row=6, column=col).border = thin_border

        
    emp_filters = {
        "employee_category": ["in", ["Staff", "Worker"]],
        "company": company
    }

    if employee:  
        emp_filters["name"] = employee

    employees = frappe.get_all(
        "Employee",
        filters=emp_filters,
        fields=["name", "employee_name", "employee_number", "date_of_joining", "relieving_date","employee_category","holiday_list"],
        order_by="FIELD(employee_category, 'Staff', 'Worker')"
    )

    start_row = 15  
    serial = 1
    status_map, lop_map = get_status_map(from_date, to_date, company)
    for emp in employees:
        
        ws.cell(row=start_row, column=1, value=serial)
        ws.cell(row=start_row, column=1).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=start_row, column=1).border = thin_border

        ws.cell(row=start_row, column=2, value="").border = thin_border

        ws.cell(row=start_row, column=3, value=emp.employee_name).border = thin_border
        ws.column_dimensions['C'].width = 23
        
        ws.cell(row=start_row, column=4, value=emp.name).border = thin_border

        doj = emp.date_of_joining.strftime("%d-%m-%Y") if emp.date_of_joining else ""
        ws.cell(row=start_row, column=5, value=doj).border = thin_border
        ws.column_dimensions['E'].width = 12

        exit_date = emp.relieving_date.strftime("%d-%m-%Y") if emp.relieving_date else ""
        ws.cell(row=start_row, column=6, value=exit_date).border = thin_border
        ws.column_dimensions['F'].width = 12

        ws.cell(row=start_row, column=7, value=emp.employee_category).border = thin_border
        ws.column_dimensions['G'].width = 15
        ws.cell(row=start_row, column=8, value="").border = thin_border
        ws.cell(row=start_row, column=9, value="").border = thin_border
    
        for col in range(10, total_cols + 1):
            ws.cell(row=start_row, column=col).border = thin_border
        holiday_list_name = emp.holiday_list
        employee_holidays = frappe.get_all(
            "Holiday",
            filters={"parent": holiday_list_name, "holiday_date": ["between", [from_date, to_date]]},
            fields=["holiday_date", "weekly_off", "national_holiday", "festival_holiday"]
        )

        wo_dates = set()
        nh_dates = set()
        fh_dates = set()
        for h in employee_holidays:
            h_date = h.holiday_date.strftime("%Y-%m-%d")
            if h.weekly_off: wo_dates.add(h_date)
            if h.national_holiday: nh_dates.add(h_date)
            if h.festival_holiday: fh_dates.add(h_date)

        shift_counts = {"A":0, "B":0, "C":0, "G":0, "G1":0, "PP":0, "GE":0}

        emp_status = status_map.get(emp.name, {})
        for i in range(num_days):
            col = 9 + i
            day_date = (from_dt + timedelta(days=i)).strftime("%Y-%m-%d")
            shift_value = emp_status.get(day_date, "")

            if not shift_value:
                if day_date in wo_dates: shift_value = "WW"
                elif day_date in nh_dates: shift_value = "NH"
                elif day_date in fh_dates: shift_value = "FH"

            ws.cell(row=start_row, column=col, value=shift_value).alignment = Alignment(horizontal="center")
            ws.cell(row=start_row, column=col).border = thin_border

            if shift_value in shift_counts: shift_counts[shift_value] += 1

        summary_col = 9 + num_days
        ws.cell(row=start_row, column=summary_col, value=shift_counts["A"]).border = thin_border
        ws.cell(row=start_row, column=summary_col).alignment = Alignment(horizontal="center")
        ws.cell(row=start_row, column=summary_col+1, value=shift_counts["B"]).border = thin_border
        ws.cell(row=start_row, column=summary_col+1).alignment = Alignment(horizontal="center")
        ws.cell(row=start_row, column=summary_col+2, value=shift_counts["C"]).border = thin_border
        ws.cell(row=start_row, column=summary_col+2).alignment = Alignment(horizontal="center")
        ws.cell(row=start_row, column=summary_col+3, value=shift_counts["G"]).border = thin_border
        ws.cell(row=start_row, column=summary_col+3).alignment = Alignment(horizontal="center")
        ws.cell(row=start_row, column=summary_col+4, value=shift_counts["G1"]).border = thin_border
        ws.cell(row=start_row, column=summary_col+4).alignment = Alignment(horizontal="center")
        ws.cell(row=start_row, column=summary_col+5, value=shift_counts["PP"]).border = thin_border
        ws.cell(row=start_row, column=summary_col+5).alignment = Alignment(horizontal="center")
        ws.cell(row=start_row, column=summary_col+6, value=shift_counts["GE"]).border = thin_border
        ws.cell(row=start_row, column=summary_col+6).alignment = Alignment(horizontal="center")
        ws.cell(row=start_row, column=summary_col+7, value=sum(shift_counts.values())).border = thin_border
        ws.cell(row=start_row, column=summary_col+7).alignment = Alignment(horizontal="center")

        working_hours = frappe.get_all(
            "Attendance",
            filters={
                "employee": emp.name,
                "attendance_date": ["between", [from_date, to_date]],
                "docstatus":["!=","2"]
            },
            fields=["total_working_hours"]
        )
        total_working_hours = sum([ot.total_working_hours for ot in working_hours])
        total_working = summary_col + 8  
        ws.cell(row=start_row, column=total_working, value=total_working_hours).border = thin_border
        ws.cell(row=start_row, column=total_working).alignment = Alignment(horizontal="center")
        lop_col = summary_col + 9 
        ws.cell(row=start_row, column=lop_col, value=lop_map.get(emp.name, 0)).border = thin_border
        ws.cell(row=start_row, column=lop_col).alignment = Alignment(horizontal="center")

        
        nh_col = summary_col + 10  
        ws.cell(row=start_row, column=nh_col, value=len(nh_dates)).border = thin_border
        ws.cell(row=start_row, column=nh_col).alignment = Alignment(horizontal="center")

        fh_col = summary_col + 11 
        ws.cell(row=start_row, column=fh_col, value=len(fh_dates)).border = thin_border
        ws.cell(row=start_row, column=fh_col).alignment = Alignment(horizontal="center")

        
        approved_ot = frappe.get_all(
            "Over Time",
            filters={
                "employee": emp.name,
                "ot_date": ["between", [from_date, to_date]],
                "workflow_state": "Approved"  # only approved OT
            },
            fields=["overtime_hours","ot_date"]
        )

        total_approved_hours = sum([ot.overtime_hours for ot in approved_ot])
        total_approved_ot_days = len(set([ot.ot_date.strftime("%Y-%m-%d") for ot in approved_ot]))
       
        total_approved_ot_col = summary_col + 13  
        ws.cell(row=start_row, column=total_approved_ot_col, value=total_approved_hours).border = thin_border
        ws.cell(row=start_row, column=total_approved_ot_col).alignment = Alignment(horizontal="center")
        
        total_approved_ot_days_col = summary_col + 14 
        ws.cell(row=start_row, column=total_approved_ot_days_col, value=total_approved_ot_days).border = thin_border
        ws.cell(row=start_row, column=total_approved_ot_days_col).alignment = Alignment(horizontal="center")

        serial += 1
        start_row += 1

    xls_file = io.BytesIO()
    wb.save(xls_file)
    xls_file.seek(0)


    frappe.local.response["filename"] = "Shift Register 1.xlsx"
    frappe.local.response["filecontent"] = xls_file.getvalue()
    frappe.local.response["type"] = "download"
