from typing import Final, TypeAlias, Union, List, Dict, Any
from mcp.server.fastmcp.tools import Tool
from ...utils import canvas_api_client, HTTPError
import base64

from ...models import CourseDetail

COURSE_RESPONSE: TypeAlias = Union[CourseDetail, Dict[str, Any]]

GRAPHQL_QUERY = """
query ($id: ID!) {
  course(id: $id) {
    _id
    id
    name
    courseCode
    state
  }
}
"""

async def get_course_by_id(course_id: str) -> Any:
    """
    Get a single Canvas course using a course_id via GraphQL.
    """
    # Q291cnNlLTEyNDQ1MDAwMDAwMDExMDE0OA== is the base64 encoded version of "Course-124450000001148"
    try:
        variables = {"id": course_id}
        response = await canvas_api_client.post_graphql_query(query=GRAPHQL_QUERY, variables=variables)
        if isinstance(response.data, dict):
            data = response.data.get("data", response.data)
        else:
            raise Exception("Response data is not a dictionary")

        course = data.get("course")
        if course is None:
            raise Exception(f"No course found for id: {course_id}")
        return CourseDetail.model_validate(course)

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


get_course_by_id_tool: Final[Tool] = Tool.from_function(
    name="get_course_by_id",
    description="Returns a single course using its ID.",
    fn=get_course_by_id,
)
