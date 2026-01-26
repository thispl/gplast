import frappe
import io
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from datetime import datetime
from openpyxl.styles import Border, Side
from openpyxl.styles import Alignment, Font, Border, Side
from datetime import datetime
from datetime import timedelta
# from gplast.gplast.report.attendance_register import attendance_register

def get_holiday_map(from_date, to_date, company=None,employee=None):
    """
    Returns dict {date: "NH"/"FH"/"WW"} based on Holiday List
    """
    holiday_map = {}
    holiday_list = frappe.db.get_value("Employee", employee, "holiday_list")
    if not holiday_list:
        return holiday_map
    # Holiday List fetch
    holidays = frappe.get_all(
        "Holiday",
        filters={"parent": holiday_list,"holiday_date": ["between", [from_date, to_date]]},
        fields=["holiday_date", "national_holiday", "festival_holiday", "weekly_off"]
    )

    for h in holidays:
        if h.national_holiday:
            holiday_map[h.holiday_date.strftime("%Y-%m-%d")] = "NH"
        elif h.festival_holiday:
            holiday_map[h.holiday_date.strftime("%Y-%m-%d")] = "FH"
        elif h.weekly_off:
            holiday_map[h.holiday_date.strftime("%Y-%m-%d")] = "WW"

    return holiday_map


def get_status_map(from_date, to_date, company=None):
    filters = frappe._dict({
        "from_date": from_date,
        "to_date": to_date,
        "company": company
    })

def get_status_map(from_date, to_date, company=None):
    # Returns a dict { employee_id: { date1: status1, date2: status2, ... } }
    attendance_records = frappe.get_all(
        "Attendance",
        filters={
            "attendance_date": ["between", [from_date, to_date]],
            "company": company
        },
        fields=["employee", "attendance_date", "status", "leave_type"]
    )
    
    status_map = {}
    for rec in attendance_records:
        emp_map = status_map.setdefault(rec.employee, {})
        # Format status
        if rec.status == "Present":
            val = "P"
        elif rec.status == "Absent":
            val = "A"
        elif rec.status == "On Leave":
            # val = rec.leave_type or "L" 
            if rec.leave_type == "Casual Leave" :
                val = "CL"
            elif rec.leave_type == "Earned Leave" :
                val = "EL"
            elif rec.leave_type == "Compensatory Off" :
                val = "C.OFF" 
            elif rec.leave_type == "Leave Without Pay" :
                val = "LWP" 
            elif rec.leave_type == "Privilege Leave" :
                val = "PL"
            elif rec.leave_type == "Sick Leave" :
                val = "SL" 
            elif rec.leave_type == "Medical Leave" :
                val = "ML"
            else:
                val = " "                             
        elif rec.status == "Half Day":
            val = "HD"
        else:
            val = ""
        
        emp_map[rec.attendance_date.strftime("%Y-%m-%d")] = val
    


    return status_map

