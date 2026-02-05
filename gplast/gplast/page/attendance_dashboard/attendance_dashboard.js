frappe.pages['attendance-dashboard'].on_page_load = function(wrapper) {

	var page = frappe.ui.make_app_page({
		parent: wrapper,
		single_column: true
	});

	$(wrapper).find('.page-head').hide();

	$(wrapper).css({
		'background-color': '#eef6ff',
		'min-height': '80vh'
	});
	

	$(wrapper).prepend(`
		<div style="
			display: flex;
			justify-content: left;
			margin: 20px 0;
			margin-left:20px;
		">
			<div style="
				padding: 14px 30px;
				font-size: 24px;
				margin-top:10px;
				font-weight: 600;
				color: #1f3b5c;
				background-color: #ffffff;
				border: 2px solid #e24a4aff;
				border-radius: 12px;
				box-shadow: 0 4px 10px rgba(0,0,0,0.05);
			">
				Attendance<br>
				&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Dashboard
			</div>

			
		</div>
		
	`);

	// Main layout (20% / 80%)
	$(wrapper).append(`

		<div style="display:flex; padding:5px 15px; gap:15px; margin-top:-30px;">

			<!-- LEFT SIDE (20%) -->
			<div id="left-panel" style="
				width:20%;
				height: 300px;
				background:#ffffff;
				border:2px solid #0a0a0aff;
				border-radius:12px;
				padding:12px;
			">
				<div class="nav-btn active" data-type="shift">Shift Wise Attendance Data</div>
				<div class="nav-btn" data-type="overall">Overall Attendance Data</div>
				<div class="nav-btn" data-type="graph">Graph Wise Data</div>

			</div>

			<!-- RIGHT SIDE (80%) -->
			<div id="right-panel" style="
				width:80%;
				hight: 500px;
				margin-top:-150px;
				background:#ffffff;
				border:2px solid #050505ff;
				border-radius:12px;
				padding:20px;
				overflow:auto;
			">
			
					<!-- TOP SINGLE LINE -->
					<div style="
						width:100%;
						height:2px;
						background:#d1d5db;
						margin-bottom:15px;
					"></div>

					<p>Shift wise format will be loaded here...</p>
				</div>

			</div>

		</div>
		<div id="loading_overlay" style="
			display: none;
			position: fixed;
			top: 0;
			left: 0;
			width: 100%;
			height: 100%;
			background: rgba(255, 255, 255, 0.8);
			z-index: 9999;
			text-align: center;
			padding-top: 200px;
			font-size: 24px;
			color: #090d11ff;
		">
			Fetching data...
		</div>
	`);	
	
	/* ===== DEFAULT LOAD ===== */
	load_shift_wise_content(wrapper);


	$(wrapper).on('click', '.nav-btn', function() {

		$('.nav-btn').removeClass('active');

		$(this).addClass('active');

		let type = $(this).data('type');

		if (type === 'shift') {
			load_shift_wise_content();
			applyFilter();
		}
		if (type === 'overall') {
			load_overall_attendance_content();
			load_overall_attendance_data();
		}
		if (type === 'graph') {
			$('#right-panel').html(`
				<h4>Graph Wise Data</h4>shift-wise attendance
				<p>Graphs and charts will be shown here...</p>
			`);
		}
	});

	/* APPLY FILTER */	
	$(wrapper).on('click', '#apply_filter', function () {
		applyFilter();
	});
	$(document).on('click', '#overall_apply', function () {
		load_overall_attendance_data();
	});

	applyFilter();

	/*  SHIFT CLICK  */
	$(wrapper).on('click', '.data-card[data-shift]', function () {

	$('.data-card').removeClass('active');
	$(this).addClass('active');

	let shift = $(this).data('shift');
	$('#loading_overlay').show();
	frappe.call({
		method: "gplast.gplast.page.attendance_dashboard.attendance_dashboard.get_shift_wise_attendance",
		args: {
			shift: shift,
			from_date: $('#from_date').val(),
			to_date: $('#to_date').val(),
			status: $('#status').val() || null
		},
		callback(r) {

			let staff = 0;
			let remaining = 0;

			(r.message || []).forEach(d => {
				if (d.employee_category === "Staff") {
					staff++;
				} else {
					remaining++;
				}
			});

			$('#category-section').show();
			$('#arrow-layer').show();
			$('#staffCnt').text(staff);
			$('#opCnt').text(remaining);

			drawArrows();

			window._shift_attendance_data = r.message || [];

			$('#table-section').empty();
		},
		always: function() {
            $('#loading_overlay').hide();
        }
	});
});
	

	/*  CATEGORY CLICK  */
	$(wrapper).on('click', '.data-card[data-cat]', function () {
		
		$('#loading_overlay').show();

		$('.data-card').removeClass('active');
		$(this).addClass('active');

		let category = $(this).data('cat'); 
		let rows = '';

		setTimeout(function() {

			(window._shift_attendance_data || []).forEach(d => {
				if (category === "Staff" && d.employee_category !== "Staff") return;
				if (category === "Operator" && d.employee_category === "Staff") return;

				rows += `
					<tr>
						<td>${d.employee_name}</td>
						<td>${d.employee}</td>
						<td>${d.department}</td>
						<td>${d.unit}</td>
						<td>${d.in_time || ''}</td>
						<td>${d.out_time || ''}</td>
						<td>${d.total_working_hours || 0}</td>
						<td><b>${d.ot_hours}</b></td>
					</tr>`;
			});

			// Render table
			$('#table-section').html(`

				<div style="display:flex; justify-content:flex-end; margin-bottom:6px;">
					<button id="download_excel"
						style="
							padding:5px 12px;
							border:1px solid black;
							background:#e9f2ff;
							cursor:pointer;
							border-radius:4px;
							font-weight:600;
						">
						⬇ Download
					</button>
				</div>

				<div style="
					max-height:350px;      
					overflow-y:auto;
					border-top:1px solid black;
					border:1px solid black;
				">
				<table id="attendance_table" class="table table-bordered" style="border:1px solid black; border-top:1px solid black; border-collapse: collapse; width:100%;">
					<thead style="position:sticky; top:0; background-color:#f0f7ff; z-index:10;"> 
						<tr>
							<th style="border:1px solid black;border-top:1px solid black;">Emp Name</th>
							<th style="border:1px solid black;border-top:1px solid black;">Emp Code</th>
							<th style="border:1px solid black;border-top:1px solid black;">Dept</th>
							<th style="border:1px solid black;border-top:1px solid black;">Unit</th>
							<th style="border:1px solid black;border-top:1px solid black;">IN</th>
							<th style="border:1px solid black;border-top:1px solid black;">OUT</th>
							<th style="border:1px solid black;border-top:1px solid black;">WH</th>
							<th style="border:1px solid black;border-top:1px solid black;">OT Hrs</th>
						</tr>
					</thead>
					<tbody>
						${(rows || '<tr><td colspan="8">No Data</td></tr>').replace(/<td>/g,'<td style="border:1px solid black;border-top:1px solid black;">')}
					</tbody>
				</table>
			`);


			$('#loading_overlay').hide();

		}, 100); 

	});


	$(wrapper).on('click', '#download_excel', function () {
    let category = $('.data-card.active').data('cat');

    let data = (window._shift_attendance_data || []).filter(d => {
        if (category === "Staff") return d.employee_category === "Staff";
        if (category === "Operator") return d.employee_category !== "Staff";
        return true;
    });

    if (!data.length) {
        frappe.msgprint("No data to download");
        return;
    }

    let columns = ["Emp Name", "Emp Code", "Dept", "Unit", "IN", "OUT", "WH", "OT Hrs"];

    let csv = columns.join(",") + "\n";

    data.forEach(d => {
        csv += `"${d.employee_name || ''}","${d.employee || ''}","${d.department || ''}","${d.unit || ''}","${d.in_time || ''}","${d.out_time || ''}","${d.total_working_hours || 0}","${d.ot_hours || 0}"\n`;
    });

    let blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    let link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `Attendance_${category}.csv`;
    link.click();
});


	$(wrapper).append(`
		<style>
			.nav-btn {
				padding:12px 10px;
				margin-bottom:10px;
				border:2px solid #4a90e2;
				border-radius:12px;
				background:#ffffff;
				color:#1f3b5c;
				font-weight:500;
				cursor:pointer;
				text-align:center;
				transition:0.3s;
			}
			.nav-btn:hover {
				background:#f0f7ff;
			}
			.nav-btn.active {
				border-color:#d4af37;
				background:#fff6d6;
				color:#7a5a00;
				font-weight:600;
			}
		</style>
	`);

};

