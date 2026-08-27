"""Sample Canvas assignment rubric REST payloads."""

ASSIGNMENT_WITH_RUBRIC_REST = {
    "id": 200001,
    "name": "Essay 1",
    "use_rubric_for_grading": True,
    "rubric_settings": {"points_possible": "12"},
    "rubric": [
        {
            "id": "crit1",
            "description": "Thesis",
            "long_description": "Clear thesis statement",
            "points": 6.0,
            "criterion_use_range": False,
            "ratings": [
                {
                    "id": "rat1",
                    "criterion_id": "crit1",
                    "description": "Excellent",
                    "long_description": "Thesis is clear and compelling",
                    "points": 6.0,
                },
                {
                    "id": "rat2",
                    "criterion_id": "crit1",
                    "description": "Needs work",
                    "long_description": "Thesis is vague",
                    "points": 3.0,
                },
            ],
        },
        {
            "id": "crit2",
            "description": "Evidence",
            "points": 6.0,
            "ratings": [
                {
                    "id": "rat3",
                    "criterion_id": "crit2",
                    "description": "Strong",
                    "points": 6.0,
                }
            ],
        },
    ],
}

ASSIGNMENT_WITHOUT_RUBRIC_REST = {
    "id": 200002,
    "name": "Homework 2",
    "rubric": None,
}
