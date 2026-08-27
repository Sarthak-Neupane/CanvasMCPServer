"""Pydantic models for Canvas API responses."""
from typing import Final, List

from .announcements.announcement_model import Announcement, AnnouncementAuthorRef
from .assignments.assignment_detail_model import AssignmentCourseRef, AssignmentDetail
from .assignments.assignment_resource_model import (
    AssignmentResource,
    AssignmentResources,
    AssignmentResourceType,
)
from .assignments.assignment_summary_model import AssignmentSummary
from .assignments.upcoming_assignment_model import UpcomingAssignment
from .calendar.calendar_event_model import CalendarEvent
from .discussions.discussion_detail_model import DiscussionDetail
from .discussions.discussion_entry_model import (
    DiscussionEntries,
    DiscussionEntry,
    DiscussionParticipant,
)
from .discussions.discussion_summary_model import DiscussionSummary
from .courses.course_calendar_model import CalendarLink
from .courses.course_detail_model import CourseDetail
from .courses.course_progress_model import CourseProgress
from .courses.course_summary_model import CourseSummary
from .courses.course_syllabus_model import CourseSyllabus
from .courses.course_term_model import Term
from .downloads.download_result_model import (
    DownloadBatchResult,
    DownloadFailure,
    DownloadedFile,
)
from .files.file_model import FileDetail, FileSummary
from .files.folder_model import FolderSummary
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
from .submissions.submission_feedback_model import (
    RubricAssessmentEntry,
    SubmissionFeedback,
    SubmissionFeedbackAttachment,
    SubmissionFeedbackComment,
)
from .modules.module_item_model import (
    CompletionRequirement,
    ContentDetails,
    ModuleItemDetail,
    ModuleItemSummary,
)
from .modules.module_summary_model import ModuleSummary
from .pages.page_detail_model import PageDetail
from .pages.page_summary_model import PageSummary
from .planner.planner_item_model import PlannerItem, PlannerSubmissionStatus
from .quizzes.quiz_detail_model import QuizDetail
from .quizzes.quiz_summary_model import QuizSummary
from .rubrics.rubric_criterion_model import RubricCriterion
from .rubrics.rubric_model import Rubric
from .rubrics.rubric_rating_model import RubricRating
from .search.search_result_model import SearchResult
from .todos.todo_item_model import TodoAssignmentRef, TodoItem

__all__: Final[List[str]] = [
    # Courses
    "CourseDetail",
    "CalendarLink",
    "CourseProgress",
    "Term",
    "CourseSummary",
    "CourseSyllabus",
    # Assignments
    "AssignmentSummary",
    "AssignmentDetail",
    "AssignmentCourseRef",
    "AssignmentResource",
    "AssignmentResources",
    "AssignmentResourceType",
    "UpcomingAssignment",
    # Calendar
    "CalendarEvent",
    # Discussions
    "DiscussionSummary",
    "DiscussionDetail",
    "DiscussionEntry",
    "DiscussionEntries",
    "DiscussionParticipant",
    # Submissions
    "AssignmentSubmissions",
    "SubmissionStatus",
    "SubmissionUserRef",
    "SubmissionFeedback",
    "SubmissionFeedbackComment",
    "SubmissionFeedbackAttachment",
    "RubricAssessmentEntry",
    # Files
    "FileSummary",
    "FileDetail",
    "FolderSummary",
    # Downloads
    "DownloadedFile",
    "DownloadFailure",
    "DownloadBatchResult",
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
    # Modules
    "ModuleSummary",
    "ModuleItemSummary",
    "ModuleItemDetail",
    "CompletionRequirement",
    "ContentDetails",
    # Pages
    "PageSummary",
    "PageDetail",
    # Planner
    "PlannerItem",
    "PlannerSubmissionStatus",
    # Quizzes
    "QuizSummary",
    "QuizDetail",
    # Rubrics
    "Rubric",
    "RubricCriterion",
    "RubricRating",
    # Search
    "SearchResult",
]
