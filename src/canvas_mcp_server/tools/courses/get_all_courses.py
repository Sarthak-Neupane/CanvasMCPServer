from typing import Final, Optional, List, Dict, Any, Union, TypeAlias
from mcp.server.fastmcp.tools import Tool
from ...utils import canvas_api_client, HTTPError
from typing import Annotated
from pydantic import Field

from .models import CoursesQueryParams, Course
from .constants import EnrollmentType, EnrollmentState, WorkflowState


# Type alias for course display fields
CoursesResponse: TypeAlias = Union[List[Course], Dict[str, Any]]

async def get_courses(
    query: CoursesQueryParams,
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
    Get Canvas courses with pagination.
    
    This tool automatically handles pagination and supports the Canvas `include` parameter to request extra course fields/relations, making responses cleaner and more focused.

    **Smart Behavior:**
    - Without `limit`: Returns ALL courses (auto-pagination)
    - With `limit=20`: Returns exactly 20 courses maximum
    - Automatically stops when no more courses available

    Args:
        query: Query parameters for retrieving courses (including Canvas 'include' options)
        limit: Maximum courses to return (omit for all courses)
        per_page: Courses per API request (affects performance)

    Returns:
        List[Course]: List of Course models.
        OR
        Dict[str, Any]: Error object with "error", "message", and "status_code" keys.
    """
    try:
        query_params = CoursesQueryParams(
            enrollment_type=query.enrollment_type or EnrollmentType.STUDENT,
            enrollment_state=query.enrollment_state or EnrollmentState.ACTIVE,
            include=query.include or [],
            exclude_blueprint_courses= query.exclude_blueprint_courses or False,
            state=query.state or WorkflowState.AVAILABLE
        )
        
        params_dict = query_params.model_dump(exclude_none=True)
        
        if limit is None:
            max_pages = 20
            courses = await canvas_api_client.get_paginated_data(
                endpoint="courses",
                params=params_dict,
                max_pages=max_pages,
                per_page=per_page
            )
        elif limit <= per_page:
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
        else:
            max_pages = (limit // per_page) + (1 if limit % per_page > 0 else 0)
            all_courses = await canvas_api_client.get_paginated_data(
                endpoint="courses",
                params=params_dict,
                max_pages=max_pages,
                per_page=per_page
            )
            courses = all_courses[:limit]
        
        course_models = [Course.model_validate(c) for c in courses]
        return course_models
        
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