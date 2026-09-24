import frappe
import json

def before_submit(doc, method=None):

    # collect ALL new rows as keys
    new_rows = set()

    for r in doc.staffing_details:
        new_rows.add((r.designation, r.department, r.gradebps))

    # get all submitted job ads except current
    old_ads = frappe.get_all(
        "Job Ad",
        filters={
            "docstatus": 1,
            "name": ["!=", doc.name]
        },
        pluck="name"
    )

    for ad in old_ads:
        old_doc = frappe.get_doc("Job Ad", ad)

        for old_row in old_doc.staffing_details:

            old_key = (
                old_row.designation,
                old_row.department,
                old_row.gradebps
            )

            if old_key in new_rows:

                frappe.throw(
                    f"""
❌ Duplicate Staffing Plan Found<br><br>

<b>Job Ad:</b> {old_doc.name}<br>

<b>Designation:</b> {old_row.designation}<br>
<b>Department:</b> {old_row.department}<br>
<b>Grade/BPS:</b> {old_row.gradebps}<br>

<b>Posted On:</b> {old_doc.custom_posted_on}<br>
<b>Closes On:</b> {old_doc.custom_closes_on}<br>
                    """
                )
def on_submit(doc, method=None):

    for row in doc.staffing_details:

        if frappe.db.exists(
            "Job Opening",
            {
                "designation": row.designation,
                "department": row.department,
                "custom_bps": row.gradebps,
                "custom_posted_on": doc.custom_posted_on,
                "custom_closes_on": doc.custom_closes_on,
            },
        ):
            continue

        job = frappe.new_doc("Job Opening")

        count = frappe.db.count(
            "Job Opening",
            filters={
                "job_title": [
                    "like",
                    "JOB-" + frappe.utils.nowdate()[2:4] + "-%",
                ]
            },
        )

        job.job_title = (
            "JOB-"
            + frappe.utils.nowdate()[2:4]
            + "-"
            + str(count + 1).zfill(3)
        )

        job.designation = row.designation
        job.company = "Women University of AJ&K Bagh"
        job.department = row.department

        job.custom_minimum_qualification = row.minimum_qualification
        job.custom_experience = row.minimum_experience
        job.custom_exp_sector = row.exp_sector
        job.custom_no_of_publications = row.minimum_publications

        job.vacancies = row.vacancies

        job.custom_minimum_cgpa = row.minimum_cgpa

        job.custom_maximum_age_limit = row.age_limit

        job.custom_minimum_age = row.minimum_age_limit

        job.custom_bps = row.gradebps

        job.description = row.eligibility_criteria

        job.custom_application_form_type = row.application_form_type

        job.custom_posted_on = doc.custom_posted_on

        job.custom_closes_on = doc.custom_closes_on

        job.custom_job_ad_reference = doc.name

        job.publish = 1

        try:

            qualifications = json.loads(
                row.selected_qualification_division or "[]"
            )

        except Exception:

            qualifications = []

        for q in qualifications:

            child = job.append(
                "custom_qualification_division_child_doctype",
                {}
            )

            child.qualification = q.get("qualification")
            child.obtained_cgpa = q.get("obtained_cgpa")
            child.total_cgpa = q.get("total_cgpa")
            child.obtained_percentage = q.get("obtained_percentage")

        job.save(ignore_permissions=True)

def before_cancel(doc, method=None):

    jobs = frappe.get_all(
        "Job Opening",
        filters={
            "custom_job_ad_reference": doc.name
        },
        fields=["name", "designation", "department"]
    )

    for job in jobs:

        applicants = frappe.get_all(
            "Job Applicant",
            filters={
                "job_title": job.name
            },
            fields=["name", "applicant_name"]
        )

        if applicants:

            msg = f"""
            <h3 style='color:red;'>Cannot Cancel Job Advertisement</h3>

            <p>
            The following Job Opening has Job Applicant(s). Please remove or transfer the applicants before cancelling this Job Advertisement.
            </p>

            <table class="table table-bordered">
                <tr>
                    <th>Job Opening</th>
                    <td>{job.name}</td>
                </tr>
                <tr>
                    <th>Designation</th>
                    <td>{job.designation}</td>
                </tr>
                <tr>
                    <th>Department</th>
                    <td>{job.department}</td>
                </tr>
            </table>

            <br>

            <b>Applicants</b><br>
            """

            for applicant in applicants:
                msg += f"• {applicant.name}"
                if applicant.applicant_name:
                    msg += f" - {applicant.applicant_name}"
                msg += "<br>"

            frappe.throw(msg)
            
def on_trash(doc, method=None):

    jobs = frappe.get_all(
        "Job Opening",
        filters={
            "custom_job_ad_reference": doc.name
        },
        pluck="name"
    )

    for job_name in jobs:

        job = frappe.get_doc("Job Opening", job_name)

        if job.docstatus == 1:
            job.cancel()

        job.delete(ignore_permissions=True)

