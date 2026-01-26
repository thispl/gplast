import frappe
import io
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from datetime import datetime
from openpyxl.styles import Border, Side
from openpyxl.styles import Alignment, Font, Border, Side
from datetime import datetime
from frappe import _
from frappe.utils import add_days, cint, flt, getdate
from datetime import timedelta
from frappe.utils import getdate






def get_opening_balance(employee: str, leave_type: str, filters: dict, carry_forwarded_leaves: float) -> float:
    start_date = filters["from_date"][1][0] 
    opening_balance_date = add_days(start_date, -1)

    
    current_allocation = frappe.get_all(
        "Leave Allocation",
        filters={
            "employee": employee,
            "leave_type": leave_type,
            "from_date": ("<=", start_date),
            "to_date": (">=", start_date),
        },
        fields=["name", "from_date", "to_date", "new_leaves_allocated"],
        limit_page_length=1
    )

    if current_allocation:
        
        opening_balance = carry_forwarded_leaves
    else:
        
        opening_balance = frappe.db.sql(
            """
            SELECT SUM(leaves)
            FROM `tabLeave Ledger Entry`
            WHERE employee = %s
            AND leave_type = %s
            AND from_date <= %s
            """,
            (employee, leave_type, opening_balance_date),
        )[0][0] or 0

    return opening_balance





def get_previous_allocation(from_date, leave_type, employee):
    """Fetch the most recent leave allocation for an employee before a given date."""
    allocation = frappe.get_all(
        "Leave Allocation",
        filters={
            "employee": employee,
            "leave_type": leave_type,
            "from_date": ("<", from_date)
        },
        fields=["name", "from_date", "to_date", "new_leaves_allocated"],
        order_by="to_date desc",
        limit_page_length=1
    )
    if allocation:
        return allocation[0]
    return None




