"""Canvas API enums - simplified and focused."""

from enum import Enum

class CoursesInclude(str, Enum):
    """Additional information that can be included with Canvas courses API calls."""
    NEEDS_GRADING_COUNT = "needs_grading_count"
    SYLLABUS_BODY = "syllabus_body"
    PUBLIC_DESCRIPTION = "public_description"
    TOTAL_SCORES = "total_scores"
    CURRENT_GRADING_PERIOD_SCORES = "current_grading_period_scores"
    GRADING_PERIODS = "grading_periods"
    TERM = "term"
    ACCOUNT = "account"
    COURSE_PROGRESS = "course_progress"
    SECTIONS = "sections"
    STORAGE_QUOTA_USED_MB = "storage_quota_used_mb"
    TOTAL_STUDENTS = "total_students"
    PASSBACK_STATUS = "passback_status"
    FAVORITES = "favorites"
    TEACHERS = "teachers"
    OBSERVED_USERS = "observed_users"
    TABS = "tabs"
    COURSE_IMAGE = "course_image"
    BANNER_IMAGE = "banner_image"
    CONCLUDED = "concluded"
    POST_MANUALLY = "post_manually"

class PerCourseInclude(str, Enum):
    ALL_COURSES = "all_courses"
    PERMISSIONS = "permissions"
    