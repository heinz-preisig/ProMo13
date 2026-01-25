

```python
class EntityDict(TypedDict):
    """Creates a new type for a dictionary that stores an entity."""
    index_set: str
    integrators: Dict[str, str]
    var_eq_forest: List[Dict[str, List[str]]]
    init_vars: List[str]
    input_vars: List[str]
    output_vars: List[str]
```

```python
class Entity():
    """Models an entity."""

    # TODO Add an explanation of what is an entity.
    # TODO: PRobably add fields for network, type, etc

    def __init__(
            self,
            entity_name: str,
            all_equations: Dict[str, equation.Equation],
            index_set: Optional[str] = None,
            integrators: Optional[Dict[str, str]] = None,
            var_eq_forest: Optional[List[Dict[str, List[str]]]] = None,
            init_vars: Optional[List[str]] = None,
            input_vars: Optional[List[str]] = None,
            output_vars: Optional[List[str]] = None,
            ) -> None:
```

