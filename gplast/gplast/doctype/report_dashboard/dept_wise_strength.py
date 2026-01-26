import frappe
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from io import BytesIO
from frappe.utils import getdate

@frappe.whitelist()
def download_daily_strength(from_date=None, to_date=None, unit=None):

    
    filters = {
        "attendance_date": ["between", [from_date, to_date]],
        "docstatus": ["!=", 2]
    }
    if unit:
        filters["unit"] = unit


    dept_list = frappe.db.get_all("Attendance", filters=filters, pluck="department")
    departments = sorted({d for d in dept_list if d})
    staff_fill = PatternFill(start_color="FFC0CB", end_color="FFC0CB", fill_type="solid")           
    company_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")   # Light Blue
    contractor_fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid") # Light Gray

    dep_designations = {}
    for dep in departments:

        dep_filter = {
            "department": dep,
            "attendance_date": ["between", [from_date, to_date]],
            "docstatus": ["!=", 2]
        }

        if unit:
            dep_filter["unit"] = unit

        desigs = frappe.db.get_all(
            "Attendance",
            filters=dep_filter,
            pluck="designation" 
        )

        dep_designations[dep] = sorted({d for d in desigs if d})


    wb = Workbook()
    ws = wb.active
    ws.title = "Daily Strength"

    thin = Side(border_style="thin", color="000000")
    border = Border(top=thin, bottom=thin, left=thin, right=thin)

    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 12

    ws.merge_cells("A1:A4")
    ws.merge_cells("B1:B4")
    ws["A1"] = "S.NO"
    ws["B1"] = "DATE"

    for col in ["A1", "B1"]:
        ws[col].font = Font(bold=True)
        ws[col].alignment = Alignment(horizontal="center", vertical="center")
        ws[col].border = border


    row1, row2, row3, row4 = 1, 2, 3, 4 
    col = 3
    col_map = {}

    for dep, desigs in dep_designations.items():

        block_items = ["Staff"] + desigs
        total_columns = 3 + (len(desigs) * 6)

        ws.merge_cells(start_row=row1, start_column=col, end_row=row1, end_column=col + total_columns - 1)
        ws.cell(row=row1, column=col).value = dep
        ws.cell(row=row1, column=col).font = Font(bold=True, size=12)
        ws.cell(row=row1, column=col).alignment = Alignment(horizontal="center", vertical="center")

        col_map[dep] = {}

        for item in block_items:

            if item == "Staff":
                ws.merge_cells(start_row=row2, start_column=col, end_row=row3, end_column=col + 2)
                # ws.cell(row=row2, column=col).value = "Staff"
                # ws.cell(row=row2, column=col).font = Font(bold=True)
                # ws.cell(row=row2, column=col).alignment = Alignment(horizontal="center", vertical="center")
                header_cell = ws.cell(row=row2, column=col)
                header_cell.value = "Staff"
                header_cell.font = Font(bold=True)
                header_cell.alignment = Alignment(horizontal="center", vertical="center")
                header_cell.fill = staff_fill 

                col_map[dep]["Staff"] = col
                

                labels = ["HC", "L/A", "P"]
                for i in range(3):
                    c = ws.cell(row=row4, column=col + i)
                    c.value = labels[i]
                    c.font = Font(bold=True)
                    c.alignment = Alignment(horizontal="center", vertical="center")
                    c.border = border
                    c.fill = staff_fill   
                    ws.column_dimensions[c.column_letter].width = 6

                col += 3

            else:
                ws.merge_cells(start_row=row2, start_column=col, end_row=row2, end_column=col + 5)
                # ws.cell(row=row2, column=col).value = item
                # ws.cell(row=row2, column=col).font = Font(bold=True)
                # ws.cell(row=row2, column=col).alignment = Alignment(horizontal="center", vertical="center")

                main_cell = ws.cell(row=row2, column=col)
                main_cell.value = item
                main_cell.font = Font(bold=True)
                main_cell.alignment = Alignment(horizontal="center", vertical="center")

                ws.merge_cells(start_row=row3, start_column=col, end_row=row3, end_column=col + 2)
                ws.merge_cells(start_row=row3, start_column=col + 3, end_row=row3, end_column=col + 5)

                # ws.cell(row=row3, column=col).value = "COMPANY EMPLOYEES"
                # ws.cell(row=row3, column=col + 3).value = "CONTRACT EMPLOYEES"
                comp_cell = ws.cell(row=row3, column=col)
                comp_cell.value = "COMPANY EMPLOYEES"
                comp_cell.font = Font(bold=True)
                comp_cell.alignment = Alignment(horizontal="center", vertical="center")
                comp_cell.fill = company_fill      

                cont_cell = ws.cell(row=row3, column=col + 3)
                cont_cell.value = "CONTRACT EMPLOYEES"
                cont_cell.font = Font(bold=True)
                cont_cell.alignment = Alignment(horizontal="center", vertical="center")
                cont_cell.fill = contractor_fill

                col_map[dep][item] = col
                
                labels = ["HC", "L/A", "P", "HC", "L/A", "P"]
                for i in range(6):
                    c = ws.cell(row=row4, column=col + i)
                    c.value = labels[i]
                    c.font = Font(bold=True)
                    c.alignment = Alignment(horizontal="center", vertical="center")
                    c.border = border
                    if i < 3:
                        c.fill = company_fill
                    else:
                        c.fill = contractor_fill
                    ws.column_dimensions[c.column_letter].width = 7

                col += 6


    overall_start = col

    ws.merge_cells(start_row=row1, start_column=overall_start, end_row=row1, end_column=overall_start + 8)
    ws.cell(row=row1, column=overall_start).value = "OVERALL TOTAL"
    ws.cell(row=row1, column=overall_start).font = Font(bold=True, size=12)
    ws.cell(row=row1, column=overall_start).alignment = Alignment(horizontal="center", vertical="center")

    ws.merge_cells(start_row=row2, start_column=overall_start, end_row=row3, end_column=overall_start + 2)
    ws.cell(row=row2, column=overall_start).value = "Staff"
    ws.cell(row=row2, column=overall_start).font = Font(bold=True)
    ws.cell(row=row2, column=overall_start).alignment = Alignment(horizontal="center", vertical="center")

    ws.merge_cells(start_row=row2, start_column=overall_start + 3, end_row=row3, end_column=overall_start + 5)
    ws.cell(row=row2, column=overall_start + 3).value = "Company Employees"
    ws.cell(row=row2, column=overall_start + 3).font = Font(bold=True)
    ws.cell(row=row2, column=overall_start + 3).alignment = Alignment(horizontal="center", vertical="center")

    ws.merge_cells(start_row=row2, start_column=overall_start + 6, end_row=row3, end_column=overall_start + 8)
    ws.cell(row=row2, column=overall_start + 6).value = "Contract Employees"
    ws.cell(row=row2, column=overall_start + 6).font = Font(bold=True)
    ws.cell(row=row2, column=overall_start + 6).alignment = Alignment(horizontal="center", vertical="center")

    labels = ["HC", "L/A", "P"]
    pos = 0
    for grp in range(3):
        for j in range(3):
            c = ws.cell(row=row4, column=overall_start + pos)
            c.value = labels[j]
            c.font = Font(bold=True)
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.border = border
            ws.column_dimensions[c.column_letter].width = 7
            pos += 1
    
    total_col_start = overall_start + 9  

    ws.merge_cells(start_row=1, start_column=total_col_start, 
                end_row=3, end_column=total_col_start + 2)
    ws.cell(row=1, column=total_col_start).value = "TOTAL"
    ws.cell(row=1, column=total_col_start).alignment = Alignment(
        horizontal="center", vertical="center", wrap_text=True
    )

    ws.cell(row=4, column=total_col_start).value = "HC"
    ws.cell(row=4, column=total_col_start + 1).value = "L/A"
    ws.cell(row=4, column=total_col_start + 2).value = "P"

    for c in range(total_col_start, total_col_start + 3):
        ws.cell(row=4, column=c).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=5, column=c).alignment = Alignment(horizontal="center", vertical="center")

    start_col = ws.max_column + 1

    groups = ["Staff", "Company Employees", "Contractor"]
    sub_cols = ["HC", "Addition", "Deletion", "Total"]

    for idx, grp in enumerate(groups):
        col_start = start_col + (idx * 4)
        col_end = col_start + 3
        ws.merge_cells(start_row=1, start_column=col_start,
                    end_row=3, end_column=col_end)
        ws.cell(row=1, column=col_start).value = grp
        ws.cell(row=1, column=col_start).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=1, column=col_start).font = Font(bold=True)

        for i, c in enumerate(sub_cols):
            ws.cell(row=4, column=col_start + i).value = c
            ws.cell(row=4, column=col_start + i).alignment = Alignment(horizontal="center", vertical="center")
            ws.cell(row=4, column=col_start + i).font = Font(bold=True)
        fill_staff = PatternFill(start_color="FFC0CB", end_color="FFC0CB", fill_type="solid")   # Pink
        fill_company = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid") # Light Blue
        fill_contractor = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid") # Light Gray

        for col_i in range(col_start, col_start + 4):
            for row_i in range(1, 6):     # Row 1–5 include headings + first data row
                cell = ws.cell(row=row_i, column=col_i)

                if grp == "Staff":
                    cell.fill = fill_staff
                elif grp == "Company Employees":
                    cell.fill = fill_company
                elif grp == "Contractor":
                    cell.fill = fill_contractor    
    start_col = ws.max_column + 1
    contractor_names = frappe.db.get_all(
        "Employee",
        filters={
            "employee_category": "Contractor",
            **({"unit": unit} if unit else {})
        },
        pluck="employee_contractor_name"
    )      

    contractor_names = sorted({cname for cname in contractor_names if cname})

    contractor_company_columns = {}

    for cname in contractor_names:
        ws.merge_cells(start_row=1, start_column=start_col, end_row=3, end_column=start_col + 3)
        ws.cell(row=1, column=start_col).value = cname
        ws.cell(row=1, column=start_col).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=1, column=start_col).font = Font(bold=True)

        for i, c in enumerate(sub_cols):
            col = start_col + i
            ws.cell(row=4, column=col).value = c
            ws.cell(row=4, column=col).alignment = Alignment(horizontal="center", vertical="center")
            ws.cell(row=4, column=col).font = Font(bold=True)

        contractor_company_columns[cname] = start_col
        start_col += 4


    ws.merge_cells(start_row=1, start_column=start_col, end_row=3, end_column=start_col + 3)
    ws.cell(row=1, column=start_col).value = "Total HC"
    ws.cell(row=1, column=start_col).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=1, column=start_col).font = Font(bold=True)

    for i, c in enumerate(sub_cols):
        col = start_col + i
        ws.cell(row=4, column=col).value = c
        ws.cell(row=4, column=col).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=4, column=col).font = Font(bold=True)

    data = frappe.db.get_all(
        "Attendance",
        filters=filters,
        fields=[
            "employee",
            "status",
            "department",
            "designation",
            "attendance_date",
            "employee.employee_category as employee_category"
        ],
        order_by="attendance_date"
    )
    filtered_data = [] 
    for d in data:
        emp_cat = frappe.db.get_value("Employee", d.employee, "employee_category")
        if not emp_cat:
            continue

        d["employee_category"] = emp_cat
        d["attendance_date"] = getdate(d["attendance_date"])
        filtered_data.append(d)
    unique_dates = sorted({d["attendance_date"] for d in filtered_data})
    row = 5
    s_no = 1
    # unique_dates = sorted({d["attendance_date"] for d in data})

    for date in unique_dates:
        
        ws.cell(row=row, column=1).value = s_no
        date_cell = ws.cell(row=row, column=2)
        date_cell.value = date
        date_cell.number_format = "DD-MM-YYYY"
        
        for dep in col_map:
            for item, start_col in col_map[dep].items():

                if item == "Staff":
                    hc = frappe.db.count("Employee", {
                        "department": dep,
                        "employee_category": "Staff",
                        "unit": unit,
                        "status": "Active"
                    })
                    la = sum(1 for d in data if d["attendance_date"] == date and d["department"] == dep and d["employee_category"] == "Staff" and d["status"] in ["Absent", "On Leave"])
                    p = sum(1 for d in data if d["attendance_date"] == date and d["department"] == dep and d["employee_category"] == "Staff" and d["status"] == "Present")

                    ws.cell(row=row, column=start_col).value = hc
                    ws.cell(row=row, column=start_col + 1).value = la
                    ws.cell(row=row, column=start_col + 2).value = p
                    for i in range(3):
                        ws.cell(row=row, column=start_col + i).fill = staff_fill

                else:
                    comp = [d for d in data if d["attendance_date"] == date and d["department"] == dep and d["designation"] == item and d["employee_category"] not in ["", "Contractor","Staff"]]
                    cont = [d for d in data if d["attendance_date"] == date and d["department"] == dep and d["designation"] == item and d["employee_category"] == "Contractor"]

                    ws.cell(row=row, column=start_col).value = frappe.db.count("Employee", {
                        "designation": item,
                        "department": dep,
                        "employee_category": ["not in", ["", "Contractor"]],
                        "unit": unit,
                        "status": "Active"
                    })
                    ws.cell(row=row, column=start_col + 1).value = len([i for i in comp if i["status"] in ["Absent", "On Leave"]])
                    ws.cell(row=row, column=start_col + 2).value = len([i for i in comp if i["status"] == "Present"])
                    for i in range(3):
                        ws.cell(row=row, column=start_col + i).fill = company_fill

                    ws.cell(row=row, column=start_col + 3).value = frappe.db.count("Employee", {
                        "designation": item,
                        "employee_category":"Contractor",
                        "unit": unit,
                        "status": "Active"
                    })
                    ws.cell(row=row, column=start_col + 4).value = len([i for i in cont if i["status"] in ["Absent", "On Leave"]])
                    ws.cell(row=row, column=start_col + 5).value = len([i for i in cont if i["status"] == "Present"])
                    for i in range(3):
                        ws.cell(row=row, column=start_col + 3 + i).fill = contractor_fill
        
        staff = [d for d in data if d["attendance_date"] == date and d["employee_category"] == "Staff"]
        # company = [d for d in data if d["attendance_date"] == date and d["employee_category"] not in ["", "Contractor"]]
        
        company = [d for d in data if d.get("attendance_date") == date and d["employee_category"] in ["Default Category", "Worker","Test"]]
        contract = [d for d in data if d["attendance_date"] == date and d["employee_category"] == "Contractor"]

        totals = [
            (  
                frappe.db.count("Employee", {"employee_category": "Staff", "unit": unit, "status": "Active"}),
                len([d for d in staff if d["status"] in ["Absent", "On Leave"]]),
                len([d for d in staff if d["status"] == "Present"])
            ),
            (  
                frappe.db.count("Employee", {"employee_category": ["not in", ["", "Contractor","Staff"]], "unit": unit, "status": "Active"}),
                len([d for d in company if d["status"] in ["Absent", "On Leave"]]),
                len([d for d in company if d["status"] == "Present"])
            ),
            (  
                frappe.db.count("Employee", {"employee_category": "Contractor", "unit": unit, "status": "Active"}),
                len([d for d in contract if d["status"] in ["Absent", "On Leave"]]),
                len([d for d in contract if d["status"] == "Present"])
            )
        ]

        staff_hc = totals[0][0]
        staff_la = totals[0][1]
        staff_p  = totals[0][2]

        company_hc = totals[1][0]
        company_la = totals[1][1]
        company_p  = totals[1][2]

        contract_hc = totals[2][0]
        contract_la = totals[2][1]
        contract_p  = totals[2][2]

        grand_hc = staff_hc + company_hc + contract_hc
        grand_la = staff_la + company_la + contract_la
        grand_p  = staff_p  + company_p  + contract_p

        ws.cell(row=row, column=total_col_start).value = grand_hc
        ws.cell(row=row, column=total_col_start + 1).value = grand_la
        ws.cell(row=row, column=total_col_start + 2).value = grand_p

        c = overall_start
        for group in totals:
            for v in group:
                ws.cell(row=row, column=c).value = v
                c += 1

        staff_filter = {"employee_category": "Staff"}

        company_emp_filter = {
            "employee_category": ["not in", ["", "Contractor","Staff"]]
        }

        contractor_filter = {"employee_category": "Contractor"}

        # row = 5
        start_col = total_col_start + 3
        
        total_hc_all = 0
        total_add_all = 0
        total_del_all = 0
        total_tot_all = 0

        hc, addi, dele, tot = get_employee_counts(from_date, to_date, staff_filter,unit)
        ws.cell(row=row, column=start_col).value = hc
        ws.cell(row=row, column=start_col + 1).value = addi
        ws.cell(row=row, column=start_col + 2).value = dele
        ws.cell(row=row, column=start_col + 3).value = tot
        total_hc_all += hc
        total_add_all += addi
        total_del_all += dele
        total_tot_all += tot


        col_off = 4
        hc, addi, dele, tot = get_employee_counts(from_date, to_date, company_emp_filter,unit)
        ws.cell(row=row, column=start_col + col_off).value = hc
        ws.cell(row=row, column=start_col + col_off + 1).value = addi
        ws.cell(row=row, column=start_col + col_off + 2).value = dele
        ws.cell(row=row, column=start_col + col_off + 3).value = tot

        total_hc_all += hc
        total_add_all += addi
        total_del_all += dele
        total_tot_all += tot


        col_off = 8
        hc, addi, dele, tot = get_employee_counts(from_date, to_date, contractor_filter,unit)
        ws.cell(row=row, column=start_col + col_off).value = hc
        ws.cell(row=row, column=start_col + col_off + 1).value = addi
        ws.cell(row=row, column=start_col + col_off + 2).value = dele
        ws.cell(row=row, column=start_col + col_off + 3).value = tot

        total_hc_all += hc
        total_add_all += addi
        total_del_all += dele
        total_tot_all += tot

        current_col = start_col + 12  

        for cname in contractor_names:
            specific_filter = {
                "employee_contractor_name": cname
            }

            hc, addi, dele, tot = get_employee_counts(from_date, to_date, specific_filter, unit)

            ws.cell(row=row, column=current_col).value = hc
            ws.cell(row=row, column=current_col + 1).value = addi
            ws.cell(row=row, column=current_col + 2).value = dele
            ws.cell(row=row, column=current_col + 3).value = tot

            current_col += 4     


        total_hc_col = start_col + 12 + (len(contractor_names) * 4)

        ws.cell(row=row, column=total_hc_col).value = total_hc_all
        ws.cell(row=row, column=total_hc_col + 1).value = total_add_all
        ws.cell(row=row, column=total_hc_col + 2).value = total_del_all
        ws.cell(row=row, column=total_hc_col + 3).value = total_tot_all

        for c in range(total_col_start, total_col_start + 3):
            ws.cell(row=row, column=c).alignment = Alignment(horizontal="center", vertical="center")
        
        row += 1
        s_no += 1

 
    max_row, max_col = ws.max_row, ws.max_column
    for r in range(1, max_row + 1):
        for c in range(1, max_col + 1):
            ws.cell(row=r, column=c).border = border

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    frappe.local.response.filename = "Daily_Strength_Report.xlsx"
    frappe.local.response.filecontent = output.read()
    frappe.local.response.type = "download"



def get_employee_counts(from_date, to_date, category_filter, unit=None):

    hc_filters = {
        "status": "Active",
        "date_of_joining": ["<", from_date],
        **category_filter
    }
    if unit:
        hc_filters["unit"] = unit

    hc = frappe.db.count("Employee", filters=hc_filters)

    add_filters = {
        "status": "Active",
        "date_of_joining": ["between", [from_date, to_date]],
        **category_filter
    }
    if unit:
        add_filters["unit"] = unit

    addition = frappe.db.count("Employee", filters=add_filters)

    del_filters = {
        "relieving_date": ["between", [from_date, to_date]],
        **category_filter
    }
    if unit:
        del_filters["unit"] = unit

    deletion = frappe.db.count("Employee", filters=del_filters)
    total = hc + addition - deletion

    return hc, addition, deletion, total
