from typing import Final, Optional, List, Dict, Any
from mcp.server.fastmcp.tools import Tool
from ...utils import canvas_api_client, HTTPError
from .types import CoursesQueryParams, EnrollmentType, EnrollmentState, CoursesInclude, CourseState, CourseDisplayField, DETAILED_FIELDS
from typing import Annotated
from pydantic import Field
from enum import Enum
import json


def filter_course_fields(
    courses: List[Dict[str, Any]], 
    display_fields: Optional[List[CourseDisplayField]] = DETAILED_FIELDS
) -> List[Dict[str, Any]]:
    """
    Filter course data to include only specified fields.
    
    Args:
        courses: List of course dictionaries from Canvas API
        display_fields: List of fields to include in output (None = all fields)
        
    Returns:
        List[Dict[str, Any]]: Filtered course data with only requested fields
    """
    if not display_fields:
        return courses  # Return all fields if none specified
    
    field_names = [field.value for field in display_fields]
    filtered_courses = []
    
    for course in courses:
        filtered_course = {}
        for field_name in field_names:
            if field_name in course:
                filtered_course[field_name] = course[field_name]
            else:
                # Field not present in response - could be because:
                # 1. Not included in API request (e.g., total_students without include)
                # 2. Field doesn't exist for this course
                # 3. Permission issue
                filtered_course[field_name] = None
        
        filtered_courses.append(filtered_course)
    
    return filtered_courses


def format_course_response(
    courses: List[Dict[str, Any]],
    query_params: CoursesQueryParams,
    display_fields: Optional[List[CourseDisplayField]],
    pagination_info: str,
    per_page: int
) -> str:
    """
    Format the course response with field filtering and smart display.
    
    Args:
        courses: Filtered course data
        query_params: Query parameters used
        display_fields: Fields that were selected for display
        pagination_info: Information about pagination
        per_page: Courses per page setting
        
    Returns:
        str: Formatted response string
    """
    result = f"Canvas Courses: {len(courses)} courses found\n\n"
    
    # Add search criteria if any were used
    search_criteria = query_params.model_dump(exclude_none=True)
    if search_criteria:
        result += f"Search Criteria:\n{json.dumps(search_criteria, indent=2, default=str)}\n\n"
    
    # Add field selection info
    if display_fields:
        field_names = [field.value for field in display_fields]
        result += f"Display Fields ({len(field_names)}):\n"
        result += f"  {', '.join(field_names)}\n\n"
    else:
        result += "Display Fields: All available fields\n\n"
    
    # Add pagination info
    result += f"Retrieval Info: {pagination_info}\n"
    result += f"Per page: {per_page}\n\n"
    
    # Add course data
    if courses:
        # With field filtering, we can show more courses without truncation
        if len(courses) <= 10:
            # Show all courses if 10 or fewer
            result += f"Course Details:\n"
            result += json.dumps(courses, indent=2, default=str)
        else:
            # Show first 5 in detail, then summary for the rest
            result += f"Detailed View (first 5 courses):\n"
            result += json.dumps(courses[:5], indent=2, default=str) + "\n\n"
            
            # Show summary of remaining courses
            result += f"Summary of Remaining {len(courses) - 5} Courses:\n"
            for i, course in enumerate(courses[5:], 6):
                course_id = course.get('id', 'Unknown')
                course_name = course.get('name', 'Unnamed Course')
                course_code = course.get('course_code', 'No Code')
                result += f"  {i}. {course_name} ({course_code}) [ID: {course_id}]\n"
                
                # Limit summary to 20 more courses
                if i >= 25:
                    remaining = len(courses) - 25
                    result += f"  ... and {remaining} more courses\n"
                    break
    else:
        result += "No courses found matching the specified criteria.\n"
        result += "\n💡 Suggestions:\n"
        result += "  - Try without filters to see all courses\n"
        result += "  - Check if enrollment_state='active' excludes completed courses\n"
        result += "  - Verify your Canvas API permissions\n"
    
    return result


async def get_courses(
    enrollment_type: Annotated[Optional[EnrollmentType], Field(
        description="Filter by enrollment type (teacher, student, ta, observer, designer)"
    )] = EnrollmentType.STUDENT,
    enrollment_state: Annotated[Optional[EnrollmentState], Field(
        description="Filter by enrollment state (active, invited_or_pending, completed)"
    )] = EnrollmentState.ACTIVE,
    exclude_blueprint_courses: Annotated[Optional[bool], Field(
        description="Exclude courses configured as blueprint courses"
    )] = None,
    include: Annotated[Optional[List[CoursesInclude]], Field(
        description="Additional information to include (sections, teachers, total_students, etc.)"
    )] = None,
    state: Annotated[Optional[List[CourseState]], Field(
        description="Filter by course workflow state (available, completed, etc.)"
    )] = None,
    display_fields: Annotated[Optional[List[CourseDisplayField]], Field(
        description="Specific course fields to display. Use 'essential' for id/name/code/state, 'detailed' for common fields, 'administrative' for admin fields, or specify individual fields. If not specified, all fields are shown."
    )] = DETAILED_FIELDS,
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
) -> str:
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
        enrollment_type: Filter by your role in the course
        enrollment_state: Filter by enrollment status
        exclude_blueprint_courses: Exclude template courses
        include: Additional data to include in API response
        state: Filter by course publication state
        display_fields: Specific fields to show in response (improves readability)
        limit: Maximum courses to return (omit for all courses)
        per_page: Courses per API request (affects performance)
        
    Returns:
        str: Formatted list of courses with only requested fields displayed
    """
    try:
        # Create and validate query parameters
        query_params = CoursesQueryParams(
            enrollment_type=enrollment_type,
            enrollment_state=enrollment_state,
            include=include or [],
            exclude_blueprint_courses=exclude_blueprint_courses,
            state=state or []
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
                courses = response.data[:limit]  # Ensure exact limit
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
        filtered_courses = filter_course_fields(courses, display_fields)
        
        # Format and return response
        return format_course_response(
            courses=filtered_courses,
            query_params=query_params,
            display_fields=display_fields,
            pagination_info=pagination_info,
            per_page=per_page
        )
        
    except HTTPError as e:
        return f"Canvas API Error: {e}"
    except Exception as e:
        return f"Unexpected error getting courses: {e}"


# Export the enhanced tool
get_courses_tool: Final[Tool] = Tool.from_function(
    name="get_courses",
    description="Get Canvas courses with intelligent pagination and customizable field display. Specify display_fields to see only the course information you need, eliminating response clutter.",
    fn=get_courses,
)