@frappe.whitelist()
def download_form25_excel(from_date=None, to_date=None, company=None, company_address = None, employee=None):
    wb = Workbook()
    ws = wb.active
    ws.title = "Form25"

    if from_date and to_date:
        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_dt = datetime.strptime(to_date, "%Y-%m-%d")
        num_days = (to_dt - from_dt).days + 1  # inclusive
    else:
        from_dt = None
        to_dt = None
        num_days = 31
    
    # Date formatter
    def format_date(date_str):
        if not date_str:
            return "_________"
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
        except:
            return date_str

    # Total columns for header rows (first 3 rows)
    total_cols = 16 + num_days

    # Row 1
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=total_cols)
    cell = ws.cell(row=1, column=1)
    cell.value = ""
    cell.font = Font(bold=True, size=14)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 20

    # Row 2
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=total_cols)
    cell = ws.cell(row=2, column=1)
    cell.value = "Form No. 25 [Prescribed under rule 77(4), 103]"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30
    # Row 3
    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=total_cols)
    cell = ws.cell(row=3, column=1)
    cell.value = "MUSTER ROLL AND REGISTER OF COMPENSATORY HOLIDAYS "
    cell.font = Font(size=14, bold=True)
    cell.alignment = Alignment(horizontal="center", vertical="center")

    right_merge_start = total_cols - 3
    right_merge_end = total_cols

    ws.merge_cells(start_row=4, start_column=right_merge_start, end_row=4, end_column=right_merge_end)
    cell = ws.cell(row=4, column=right_merge_start)
    cell.value = "For the period"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[4].height = 20

    # Row 5 -> "From <date>"
    ws.merge_cells(start_row=5, start_column=right_merge_start, end_row=5, end_column=right_merge_end)
    cell = ws.cell(row=5, column=right_merge_start)
    cell.value = f"From {format_date(from_date)}"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[5].height = 20

    # Row 6 -> "To <date>"
    ws.merge_cells(start_row=6, start_column=right_merge_start, end_row=6, end_column=right_merge_end)
    cell = ws.cell(row=6, column=right_merge_start)
    cell.value = f"To {format_date(to_date)}"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[6].height = 20

    # Border for merged ranges (rows 4, 5, 6)
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )
    for r in (4, 5, 6):
        for c in range(right_merge_start, right_merge_end + 1):
            ws.cell(row=r, column=c).border = thin_border

   
    # 5th row - Name and Address of the Factory (A to J)
    ws.merge_cells(start_row=5, start_column=1, end_row=5, end_column=7)
    cell = ws.cell(row=5, column=1)
    cell.value = "Name and Address of the Factory :"
    cell.font = Font( size=12)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[5].height = 20

    ws.merge_cells(start_row=8, start_column=1, end_row=8, end_column=7)
    cell = ws.cell(row=8, column=1)
    cell.value = "Registration No:"
    cell.font = Font( size=12)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[5].height = 20
    for col in range(1, 8):   
        ws.cell(row=8, column=col).border = thin_border

    ws.merge_cells(start_row=5, start_column=11, end_row=5, end_column=17)
    cell = ws.cell(row=5, column=11)
    cell.value = "Festival Holidays Approval Proceedings No. and Date:\nApproved Festival Holidays:"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[5].height = 40
    for col in range(11, 18): 
        ws.cell(row=5, column=col).border = thin_border 

    for col in range(11, 18):  
        ws.cell(row=6, column=col, value=str(col-10))  
        ws.cell(row=6, column=col).border = thin_border
        ws.cell(row=6, column=col).alignment = Alignment(horizontal="center", vertical="center")

    ws.row_dimensions[6].height = 20

    # for col in range(11, 18):  # 11 to 17
    #     ws.cell(row=7, column=col, value= " ") 
    #     ws.cell(row=7, column=col).border = thin_border
    #     ws.cell(row=7, column=col).alignment = Alignment(horizontal="center", vertical="center")

    # ws.row_dimensions[7].height = 20
    
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
        else:
            value = ""  # empty box

        cell = ws.cell(row=7, column=col, value=value)
        cell.border = thin_border
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.column_dimensions[cell.column_letter].width = 15

    # Increase row height for 2 lines
    ws.row_dimensions[7].height = 30

    ws.merge_cells(start_row=6, start_column=1, end_row=6, end_column=7)
    cell = ws.cell(row=6, column=1)
    cell.value = f"{company}\n{company_address}"  
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[6].height = 30  

    ws.row_dimensions[7].height = 15
    ws.row_dimensions[8].height = 15

    ws.row_dimensions[9].height = 30   
    ws.row_dimensions[10].height = 30  

    headers = [
        "Serial Number",
        "Serial Number\nin Register\nof adult workers",
        "Name of the worker",         
        "Worker Identity Number",      
        "Time at which work commences",
        "Rest Interval",
        "Time at which work ends"
    ]   

    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    col_num = 1
    for header in headers:
        if header == "Name of the worker":
            ws.merge_cells(start_row=9, start_column=col_num, end_row=11, end_column=col_num+1)
            cell = ws.cell(row=9, column=col_num)
            cell.value = header
            cell.font = Font(size=12)
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

            for row in range(9, 12):
                ws.cell(row=row, column=col_num).border = thin_border
                ws.cell(row=row, column=col_num+1).border = thin_border

            col_num += 2

        elif header == "Worker Identity Number":
            ws.merge_cells(start_row=9, start_column=col_num, end_row=11, end_column=col_num+1)
            cell = ws.cell(row=9, column=col_num)
            cell.value = header
            cell.font = Font(size=12)
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

            for row in range(9, 12):
                ws.cell(row=row, column=col_num).border = thin_border
                ws.cell(row=row, column=col_num+1).border = thin_border

            col_num += 2

        else:
            ws.merge_cells(start_row=9, start_column=col_num, end_row=11, end_column=col_num)
            cell = ws.cell(row=9, column=col_num)
            cell.value = header
            cell.font = Font(size=12)
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

            for row in range(9, 12):
                ws.cell(row=row, column=col_num).border = thin_border

            col_num += 1


    ws.cell(row=9, column=10).value = "Hours"
    ws.cell(row=10, column=10).value = "Relay"
    ws.cell(row=11, column=10).value = "Scheme of Shifts"

    for r in range(9, 12):
        cell = ws.cell(row=r, column=10)
        cell.font = Font(size=12)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border    
    for row in range(9, 12):
        ws.cell(row=row, column=10).border = thin_border

     
    start_col = 11
    end_col = start_col + num_days - 1  

    ws.merge_cells(start_row=11, start_column=start_col, end_row=11, end_column=end_col)
    cell = ws.cell(row=11, column=start_col)
    cell.value = "Daily Hours of work including overtime (if any)"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    for c in range(start_col, end_col + 1):
        merged_cell = ws.cell(row=11, column=c)
        merged_cell.border = thin_border


    for i, col in enumerate(range(start_col, end_col + 1), start=1):
        ws.merge_cells(start_row=9, start_column=col, end_row=10, end_column=col)

        cell = ws.cell(row=9, column=col)
        cell.value = i
        cell.font = Font(size=12)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        
        for r in range(9, 11):
            ws.cell(row=r, column=col).border = thin_border

    next_col = end_col + 1

    ws.merge_cells(start_row=9, start_column=next_col, end_row=11, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Total Days Worked"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border
    ws.cell(row=11, column=next_col).border = thin_border

    next_col += 1
    ws.merge_cells(start_row=9, start_column=next_col, end_row=11, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Number of days on Loss of Pay"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border
    ws.cell(row=11, column=next_col).border = thin_border

    next_col += 1
    ws.merge_cells(start_row=9, start_column=next_col, end_row=11, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Total Hours Worked"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border
    ws.cell(row=11, column=next_col).border = thin_border

    next_col += 1
    ws.merge_cells(start_row=9, start_column=next_col, end_row=11, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Benefit availed for working on National Holiday"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border
    ws.cell(row=11, column=next_col).border = thin_border

    next_col += 1
    ws.merge_cells(start_row=9, start_column=next_col, end_row=11, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Benefit availed for working on Festival Holiday"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border
    ws.cell(row=11, column=next_col).border = thin_border

    next_col += 1
    ws.merge_cells(start_row=9, start_column=next_col, end_row=11, end_column=next_col)
    cell = ws.cell(row=9, column=next_col)
    cell.value = "Remarks"
    cell.font = Font(size=12)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=9, column=next_col).border = thin_border
    ws.cell(row=10, column=next_col).border = thin_border
    ws.cell(row=11, column=next_col).border = thin_border
    
    for col in range(start_col, end_col + 1):
        ws.cell(row=9, column=col).border = thin_border


    for col in range(1, total_cols+1):
        ws.cell(row=2, column=col).border = thin_border

    for col in range(1, total_cols+1):
        ws.cell(row=3, column=col).border = thin_border


    for col in range(1, 8):
        ws.cell(row=5, column=col).border = thin_border

    for col in range(1, 8):
        ws.cell(row=6, column=col).border = thin_border

    if employee:
        employees = frappe.get_all(
            "Employee",
            filters={"name": employee, "company": company},
            fields=["name", "employee_name", "employee_number", "date_of_joining", "relieving_date"]
        )
    else:
        employees = frappe.get_all(
            "Employee",
            filters={"employee_category": ["in", ["Staff", "Worker"]], "company": company},
            fields=["name", "employee_name", "employee_number", "date_of_joining", "relieving_date"]
        )

    start_row = 12 
    serial = 1
    status_map = get_status_map(from_date, to_date, company)
    for emp in employees:
        holiday_map = get_holiday_map(from_date, to_date, company, emp.name)
        ws.cell(row=start_row, column=1, value=serial)
        ws.cell(row=start_row, column=1).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=start_row, column=1).border = thin_border

        ws.cell(row=start_row, column=2, value="").border = thin_border

        ws.merge_cells(start_row=start_row, start_column=3, end_row=start_row, end_column=4)
        cell = ws.cell(row=start_row, column=3)
        cell.value = emp.employee_name  
        cell.alignment = Alignment(horizontal="left", vertical="center")
        cell.border = thin_border
        ws.cell(row=start_row, column=4).border = thin_border  
        ws.merge_cells(start_row=start_row, start_column=5, end_row=start_row, end_column=6)
        cell = ws.cell(row=start_row, column=5)
        cell.value = emp.name  
        cell.alignment = Alignment(horizontal="left", vertical="center")
        cell.border = thin_border
        ws.cell(row=start_row, column=6).border = thin_border  

        ws.cell(row=start_row, column=7, value="08:00").border = thin_border
        ws.cell(row=start_row, column=8, value="00:30").border = thin_border
        ws.cell(row=start_row, column=9, value="17:00").border = thin_border
        for col in range(10, total_cols + 1):
            ws.cell(row=start_row, column=col).border = thin_border
        emp_status = status_map.get(emp.name, {})
        
        for i in range(num_days):
            col = 11 + i  
            day_date = (from_dt + timedelta(days=i)).strftime("%Y-%m-%d")
            if day_date in holiday_map:
                value = holiday_map[day_date]
            else:
                value = emp_status.get(day_date, "")
            ws.cell(row=start_row, column=col, value=value).alignment = Alignment(horizontal="center", vertical="center")
            ws.cell(row=start_row, column=col).border = thin_border

        total_days_worked = 0
        total_days_absent = 0
        total_hrs = 0
        total_nh = 0
        total_fh = 0

        for i in range(num_days):
            day_date = (from_dt + timedelta(days=i)).strftime("%Y-%m-%d")
            if day_date in holiday_map:
                val = holiday_map[day_date]
            else:
                val = emp_status.get(day_date, "")

            if val in ["P", "EL", "CL", "SL", "WW"]:
                total_days_worked += 1
            elif val == "HD":  
                total_days_worked += 0.5
                total_days_absent += 0.5
            elif val in ["A", "LOP"]:
                total_days_absent += 1
            elif val == "NH":
                total_nh += 1
            elif val == "FH":
                total_fh += 1      

        total_hrs = total_days_worked * 8

        total_worked_col = 11 + num_days
        ws.cell(row=start_row, column=total_worked_col, value=total_days_worked).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=start_row, column=total_worked_col).border = thin_border

        total_absent_col = total_worked_col + 1
        ws.cell(row=start_row, column=total_absent_col, value=total_days_absent).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=start_row, column=total_absent_col).border = thin_border

        total_hrs_col = total_absent_col + 1
        ws.cell(row=start_row, column=total_hrs_col, value=total_hrs).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=start_row, column=total_hrs_col).border = thin_border

        total_nh_col = total_hrs_col + 1
        ws.cell(row=start_row, column=total_nh_col, value=total_nh).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=start_row, column=total_nh_col).border = thin_border

        total_fh_col = total_nh_col + 1
        ws.cell(row=start_row, column=total_fh_col, value=total_fh).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=start_row, column=total_fh_col).border = thin_border

        serial += 1
        start_row += 1


    xls_file = io.BytesIO()
    wb.save(xls_file)
    xls_file.seek(0)

    frappe.local.response["filename"] = "Form25.xlsx"
    frappe.local.response["filecontent"] = xls_file.getvalue()
    frappe.local.response["type"] = "download"
