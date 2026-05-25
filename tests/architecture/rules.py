from typing import TypedDict


class LayerRule(TypedDict, total=False):
    forbidden: list[str]
    allowed: list[str]


RULES: dict[str, LayerRule] = {
    "domain": {
        "forbidden": ["application", "interfaces", "infrastructure"],
    },
    "application": {
        "forbidden": ["interfaces", "infrastructure"],
    },
    "interfaces": {
        "forbidden": ["infrastructure"],
    },
    "shared": {
        "forbidden": ["application", "interfaces", "infrastructure", "domain"],
    },
    "infrastructure": {
        "forbidden": [],
    },
}
