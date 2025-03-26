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
EQUATION_FILE = {
    "type": "object",
    "properties": {
        "variables": {
            "type": "object",
            "patternProperties": {
                "^V_\\d+$": {
                    "type": "object",
                    "properties": {
                        "equations": {
                            "type": "object",
                            "patternProperties": {
                                "^E_\\d+$": {
                                    "type": "object",
                                    "properties": {
                                        "rhs": {
                                            "type": "object",
                                            "properties": {
                                                "global_ID": {"type": "string"},
                                                "latex": {"type": "string"},
                                            },
                                            "required": ["global_ID"],
                                            "additionalProperties": True,
                                        }
                                    },
                                    "additionalProperties": True,
                                }
                            },
                            "additionalProperties": False,
                            "minProperties": 0,
                        }
                    },
                    "required": ["equations"],
                    "additionalProperties": True,
                }
            },
            "additionalProperties": False,
        }
    },
    "required": ["variables"],
    "additionalProperties": True,
}
