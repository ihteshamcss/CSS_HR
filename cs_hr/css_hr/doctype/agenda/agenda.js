// Copyright (c) 2026, CSS and contributors
// For license information, please see license.txt


// frappe.ui.form.on('Agenda', {

// 	meeting_list: function (frm) {

// 		if (!frm.doc.meeting_list || frm.doc.meeting_list.length === 0) {
// 			frm.clear_table('custom_agenda_point');
// 			frm.refresh_field('custom_agenda_point');
// 			return;
// 		}

// 		frm.clear_table('custom_agenda_point');

// 		let total = frm.doc.meeting_list.length;
// 		let done = 0;

// 		frm.doc.meeting_list.forEach(row => {

// 			if (!row.meeting) {
// 				done++;
// 				return;
// 			}

// 			frappe.call({
// 				method: "frappe.client.get",
// 				args: {
// 					doctype: "Meetings",
// 					name: row.meeting
// 				},
// 				callback: function (r) {

// 					if (r.message && r.message.moms) {

// 						r.message.moms.forEach(m => {

// 							let child = frm.add_child('custom_agenda_point');

// 							// MOM data
// 							child.mom = m.mom;

// 							// ✅ Meeting reference from meeting_list
// 							child.meeting_reference = row.meeting;
// 						});
// 					}

// 					done++;

// 					if (done === total) {
// 						frm.refresh_field('custom_agenda_point');
// 					}
// 				}
// 			});
// 		});
// 	}

// });

/**
 * Shared function to fetch MOMs
 */



// frappe.ui.form.on('Agenda', {
// 	meeting_list: function (frm) {
// 		if (!frm.doc.meeting_list) return;

// 		frm.clear_table('custom_agenda_point');

// 		frm.doc.meeting_list.forEach(row => {
// 			frappe.call({
// 				method: "frappe.client.get",
// 				args: {
// 					doctype: "Meetings",
// 					name: row.meeting
// 				},
// 				callback: function (r) {
// 					if (r.message?.moms) {
// 						r.message.moms.forEach(m => {
// 							let c = frm.add_child('custom_agenda_point');
// 							c.mom = m.mom;
// 							c.meeting_reference = row.meeting;
// 						});
// 						frm.refresh_field('custom_agenda_point');
// 					}
// 				}
// 			});
// 		});
// 	}
// });