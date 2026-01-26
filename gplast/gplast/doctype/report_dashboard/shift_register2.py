import frappe
import io
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from datetime import datetime
from openpyxl.styles import Border, Side
from openpyxl.styles import Alignment, Font, Border, Side
from datetime import datetime
from openpyxl.utils import get_column_letter
from datetime import timedelta
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
        fields=["employee", "attendance_date", "shift", "status"]
    )
    
    status_map = {}
    lop_map = {}
    
    for rec in attendance_records:
        emp_map = status_map.setdefault(rec.employee, {})
        emp_map[rec.attendance_date.strftime("%Y-%m-%d")] = rec.shift or ""
        
        if rec.status == "On Leave" and rec.leave_type == "Leave Without Pay":
            lop_map[rec.employee] = lop_map.get(rec.employee, 0) + 1

    
    return status_map, lop_map



@frappe.whitelist()
def download_form25_excel(from_date=None, to_date=None, company=None, company_address = None, employee=None):
    wb = Workbook()
    ws = wb.active
    ws.title = "Shift Register 2"

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

    total_cols = 36 + num_days

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

    ws.merge_cells(start_row=5, start_column=1, end_row=5, end_column=7)
    cell = ws.cell(row=5, column=1)
    cell.value = "Name and Address of the Factory :"
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
        ws.cell(row=6, column=col).font = Font(size=12, bold=True)
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
        "Father Name",
        "Designation or Nature Work",
        "Place of Employement",
        "Date of Birth",
        "Period of Work",
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

    
    start_col = 14
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
    cell.value = "Number and Date of Exampting Order"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border
    col_letter = get_column_letter(next_col)
    ws.column_dimensions[col_letter].width = 12

    next_col += 1
    ws.merge_cells(start_row=9, start_column=next_col, end_row=10, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Year"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border

    quarters = ["January to March", "April to June", "July to September", "October to December"]

    next_col += 1
    ws.merge_cells(start_row=9, start_column=next_col, end_row=9, end_column=next_col+3)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Weekly rest days lost due to the Exempting order in……"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for i, q in enumerate(quarters):
        col = next_col + i
        cell = ws.cell(row=10, column=col)
        cell.value = q
        cell.font = Font(size=12)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
        ws.cell(row=9, column=col).border = thin_border

    next_col += 4
    ws.merge_cells(start_row=9, start_column=next_col, end_row=9, end_column=next_col+3)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Date of Compensatory Holiday given in……"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


    for i, q in enumerate(quarters):
        col = next_col + i
        cell = ws.cell(row=10, column=col)
        cell.value = q
        cell.font = Font(size=12)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
        ws.cell(row=9, column=col).border = thin_border

    next_col += 4
    ws.merge_cells(start_row=9, start_column=next_col, end_row=10, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Lost rest days Carried on to the next year"
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
    
    ws.merge_cells(start_row=12, start_column=12, end_row=13, end_column=12)
    relay_cell = ws.cell(row=12, column=12)
    relay_cell.value = "Staff / Worker"
    relay_cell.font = Font(size=12)
    relay_cell.alignment = Alignment(horizontal="center", vertical="center")

    for col in range(start_col, total_cols + 1):
        ws.cell(row=13, column=col).border = thin_border
    
    ws.merge_cells(start_row=12, start_column=13, end_row=12, end_column=13)
    hours_cell = ws.cell(row=12, column=13)
    hours_cell.value = "Relays"
    hours_cell.font = Font(size=12)
    hours_cell.alignment = Alignment(horizontal="center", vertical="center")

    ws.merge_cells(start_row=13, start_column=13, end_row=13, end_column=13)
    hours_cell = ws.cell(row=13, column=13)
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
        fields=["name", "employee_name", "employee_number", "date_of_joining", "relieving_date","employee_category","holiday_list","father_name","designation","date_of_birth","employee_plant"],
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
        ws.column_dimensions['D'].width = 14

        doj = emp.date_of_joining.strftime("%d-%m-%Y") if emp.date_of_joining else ""
        dob = emp.date_of_birth.strftime("%d-%m-%Y") if emp.date_of_birth else ""
        ws.cell(row=start_row, column=5, value=emp.father_name).border = thin_border
        ws.column_dimensions['E'].width = 20

        exit_date = emp.relieving_date.strftime("%d-%m-%Y") if emp.relieving_date else ""
        ws.cell(row=start_row, column=6, value=emp.designation).border = thin_border
        ws.column_dimensions['F'].width = 32

        ws.cell(row=start_row, column=7, value=emp.employee_plant).border = thin_border
        ws.column_dimensions['G'].width = 14
        ws.cell(row=start_row, column=8, value=dob).border = thin_border
        ws.column_dimensions['H'].width = 12
        ws.cell(row=start_row, column=9, value="").border = thin_border
        ws.cell(row=start_row, column=10, value=doj).border = thin_border
        ws.column_dimensions['J'].width = 14
        ws.cell(row=start_row, column=11, value=exit_date).border = thin_border
        ws.column_dimensions['K'].width = 12
        ws.cell(row=start_row, column=12, value=emp.employee_category).border = thin_border
        ws.column_dimensions['L'].width = 15
        ws.cell(row=start_row, column=13, value="").border = thin_border

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
            h_date = h.holiday_date  
            if h.weekly_off:
                wo_dates.add(h_date)
            if h.national_holiday:
                nh_dates.add(h_date)
            if h.festival_holiday:
                fh_dates.add(h_date)
        
        year_start = datetime(from_dt.year, 1, 1).date()
        year_end = datetime(from_dt.year, 12, 31).date()
        holiday_list_name = emp.holiday_list
        quarter_counts = [0, 0, 0, 0]

        if holiday_list_name:
            employee_holidays = frappe.get_all(
                "Holiday",
                filters={"parent": holiday_list_name, "holiday_date": ["between", [year_start, year_end]]},
                fields=["holiday_date", "weekly_off"]
            )
            wo_dates = [h.holiday_date for h in employee_holidays if h.weekly_off]

            for wo_date in wo_dates:
                month = wo_date.month
                if 1 <= month <= 3:
                    quarter_counts[0] += 1
                elif 4 <= month <= 6:
                    quarter_counts[1] += 1
                elif 7 <= month <= 9:
                    quarter_counts[2] += 1
                elif 10 <= month <= 12:
                    quarter_counts[3] += 1
        else:
            wo_dates = []
        
        comp_leave_counts = [0, 0, 0, 0]  

        comp_leaves = frappe.get_all(
            "Compensatory Leave Request",
            filters={
                "employee": emp.name,
                "work_from_date": ["between", [year_start, year_end]],
                "workflow_state": "Approved"
            },
            fields=["work_from_date"]
        )

        for cl in comp_leaves:
            cl_date = cl["work_from_date"]
            month = cl_date.month
            if 1 <= month <= 3:
                comp_leave_counts[0] += 1
            elif 4 <= month <= 6:
                comp_leave_counts[1] += 1
            elif 7 <= month <= 9:
                comp_leave_counts[2] += 1
            elif 10 <= month <= 12:
                comp_leave_counts[3] += 1


        shift_counts = {"A":0, "B":0, "C":0, "G":0, "G1":0, "PP":0, "GE":0}

        emp_status = status_map.get(emp.name, {})
        for i in range(num_days):
            col = 14 + i
            day_date_obj = (from_dt + timedelta(days=i)).date()  # <-- datetime.date
            shift_value = emp_status.get(day_date_obj.strftime("%Y-%m-%d"), "")

            if not shift_value:
                if day_date_obj in wo_dates:
                    shift_value = "WW"
                elif day_date_obj in nh_dates:
                    shift_value = "NH"
                elif day_date_obj in fh_dates:
                    shift_value = "FH"

            ws.cell(row=start_row, column=col, value=shift_value).alignment = Alignment(horizontal="center")
            ws.cell(row=start_row, column=col).border = thin_border

            if shift_value in shift_counts: shift_counts[shift_value] += 1

        summary_col = 14 + num_days
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

        nh_col = summary_col + 7  
        ws.cell(row=start_row, column=nh_col, value=len(nh_dates)).border = thin_border
        ws.cell(row=start_row, column=nh_col).alignment = Alignment(horizontal="center")

        fh_col = summary_col + 8 
        ws.cell(row=start_row, column=fh_col, value=len(fh_dates)).border = thin_border
        ws.cell(row=start_row, column=fh_col).alignment = Alignment(horizontal="center")

        remark_col = summary_col + 9 
        ws.cell(row=start_row, column=remark_col, value="").border = thin_border

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
        
        total_approved_ot_col = summary_col + 10
        ws.cell(row=start_row, column=total_approved_ot_col, value=total_approved_hours).border = thin_border
        ws.cell(row=start_row, column=total_approved_ot_col).alignment = Alignment(horizontal="center")

        exampting_order = summary_col + 11  
        ws.cell(row=start_row, column=exampting_order, value="").border = thin_border
        ws.cell(row=start_row, column=exampting_order).alignment = Alignment(horizontal="center")


        from_dt_obj = datetime.strptime(from_date, "%Y-%m-%d")
        year_value = from_dt_obj.year

        year_col = exampting_order + 1
        ws.cell(row=start_row, column=year_col, value=year_value).border = thin_border
        ws.cell(row=start_row, column=year_col).alignment = Alignment(horizontal="center")

        weekly_off_start_col = year_col + 1  
        for i, count in enumerate(quarter_counts):
            ws.cell(row=start_row, column=weekly_off_start_col + i, value=count).border = thin_border
            ws.cell(row=start_row, column=weekly_off_start_col).alignment = Alignment(horizontal="center")

        comp_start_col = year_col + 5  
        for i, count in enumerate(comp_leave_counts):
            ws.cell(row=start_row, column=comp_start_col + i, value=count).border = thin_border
            ws.cell(row=start_row, column=comp_start_col).alignment = Alignment(horizontal="center")

        lost_rest_days=comp_start_col+4
        ws.cell(row=start_row, column=lost_rest_days, value="").border = thin_border

        remark=lost_rest_days+1
        ws.cell(row=start_row, column=remark, value="").border = thin_border



        serial += 1
        start_row += 1


    xls_file = io.BytesIO()
    wb.save(xls_file)
    xls_file.seek(0)
    frappe.local.response["filename"] = "Shift Register 2.xlsx"
    frappe.local.response["filecontent"] = xls_file.getvalue()
    frappe.local.response["type"] = "download"
