import React, {Component} from "react"
import {TextField, ArrayField, GroupField} from "react-invenio-forms"

// TODO list of courses, selecting one changes all the inputs below
// Example: single static course
const courses = [
    {
        department: "Design MFA",
        department_code: "DESGN",
        section: "DESGN-5000-1",
        section_refid: "COURSE_SECTION-3-42782",
        title: "Introduction to Design",
        term: "Fall 2025",
        instructors: [
            {
                first_name: "John",
                middle_name: "",
                last_name: "Doe",
                username: "jdoe",
                employee_id: "12345",
                uid: "12346",
            },
            {
                first_name: "Jane",
                middle_name: "",
                last_name: "Smith",
                username: "jsmith",
                employee_id: "67890",
                uid: "12345",
            },
        ],
        instructors_string: "John Doe, Jane Smith",
    }
]

export class CourseField extends Component {
    constructor(props) {
        super(props)
        this.state = {
            series: "",
        }
    }

    render() {
        // Prepopulate the form with static example data
        const courseData = courses[0]
        const {
            fieldPath, // injected by the custom field loader
        } = this.props

        return (
        <div>
            <h4>Course Information</h4>
            <TextField
                fieldPath={`${fieldPath}.department`}
                label="Department"
                defaultValue={courseData.department}
            />
            <TextField
                fieldPath={`${fieldPath}.department_code`}
                label="Department Code"
                defaultValue={courseData.department_code}
            />
            <TextField
                fieldPath={`${fieldPath}.section`}
                label="Section"
                defaultValue={courseData.section}
            />
            <TextField
                fieldPath={`${fieldPath}.section_refid`}
                label="Section ID"
                defaultValue={courseData.section_refid}
            />
            <TextField
                fieldPath={`${fieldPath}.title`}
                label="Course Title"
                defaultValue={courseData.title}
            />
            <TextField
                fieldPath={`${fieldPath}.term`}
                label="Term"
                defaultValue={courseData.term}
            />
            <ArrayField
                fieldPath={`${fieldPath}.instructors`}
                label="Instructors"
                defaultValue={courseData.instructors}
            >
                {({arrayHelpers, indexPath}) => (
                    <GroupField>
                        <TextField fieldPath={`${indexPath}.first_name`} label="First Name" />
                        <TextField fieldPath={`${indexPath}.middle_name`} label="Middle Name" />
                        <TextField fieldPath={`${indexPath}.last_name`} label="Last Name" />
                        <TextField fieldPath={`${indexPath}.username`} label="Username" />
                        <TextField
                            fieldPath={`${indexPath}.employee_id`}
                            label="Employee ID"
                        />
                        <TextField
                            fieldPath={`${indexPath}.uid`}
                            label="Universal ID"
                        />
                    </GroupField>
                )}
            </ArrayField>
        </div>
        )
    }
}

export default CourseField