function load_shift_wise_content() {

    let CARD_WIDTH = '200px';
    let CARD_HEIGHT = '80px';

	let CARD_WIDTH1 = '180px';
    let CARD_HEIGHT1 = '75px';

    $('#right-panel').html(`
        <!-- FILTER SECTION -->
        <div class="filter-section">
            <select id="status" class="form-control filter-item">
                <option value="">All</option>
                <option value="Present" selected>Present</option>
                <option value="Absent">Absent</option>
                <option value="Leave">On Leave</option>
                <option value="half day">Half Day</option>
            </select>

            <input type="date" id="from_date" class="form-control filter-item">
            <input type="date" id="to_date" class="form-control filter-item">

            <button class="btn btn-primary filter-item" id="apply_filter">
                Apply
            </button>
        </div>

        <!-- SHIFT RECTANGLES -->
        <div class="section-gap"
             style="display:flex; gap:40px; flex-wrap:wrap;">

            ${['A','B','C'].map(s => `
                <div class="data-card"
                     id="shift${s}_card"
                     data-shift="${s}"
                     style="
                        background:#ffdde0;
                        border:4px solid #e24a4a;
                        border-radius:12px;
						margin-top:20px;
						margin-left:70px;
                        width:${CARD_WIDTH};
                        height:${CARD_HEIGHT};
                        display:flex;
                        flex-direction:column;
                        justify-content:center;
                        align-items:center;
                        cursor:pointer;
                     ">
                    <div style="font-size:16px;margin-top:6px;font-weight:bold;">
                        Shift : ${s}
                    </div>
                    <div id="shift${s}"
                         style="font-size:24px; font-weight:bold; color:black; margin-top:6px;">
                        0
                    </div>
                </div>
            `).join('')}
        </div>
				
		<div id="arrow-layer"
			style="
				position:relative;
				height:80px;
				margin-left:40px;
				display:none;
			">
		</div>


        <!-- CATEGORY RECTANGLES -->
			<div id="category-section"
				class="section-gap"
				style="display:none;">

				<div id="category-row"
					style="
						display:flex;
						gap:40px;
						flex-wrap:nowrap;
						justify-content:flex-start;
						margin-left:40px;
					">

					<!-- STAFF -->
					<div class="data-card"
						id="staff_card"
						data-cat="Staff"
						style="
							background: #e6f4ea;   
							border: 4px solid #2f8f46;
							border-radius:12px;
							margin-top:-30px;
							margin-left:170px;
							width:${CARD_WIDTH1};
							height:${CARD_HEIGHT1};
							display:flex;
							flex-direction:column;
							justify-content:center;
							align-items:center;
							cursor:pointer;
						">
						<div style="font-size:16px;font-weight:bold;">Staff</div>
						<div id="staffCnt"
							style="font-size:24px;font-weight:bold;color:black;margin-top:6px;">
							0
						</div>
					</div>

					<!-- OPERATOR -->
					<div class="data-card"
						id="operator_card"
						data-cat="Operator"
						style="
							background: #e6f4ea;   
							border: 4px solid #2f8f46;
							border-radius:12px;
							margin-top:-30px;
							margin-left:170px;
							width:${CARD_WIDTH1};
							height:${CARD_HEIGHT1};
							display:flex;
							flex-direction:column;
							justify-content:center;
							align-items:center;
							cursor:pointer;
						">
						<div style="font-size:16px;font-weight:bold;">Operator</div>
						<div id="opCnt"
							style="font-size:24px;font-weight:bold;color:black;margin-top:6px;">
							0
						</div>
					</div>

				</div>
			</div>


        <!-- TABLE -->
        <div id="table-section" class="section-gap"></div>
    `);

    let yesterday = get_yesterday();
    $('#from_date').val(yesterday);
    $('#to_date').val(yesterday);
}