@frappe.whitelist()
def download_leave_wages_excel(from_date, to_date, company=None, employee=None,department=None):
    wb = Workbook()
    ws = wb.active
    ws.title = "Leave Wages"
    
    
    
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
 
    for row in ws.iter_rows(min_row=1, max_row=6, min_col=1, max_col=22):
            for cell in row:
                cell.border = thin_border
    
    ws.merge_cells("A1:V1")
    ws["A1"]="Form 15 (Prescribed under rules 87,88)"
    ws["A1"].alignment= Alignment(horizontal="center")
    
    
    ws.merge_cells("A2:V2")
    ws["A2"]="REGISTER OF LEAVE WITH WAGES"
    ws["A2"].alignment= Alignment(horizontal="center")
    ws["A2"].font=Font(bold=True,size=16)
    
    start_date = getdate(from_date)
    
    ws.merge_cells("A3:K3")
    ws["A3"]=f"""Name and Address of the factory:{company or ""}"""
    
    
    ws.merge_cells("L3:R3")
    ws["L3"]="Name of the Manager / In-charge:"
    
    ws.merge_cells("S3:V3")
    ws["S3"] = f"For the month of: {start_date.strftime('%B')}"
    
    
    ws.merge_cells("A4:K4")
    ws["A4"]="Name and Address of the Occupier:"
    
    ws.merge_cells("L4:R4")
    ws["L4"]="Registration No:"
    
    ws.merge_cells("S4:V4")
    ws["S4"] = f"Year: {start_date.year}"
    
    
    ws.merge_cells("A5:A6") 
    ws.merge_cells("B5:B6") 
    ws.merge_cells("C5:C6") 
    ws.merge_cells("D5:D6") 
    
    ws["A5"]="S.No."
    ws["A5"].alignment= Alignment(vertical="top" , horizontal="center" )
    ws["B5"]="S.No. in Register of adult workers and young persons"
    ws["B5"].alignment= Alignment(vertical="top" , horizontal="center" )
    ws["C5"]="Name of the worker"
    ws["C5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["D5"]="Worker Identity Number"
    ws["D5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["E5"]="Leave at the beginning of the month"
    ws["E5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["F5"]="Leave earned during the period"
    ws["F5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["G5"]="Leave availed during the month"
    ws["G5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["H5"]="Leave balance at the end of the month"
    ws["H5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["I5"]="Leave at the beginning of the month"
    ws["I5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["J5"]="Leave availed during the month"
    ws["J5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["K5"]="Leave balance at the end of the month"
    ws["K5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["L5"]="Leave at the beginning of the month"
    ws["L5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["M5"]="Leave availed during the month"
    ws["M5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["N5"]="Leave balance at the end of the month"
    ws["N5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["O5"]="Date of giving notice of pregnancy / Delivery"
    ws["O5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["P5"]="Amount of maternity benefit paid in advance of expected delivery and date of payment"
    ws["P5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["Q5"]="Subsequent Payment of Maternity benefit and date of payment"
    ws["Q5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["R5"]="Amount paid as Medical Bonus and Date of payment"
    ws["R5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["S5"]="Leave with Wages as per Sections 9 or 10 of the Maternity Benefit Act, 1961"
    ws["S5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["T5"]="Whether nomination received from the Worker"
    ws["T5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["U5"]="Amount paid as Gratuity in case of demise / exit of the worker"
    ws["U5"].alignment= Alignment(vertical="top" , horizontal="center")
    ws["V5"]="Remarks"
    ws["V5"].alignment= Alignment(vertical="top" , horizontal="center")
    
    ws.merge_cells("E6:H6")
    ws.merge_cells("I6:K6")
    ws.merge_cells("L6:N6")
    ws.merge_cells("O6:S6")
    ws.merge_cells("T6:V6")
    
    ws["E6"]="Earned Leave"
    ws["E6"].alignment= Alignment(horizontal="center")
    ws["I6"]="Medical Leave"
    ws["I6"].alignment= Alignment(horizontal="center")
    ws["L6"]="Other Leave"
    ws["L6"].alignment= Alignment(horizontal="center")
    ws["O6"]="Maternity Benefits"
    ws["O6"].alignment= Alignment(horizontal="center")
    ws["T6"]="Gratuity Benefits"
    ws["T6"].alignment= Alignment(horizontal="center")
    
    column_widths = {
        'A': 5,    
        'B': 45,   
        'C': 30,   
        'D': 30,   
        'E': 35,   
        'F': 35,   
        'G': 35,   
        'H': 35,   
        'I': 35,   
        'J': 35,   
        'K': 35,   
        'L': 35,   
        'M': 35,   
        'N': 35,   
        'O': 45,   
        'P': 75,   
        'Q': 60,   
        'R': 60,   
        'S': 65,   
        'T': 40,   
        'U': 60,   
        'V': 20,  
    }

    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width
    
    row =7
    
    filters = {"from_date": ["between", [from_date, to_date]]}

    if company:
        filters["company"] = company
    if employee:
        filters["employee"] = employee    
    if department:
        filters["department"] = department
        
    leave_allocations = frappe.db.get_all(
        "Leave Allocation",
        filters=filters,
        fields=[
            "from_date",
            "employee",
            "employee_name",
            "department",
            "company",
            "new_leaves_allocated",
            "leave_type",
        ]
    )    
    
    
    employee_map = {}
    for la in leave_allocations:
        emp = la.employee
        if emp not in employee_map:
            employee_map[emp] = {
                "name": la.employee_name,
                "earned": {"beginning": 0, "earned": 0, "availed": 0, "balance": 0},
                "medical": {"beginning": 0, "earned": 0, "availed": 0, "balance": 0},
                "other": {"beginning": 0, "earned": 0, "availed": 0, "balance": 0},
            }

        start_date = filters["from_date"][1][0] 

        carry_forwarded_leaves = frappe.db.sql(
            """
            SELECT SUM(leaves)
            FROM `tabLeave Ledger Entry`
            WHERE employee = %s
            AND leave_type = %s
            AND is_carry_forward = 1
            AND from_date <= %s
            """,
            (la.employee, la.leave_type, filters["from_date"][1][0]),
        )[0][0] or 0

        
        opening = get_opening_balance(
            la.employee,
            la.leave_type,
            filters,
            carry_forwarded_leaves=carry_forwarded_leaves,
        )

        earned = la.new_leaves_allocated or 0
        leave_apps = frappe.db.sql(
            """
            SELECT from_date, to_date
            FROM `tabLeave Application`
            WHERE employee = %s
            AND leave_type = %s
            AND status = 'Approved'
            AND (
                    (from_date BETWEEN %s AND %s) OR
                    (to_date BETWEEN %s AND %s) OR
                    (%s BETWEEN from_date AND to_date) OR
                    (%s BETWEEN from_date AND to_date)
                )
            """,
            (
                la.employee,
                la.leave_type,
                from_date, to_date,
                from_date, to_date,
                from_date, to_date
            ),
            as_dict=True
        )

        leaves_taken = 0
        report_start = datetime.strptime(from_date, "%Y-%m-%d").date()
        report_end = datetime.strptime(to_date, "%Y-%m-%d").date()

        for app in leave_apps:
            leave_start = app["from_date"]
            leave_end = app["to_date"]
            overlap_start = max(report_start, leave_start)
            overlap_end = min(report_end, leave_end)
            if overlap_start <= overlap_end:
                leaves_taken += (overlap_end - overlap_start).days + 1

        balance = (opening + earned) - leaves_taken

        if la.leave_type == "Earned Leave":
            employee_map[emp]["earned"] = {
                "beginning": opening,
                "earned": earned,
                "availed": leaves_taken,
                "balance": balance,
            }

        elif la.leave_type == "Medical Leave":
            employee_map[emp]["medical"] = {
                "beginning": opening,
                "earned": earned,
                "availed":leaves_taken,
                "balance": balance,
            }

        else:  
            employee_map[emp]["other"]["beginning"] += opening
            employee_map[emp]["other"]["earned"] += earned
            employee_map[emp]["other"]["availed"] += leaves_taken
            employee_map[emp]["other"]["balance"] += balance
   
   
   
   
       

    for idx, (emp, data) in enumerate(employee_map.items(), start=1):
        ws.cell(row=row, column=1, value=idx).alignment= Alignment(horizontal="center")  
        ws.cell(row=row, column=2, value="")  
        ws.cell(row=row, column=3, value=data["name"])  
        ws.cell(row=row, column=4, value=emp)  
        
        
        ws.cell(row=row, column=5, value=data["earned"]["beginning"])
        ws.cell(row=row, column=6, value=data["earned"]["earned"])
        ws.cell(row=row, column=7, value=data["earned"]["availed"])
        ws.cell(row=row, column=8, value=data["earned"]["balance"])
        
        
        ws.cell(row=row, column=9, value=data["medical"]["beginning"])
        ws.cell(row=row, column=10, value=data["medical"]["availed"])
        ws.cell(row=row, column=11, value=data["medical"]["balance"])
        
        
        ws.cell(row=row, column=12, value=data["other"]["beginning"])
        ws.cell(row=row, column=13, value=data["other"]["availed"])
        ws.cell(row=row, column=14, value=data["other"]["balance"])
        
        
        date_of_delivery = frappe.db.get_value('Maternal Records', {'name': emp}, 'date_of_delivery')
        advance_amount = frappe.db.get_value('Maternal Records', {'name': emp}, 'advance_maternity_benefit_amount')
        advance_date = frappe.db.get_value('Maternal Records', {'name': emp}, 'advance_maternity_benefit_payment_date')
        subsequent_amount = frappe.db.get_value('Maternal Records', {'name': emp}, 'subsequent_maternity_benefit_amount')
        subsequent_date = frappe.db.get_value('Maternal Records', {'name': emp}, 'subsequent_maternity_benefit_payment_date')
        medical_amount = frappe.db.get_value('Maternal Records', {'name': emp}, 'medical_bonus_amount')
        medical_date = frappe.db.get_value('Maternal Records', {'name': emp}, 'medical_bonus_payment_date')
        leave_with_wages = frappe.db.get_value('Maternal Records', {'name': emp}, 'leave_with_wages')

        ws.cell(row=row, column=15, value=date_of_delivery.strftime("%d-%m-%Y") if date_of_delivery else "")
        if advance_amount and advance_date :
            ws.cell(row=row, column=16, value=f"{advance_amount or ''}/{advance_date.strftime('%d-%m-%Y') if advance_date else ''}" )
        else:
            ws.cell(row=row, column=16, value="")
        
        if subsequent_amount and subsequent_date:     	
            ws.cell(row=row, column=17, value=f"{subsequent_amount or ''}/{subsequent_date.strftime('%d-%m-%Y') if subsequent_date else ''}")
        else:
            ws.cell(row=row, column=17, value="")
        
        if medical_amount and medical_date:
            ws.cell(row=row, column=18, value=f"{medical_amount or ''}/{medical_date.strftime('%d-%m-%Y') if medical_date else ''}")
        else:
            ws.cell(row=row, column=18, value="")
        ws.cell(row=row, column=19, value=leave_with_wages or "")
        ws.cell(row=row, column=20, value="")
        ws.cell(row=row, column=21, value="")
        ws.cell(row=row, column=22, value="")
        
        
        for col in range(1, 23):
            ws.cell(row=row, column=col).border = thin_border

        row += 1


                

 
 
 
 
 
 
    xls_file = io.BytesIO()
    wb.save(xls_file)
    xls_file.seek(0)


    frappe.local.response["filename"] = "Leave Wages.xlsx"
    frappe.local.response["filecontent"] = xls_file.getvalue()
    frappe.local.response["type"] = "download"