from enum import StrEnum
from pathlib import Path
from string import Template

from . import exceptions
from .context import IOContext


class PathTemplateStrings(StrEnum):
    ONTOLOGY_REPOSITORY_DIR = "$repository_location/"
    ONTOLOGY_DIR = ONTOLOGY_REPOSITORY_DIR + "$ontology_name/"
    MODEL_LIBRARY_DIR = ONTOLOGY_DIR + "models/"
    MODEL_DIR = MODEL_LIBRARY_DIR + "$model_name/"
    INSTANTIATION_LIBRARY_DIR = MODEL_DIR + "instantiations/"

    ONTOLOGY_INDEX_FILE = ONTOLOGY_REPOSITORY_DIR + ".repository_index.json"
    MODEL_INDEX_FILE = MODEL_LIBRARY_DIR + ".repository_index.json"
    INSTANTIATION_INDEX_FILE = INSTANTIATION_LIBRARY_DIR + ".repository_index.json"


def resolve(ontology_context: IOContext, template_string: PathTemplateStrings) -> Path:
    template = Template(template_string)
    path_parameters = {
        "repository_location": ontology_context.repository_location,
        "ontology_name": ontology_context.ontology_name,
        "model_name": ontology_context.model_name,
        "instantiation_name": ontology_context.instantiation_name,
    }

    _validate_parameters_for_template(template, path_parameters)

    path_string = template.substitute(path_parameters)

    return Path(path_string)


def _validate_parameters_for_template(
    template: Template, path_parameters: dict[str, str]
) -> None:
    template_identifiers = template.get_identifiers()
    for key, value in path_parameters.items():
        if key in template_identifiers and not value:
            error_msg = "Insufficient data in IOContext"
            raise exceptions.IOContextError(error_msg)
