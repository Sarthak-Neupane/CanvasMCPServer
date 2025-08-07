from enum import Enum

class DefaultView(str, Enum):
    FEED = "feed"
    WIKI = "wiki"
    MODULES = "modules"
    ASSIGNMENTS = "assignments"
    SYLLABUS = "syllabus"

