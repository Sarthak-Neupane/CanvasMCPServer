from typing import Final, Optional, List, Dict, Any, Union, TypeAlias
from mcp.server.fastmcp.tools import Tool
from ...utils import canvas_api_client, HTTPError
from typing import Annotated
from pydantic import Field
import json

from .models import CoursesQueryParams, Course
from .constants import EnrollmentType, EnrollmentState, WorkflowState, CourseDisplayField, CoursesInclude

COURSE_DETAILED_FIELDS = [
    CourseDisplayField.ID,
    CourseDisplayField.NAME,
    CourseDisplayField.COURSE_CODE,
    CourseDisplayField.WORKFLOW_STATE,
    CourseDisplayField.START_AT,
    CourseDisplayField.END_AT,
    CourseDisplayField.ENROLLMENT_TERM_ID,
    CourseDisplayField.DEFAULT_VIEW,
]

# Type alias for course display fields
CoursesResponse: TypeAlias = Union[List[Dict[str, Any]], Dict[str, Any]]

def filter_course_fields(
    courses: List[Course], 
    display_fields: Optional[List[CourseDisplayField]] = COURSE_DETAILED_FIELDS
) -> List[Dict[str, Any]]:
    """
    Filter course data to include only specified fields.
    
    Args:
        courses: List of course dictionaries from Canvas API
        display_fields: List of fields to include in output (None = all fields)
        
    Returns:
        List[Dict[str, Any]]: Filtered course data with only requested fields
    """

    field_names = [field.value for field in (display_fields or COURSE_DETAILED_FIELDS)]
    filtered_courses = [
        {field_name: getattr(course, field_name, None) for field_name in field_names}
        for course in courses
    ]
    return filtered_courses

async def get_courses(
    query: CoursesQueryParams,
    display_fields: Optional[List[CourseDisplayField]] = None,
    limit: Annotated[Optional[int], Field(
        description="Maximum number of courses to return. If not specified, returns all available courses.",
        ge=1,
        le=1000
    )] = None,
    per_page: Annotated[int, Field(
        description="Number of courses per API request (1-100, default: 50)",
        ge=1, 
        le=100
    )] = 50
) -> CoursesResponse:
    """
    Get Canvas courses with pagination and customizable field display.
    
    This tool automatically handles pagination and allows you to specify exactly which
    course fields you want to see, making responses cleaner and more focused.
    
    **Field Selection Examples:**
    - `display_fields=["id", "name", "course_code"]` → Just the basics
    - `display_fields=["id", "name", "total_students", "start_at"]` → Course overview with stats
    - No display_fields → All available course data
    
    **Smart Behavior:**
    - Without `limit`: Returns ALL courses (auto-pagination)
    - With `limit=20`: Returns exactly 20 courses maximum
    - Field filtering eliminates response truncation issues
    - Automatically stops when no more courses available
    
    Args:
        query: Query parameters for retrieving courses. Accepts CoursesQueryParams
        display_fields: Specific fields to show in response (improves readability)
        limit: Maximum courses to return (omit for all courses)
        per_page: Courses per API request (affects performance)
        
    Returns:
        List[Dict[str, Any]]: List of filtered course objects.
            OR
        Dict[str, Any]: Error object with "error", "message", and "status_code" keys.
    """
    try:
        # Create and validate query parameters
        query_params = CoursesQueryParams(
            enrollment_type=query.enrollment_type or EnrollmentType.STUDENT,
            enrollment_state=query.enrollment_state or EnrollmentState.ACTIVE,
            include=query.include or [],
            exclude_blueprint_courses= query.exclude_blueprint_courses or False,
            state=query.state or WorkflowState.AVAILABLE
        )
        
        params_dict = query_params.model_dump(exclude_none=True)
        
        # Determine pagination strategy
        if limit is None:
            # No limit specified - get ALL courses with reasonable pagination
            max_pages = 20  # Reasonable limit to prevent infinite loops
            courses = await canvas_api_client.get_paginated_data(
                endpoint="courses",
                params=params_dict,
                max_pages=max_pages,
                per_page=per_page
            )
            pagination_info = f"Retrieved all available courses (up to {max_pages} pages)"
            
        elif limit <= per_page:
            # Small limit - single API call is sufficient
            params_dict['per_page'] = limit
            response = await canvas_api_client.get_canvas_data(
                endpoint="courses", 
                params=params_dict
            )
            
            if isinstance(response.data, list):
                courses = response.data[:limit]  
            elif isinstance(response.data, dict):
                courses = [response.data]
            else:
                courses = []
            
            pagination_info = f"Single request for {limit} courses"
            
        else:
            # Large limit - use pagination but stop at limit
            max_pages = (limit // per_page) + (1 if limit % per_page > 0 else 0)
            all_courses = await canvas_api_client.get_paginated_data(
                endpoint="courses",
                params=params_dict,
                max_pages=max_pages,
                per_page=per_page
            )
            courses = all_courses[:limit]  # Trim to exact limit
            pagination_info = f"Paginated request, limited to {limit} courses"
        
        # Apply field filtering
        course_models = [Course.model_validate(c) for c in courses]
        filtered_courses = filter_course_fields(course_models, display_fields)
        
        # Format and return response
        return filtered_courses
        
    except HTTPError as e:
        return {
            "error": "HTTP Error",
            "message": str(e),
            "status_code": e.status_code
        }
    except Exception as e:
        return {
            "error": "Unexpected Error",
            "message": str(e)
        }


# Export the enhanced tool
get_all_courses_tool: Final[Tool] = Tool.from_function(
    name="get_all_courses",
    description="Get Canvas courses with intelligent pagination and customizable field display. Specify display_fields to see only the course information you need, eliminating response clutter.",
    fn=get_courses,
)