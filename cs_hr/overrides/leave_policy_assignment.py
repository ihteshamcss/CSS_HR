import frappe

from hrms.hr.doctype.leave_policy_assignment.leave_policy_assignment import (
    LeavePolicyAssignment,
)


class CustomLeavePolicyAssignment(LeavePolicyAssignment):

    def is_dependent_leave(self, leave_type):
        """
        Check whether the Leave Type consumes another Leave Type.
        """

        return bool(
            frappe.db.get_value(
                "Leave Type",
                leave_type,
                "custom_deduct_from_leave_type",
            )
        )


    def create_leave_allocation(
        self,
        annual_allocation,
        leave_details,
        date_of_joining,
    ):
        """
        Create a Leave Allocation.

        For dependent Leave Types:

            annual allocation may be anything,
            but actual allocation is ALWAYS 0.

        Example:

            Leave Policy:

                LFP Faculty       8
                Ex-Pakistan       0

            Result:

                LFP Faculty allocation       8
                Ex-Pakistan allocation      0
        """

        # ---------------------------------------------------------
        # Standard carry-forward behavior.
        # ---------------------------------------------------------

        carry_forward = self.carry_forward

        if self.carry_forward and not leave_details.is_carry_forward:
            carry_forward = 0

        # ---------------------------------------------------------
        # Calculate normal allocation first.
        # ---------------------------------------------------------

        new_leaves_allocated = self.get_new_leaves(
            annual_allocation,
            leave_details,
            date_of_joining,
        )

        # ---------------------------------------------------------
        # DEPENDENT LEAVE
        #
        # Force allocation to ZERO.
        # ---------------------------------------------------------

        if self.is_dependent_leave(leave_details.name):

            new_leaves_allocated = 0
            carry_forward = 0

        # ---------------------------------------------------------
        # NORMAL LEAVE
        #
        # Preserve standard HRMS behavior:
        # skip zero allocation.
        # ---------------------------------------------------------

        elif (
            new_leaves_allocated == 0
            and not leave_details.is_earned_leave
        ):

            text = _(
                "Leave allocation is skipped for {0}, "
                "because number of leaves to be allocated is 0."
            ).format(
                frappe.bold(leave_details.name)
            )

            frappe.get_doc(
                {
                    "doctype": "Comment",
                    "comment_type": "Comment",
                    "reference_doctype": "Leave Policy Assignment",
                    "reference_name": self.name,
                    "content": text,
                }
            ).insert(
                ignore_permissions=True
            )

            return None, 0

        # ---------------------------------------------------------
        # Create allocation even though dependent allocation is 0.
        # ---------------------------------------------------------

        allocation = frappe.get_doc(
            {
                "doctype": "Leave Allocation",
                "employee": self.employee,
                "leave_type": leave_details.name,
                "from_date": self.effective_from,
                "to_date": self.effective_to,
                "new_leaves_allocated": new_leaves_allocated,
                "leave_period": (
                    self.leave_period
                    if self.assignment_based_on == "Leave Policy"
                    else ""
                ),
                "leave_policy_assignment": self.name,
                "leave_policy": self.leave_policy,
                "carry_forward": carry_forward,
            }
        )

        allocation.save(
            ignore_permissions=True
        )

        allocation.submit()

        return allocation.name, new_leaves_allocated