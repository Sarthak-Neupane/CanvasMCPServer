from typing import Annotated, List, Optional

from pydantic import BaseModel, Field


class Grades(BaseModel):
    currentScore: Annotated[
        Optional[float],
        Field(
            description="Current score based on graded assignments only",
            examples=[92.5],
        ),
    ] = None
    currentGrade: Annotated[
        Optional[str],
        Field(description="Current grade (letter or scheme value)", examples=["A-"]),
    ] = None
    finalScore: Annotated[
        Optional[float],
        Field(
            description="Final score counting ungraded assignments as zero",
            examples=[85.0],
        ),
    ] = None
    finalGrade: Annotated[
        Optional[str],
        Field(description="Final grade (letter or scheme value)", examples=["B"]),
    ] = None


class GradeUserRef(BaseModel):
    id: Annotated[
        Optional[str],
        Field(alias="_id", description="The numeric Canvas ID of the user"),
    ] = None
    name: Annotated[Optional[str], Field(description="The user's name")] = None


class EnrollmentGrade(BaseModel):
    id: Annotated[
        str,
        Field(alias="_id", description="The numeric Canvas ID of the enrollment"),
    ]
    type: Annotated[
        Optional[str],
        Field(description="Enrollment type", examples=["StudentEnrollment"]),
    ] = None
    user: Annotated[
        Optional[GradeUserRef],
        Field(description="The enrolled user"),
    ] = None
    grades: Annotated[
        Optional[Grades],
        Field(description="Grades for the current grading period or course"),
    ] = None


class CourseGrades(BaseModel):
    """Grades for a course (one entry per visible student enrollment)."""

    courseId: Annotated[
        str, Field(description="The numeric Canvas ID of the course")
    ]
    courseName: Annotated[
        Optional[str], Field(description="The name of the course")
    ] = None
    enrollments: Annotated[
        List[EnrollmentGrade],
        Field(
            description=(
                "Visible student enrollments with grades. Students see only "
                "their own enrollment; teachers see all students."
            ),
        ),
    ]
