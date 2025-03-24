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
    "additionalProperties": True,
}
VARIABLE_FILE = {
    "type": "object",
    "properties": {
        "variables": {
            "type": "object",
            "patternProperties": {
                "^V_\\d+$": {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string"},
                        "IRI": {"type": "string"},
                        "doc": {"type": "string"},
                        "index_structures": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["label", "IRI", "doc", "index_structures"],
                    "additionalProperties": True,
                }
            },
            "additionalProperties": False,
        }
    },
    "required": ["variables"],
    "additionalProperties": True,
}
