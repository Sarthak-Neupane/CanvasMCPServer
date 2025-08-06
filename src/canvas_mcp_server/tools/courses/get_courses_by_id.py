from typing import Final
from mcp.server.fastmcp.tools import Tool
from ...utils import canvas_api_client, HTTPError
from .models import Course, PerCourseQueryParams


async def get_courses_by_id(query: PerCourseQueryParams) -> Course:
    query_params = PerCourseQueryParams(
        course_id=query.course_id,
        include=query.include or []
    )
    response = await canvas_api_client.get_canvas_data(
        endpoint=f"courses/{query.course_id}",
        params=query_params.to_dict()
    )
    if response.status_code != 200:
        raise HTTPError(f"Failed to retrieve course {query.course_id}: {response}")

    return Course.model_validate(response.data)


# Export the enhanced tool
get_course_by_id_tool: Final[Tool] = Tool.from_function(
    name="get_course_by_id",
    description="Returns a single course using its ID.",
    fn=get_courses_by_id,
)
