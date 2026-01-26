// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Permission', {
	permission_hour(frm){
        frm.trigger('get_from_time_and_to_time');
    },
    session(frm){
        frm.trigger('get_from_time_and_to_time');
    },
    shift(frm){
        frm.trigger('get_from_time_and_to_time');
    },
    get_from_time_and_to_time:function(frm){
        if (frm.doc.session && frm.doc.permission_hour && frm.doc.shift && frm.doc.permission_date){
			// console.log("message")
            frappe.call({
                "method": "gplast.gplast.doctype.attendance_permission.attendance_permission.get_from_time_and_to_time",
                "args": {
                    "shift":frm.doc.shift,
                    "session":frm.doc.session,
                    "permission_hour":frm.doc.permission_hour,
					"permission_date":frm.doc.permission_date
                },	
                callback(r){
					// console.log(r.message)
                    $.each(r.message,function(i,v){
                        if (frm.doc.permission_hour != ''){
                            frm.set_value('from_time',v.permission_from_time)
                            frm.set_value('to_time',v.permission_to_time)
                        }
                        else{
                            frm.set_value('from_time','00:00:00')
                            frm.set_value('to_time','00:00:00')
                        }
                    })
                }
            })
        }
		else{
			frm.set_value('from_time','00:00:00')
			frm.set_value('to_time','00:00:00')
		}
    },
	permission_date(frm){
		frm.call('sat_res').then(j=>{
			// if (j.message) {
			// 	frm.fields_dict.perm.$wrapper.empty().append(j.message)
			// }
		})	
	},
	total_time(frm){
		frm.call('hour_res').then(j=>{
			
		})	
	},

	refresh: function(frm) {
		  if (!frm.doc.__islocal) {
            if (frm.doc.workflow_state === "Preview" && !["Administrator", frm.doc.owner].includes(frappe.session.user)) {
                $.each(frm.fields_dict, function(fieldname, field) {
                    frm.set_df_property(fieldname, "read_only", 1);
                });
                frm.refresh_fields();   
            }
        }
	},
    // before_save(frm){
    //     if(frm.doc.employee){
    //         approver = frappe.db.get_value("Approvers",{'employee':frm.doc.employee},'total_number_of_approvers')
    //         frm.set_value("total_leave_approvers",approver)

    //     }
    // }
						
});
