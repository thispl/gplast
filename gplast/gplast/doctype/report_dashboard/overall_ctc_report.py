import frappe
import math
from datetime import datetime
from collections import defaultdict
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill


@frappe.whitelist()
def download(from_date, to_date, contractor_name=None):

    from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")
    month_name = from_date_obj.strftime("%B").upper()
    year = from_date_obj.strftime("%Y")

    wb = Workbook()
    ws = wb.active
    ws.title = "Contractor Bill"

    header_font = Font(bold=True)
    title_font = Font(bold=True, size=12)
    center = Alignment(horizontal="center", vertical="center", wrap_text=True)

    fill = PatternFill("solid", fgColor="D9EAF7")
    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)


    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=20)
    ws.cell(
        row=1,
        column=1,
        value=f"Contractors Bill Details for the month of {month_name} {year}"
    ).font = title_font
    ws.cell(row=1, column=1).alignment = center


    headers = [
        "S.No", "Contractor Name", "No.of Persons", "Total Working Days",
        "OT Hours", "Gross Wages", "OT Wages", "Attendance Incentive",
        "Total Gross Amount", "PF 13.00%", "ESI 3.25%",
        "Service Charges 8.33% on Gross", "LWF", "Total CTC Amount",
        "CGST (9%)", "SGST (9%)", "Net Gross",
        "Late Deduction", "Canteen Deduction", "Net Payable"
    ]

    for col, h in enumerate(headers, start=1):
        c = ws.cell(row=3, column=col, value=h)
        c.font = header_font
        c.fill = fill
        c.alignment = center
        c.border = border
        ws.column_dimensions[c.column_letter].width = 18

    filters = {
        "docstatus": 0,
        "start_date": (">=", from_date),
        "end_date": ("<=", to_date),
        "employment_type": "Contract"
    }

    if contractor_name:
        filters["contractor_name"] = contractor_name

    slips = frappe.get_all(
        "Salary Slip",
        filters=filters,
        fields=[
            "name", "employee", "contractor_name",
            "payment_days",
            "gross_pay",
            "net_pay","total_present_days_of_employee", "total_present_days_in_a_month",
            "ot_", "lwf"
        ]
    )

    if not slips:
        frappe.throw("No Salary Slips found for given period")

    contractor_map = defaultdict(list)
    for s in slips:
        contractor_map[s.contractor_name].append(s)

    row = 4
    sno = 1

    # for contractor, records in contractor_map.items():

    #     persons = set()
    #     total_days = ot_hours= days_worked = 0
    #     gross = ot_wages = attn = 0
    #     pf = esi = lwf = basic= total_gross_1= 0
    #     late = canteen = net = 0

    #     for r in records:
    #         emp = frappe.get_doc("Employee", r.employee)
    #         wages = emp.salary_total or 0
            
    #         basic += emp.basic
    #         # frappe.log_error(str(basic), "basic")
    #         other_allow = emp.other_allowance or 0
    #         ot_days = ot_hours / 8
    #         days_worked += r.total_present_days_of_employee or 0
    #         # frappe.log_error(str(days_worked), "days_worked")
    #         persons.add(r.employee)
    #         total_days += r.total_present_days_in_a_month or 0
            
    #         ot_hours += r.ot_ or 0

    #         heat_al =  0
    #         basicslip = frappe.db.get_value( "Salary Detail", {'parent': r.name, "salary_component": "Basic"}, "amount" ) or 0
    #         otherall = frappe.db.get_value( "Salary Detail", {'parent': r.name, "salary_component": "Other Allowance"}, "amount") or 0
    #         gross += (basicslip + otherall +heat_al)

    #         overtime = frappe.db.get_value("Salary Detail",{'parent':r.name,"salary_component":"Overtime"},['amount']) or 0
    #         ot_wages +=  math.ceil(overtime)
    #         att_bonus = frappe.db.get_value("Salary Detail",{'parent':r.name,"salary_component":"Attendance Bonus"},['amount']) or 0
    #         attn +=  att_bonus or 0
    #         if (emp.basic or 0) > 0 or basicslip > 0:
    #             pf += (basic * (r.total_present_days_of_employee or 0)) * 0.13
    #         lwf += r.lwf_amount or 0
    #         late_ded = frappe.db.get_value("Salary Detail",{'parent':r.name,"salary_component":"Late Penalty"},['amount']) or 0
    #         late += late_ded or 0
    #         canteen_ded = frappe.db.get_value("Salary Detail",{'parent':r.name,"salary_component":"Canteen"},['amount']) or 0
    #         canteen +=  canteen_ded
    #         net += r.net_pay or 0

    #     total_gross = gross + ot_wages + attn
    #     esi += math.ceil(total_gross*0.0325) or 0
    #     service_charges = round(total_gross * 0.0833, 2)
    #     total_ctc = total_gross + pf + esi + service_charges + lwf
    #     cgst = round(total_ctc * 0.09, 2)
    #     sgst = round(total_ctc * 0.09, 2)
    #     net_gross = total_ctc + cgst + sgst

    #     values = [
    #         sno, contractor, len(persons), days_worked,
    #         ot_hours, gross, ot_wages, attn,
    #         total_gross, pf, esi, service_charges,
    #         lwf, total_ctc, cgst, sgst,
    #         net_gross, late, canteen, net
    #     ]

    #     for col, val in enumerate(values, start=1):
    #         c = ws.cell(row=row, column=col, value=round(val, 2) if isinstance(val, (int, float)) else val)
    #         c.alignment = center
    #         c.border = border

    #     sno += 1
    #     row += 1

    all_rows = []  

    for contractor, records in contractor_map.items():
        persons = set()
        total_days = ot_hours = days_worked = 0
        gross = ot_wages = attn = pf = esi = lwf = basic = total_gross_1 = 0
        late = canteen = net = 0

        for r in records:
            emp = frappe.get_doc("Employee", r.employee)
            basic += emp.basic
            other_allow = emp.other_allowance or 0
            ot_days = ot_hours / 8
            days_worked += r.total_present_days_of_employee or 0
            persons.add(r.employee)
            total_days += r.total_present_days_in_a_month or 0
            ot_hours += r.ot_ or 0

            heat_al = 0
            basicslip = frappe.db.get_value("Salary Detail", {'parent': r.name, "salary_component": "Basic"}, "amount") or 0
            otherall = frappe.db.get_value("Salary Detail", {'parent': r.name, "salary_component": "Other Allowance"}, "amount") or 0
            gross += (basicslip + otherall + heat_al)

            overtime = frappe.db.get_value("Salary Detail", {'parent': r.name, "salary_component": "Overtime"}, ['amount']) or 0
            ot_wages += math.ceil(overtime)
            att_bonus = frappe.db.get_value("Salary Detail", {'parent': r.name, "salary_component": "Attendance Bonus"}, ['amount']) or 0
            attn += att_bonus or 0

            if (emp.basic or 0) > 0 or basicslip > 0:
                pf += (basic * (r.total_present_days_of_employee or 0)) * 0.13

            lwf += r.lwf_amount or 0
            late_ded = frappe.db.get_value("Salary Detail", {'parent': r.name, "salary_component": "Late Penalty"}, ['amount']) or 0
            late += late_ded or 0
            canteen_ded = frappe.db.get_value("Salary Detail", {'parent': r.name, "salary_component": "Canteen"}, ['amount']) or 0
            canteen += canteen_ded or 0
            net += r.net_pay or 0

        total_gross = gross + ot_wages + attn
        esi += math.ceil(total_gross * 0.0325)
        service_charges = round(total_gross * 0.0833, 2)
        total_ctc = total_gross + pf + esi + service_charges + lwf
        cgst = round(total_ctc * 0.09, 2)
        sgst = round(total_ctc * 0.09, 2)
        net_gross = total_ctc + cgst + sgst

        row_values = [
            sno, contractor, len(persons), days_worked,
            ot_hours, gross, ot_wages, attn,
            total_gross, pf, esi, service_charges,
            lwf, total_ctc, cgst, sgst,
            net_gross, late, canteen, net
        ]

        for col, val in enumerate(row_values, start=1):
            c = ws.cell(row=row, column=col, value=round(val, 2) if isinstance(val, (int, float)) else val)
            c.alignment = center
            c.border = border

        all_rows.append(row_values)
        sno += 1
        row += 1

    total_row = ["", "TOTAL"]

    for col_index in range(2, 20): 
        total = sum(r[col_index] for r in all_rows if isinstance(r[col_index], (int, float)))
        total_row.append(total)

    for col, val in enumerate(total_row, start=1):
        c = ws.cell(row=row, column=col, value=round(val, 2) if isinstance(val, (int, float)) else val)
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor="D9EAF7")
        c.alignment = center
        c.border = border


    file_name = f"Contractor_Bill_{month_name}_{year}.xlsx"
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    frappe.response["filename"] = file_name
    frappe.response["filecontent"] = output.getvalue()
    frappe.response["type"] = "binary"
