import json
import logging
import typing
from abc import ABC, abstractmethod
from pathlib import Path

import jsonschema

from . import exceptions, json_schemas, path_resolver
from .context import IOContext

logger = logging.getLogger(__name__)


class BaseJsonFileReader(ABC):
    _template_string: path_resolver.PathTemplateStrings
    _access_err_msg: str
    _corrupted_err_msg: str
    _schema: dict[str, typing.Any]

    def __init__(self, context: IOContext) -> None:
        self._context = context

    def read(self) -> typing.Any:
        content = self._get_file_content()
        json_data = self._convert_content_to_json(content)
        self._validate_json(json_data)
        filtered_data = self._filter_data(json_data)

        return filtered_data

    def _get_file_content(self) -> str:
        file_path = path_resolver.resolve(self._context, self._template_string)

        return self._read_file(file_path)

    def _read_file(self, file_path: Path) -> str:
        try:
            with file_path.open("r") as file:
                file_content = file.read()
        except (FileNotFoundError, PermissionError) as err:
            logger.error(err)
            raise exceptions.DataIOError(self._access_err_msg) from err

        return file_content

    def _convert_content_to_json(self, content: str) -> typing.Any:
        try:
            data = json.loads(content)
        except json.JSONDecodeError as err:
            logger.error(err)
            raise exceptions.DataIOError(self._corrupted_err_msg) from err

        return data

    def _validate_json(self, data: typing.Any) -> None:
        try:
            jsonschema.validate(data, self._schema)
        except jsonschema.ValidationError as err:
            logger.error(err)
            raise exceptions.DataIOError(self._corrupted_err_msg) from err

    @abstractmethod
    def _filter_data(self, data: typing.Any) -> typing.Any:
        pass


class OntologyRepositoryIndexFileReader(BaseJsonFileReader):
    _template_string = path_resolver.PathTemplateStrings.ONTOLOGY_INDEX_FILE
    _access_err_msg = "Can not access ontology repository index"
    _corrupted_err_msg = "Corrupted ontology repository index"
    _schema = json_schemas.REPOSITORY_INDEX_FILE

    def _filter_data(self, data: typing.Any) -> typing.Any:
        return data


class ModelRepositoryIndexFileReader(BaseJsonFileReader):
    _template_string = path_resolver.PathTemplateStrings.MODEL_INDEX_FILE
    _access_err_msg = "Can not access model repository index"
    _corrupted_err_msg = "Corrupted model repository index"
    _schema = json_schemas.REPOSITORY_INDEX_FILE

    def _filter_data(self, data: typing.Any) -> typing.Any:
        return data


class InstantiationRepositoryIndexFileReader(BaseJsonFileReader):
    _template_string = path_resolver.PathTemplateStrings.INSTANTIATION_INDEX_FILE
    _access_err_msg = "Can not access instantiation repository index"
    _corrupted_err_msg = "Corrupted instantiation repository index"
    _schema = json_schemas.REPOSITORY_INDEX_FILE

    def _filter_data(self, data: typing.Any) -> typing.Any:
        return data


class IndexFileReader(BaseJsonFileReader):
    _template_string = path_resolver.PathTemplateStrings.INDEX_FILE
    _access_err_msg = "Can not access index data"
    _corrupted_err_msg = "Corrupted index data"
    _schema = json_schemas.INDEX_FILE

    def _filter_data(self, data: typing.Any) -> typing.Any:
        cleaned_data = []
        for idx_id, idx_data in data["indices"].items():
            new_index_data = {"identifier": idx_id}
            new_index_data["iri"] = idx_data["IRI"]
            new_index_data["label"] = idx_data["label"]
            cleaned_data.append(new_index_data)

        return cleaned_data


class VariableFileReader(BaseJsonFileReader):
    _template_string = path_resolver.PathTemplateStrings.VARIABLE_FILE
    _access_err_msg = "Can not access variable data"
    _corrupted_err_msg = "Corrupted variable data"
    _schema = json_schemas.VARIABLE_FILE

    def _filter_data(self, data: typing.Any) -> typing.Any:
        cleaned_data = []
        for var_id, var_data in data["variables"].items():
            new_variable_data = {"identifier": var_id}
            new_variable_data["iri"] = var_data["IRI"]
            new_variable_data["label"] = var_data["label"]
            new_variable_data["doc"] = var_data["doc"]
            new_variable_data["indices"] = var_data["index_structures"]

            cleaned_data.append(new_variable_data)

        return cleaned_data


class EquationFileReader(BaseJsonFileReader):
    _template_string = path_resolver.PathTemplateStrings.EQUATION_FILE
    _access_err_msg = "Can not access equation data"
    _corrupted_err_msg = "Corrupted equation data"
    _schema = json_schemas.EQUATION_FILE

    def _filter_data(self, data: typing.Any) -> typing.Any:
        cleaned_data = []
        for var_id, var_data in data["variables"].items():
            for eq_id, eq_data in var_data["equations"].items():
                new_equation_data = {"identifier": eq_id}
                rhs_variables = self._parse_variables_from_rhs(
                    eq_data["rhs"]["global_ID"]
                )

                new_equation_data["variables"] = [var_id] + rhs_variables

                cleaned_data.append(new_equation_data)

        return cleaned_data

    def _parse_variables_from_rhs(self, rhs: str) -> list[str]:
        variables = set()
        for term in rhs.split():
            if "V_" in term:
                variables.add(term)

        return sorted(list(variables), key=self._sorting_key)

    def _sorting_key(self, element: str) -> int:
        return int(element.split("_")[1])