function get_yesterday() {
	let d = new Date();
	d.setDate(d.getDate() - 1);
	return d.toISOString().split('T')[0];
}

function drawArrows() {

    let shift = $('.data-card[data-shift].active');
    let staff = $('#staff_card');
    let operator = $('#operator_card');

    if (!shift.length || !staff.length) return;

    let shiftOffset = shift.offset();
    let staffOffset = staff.offset();
    let opOffset = operator.offset();

    let containerOffset = $('#arrow-layer').offset();

    let sx = shiftOffset.left + shift.outerWidth() / 2 - containerOffset.left;
    let sy = 0;
	
    let staffX = staffOffset.left + staff.outerWidth() / 2 - containerOffset.left;
    let staffY = 60;
	

    let opX = opOffset.left + operator.outerWidth() / 2 - containerOffset.left;
    let opY = 60;
	
    $('#arrow-layer').html(`
        <svg width="100%" height="80">

            <!-- Arrow to Staff -->
            <line x1="${sx}" y1="${sy}"
                  x2="${staffX}" y2="${staffY}"
                  stroke="#b0c4de"
                  stroke-width="2"/>

            <!-- Arrow to Operator -->
            <line x1="${sx}" y1="${sy}"
                  x2="${opX}" y2="${opY}"
                  stroke="#b0c4de"	
                  stroke-width="2"/>

        </svg>
    `);
}

