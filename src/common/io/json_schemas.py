REPOSITORY_INDEX_FILE = {
    "type": "array",
    "items": {"type": "string"},
}
INDEX_FILE = {
    "type": "object",
    "properties": {
        "indices": {
            "type": "object",
            "patternProperties": {
                "^I_\\d+$": {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string"},
                        "IRI": {"type": "string"},
                    },
                    "required": ["label", "IRI"],
                    "additionalProperties": True,
                }
            },
            "additionalProperties": False,
        }
    },
    "required": ["indices"],
}
