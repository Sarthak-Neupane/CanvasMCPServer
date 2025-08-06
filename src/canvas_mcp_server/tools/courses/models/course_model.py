from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Annotated
from enum import Enum
from datetime import datetime

from .course_term_model import Term
from .course_progress_model import CourseProgress
from .course_calendar_model import CalendarLink
from ..constants import DefaultView, WorkflowState

class GradingPeriod(BaseModel):
    pass


class Enrollment(BaseModel):
    pass

class Course(BaseModel):
    id: Annotated[
        int, Field(description="the unique identifier for the course", example=370663)
    ]
    name: Annotated[
        str,
        Field(description="the full name of the course", example="InstructureCon 2012"),
    ]
    course_code: Annotated[
        str, Field(description="the course code", example="INSTCON12")
    ]
    workflow_state: Annotated[
        WorkflowState,
        Field(description="the current state of the course", example="available"),
    ]
    account_id: Annotated[
        int, Field(description="the account associated with the course", example=81259)
    ]
    root_account_id: Annotated[
        int,
        Field(description="the root account associated with the course", example=81259),
    ]
    enrollment_term_id: Annotated[
        int,
        Field(description="the enrollment term associated with the course", example=34),
    ]

    sis_course_id: Annotated[
        Optional[str],
        Field(description="the SIS identifier for the course, if defined."),
    ] = None
    uuid: Annotated[
        Optional[str],
        Field(
            description="the UUID of the course",
            example="WvAHhY5FINzq5IyRIJybGeiXyFkG3SqHUPb7jZY5",
        ),
    ] = None
    integration_id: Annotated[
        Optional[str],
        Field(description="the integration identifier for the course, if defined."),
    ] = None
    sis_import_id: Annotated[
        Optional[int],
        Field(description="the unique identifier for the SIS import.", example=34),
    ] = None
    original_name: Annotated[
        Optional[str],
        Field(
            description="the actual course name (if nickname is set).",
            example="InstructureCon-2012-01",
        ),
    ] = None
    grading_periods: Annotated[
        Optional[List[GradingPeriod]],
        Field(description="A list of grading periods associated with the course"),
    ] = None
    grading_standard_id: Annotated[
        Optional[int],
        Field(
            description="the grading standard associated with the course", example=25
        ),
    ] = None
    grade_passback_setting: Annotated[
        Optional[str],
        Field(
            description="the grade_passback_setting set on the course",
            example="nightly_sync",
        ),
    ] = None
    created_at: Annotated[
        Optional[datetime],
        Field(
            description="the date the course was created",
            example="2012-05-01T00:00:00-06:00",
        ),
    ] = None
    start_at: Annotated[
        Optional[datetime],
        Field(
            description="the start date for the course",
            example="2012-06-01T00:00:00-06:00",
        ),
    ] = None
    end_at: Annotated[
        Optional[datetime],
        Field(
            description="the end date for the course",
            example="2012-09-01T00:00:00-06:00",
        ),
    ] = None
    locale: Annotated[
        Optional[str], Field(description="the course-set locale", example="en")
    ] = None
    enrollments: Annotated[
        Optional[List[Enrollment]],
        Field(
            description="A list of enrollments linking the current user to the course"
        ),
    ] = None
    total_students: Annotated[
        Optional[int],
        Field(
            description="the total number of active and invited students in the course",
            example=32,
        ),
    ] = None
    calendar: Annotated[
        Optional[CalendarLink], Field(description="course calendar")
    ] = None
    default_view: Annotated[
        Optional[DefaultView],
        Field(
            description="the type of page that users will see when they first visit the course",
            example="feed",
        ),
    ] = None
    syllabus_body: Annotated[
        Optional[str],
        Field(
            description="user-generated HTML for the course syllabus",
            example="<p>syllabus html goes here</p>",
        ),
    ] = None
    needs_grading_count: Annotated[
        Optional[int],
        Field(description="the number of submissions needing grading", example=17),
    ] = None
    term: Annotated[
        Optional[Term], Field(description="the enrollment term object for the course")
    ] = None
    course_progress: Annotated[
        Optional[CourseProgress],
        Field(description="information on progress through the course"),
    ] = None
    apply_assignment_group_weights: Annotated[
        Optional[bool],
        Field(
            description="weight final grade based on assignment group percentages",
            example=True,
        ),
    ] = None
    permissions: Annotated[
        Optional[Dict[str, bool]],
        Field(description="the permissions the user has for the course"),
    ] = None
    is_public: Annotated[Optional[bool], Field(example=True)] = None
    is_public_to_auth_users: Annotated[Optional[bool], Field(example=True)] = None
    public_syllabus: Annotated[Optional[bool], Field(example=True)] = None
    public_syllabus_to_auth: Annotated[Optional[bool], Field(example=True)] = None
    public_description: Annotated[
        Optional[str],
        Field(
            description="the public description of the course",
            example="Come one, come all to InstructureCon 2012!",
        ),
    ] = None
    storage_quota_mb: Annotated[Optional[int], Field(example=5)] = None
    storage_quota_used_mb: Annotated[Optional[float], Field(example=5)] = None
    hide_final_grades: Annotated[Optional[bool], Field(example=False)] = None
    license: Annotated[Optional[str], Field(example="Creative Commons")] = None
    allow_student_assignment_edits: Annotated[Optional[bool], Field(example=False)] = (
        None
    )
    allow_wiki_comments: Annotated[Optional[bool], Field(example=False)] = None
    allow_student_forum_attachments: Annotated[Optional[bool], Field(example=False)] = (
        None
    )
    open_enrollment: Annotated[Optional[bool], Field(example=True)] = None
    self_enrollment: Annotated[Optional[bool], Field(example=False)] = None
    restrict_enrollments_to_course_dates: Annotated[
        Optional[bool], Field(example=False)
    ] = None
    course_format: Annotated[Optional[str], Field(example="online")] = None
    access_restricted_by_date: Annotated[
        Optional[bool],
        Field(
            description="if this user is currently prevented from viewing the course",
            example=False,
        ),
    ] = None
    time_zone: Annotated[
        Optional[str],
        Field(
            description="The course's IANA time zone name.", example="America/Denver"
        ),
    ] = None
    blueprint: Annotated[
        Optional[bool],
        Field(
            description="whether the course is set as a Blueprint Course", example=True
        ),
    ] = None
    blueprint_restrictions: Annotated[
        Optional[Dict[str, bool]],
        Field(description="Set of restrictions applied to all locked course objects"),
    ] = None
    blueprint_restrictions_by_object_type: Annotated[
        Optional[Dict[str, Dict[str, bool]]],
        Field(description="Sets of restrictions differentiated by object type"),
    ] = None
    template: Annotated[
        Optional[bool],
        Field(description="whether the course is set as a template", example=True),
    ] = None