function applyFilter() {
    let from_date = $('#from_date').val() || get_yesterday();
    let to_date = $('#to_date').val() || get_yesterday();
	$('#loading_overlay').show();
    frappe.call({
        method: "gplast.gplast.page.attendance_dashboard.attendance_dashboard.get_shift_count",
        args: {
            from_date: from_date,
            to_date: to_date,
            status: $('#status').val() || null
        },
        callback(r) {
            $('#shiftA,#shiftB,#shiftC').text(0);
            (r.message || []).forEach(d => {
                $('#shift' + d.shift).text(d.count);
            });
        },
		always: function() {
            // Hide loading after fetch
            $('#loading_overlay').hide();
        }
    });
}

function load_overall_attendance_data() {

	$('#loading_overlay').show();

	frappe.call({
		method: "gplast.gplast.page.attendance_dashboard.attendance_dashboard.get_overall_attendance",
		args: {
			from_date: $('#overall_from_date').val(),
			to_date: $('#overall_to_date').val(),
			shift: overall_shift_link ? overall_shift_link.get_value() : null,
			department: overall_department ? overall_department.get_value() : null
		},
		callback(r) {

			let rows = '';
			let i = 1;

			(r.message || []).forEach(d => {

				rows += `
					<tr>
						<td class="text-center">${i++}</td>
						<td class="text-left">${d.company}</td>
						<td class="text-left">${d.department}</td>
						<td class="text-center">${d.shift || ''}</td>
						<td class="text-center">${d.present_count}</td>
						<td class="text-center">${d.absent_count}</td>
						<td class="text-center">${d.absent_percent}%</td>
					</tr>
					`;
			});

			$('#overall_table_body').html(
				rows || `<tr><td colspan="8">No Data</td></tr>`
			);
		},
		always() {
			$('#loading_overlay').hide();
		}
	});
}


