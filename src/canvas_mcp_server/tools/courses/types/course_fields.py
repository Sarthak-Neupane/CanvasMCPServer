from enum import Enum

class CourseDisplayField(Enum):
    ID = "id"
    NAME = "name"
    COURSE_CODE = "course_code"
    UUID = "uuid"
    SIS_COURSE_ID = "sis_course_id"
    INTEGRATION_ID = "integration_id"
    WORKFLOW_STATE = "workflow_state"
    ACCOUNT_ID = "account_id"
    ROOT_ACCOUNT_ID = "root_account_id"
    ENROLLMENT_TERM_ID = "enrollment_term_id"
    CREATED_AT = "created_at"
    START_AT = "start_at"
    END_AT = "end_at"
    DEFAULT_VIEW = "default_view"
    TIME_ZONE = "time_zone"
    LOCALE = "locale"
    COURSE_FORMAT = "course_format"
    STORAGE_QUOTA_MB = "storage_quota_mb"
    STORAGE_QUOTA_USED_MB = "storage_quota_used_mb"
    HIDE_FINAL_GRADES = "hide_final_grades"
    OPEN_ENROLLMENT = "open_enrollment"
    SELF_ENROLLMENT = "self_enrollment"
    TOTAL_STUDENTS = "total_students"
    SYLLABUS_BODY = "syllabus_body"
    NEEDS_GRADING_COUNT = "needs_grading_count"
    TEACHERS = "teachers"
    SECTIONS = "sections"

DETAILED_FIELDS = [
    CourseDisplayField.ID,
    CourseDisplayField.NAME,
    CourseDisplayField.COURSE_CODE,
    CourseDisplayField.WORKFLOW_STATE,
    CourseDisplayField.START_AT,
    CourseDisplayField.END_AT,
    CourseDisplayField.ENROLLMENT_TERM_ID,
    CourseDisplayField.DEFAULT_VIEW,
]

