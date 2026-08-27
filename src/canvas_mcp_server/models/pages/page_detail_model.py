from typing import Annotated, Optional

from pydantic import Field

from ..common.untrusted_content import UntrustedContentMixin
from .page_summary_model import PageSummary


class PageDetail(PageSummary, UntrustedContentMixin):
    """Full wiki page content including HTML body and optional plain text."""

    body: Annotated[
        Optional[str],
        Field(description="Page content as HTML"),
    ] = None
    body_text: Annotated[
        Optional[str],
        Field(
            description=(
                "Plain-text version of body (script/style stripped). "
                "Populated by get_page when body HTML is present."
            ),
        ),
    ] = None