function downloadExcel() {

    let csv = 'Emp Name,Emp Code,Dept,Unit,IN,OUT,WH,OT Hrs\n';

    fullTableData.forEach(d => {
        csv += `"${d.employee_name}","${d.employee}","${d.department}","${d.unit}","${d.in_time || ''}","${d.out_time || ''}","${d.working_hours || 0}","${d.ot_hours}"\n`;
    });

    let blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    let link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "Attendance_Data.csv";
    link.click();
}
let overall_shift_link ,overall_department ;
function load_overall_attendance_content() {

	$('#right-panel').html(`

		<div style="
			display:flex;
			justify-content:flex-end;
			gap:12px;
			margin-bottom:15px;
			align-items:center;
			width:100%;
		">
		<div class="filter-section">
			<div class="overall-filter-bar">
				<div id="overall_department_field"></div>
				<div id="overall_shift_field"></div>

				<input type="date" id="overall_from_date" class="form-control date-small">
				<input type="date" id="overall_to_date" class="form-control date-small">

				<button class="btn btn-primary" id="overall_apply">
					Apply
				</button>
			</div>
		</div>
		</div>

		<div style="display:flex; justify-content:flex-end; margin-bottom:6px;">
			<button id="overall_download"
				style="
					padding:5px 12px;
					border:1px solid black;
					background:#e9f2ff;
					cursor:pointer;
					border-radius:4px;
					font-weight:600;
					margin-top:-60px;
					width:120px;  
            		height:40px;
				">
				⬇ Download
			</button>
		</div>
		<!-- TABLE -->
		<div class="table-section">
		<div style="overflow:auto; max-height:420px;margin-top:-20px;">
			<table class="table table-bordered overall-table">
				<thead>
					<tr>
						<th>S.No</th>
						<th class="text-left">Company</th>
						<th class="text-left">Department</th>
						<th class="text-center">Shift</th>
						<th class="text-center">Present</th>
						<th class="text-center">Absent / Leave / LOP</th>
						<th class="text-center">Absent %</th>
					</tr>
				</thead>
				<tbody id="overall_table_body"></tbody>
			</table>
		</div>
		</div>	
	`);
		
		overall_department = frappe.ui.form.make_control({
			parent: $('#overall_department_field'),
			df: {
				fieldtype: 'Link',
				label: 'Department',
				fieldname: 'department',
				options: 'Department',
				placeholder: 'All Departments'
			},
			render_input: true
		});
		overall_department.refresh();

	overall_shift_link = frappe.ui.form.make_control({
		parent: $('#overall_shift_field'),
		df: {
			fieldtype: 'Link',
			label: 'Shift',
			fieldname: 'shift',
			options: 'Shift Type',   
			placeholder: 'All Shifts'
		},
		render_input: true
	});

	overall_shift_link.refresh();

	let y = get_yesterday();
	$('#overall_from_date').val(y);
	$('#overall_to_date').val(y);

	load_overall_attendance_data(); 
}

$(document).on('click', '#overall_download', function () {

	let rows = [];
	let headers = [];

	$('.overall-table thead th').each(function () {
		headers.push($(this).text().trim());
	});

	$('.overall-table tbody tr').each(function () {
		let row = [];
		$(this).find('td').each(function () {
			row.push($(this).text().trim());
		});
		rows.push(row);
	});

	if (rows.length === 0) {
		frappe.msgprint(__('No data available to download'));
		return;
	}

	let excel_data = [];
	excel_data.push(headers);

	rows.forEach(r => {
		excel_data.push(r);
	});

	// 5️⃣ Convert to CSV
	let csv = excel_data.map(e => e.join(",")).join("\n");

	// 6️⃣ Trigger download
	let blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
	let url = URL.createObjectURL(blob);

	let a = document.createElement("a");
	a.href = url;
	a.download = "Overall_Attendance.csv";
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
});
