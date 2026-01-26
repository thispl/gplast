// Copyright (c) 2024, TEAMPROO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Miss Punch Application", {

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
	
	before_save(frm){
		if(frm.doc.shift=="G" || frm.doc.shift =="1"){
			frappe.call({
				"method": 'gplast.gplast.doctype.on_duty_application.on_duty_application.get_time_diff',
				args: {
					"from_time": frm.doc.in_time,
					"to_time": frm.doc.out_time,
				},
				callback: function (r) {
					if (r.message<0) {
						
						frappe.msgprint("Kindly set the Proper Out Time")
						frappe.validated=false
					}
				}
			});
		}
		frappe.db.get_value('Approvers', { 'employee': frm.doc.employee }, 'total_number_of_approvers')
                .then(response => {
                    if (response.message) {
                        frm.set_value('total_leave_approvers', response.message.total_number_of_approvers);
                        frm.refresh_field('total_leave_approvers');
                    }
                });
		
	},
    attendance_date:function(frm) {
		if (frm.doc.__islocal){
			frappe.call({
				'method':'frappe.client.get_value',
				'args':{
					'doctype':'Attendance',
					'filters':{
						'employee':frm.doc.employee,
						'attendance_date':frm.doc.attendance_date,
						'docstatus':['!=', 2]
					},
					'fieldname':['name','in_time','out_time','shift']
				},
				callback(r){
					if(r.message){
						if(r.message.in_time && r.message.out_time){
						// 	// frappe.validated=false
                    	// 	// frappe.msgprint("Already Available checkins are against this date")
							if (!frappe.user.has_role("Miss Punch Role")) {
								frappe.validated = false;
								frappe.msgprint("Already Available checkins are against this date");
							}
							else
								frm.set_df_property('in_time', 'read_only', 0);
								frm.set_df_property('out_time', 'read_only', 0);
						}
						if(!r.message.in_time && !r.message.out_time){
							frappe.validated=false
                    		frappe.msgprint("There is no checkin or checkout present for this date")
						}
						if(r.message.in_time){
							frm.set_value('in_time',r.message.in_time)
							frm.set_value('in', 1)
							frm.set_df_property('in_time', 'read_only', 1);
						}
						if(r.message.out_time){
							frm.set_value('out_time',r.message.out_time)
							frm.set_value('out', 1)
							frm.set_df_property('out_time', 'read_only', 1);
						}
						if(r.message.shift){
							frm.set_value('shift',r.message.shift)
							frm.set_df_property('shift', 'read_only', 1);
						}
						if (!r.message.in_time ) {
							let attendance_date = frm.doc.attendance_date;
							let in_time = `${attendance_date} 00:00:00`;
							frm.set_value('in_time', in_time);
						}
						
						if (!r.message.out_time) {
							let attendance_date = frm.doc.attendance_date;
							let out_time = `${attendance_date} 00:00:00`;
							frm.set_value('out_time', out_time);
						}
						// console.log(r.message)
						
						// 	frm.set_value('in_time',r.message.in_time)
						// 	frm.set_value('out_time',r.message.out_time)
						// 	frm.set_value('shift',r.message.shift)
						
					}
                    if(!r.message.name){
                        frappe.msgprint("There is no attendance for this employee")
                    }
				}
			})
		}
    },
	validate(frm) {
		if (frm.doc.workflow_state != 'Rejected') {
			frappe.call({
				'method':'frappe.client.get_value',
				'args':{
					'doctype':'Attendance',
					'filters':{
						'employee':frm.doc.employee,
						'attendance_date':frm.doc.attendance_date,
						'docstatus':['!=', 2]
					},
					'fieldname':['name','in_time','out_time','shift']
				},
				callback(r){
					if(!r.message.name){
						frappe.validated=false
						frappe.msgprint("There is no attendance for this employee")
					}
					if(r.message.in_time && r.message.out_time){
						// frappe.validated=false
						// frappe.msgprint("Already Available checkins are against this date")
						if (!frappe.user.has_role("Miss Punch Role")) {
								frappe.validated = false;
								frappe.msgprint("Already Available checkins are against this date");
							}
						else
							frm.set_df_property('in_time', 'read_only', 0);
							frm.set_df_property('out_time', 'read_only', 0);

					}
					if(!r.message.in_time && !r.message.out_time){
						frappe.validated=false
						frappe.msgprint("There is no checkin or checkout present for this date")
					}
				}
			})
		}
        
	},
});
