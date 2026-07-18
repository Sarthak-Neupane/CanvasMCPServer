"""Pydantic models for Canvas API responses."""
from typing import Final, List

from .announcements.announcement_model import Announcement, AnnouncementAuthorRef
from .assignments.assignment_detail_model import AssignmentCourseRef, AssignmentDetail
from .assignments.assignment_summary_model import AssignmentSummary
from .assignments.upcoming_assignment_model import UpcomingAssignment
from .courses.course_calendar_model import CalendarLink
from .courses.course_detail_model import CourseDetail
from .courses.course_progress_model import CourseProgress
from .courses.course_summary_model import CourseSummary
from .courses.course_term_model import Term
from .grades.course_grades_model import (
    CourseGrades,
    EnrollmentGrade,
    Grades,
    GradeUserRef,
)
from .submissions.submission_status_model import (
    AssignmentSubmissions,
    SubmissionStatus,
    SubmissionUserRef,
)
from .todos.todo_item_model import TodoAssignmentRef, TodoItem

__all__: Final[List[str]] = [
    # Courses
    "CourseDetail",
    "CalendarLink",
    "CourseProgress",
    "Term",
    "CourseSummary",
    # Assignments
    "AssignmentSummary",
    "AssignmentDetail",
    "AssignmentCourseRef",
    "UpcomingAssignment",
    # Submissions
    "AssignmentSubmissions",
    "SubmissionStatus",
    "SubmissionUserRef",
    # Grades
    "CourseGrades",
    "EnrollmentGrade",
    "Grades",
    "GradeUserRef",
    # Announcements
    "Announcement",
    "AnnouncementAuthorRef",
    # Todos
    "TodoItem",
    "TodoAssignmentRef",
]
