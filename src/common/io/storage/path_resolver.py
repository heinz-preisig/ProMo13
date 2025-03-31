from enum import StrEnum
from pathlib import Path
from string import Template

from src.common.io import context
from src.common.io.storage import exceptions


class PathTemplateStrings(StrEnum):
    ONTOLOGY_REPOSITORY_DIR = "$repository_location/"
    ONTOLOGY_DIR = f"{ONTOLOGY_REPOSITORY_DIR}$ontology_name/"
    MODEL_LIBRARY_DIR = f"{ONTOLOGY_DIR}models/"
    MODEL_DIR = f"{MODEL_LIBRARY_DIR}$model_name/"
    INSTANTIATION_LIBRARY_DIR = f"{MODEL_DIR}instantiations/"

    ONTOLOGY_INDEX_FILE = f"{ONTOLOGY_REPOSITORY_DIR}.repository_index.json"
    MODEL_INDEX_FILE = f"{MODEL_LIBRARY_DIR}.repository_index.json"
    INSTANTIATION_INDEX_FILE = f"{INSTANTIATION_LIBRARY_DIR}.repository_index.json"
    INDEX_FILE = f"{ONTOLOGY_DIR}variables_v8.json"
    VARIABLE_FILE = f"{ONTOLOGY_DIR}variables_v8.json"
    EQUATION_FILE = f"{ONTOLOGY_DIR}variables_v8.json"


def resolve(
    io_context: context.IOContext, template_string: PathTemplateStrings
) -> Path:
    template = Template(template_string)
    path_parameters = {
        "repository_location": io_context.repository_location,
        "ontology_name": io_context.ontology_name,
        "model_name": io_context.model_name,
        "instantiation_name": io_context.instantiation_name,
    }

    _validate_parameters_for_template(template, path_parameters, io_context)

    path_string = template.substitute(path_parameters)

    return Path(path_string)


def _validate_parameters_for_template(
    template: Template, path_parameters: dict[str, str], io_context: context.IOContext
) -> None:
    template_identifiers = template.get_identifiers()
    for key, value in path_parameters.items():
        if key in template_identifiers and not value:
            error_msg = "Insufficient IOContext to access data"
            raise exceptions.IOStorageError(error_msg)
