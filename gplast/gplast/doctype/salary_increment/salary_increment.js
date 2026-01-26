// Copyright (c) 2025, Teampro and contributors
// For license information, please see license.txt

const percentFields = [
    'basic_percent',
    'cca_percent',
    'hra_percent',
    'special_allowance_percent',
    'conveyance_allowance_percent',
    'medical_allowances_percent',
    'shift_allowance_percent',
    'other_allowance_percent',
    'arrear_basic_percent',
    'arrear_hra_percent',
    'uniform_allowance_percent',
    'magazine_allowances_percent'
];
frappe.ui.form.on('Salary Increment', {
	revised_basic(frm) {
        frm.trigger('get_revised_total');
        // if(frm.doc.increment_by=='Percentage'){
            frm.set_value('revise_basic',frm.doc.revised_basic+frm.doc.basic)
        // }
    },
	revised_uniform_allowance(frm) {
        frm.trigger('get_revised_total');
        // if(frm.doc.increment_by=='Percentage'){
            frm.set_value('revise_uniform_allowance',frm.doc.revised_uniform_allowance+frm.doc.cca)
        // }
    },
	revised_magazine_allowance(frm) {
        frm.trigger('get_revised_total');
        // if(frm.doc.increment_by=='Percentage'){
            frm.set_value('revise_magazine_allowance',frm.doc.revised_magazine_allowance+frm.doc.magazine_allowances)
        // }
    },
	revised_arrear_hra(frm) {
        frm.trigger('get_revised_total');
        // if(frm.doc.increment_by=='Percentage'){
            frm.set_value('revise_arrear_hra',frm.doc.revised_arrear_hra+frm.doc.arrear_hra)
        // }
    },
	revised_arrear_basic(frm) {
        frm.trigger('get_revised_total');
        // if(frm.doc.increment_by=='Percentage'){
            frm.set_value('revise_arrear_basic',frm.doc.revised_arrear_basic+frm.doc.arrear_basic)
        // }
    },
	revised_other_allowance(frm) {
        frm.trigger('get_revised_total');
        // if(frm.doc.increment_by=='Percentage'){
            frm.set_value('revise_other_allowance',frm.doc.revised_other_allowance+frm.doc.other_allowance)
        // }
    },
	revised_shift_allowance(frm) {
        frm.trigger('get_revised_total');
        // if(frm.doc.increment_by=='Percentage'){
            frm.set_value('revise_shift_allowance',frm.doc.revised_shift_allowance+frm.doc.shift_allowance)
        // }
    },
	revised_allowances(frm) {
        frm.trigger('get_revised_total');
        // if(frm.doc.increment_by=='Percentage'){
            frm.set_value('revise_allowances',frm.doc.revised_allowances+frm.doc.medical_allowances)
        // }
    },
	revised_conveyance_allowance(frm) {
        frm.trigger('get_revised_total');
        // if(frm.doc.increment_by=='Percentage'){
            frm.set_value('revise_conveyance_allowance',frm.doc.revised_conveyance_allowance+frm.doc.conveyance_allowance)
        // }
    },
	revised_special_allowance(frm) {
        frm.trigger('get_revised_total');
        // if(frm.doc.increment_by=='Percentage'){
            frm.set_value('revise_special_allowance',frm.doc.revised_special_allowance+frm.doc.special_allowance)
        // }
    },
	revised_hra(frm) {
        frm.trigger('get_revised_total');
        // if(frm.doc.increment_by=='Percentage'){
            frm.set_value('revise_hra',frm.doc.revised_hra+frm.doc.house_rent_allowance)
        // }
    },
	revised_cca(frm) {
        frm.trigger('get_revised_total');
        // if(frm.doc.increment_by=='Percentage'){
            frm.set_value('revise_cca',frm.doc.revised_cca+frm.doc.cca)
        // }
    },
	// get_totals(frm){
	// 	let tot=frm.doc.revised_basic+frm.doc.revised_cca+frm.doc.revised_hra+frm.doc.revised_special_allowance+frm.doc.revised_conveyance_allowance+frm.doc.revised_allowances+
	// 	frm.doc.revised_shift_allowance+frm.doc.revised_other_allowance+frm.doc.revised_arrear_basic+frm.doc.revised_arrear_hra+frm.doc.revised_uniform_allowance+frm.doc.revised_magazine_allowance
	// 	frm.set_value('revised_total',tot)
    //     if(frm.doc.increment_by=='Percentage'){
    //         frm.set_value('revised_tota',tot+salary_total)
    //     }
	// },
	get_revised_total(frm){
		let tot=frm.doc.revised_basic+frm.doc.revised_cca+frm.doc.revised_hra+frm.doc.revised_special_allowance+frm.doc.revised_conveyance_allowance+frm.doc.revised_allowances+
		frm.doc.revised_shift_allowance+frm.doc.revised_other_allowance+frm.doc.revised_arrear_basic+frm.doc.revised_arrear_hra+frm.doc.revised_uniform_allowance+frm.doc.revised_magazine_allowance
		frm.set_value('revised_total',tot)
        // if(frm.doc.increment_by=='Percentage'){
            frm.set_value('revise_total',tot+frm.doc.salary_total)
        // }
	},
	increment_by(frm){
		// if(frm.doc.increment_by=='Percentage'){
			frm.set_value('revised_basic',0)
			frm.set_value('revised_cca',0)
			frm.set_value('revised_hra',0)
			frm.set_value('revised_special_allowance',0)
			frm.set_value('revised_conveyance_allowance',0)
			frm.set_value('revised_shift_allowance',0)
			frm.set_value('revised_other_allowance',0)
			frm.set_value('revised_arrear_basic',0)
			frm.set_value('revised_arrear_hra',0)
			frm.set_value('revised_uniform_allowance',0)
			frm.set_value('revised_magazine_allowance',0)
			frm.set_value('revised_allowances',0)
			frm.set_value('revised_total',0)
		// }
        // if(frm.doc.increment_by=='Percentage'){
            frm.set_value('revise_basic',frm.doc.basic)
			frm.set_value('revise_cca',frm.doc.cca)
			frm.set_value('revise_hra',frm.doc.house_rent_allowance)
			frm.set_value('revise_special_allowance',frm.doc.special_allowance)
			frm.set_value('revise_conveyance_allowance',frm.doc.conveyance_allowance)
			frm.set_value('revise_shift_allowance',frm.doc.shift_allowance)
			frm.set_value('revise_other_allowance',frm.doc.other_allowance)
			frm.set_value('revise_arrear_basic',frm.doc.arrear_basic)
			frm.set_value('revise_arrear_hra',frm.doc.arrear_hra)
			frm.set_value('revise_uniform_allowance',frm.doc.uniform_allowance)
			frm.set_value('revise_magazine_allowance',frm.doc.magazine_allowances)
			frm.set_value('revise_allowances',frm.doc.medical_allowances)
			frm.set_value('revise_total',frm.doc.salary_total)
        // }
	},
	total_amount(frm){
		if (frm.doc.total_amount > 0){
			frm.trigger('get_percentage_amount');
		}else{
			frm.set_value('revised_basic',0)
			frm.set_value('revised_cca',0)
			frm.set_value('revised_hra',0)
			frm.set_value('revised_special_allowance',0)
			frm.set_value('revised_conveyance_allowance',0)
			frm.set_value('revised_shift_allowance',0)
			frm.set_value('revised_other_allowance',0)
			frm.set_value('revised_arrear_basic',0)
			frm.set_value('revised_arrear_hra',0)
			frm.set_value('revised_uniform_allowance',0)
			frm.set_value('revised_magazine_allowance',0)
			frm.set_value('revised_allowances',0)
			frm.set_value('revised_total',0)
		}
			
	},
	
	basic_percent(frm) {
        validate_and_update(frm, 'basic_percent');
    },
    cca_percent(frm) {
        validate_and_update(frm, 'cca_percent');
    },
    hra_percent(frm) {
        validate_and_update(frm, 'hra_percent');
    },
    special_allowance_percent(frm) {
        validate_and_update(frm, 'special_allowance_percent');
    },
    conveyance_allowance_percent(frm) {
        validate_and_update(frm, 'conveyance_allowance_percent');
    },
    medical_allowances_percent(frm) {
        validate_and_update(frm, 'medical_allowances_percent');
    },
    shift_allowance_percent(frm) {
        validate_and_update(frm, 'shift_allowance_percent');
    },
    other_allowance_percent(frm) {
        validate_and_update(frm, 'other_allowance_percent');
    },
    arrear_basic_percent(frm) {
        validate_and_update(frm, 'arrear_basic_percent');
    },
    arrear_hra_percent(frm) {
        validate_and_update(frm, 'arrear_hra_percent');
    },
    uniform_allowance_percent(frm) {
        validate_and_update(frm, 'uniform_allowance_percent');
    },
    magazine_allowances_percent(frm) {
        validate_and_update(frm, 'magazine_allowances_percent');
    },

    total_amount(frm) {
        frm.trigger('get_percentage_amount');
    },

    get_percentage_amount(frm) {
        const fields = [
            { percent: 'basic_percent', revised: 'revised_basic' },
            { percent: 'cca_percent', revised: 'revised_cca' },
            { percent: 'hra_percent', revised: 'revised_hra' },
            { percent: 'special_allowance_percent', revised: 'revised_special_allowance' },
            { percent: 'conveyance_allowance_percent', revised: 'revised_conveyance_allowance' },
            { percent: 'medical_allowances_percent', revised: 'revised_allowances' },
            { percent: 'shift_allowance_percent', revised: 'revised_shift_allowance' },
            { percent: 'other_allowance_percent', revised: 'revised_other_allowance' },
            { percent: 'arrear_basic_percent', revised: 'revised_arrear_basic' },
            { percent: 'arrear_hra_percent', revised: 'revised_arrear_hra' },
            { percent: 'uniform_allowance_percent', revised: 'revised_uniform_allowance' },
            { percent: 'magazine_allowances_percent', revised: 'revised_magazine_allowance' }
        ];

        const total = frm.doc.total_amount || 0;

        fields.forEach(field => {
            const percent_value = frm.doc[field.percent] || 0;
            const calculated_value = (percent_value > 0 && total > 0) ? (total * percent_value) / 100 : 0;        
            frm.set_value(field.revised, calculated_value);
        });
    }



});
function validate_and_update(frm, field_name) {
	const percentFields = [
		'basic_percent',
		'cca_percent',
		'hra_percent',
		'special_allowance_percent',
		'conveyance_allowance_percent',
		'medical_allowances_percent',
		'shift_allowance_percent',
		'other_allowance_percent',
		'arrear_basic_percent',
		'arrear_hra_percent',
		'uniform_allowance_percent',
		'magazine_allowances_percent'
	];

	let total_percent = 0;
	percentFields.forEach(field => {
		total_percent += parseFloat(frm.doc[field]) || 0;
	});

	frm.set_value('total_percent', total_percent);

	if (total_percent > 100) {
		frm.set_value(field_name, 0);
		frappe.throw("Total percentage should not exceed 100%");
	} else {
		frm.trigger('get_percentage_amount');
	}
}

