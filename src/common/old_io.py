"""
Handle data I/O

The IOHandler class stores the parameters necessary to generate the
necessary paths to access the data files. Data is retrieved by using
the IOHandler properties.

.. _usage_example:
Example:

    .. code-block:: python

      import io

      path_parameters = {'repository_path': '.', 'ontology_name': 'Test'}
      io_handler = io.IOHandler()
      io_handler.add_path_parameters(path_parameters)

      all_variables = io_handler.all_variables

Classes:
    IOHandler: Handle I/O operations

Constants:
    PathTemplates(dataclass): Templates for the paths to data files.
    AllowedPathParameters(TypedDict): Parameters used to build paths.
"""

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint as pp
from typing import ClassVar, Dict, List, Optional, Tuple, TypedDict

from src.common import old_corelib
from src.common.old_corelib.entity import EntityMap


@dataclass(frozen=True)
class PathTemplates:
    """Templates for the paths to data files"""

    # For the ontologies
    # Folders
    ONTOLOGY_REPOSITORY_DIR: ClassVar[str] = "{repository_path}/"
    ONTOLOGY_DIR: ClassVar[str] = ONTOLOGY_REPOSITORY_DIR + "{ontology_name}/"
    LATEX_DIR: ClassVar[str] = ONTOLOGY_DIR + "LaTeX/"
    MODEL_LIBRARY_DIR: ClassVar[str] = ONTOLOGY_DIR + "models/"
    MODEL_DIR: ClassVar[str] = MODEL_LIBRARY_DIR + "{model_name}/"

    # Files
    ONTOLOGY_FILE: ClassVar[str] = ONTOLOGY_DIR + "ontology.json"
    VARIABLES_FILE: ClassVar[str] = ONTOLOGY_DIR + "variables_v8.json"
    ENTITIES_FILE: ClassVar[str] = ONTOLOGY_DIR + "entities.json"
    ARC_OPTIONS_FILE: ClassVar[str] = ONTOLOGY_DIR + "arc_options.json"
    MODEL_FILE: ClassVar[str] = MODEL_DIR + "model.json"
    MODEL_FILE_FLAT: ClassVar[str] = MODEL_DIR + "model_flat.json"
    INSTANTIATION_FILE: ClassVar[str] = MODEL_DIR + "instantiation.json"
    LATEX_IMG_FILE: ClassVar[str] = LATEX_DIR + "{component_id}"

    # For the code folder
    # TODO: Move the file to a better location
    TRANSLATION_TEMPLATE_FILE: ClassVar[str] = (
        "packages/Utilities/TranslationManager"
        "/resources/language_configurations/{language}/translation_template.json"
    )


class AllowedPathParameters(TypedDict, total=False):
    """Parameters used to build paths"""

    repository_path: str
    ontology_name: str
    model_name: str
    output_language: str
    component_id: str


class IOHandler:
    """
    Handle I/O operations

    Controls the reading and writing of data files. Paths to the files are
    built using data provided by the user. This allows for a flexible
    approach to handling files in different locations.

    Check :ref:`here <usage_example>` for a usage example.
    """

    def __init__(self):
        self._path_parameters: AllowedPathParameters = {}

        # TODO: Remove this when a selection for the repository is allowed
        repo_path = str(Path("../../Ontology_Repository").resolve())
        self._path_parameters["repository_path"] = repo_path

        self._all_entities: old_corelib.EntityMap | None = None
        self._all_equations: old_corelib.EquationMap | None = None
        self._all_indices: old_corelib.IndexMap | None = None
        self._all_variables: old_corelib.VariableMap | None = None

    @property
    def all_entities(self) -> old_corelib.EntityMap | None:
        """All the entities in the ontology"""
        if self._all_entities is None:
            self._load_entity_from_file()

        return self._all_entities

    @property
    def all_equations(self) -> old_corelib.EquationMap | None:
        """All the equations in the ontology"""
        if self._all_equations is None:
            self._load_var_idx_eq_from_file()

        return self._all_equations

    @property
    def all_indices(self) -> old_corelib.IndexMap | None:
        """All the indices in the ontology"""
        if self._all_indices is None:
            self._load_var_idx_eq_from_file()

        return self._all_indices

    @property
    def all_variables(self) -> old_corelib.VariableMap | None:
        """All the variables in the ontology"""
        if self._all_variables is None:
            self._load_var_idx_eq_from_file()

        return self._all_variables

    def add_path_parameters(self, parameters: AllowedPathParameters):
        # TODO-Python3.11: change to use typing.Unpack for easier use
        # TODO This needs to change to something where we can see the parameters
        # when calling
        self._path_parameters.update(parameters)
        # pp(self._path_parameters)

    def get_imgs_paths(self, ids: list[str]) -> list[Path]:
        paths = []
        for component_id in ids:
            self.add_path_parameters({"component_id": component_id})
            paths.append(self._build_path(PathTemplates.LATEX_IMG_FILE))

        return paths

    def get_instantiation_data(self) -> dict[str, dict[tuple[str, ...], str]]:
        path = self._build_path(PathTemplates.INSTANTIATION_FILE)

        if not path.is_file():
            return {}

        with open(
            path,
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        tuples_dict = {}
        for key, dict_value in data.items():
            tuples_dict[key] = {
                ast.literal_eval(str_key): value
                for str_key, value in dict_value.items()
            }

        return tuples_dict

    def set_instantiation_data(
        self, data: dict[str, dict[tuple[str, ...], str]]
    ) -> None:
        no_tuple_dict = {}
        for key, dict_value in data.items():
            no_tuple_dict[key] = {
                str(tuple_key): value for tuple_key, value in dict_value.items()
            }

        path = self._build_path(PathTemplates.INSTANTIATION_FILE)
        with open(
            path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(no_tuple_dict, file, indent=4)

    def _build_path(self, path_template: str) -> Path:
        return Path(path_template.format(**self._path_parameters))

    def _load_var_idx_eq_from_file(
        self,
    ) -> tuple[old_corelib.VariableMap, old_corelib.IndexMap, old_corelib.EquationMap]:
        path = self._build_path(PathTemplates.VARIABLES_FILE)

        with open(
            path,
            encoding="utf-8",
        ) as file:
            data = json.load(file, cls=old_corelib.VarEqJSONDecoder)

        variables = data["variables"]
        equations = data["equations"]

        # # Loading the indices
        indices = {}
        # for idx_id, idx_info in data["indices"].items():
        #   # TODO: Go over the tokens in the indices
        #   del idx_info["tokens"]
        #   indices[idx_id] = corelib.Index(idx_id, **idx_info)

        return (variables, indices, equations)

    def _load_entity_from_file(self) -> EntityMap:
        return {}
