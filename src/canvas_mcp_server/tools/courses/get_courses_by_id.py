"""Tool for fetching a single Canvas course via the GraphQL API."""

from typing import Annotated, Any, Dict, Final, TypeAlias, Union

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...errors import as_tool_error
from ...models import CourseDetail
from ...utils import canvas_api_client

CourseResponse: TypeAlias = Union[CourseDetail, Dict[str, Any]]

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


async def get_course_by_id(
    course_id: Annotated[
        str,
        Field(
            description=(
                "The course ID. Accepts either the numeric Canvas ID "
                "(e.g. '123456') or the GraphQL global ID."
            ),
        ),
    ],
) -> CourseResponse:
    """
    Get a single Canvas course by its ID via GraphQL.

    Returns course details (id, name, course code, state),
    or an error object with "error", "message", and optionally "status_code" keys.
    """
    try:
        variables = {"id": course_id}
        response = await canvas_api_client.post_graphql_query(
            query=GRAPHQL_QUERY, variables=variables
        )
        if not isinstance(response.data, dict):
            raise Exception("Response data is not a dictionary")
        data = response.data.get("data", response.data)

        course = data.get("course")
        if course is None:
            raise Exception(f"No course found for id: {course_id}")
        return CourseDetail.model_validate(course)

    except Exception as e:
        return as_tool_error(e, source="canvas_graphql")


get_course_by_id_tool: Final[Tool] = Tool.from_function(
    name="get_course_by_id",
    description=(
        "Get detailed information about a single Canvas course by its ID "
        "(numeric or GraphQL global ID)."
    ),
    fn=get_course_by_id,
)
