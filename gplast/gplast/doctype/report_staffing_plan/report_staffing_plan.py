import frappe
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime,datetime,get_first_day,get_last_day,today,add_to_date)

from frappe.model.document import Document

class ReportStaffingPlan(Document):
    pass

@frappe.whitelist(allow_guest=True)
def report_staffing_plan(cost__center, department):
    year1 = getdate().year
        
    date_1 = getdate()
    year2 = add_to_date(date_1, days=365).year
        
    year =f"""{year1}-{year2}"""
  

 
    s_date=  frappe.db.get_value("Fiscal Year",{"name":year},"year_start_date")
    s_date_obj=getdate(s_date)
    start_date=s_date_obj.strftime('%d-%m-%Y')
        
        
    e_date=  frappe.db.get_value("Fiscal Year",{"name":year},"year_end_date")
    e_date_obj=getdate(e_date)
    end_date=e_date_obj.strftime('%d-%m-%Y')
        
  
        
        
    conditions = [["docstatus", "!=", 2], ["workflow_state", "=", "Approved"],["posting_date","between",[start_date,end_date]]]

    if cost__center:
        conditions.append(["cost__center", "=", cost__center])
    if department:
        conditions.append(["department", "=", department])

    job_request_data = frappe.db.get_all(
        "Job Requisition",
        filters=conditions,
        fields=["cost__center", "designation_code", "designation", "department", "no_of_positions"]
    )

    designation_summary = {}

    for job in job_request_data:
        cc = job["cost__center"]
        code = job["designation_code"]

        if cc not in designation_summary:
            designation_summary[cc] = {}

        if code not in designation_summary[cc]:
            designation_summary[cc][code] = {
                "designation": job["designation"],
                "department": job["department"],
                "cost__center": job["cost__center"],
                "total_positions": 0
            }

        designation_summary[cc][code]["total_positions"] += job["no_of_positions"]

    data = """
        <div style="overflow-x: auto; color: black;">
            <table border="1" style="border-collapse:collapse; width:100%;">
                <thead>
                    <tr style="background-color:orange; font-size:17px; text-align:center; color:black;">
                        <th colspan="3" rowspan="2" style="padding:10px;">Cost Center</th>
                        <th colspan="21" style="padding:10px;">STAFFING PLAN REPORT</th>
                    </tr>
                    <tr style="background-color:orange; font-size:15px; text-align:center; color:black;">
                        <th colspan="3" style="padding:10px;">Department</th>
                        <th colspan="3" style="padding:10px;">Designation</th>
                        <th colspan="2" style="padding:10px;">Available</th>
                        <th colspan="2" style="padding:10px;">Job Request</th>
                        <th colspan="2" style="padding:10px;">Staffing Plan</th>
                        <th colspan="2" style="padding:10px;">ManPower Request</th>
                        <th colspan="2" style="padding:10px;">Vacant</th>
                        <th colspan="2" style="padding:10px;">Recruited</th>
                        <th colspan="2" style="padding:10px;">Recommended Designation</th>
                        <th colspan="2" style="padding:10px;">Reason for Designation Change</th>
                    </tr>
                </thead>
                <tbody>
    """

    for cc, designations in designation_summary.items():
        for code, details in designations.items():
            if cc:
                employee_count = frappe.db.count("Employee", {
                    "designation_code": code,
                    "department": details["department"],
                    "status": "Active"
                })

                total_vacancy_count = 0
                recruited_count = 0
                previous_recruited_count = 0
                total_recruited_count = 0
                approve_date = None

                
                manpower_requests = frappe.db.get_all(
                    "Manpower Request",
                    filters={"new_designation_code": code, "workflow_state": "Approved","approve_date":["between",[start_date,end_date]]},
                    fields=["vacancy_count", "approve_date"],
                    order_by="approve_date desc"
                )
                if manpower_requests:
                    latest_request = manpower_requests[0]
                    approve_date = latest_request.get("approve_date")
                    recruitments = frappe.db.get_all(
                        "Employee",
                        filters={
                            "designation_code": code,
                            "creation": [">=", approve_date],
                            "status": "Active"
                        },
                        order_by="creation desc"
                    )

                    if recruitments:
                        
                        recruited_count = len(recruitments[:1])  
                        previous_recruited_count = len(recruitments[1:2]) 
                        total_recruited_count = len(recruitments)
                        total_recruited_count = total_recruited_count + recruited_count
                        
                        frappe.errprint(total_recruited_count)
                    
                    for req in manpower_requests:
                        total_vacancy_count += req.get("vacancy_count", 0)
                        frappe.errprint("HI")
                        frappe.errprint(total_vacancy_count)
                        
                
                available = employee_count - recruited_count
                job_request = details["total_positions"] - previous_recruited_count
                staffing_plan = available + job_request
                manpower_request = total_vacancy_count - total_recruited_count
                vacant = total_vacancy_count - total_recruited_count

                data += f"""
                    <tr style="background-color:yellow; font-size:13px; font-weight:400; text-align:center;">
                        <td colspan="3" style="padding:10px;">{cc}</td>
                        <td colspan="3" style="padding:10px;">{details['department']}</td>
                        <td colspan="3" style="padding:10px;">{details['designation']}</td>
                        <td colspan="2" style="padding:10px;">{available  if available>=0 else 0}</td>
                        <td colspan="2" style="padding:10px;">{job_request if job_request>=0 else 0}</td>
                        <td colspan="2" style="padding:10px;">{staffing_plan if staffing_plan>=0 else 0}</td>
                        <td colspan="2" style="padding:10px;">{manpower_request if manpower_request>=0 else 0}</td>
                        <td colspan="2" style="padding:10px;">{vacant if vacant>=0 else 0}</td>
                        
                    """
                feedback_filters = {
                    'docstatus': ['!=', 2],
                    'recommended': 'Yes',
                    'recommended_designation': ['!=', 'None']
                }

                if frappe.db.exists('Interview Feedback', feedback_filters):
                    interview_doc = frappe.db.get_value('Interview', {'designation':details['designation'],'docstatus':1}, 'name')
                    if interview_doc:
                        recommended_designation =frappe.db.get_value('Interview Feedback',{'interview':interview_doc,'docstatus':1}, 'recommended_designation')
                        reason_for_designation_change =frappe.db.get_value('Interview Feedback',{'interview':interview_doc,'docstatus':1}, 'reason_for_designation_change')
                        if recommended_designation:
                            # count = frappe.db.count('Employee', {'designation': recommended_designation})
                            count = frappe.db.count('Employee',{'designation': recommended_designation,'creation': (">=", approve_date)})
                            if count and details['designation'] != recommended_designation:
                                
                                recruited_count +=count
                                data += f"""
                                            <td colspan="2" style="padding:10px;">{recruited_count if recruited_count>=0 else 0}</td>
                                            <td colspan="2" style="padding:10px;">{recommended_designation or ''}</td>
                                            <td colspan="2" style="padding:10px;">{reason_for_designation_change or ''}</td>
                                            """
                            
                            else:
                                data += f"""<td colspan="2" style="padding:10px;">{recruited_count if recruited_count>=0 else 0}</td>
                                <td colspan="2" style="padding:10px;"></td>
                                <td colspan="2" style="padding:10px;"></td>"""
                        else:
                            data += f"""<td colspan="2" style="padding:10px;">{recruited_count if recruited_count>=0 else 0}</td>
                            <td colspan="2" style="padding:10px;"></td>
                                        <td colspan="2" style="padding:10px;"></td>"""
                    else:
                        data += f"""<td colspan="2" style="padding:10px;">{recruited_count if recruited_count>=0 else 0}</td>
                        <td colspan="2" style="padding:10px;"></td>
                                        <td colspan="2" style="padding:10px;"></td>"""
                else:
                    data += f"""<td colspan="2" style="padding:10px;">{recruited_count if recruited_count>=0 else 0}</td>
                    <td colspan="2" style="padding:10px;"></td>
                                        <td colspan="2" style="padding:10px;"></td>"""
                data +="""</tr>"""
    data += """
                </tbody>
            </table>
        </div>
    """

    return data

    #             data += f"""
    #                 <tr style="background-color:yellow; font-size:13px; font-weight:400; text-align:center;">
    #                     <td colspan="3" style="padding:10px;">{cc}</td>
    #                     <td colspan="3" style="padding:10px;">{details['department']}</td>
    #                     <td colspan="3" style="padding:10px;">{details['designation']}</td>
    #                     <td colspan="2" style="padding:10px;">{available  if available>=0 else 0}</td>
    #                     <td colspan="2" style="padding:10px;">{job_request if job_request>=0 else 0}</td>
    #                     <td colspan="2" style="padding:10px;">{staffing_plan if staffing_plan>=0 else 0}</td>
    #                     <td colspan="2" style="padding:10px;">{manpower_request if manpower_request>=0 else 0}</td>
    #                     <td colspan="2" style="padding:10px;">{vacant if vacant>=0 else 0}</td>
    #                     <td colspan="2" style="padding:10px;">{recruited_count if recruited_count>=0 else 0}</td>
    #                 """
                    
    #             if frappe.db.exists('Interview Feedback',{'recommended':'Yes','recommended_designation':['!=','None']}):
    #                 owner = frappe.db.get_value('Interview Feedback',{'recommended':'Yes','recommended_designation':['!=','None']},['owner'])
                    
    #                 if owner:
    #                     dept = frappe.db.get_value('Employee',{'user_id':owner},['department'])
    #                     if dept:
    #                         if frappe.db.exists(
    #                             "Job Requisition",
    #                             filters={"docstatus":["!=", 2],"workflow_state": "Approved","posting_date":["between",[start_date,end_date]],'department':dept}):
    #                             designation1 = frappe.db.get_value("Job Requisition",{"docstatus":["!=", 2],"workflow_state": "Approved","posting_date":["between",[start_date,end_date]],'department':dept},['designation'])    
    #                             designation2 = frappe.db.get_value('Interview Feedback',{'recommended':'Yes','recommended_designation':['!=','None']},['recommended_designation'])
    #                             reason_for_designation_change = frappe.db.get_value('Interview Feedback',{'recommended':'Yes','recommended_designation':['!=','None']},['reason_for_designation_change'])
    #                             if designation1 == designation2:    
    #                                 data +=f""" <td colspan="2" style="padding:10px;">{vacant if vacant>=0 else 0}</td>
    #                                     <td colspan="2" style="padding:10px;">{recruited_count if recruited_count>=0 else 0}</td>"""
    #             data +="""</tr>"""
            


    # data += """
    #             </tbody>
    #         </table>
    #     </div>
    # """

    # return data

@frappe.whitelist()
def get_department(user):
    cc = frappe.db.get_value('Employee',{'user_id':user},'payroll_cost_center')
    deps = frappe.db.get_all(
        "User Permission",
        filters={
            "user": user,
            "allow": "Department"
        },
        fields=["for_value"],
        pluck="for_value"     
    )
    return {"cost_center": cc, "departments": deps}