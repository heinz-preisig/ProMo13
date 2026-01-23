"""A simple wrapper class for variables and equations to be used in list models."""


class SimpleVar:
    """A simple wrapper class for variables and equations to be used in list models."""

    # Class variable to store the model reference
    _model = None
    _debug = True  # Enable debug output

    def __init__(self, var_id, model=None):
        self._id = var_id
        self._equation = None
        self._variable = None
        self._model = model or SimpleVar._model

        if self._debug:
            print(f"[SimpleVar] Created with ID: {var_id}, Model: {model is not None}")

    @property
    def var_id(self):
        return self._id

    def get_id(self):
        return self._id

    def get_img_path(self):
        """Get the image path for this variable/equation."""
        if self._debug:
            print(f"[SimpleVar] Getting image path for ID: {self._id}")
            print(f"[SimpleVar] Model available: {self._model is not None}")

        # First try to get the model from instance, then from class
        model = self._model or SimpleVar._model

        if model:
            if self._debug:
                print(f"[SimpleVar] Model has all_equations: {hasattr(model, 'all_equations')}")
                print(f"[SimpleVar] Model has all_variables: {hasattr(model, 'all_variables')}")

            # Check if this is an equation
            if hasattr(model, 'all_equations') and self._id in model.all_equations:
                self._equation = model.all_equations.get(self._id)
                if hasattr(self._equation, 'get_img_path') and callable(self._equation.get_img_path):
                    path = self._equation.get_img_path()
                    if self._debug:
                        print(f"[SimpleVar] Found equation image path: {path}")
                    return path

            # Check if this is a variable
            if hasattr(model, 'all_variables') and self._id in model.all_variables:
                self._variable = model.all_variables.get(self._id)
                if hasattr(self._variable, 'get_img_path') and callable(self._variable.get_img_path):
                    path = self._variable.get_img_path()
                    if self._debug:
                        print(f"[SimpleVar] Found variable image path: {path}")
                    return path

        # Default fallback
        default_path = ":/icons/equation.png" if self._id and 'eq_' in self._id else ":/icons/variable.png"
        if self._debug:
            print(f"[SimpleVar] Using default image path: {default_path}")
        return default_path

    def get_display_text(self):
        """Return a more detailed display text for the variable/equation."""
        # Try to get the equation or variable details if they exist in the model
        model = self._model or SimpleVar._model

        if model:
            if not self._equation and self._id in getattr(model, 'all_equations', {}):
                self._equation = model.all_equations.get(self._id)
            if not self._variable and self._id in getattr(model, 'all_variables', {}):
                self._variable = model.all_variables.get(self._id)

        if self._equation:
            return f"{self._id}: {self._equation.equation if hasattr(self._equation, 'equation') else 'No equation'}"
        elif self._variable:
            return f"{self._id}: {self._variable.value if hasattr(self._variable, 'value') else 'No value'}"
        return self._id

    def __repr__(self):
        return f"SimpleVar({self._id})"

    @classmethod
    def set_model(cls, model):
        """Set the model reference for all SimpleVar instances."""
        cls._model = model
