frappe.ui.form.on('Manpower Request', {
    setup(frm){
        if (frm.doc.workflow_state && frm.doc.workflow_state != "Draft") {
            Object.keys(frm.fields_dict).forEach(fieldname => {
                frm.set_df_property(fieldname, "read_only", 1);
                frm.set_df_property('prepared_by',"read_only",1)
            });
            frm.disable_save(); 
        }
        if (frm.doc.workflow_state =='Draft'){
            const is_owner = frm.doc.owner === frappe.session.user;
            frm.fields.forEach(function(field) {
                if (field.df && field.df.fieldname) {
                    frm.set_df_property(field.df.fieldname, 'read_only', !is_owner);
                }
            });
        }
        var user =frappe.session.user
        if (frm.is_new()){
            
            frappe.call({
                method: "gplast.gplast.doctype.manpower_request.manpower_request.get_employee",
                args:{
                    user:user,
                },
                callback(r) {
                    if (r.message){
                        frm.set_value('prepared_by',r.message)
                    }
                }
            });
        }    
        frappe.call({
            method: "gplast.gplast.doctype.manpower_request.manpower_request.get_department",
            args: {
                user: user
            },
            callback(r) {
                if (r.message) {
                    let allowed_deps = r.message;   
                    frm.set_query("employee_id", function() {
                        return {
                            filters: {
                                status:"Active",
                                department: ["in", allowed_deps]
                            }
                        };
                    });
                }
            }
        });
        frappe.call({
            method: "gplast.gplast.doctype.manpower_request.manpower_request.get_department",
            args:{
                user:user,
            },
            callback(r) {
                if (frappe.session.user === "Administrator") {
                    frm.set_query('job_requisition_id', () => {
                        return {
                            filters: {
                                workflow_state: 'Approved'
                            }
                        }
                    });
                    frm.set_query("employee_id", function () {
                        return {
                            filters: {}
                        };
                    });
                    return; 
                }
                if (r.message){
                    console.log(r.message)
                    var department=r.message
                    frm.set_query('job_requisition_id', () => {
                        return {
                            filters: {
                                department: ["in", r.message],
                                workflow_state:'Approved'
                            }
                        }
                    });
                    // frappe.call({
                    //     method: "gplast.gplast.doctype.manpower_request.manpower_request.get_left_employees",
                    //     args: {
                    //         department: department
                    //     },
                    //     callback(res) {
                    //         console.log(res.message)
                    //         if (res.message && res.message > 0) {
                    //             frm.set_df_property('apply_for_left_employee', 'hidden', 0)
                    //         }
                    //         else{
                    //             frm.set_df_property('apply_for_left_employee', 'hidden', 1)
                    //         }
                    //     }
                    // });
                    if (frm.doc.apply_for_left_employee == 0) {
                        // if (frm.doc.job_requisition_id){
                        //     frappe.call({
                        //         method:"gplast.gplast.doctype.manpower_request.manpower_request.get_designation_code",
                        //         args:{
                        //             job_id:frm.doc.job_requisition_id,
                        //         },
                        //         callback(res) {
                        //             console.log(res.message)
                        //             frm.set_value("new_designation_code" , res.message)
                        //         }
                        //     });
                        // }
                        
                        frm.set_df_property('cost_center', 'reqd', 1);
                        frm.set_df_property('location', 'reqd', 0);
                        frm.set_df_property('vacancy_count', 'reqd', 1);
                    }
                    if (frm.doc.apply_for_left_employee == 1){
                        frm.set_value("vacancy_due_to", "Resignation");
                        frm.set_df_property('vacancy_due_to', 'read_only', 1);
                        frm.set_value("no_of_vacancy", "1");
                        frm.set_df_property('no_of_vacancy', 'read_only', 1);
                        frm.set_df_property('vacancy_count', 'hidden', 1);
                        if (frm.doc.employee_id_due){
                            frappe.call({
                                method:"gplast.gplast.doctype.manpower_request.manpower_request.get_designation_code_from_left",
                                args:{
                                    employee_id_due:frm.doc.employee_id_due,
                                },
                                callback(res) {
                                   if (res.message) {
                                        frm.set_value("new_designation_code", res.message.designation_code);
                                        frm.set_value("new_department", res.message.department);
                                        frm.set_value("new_designation", res.message.designation);
                                        frm.set_df_property('no_of_vacancy', 'read_only', 0);
                                    }
                                }
                            });
                        }
                    }

                }
                else{
                    frm.set_query('job_requisition_id', () => {
                        return {
                            filters: {
                                workflow_state:'Approved'
                            }
                        }
                    });
                    frm.set_df_property('cost_center', 'reqd', 0);
                    frm.set_df_property('location', 'reqd', 0);
                }
            }
        });
        if (frm.doc.apply_for_left_employee == 0) {
            if (frm.doc.job_requisition_id){
                frappe.call({
                    method:"gplast.gplast.doctype.manpower_request.manpower_request.get_designation_code",
                    args:{
                        job_id:frm.doc.job_requisition_id,
                    },
                    callback(res) {
                        console.log(res.message)
                        if (res.message) {
                            frm.set_value("new_designation_code", res.message.designation_code);
                            frm.set_value("new_department", res.message.department);
                            frm.set_value("new_designation", res.message.designation);
                            frm.set_value("no_of_vacancy", res.message.no_of_positions);
                            frm.set_value("vacancy_due_to",res.message.reason);
                            frm.set_df_property('vacancy_due_to', 'read_only', 1);
                            frm.set_df_property('vacancy_count', 'reqd', 1);
                            
                        }
                    }
                });
            }
        }
        if (frm.doc.apply_for_left_employee == 1){
            frm.set_value("vacancy_due_to", "Resignation");
            frm.set_df_property('vacancy_due_to', 'read_only', 1);
            frm.set_value("no_of_vacancy", "1");
            frm.set_df_property('no_of_vacancy', 'read_only', 1);
            frm.set_df_property('vacancy_count', 'hidden', 1);
            if (frm.doc.employee_id_due){
                frappe.call({
                    method:"gplast.gplast.doctype.manpower_request.manpower_request.get_designation_code_from_left",
                    args:{
                        employee_id_due:frm.doc.employee_id_due,
                    },
                    callback(res) {
                        if (res.message) {
                            frm.set_value("new_designation_code", res.message.designation_code);
                            frm.set_value("new_department", res.message.department);
                            frm.set_value("new_designation", res.message.designation);
                            frm.set_df_property('no_of_vacancy', 'read_only', 0);
                        }
                    }
                });
            }
        }
        
    },
    employee_id: function(frm) {
        var user = frappe.session.user;
        if (frm.doc.filled_by == "Internal Transfer" || frm.doc.filled_by == "Promotion") {
            if (frm.doc.employee_id) {
                frappe.db.get_value("Employee", frm.doc.employee_id, "gender")
                    .then(r => {
                        if (r && r.message) {
                            frm.set_value("sex", r.message.gender);
                        }
                    });
                frappe.db.get_value("Employee", frm.doc.employee_id, "unit")
                    .then(r => {
                        if (r && r.message) {
                            frm.set_value("unit", r.message.unit);
                        }
                    });
                frappe.db.get_value("Employee", frm.doc.employee_id, "payroll_cost_center")
                    .then(r => {
                        if (r && r.message) {
                            frm.set_value("_cost_center", r.message.payroll_cost_center);
                        }
                    });
            }
            if (! frm.doc.employee_id) {
                frm.set_value("sex", " ");
                frm.set_value("_cost_center", " ");
                frm.set_value("unit", " ");
            }
        }
        frappe.call({
            method: "gplast.gplast.doctype.manpower_request.manpower_request.get_department",
            args: {
                user: user
            },
            callback(r) {
                if (frappe.session.user !== "Administrator") {
                    if (r.message) {
                        let allowed_deps = r.message;   
                        frm.set_query("employee_id", function() {
                            return {
                                filters: {
                                    status: "Active",
                                    department: ["in", allowed_deps],
                                }
                            };
                        });
                    }
                }
                else {
                    frm.set_query("employee_id", function () {
                        return {
                            filters: {}
                        };
                    });
                }
            }
        });
        
        if (frm.doc.filled_by != "New Candidate" && frm.doc.reporting_to) {
            frappe.db.get_value("Employee",{"name" :frm.doc.reporting_to},"employee_name",(r) => {
                    if (r && r.employee_name) {
                        frm.set_value("hod", r.employee_name);
                    }
                }
            );
        }
        
        if(!frm.doc.employee_id){
            frm.set_value("hod","")
        }
    },
    job_requisition_id(frm){
        let user_email = frappe.session.user;
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Employee",
                    filters: { user_id: user_email },
                    fields: ["name", "employee_name","unit","payroll_cost_center","department"],
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {

                        let emp = r.message[0];

                        frm.set_value("prepared_by", emp.name);
                        frm.set_value("prepared_by_employee_name", emp.employee_name);
                        frm.set_value("cost_center", emp.payroll_cost_center);
                        frm.set_value("unit_for_employee", emp.unit);
                        frm.set_value("prepared_by_employee_department", emp.department);
                    }
                }
            });
            if (frm.doc.apply_for_left_employee == 0) {
            if (frm.doc.job_requisition_id){
                frappe.call({
                    method:"gplast.gplast.doctype.manpower_request.manpower_request.get_designation_code",
                    args:{
                        job_id:frm.doc.job_requisition_id,
                    },
                    callback(res) {
                        console.log(res.message)
                        if (res.message) {
                            frm.set_value("new_designation_code", res.message.designation_code);
                            frm.set_value("new_department", res.message.department);
                            frm.set_value("new_designation", res.message.designation);
                            frm.set_value("no_of_vacancy", res.message.no_of_positions);
                            frm.set_value("vacancy_due_to",res.message.reason);
                            frm.set_df_property('vacancy_due_to', 'read_only', 1);
                        }

                    }
                });
            }
        }
    },
    apply_for_left_employee(frm){
        if (frm.doc.apply_for_left_employee){
            const options = ['Resignation'];
            frm.set_df_property('vacancy_due_to', 'options', options);
            frm.set_df_property('job_requisition_id', 'reqd', 0);
            frm.set_df_property('job_requisition_id', 'hidden', 1);
            frm.set_value('job_requisition_id','')
            if (frm.doc.apply_for_left_employee == 1){
                frm.set_value("vacancy_due_to", "Resignation");
                frm.set_df_property('vacancy_due_to', 'read_only', 1);
                frm.set_value("no_of_vacancy", "1");
                frm.set_df_property('no_of_vacancy', 'read_only', 1);
                frm.set_df_property('vacancy_count', 'hidden', 1);
                if (frm.doc.employee_id_due){
                    frappe.call({
                        method:"gplast.gplast.doctype.manpower_request.manpower_request.get_designation_code_from_left",
                        args:{
                            employee_id_due:frm.doc.employee_id_due,
                        },
                        callback(res) {
                            if (res.message) {
                                frm.set_value("new_designation_code", res.message.designation_code);
                                frm.set_value("new_department", res.message.department);
                                frm.set_value("new_designation", res.message.designation);
                                frm.set_df_property('no_of_vacancy', 'read_only', 0);
                            }
                        }
                    });
                }     
            }
        }
        else{
            const options = ['Resignation','Expansion','Workload','Quantity Policy','Termination', 'Left'];
            frm.set_df_property('vacancy_due_to', 'options', options);
            frm.set_df_property('job_requisition_id', 'reqd', 1);
            frm.set_df_property('job_requisition_id', 'hidden', 0)
            frm.set_df_property('vacancy_count', 'reqd', 1);
        }
        if (frm.doc.apply_for_left_employee == 1 ||frm.doc.apply_for_left_employee == 0 ) {

            let user_email = frappe.session.user;
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Employee",
                    filters: { user_id: user_email },
                    fields: ["name", "employee_name","unit","payroll_cost_center","department"],
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {

                        let emp = r.message[0];

                        frm.set_value("prepared_by", emp.name);
                        frm.set_value("prepared_by_employee_name", emp.employee_name);
                        frm.set_value("cost_center", emp.payroll_cost_center);
                        frm.set_value("unit_for_employee", emp.unit);
                        frm.set_value("prepared_by_employee_department", emp.department);
                    }
                }
            });
            

            frappe.call({
                method: "gplast.gplast.doctype.manpower_request.manpower_request.get_sub_designation_codes",
                callback: function(r) {
                    frm.set_query("new_designation_code", function() {
                        return {
                            filters: [
                                ["Sub Designation", "designation_code", "in", r.message]
                            ]
                        };
                    });
                }
            });
        

        }
    },
    onload(frm){
        if (frm.is_new()) {
            if(!frm.doc.prepared_by){
                frm.trigger("get_department");
                let user_email = frappe.session.user;
                frappe.call({
                    method: "frappe.client.get_list",
                    args: {
                        doctype: "Employee",
                        filters: { user_id: user_email , status:"Active",},
                        fields: ["name", "employee_name","unit","payroll_cost_center","department"],
                        limit_page_length: 1
                    },
                    callback: function(r) {
                        if (r.message && r.message.length > 0) {

                            let emp = r.message[0];

                            frm.set_value("prepared_by", emp.name);
                            frm.set_value("prepared_by_employee_name", emp.employee_name);
                            frm.set_value("cost_center", emp.payroll_cost_center);
                            frm.set_value("unit_for_employee", emp.unit);
                            frm.set_value("prepared_by_employee_department", emp.department);
                        }
                    }
                });
            }
            
        }
        
            
        
        
    },

    vacancy_due_to(frm){
        var user = frappe.session.user;
        if (frappe.session.user !== "Administrator") {
            if(frm.doc.vacancy_due_to == 'Resignation'){
                frappe.call({
                    method: "gplast.gplast.doctype.manpower_request.manpower_request.get_left_employees_list",
                    args:{
                        department:frm.doc.prepared_by_employee_department,
                        user:user
                    },
                    callback(r){
                        if(r.message){
                            console.log(r.message)
                            frm.set_query('employee_id_due', ()=> {
                                return{
                                    filters: {
                                        name : ["in",r.message]
                                    }
                                }
                            })
                        }
                    }



                })

            }
        }

    },
    get_department(frm){
        var user =frappe.session.user
        frappe.call({
            method: "gplast.gplast.doctype.manpower_request.manpower_request.get_department",
            args:{
                user:user,
            },
            callback(r) {
                if (r.message){
                    frm.set_value('department',r.message)
                }
            }
        });
    },
    employee_id_due(frm){
       if (frm.doc.apply_for_left_employee == 1){
            frm.set_value("vacancy_due_to", "Resignation");
            frm.set_df_property('vacancy_due_to', 'read_only', 1);
            frm.set_value("no_of_vacancy", "1");
            frm.set_df_property('no_of_vacancy', 'read_only', 1);
            frm.set_df_property('vacancy_count', 'hidden', 1);
            if (frm.doc.employee_id_due){
                frappe.call({
                    method:"gplast.gplast.doctype.manpower_request.manpower_request.get_designation_code_from_left",
                    args:{
                        employee_id_due:frm.doc.employee_id_due,
                    },
                    callback(res) {
                        if (res.message) {
                            frm.set_value("new_designation_code", res.message.designation_code);
                            frm.set_value("new_department", res.message.department);
                            frm.set_value("new_designation", res.message.designation);
                            frm.set_df_property('no_of_vacancy', 'read_only', 0);
                        }
                    }
                });
                if(frm.doc.filled_by == "New Candidate"){
                    frappe.db.get_value("Employee", frm.doc.employee_id_due, "gender")
                        .then(r => {
                            if (r && r.message) {
                                frm.set_value("sex", r.message.gender);
                            }
                        });
                    frappe.db.get_value("Employee", frm.doc.employee_id_due, "unit")
                        .then(r => {
                            if (r && r.message) {
                                frm.set_value("unit", r.message.unit);
                            }
                        });
                    frappe.db.get_value("Employee", frm.doc.employee_id_due, "payroll_cost_center")
                        .then(r => {
                            if (r && r.message) {
                                frm.set_value("_cost_center", r.message.payroll_cost_center);
                            }
                        });
                }
                 
            }  
            else {
                frm.set_value("sex", " ");
                frm.set_value("_cost_center", " ");
                frm.set_value("unit", " ");
            }
            
        } 
    }
});
