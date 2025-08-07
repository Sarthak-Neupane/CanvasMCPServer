from typing import Final, List, Dict, Any, Union, TypeAlias
from mcp.server.fastmcp.tools import Tool
from ...utils import canvas_api_client, HTTPError
from pydantic import Field

from ...models import CourseSummary

# Type alias for course display fields
CoursesResponse: TypeAlias = Union[List[CourseSummary], Dict[str, Any]]

GRAPHQL_QUERY = """
query {
  allCourses {
    id
    name
    courseCode
    state
  }
}
"""

async def get_all_courses() -> CoursesResponse:
    """
    Get all Canvas courses with only summary fields via GraphQL.
    """
    try:
        response = await canvas_api_client.post_graphql_query(GRAPHQL_QUERY)
        if isinstance(response.data, dict):
            data = response.data.get("data", response.data)
        else:
            raise Exception("Response data is not a dictionary")

        course_list = data["allCourses"]
        courses = [CourseSummary.model_validate(course) for course in course_list]
        return courses

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
    fn=get_all_courses,
)