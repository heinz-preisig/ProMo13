import json
import logging
import typing
from pathlib import Path

import jsonschema

from . import exceptions, json_schemas, path_resolver
from .context import IOContext, IOContextMember

logger = logging.getLogger(__name__)


class JSONFileReader:
    def get_repository_index_options(
        self, context_member: IOContextMember, context: IOContext
    ) -> list[str]:
        content = self._get_repository_index_file_content(context_member, context)
        options = self._process_repository_index_file_content(context_member, content)

        return options

    def _get_repository_index_file_content(
        self, context_member: IOContextMember, context: IOContext
    ) -> str:
        path = self._get_path_to_repository_index_file(context_member, context)

        access_error_msg = f"Can not access {context_member} repository index"
        file_content = self._get_file_content(path, access_error_msg)

        return file_content

    def _get_path_to_repository_index_file(
        self, context_member: IOContextMember, context: IOContext
    ) -> Path:
        match context_member:
            case IOContextMember.ONTOLOGY:
                template = path_resolver.PathTemplateStrings.ONTOLOGY_INDEX_FILE
            case IOContextMember.MODEL:
                template = path_resolver.PathTemplateStrings.MODEL_INDEX_FILE
            case IOContextMember.INSTANTIATION:
                template = path_resolver.PathTemplateStrings.INSTANTIATION_INDEX_FILE

        path = path_resolver.resolve(context, template)
        return path

    def _get_file_content(self, file_path: Path, error_msg: str) -> str:
        try:
            with file_path.open("r") as file:
                file_content = file.read()
        except (FileNotFoundError, PermissionError) as err:
            logger.error(err)
            raise exceptions.DataIOError(error_msg) from err

        return file_content

    def _process_repository_index_file_content(
        self, context_member: IOContextMember, content: str
    ) -> list[str]:
        corrupted_error_msg = f"Corrupted {context_member} repository index"
        data: list[str] = self._load_json(content, corrupted_error_msg)

        schema = json_schemas.REPOSITORY_INDEX_FILE
        self._validate_json(data, schema, corrupted_error_msg)

        return data

    def _load_json(self, json_str: str, error_msg: str) -> typing.Any:
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as err:
            logger.error(err)
            raise exceptions.DataIOError(error_msg) from err

        return data

    def _validate_json(
        self, data: typing.Any, schema: typing.Any, error_msg: str
    ) -> None:
        try:
            jsonschema.validate(data, schema)
        except jsonschema.ValidationError as err:
            logger.error(err)
            raise exceptions.DataIOError(error_msg) from err

    def read_index_file(self, context: IOContext) -> typing.Any:
        file_path = path_resolver.resolve(
            context, path_resolver.PathTemplateStrings.INDEX_FILE
        )
        error_msg = "Can not access index file"
        content = self._get_file_content(file_path, error_msg)

        data = self._load_json(content, error_msg)

        cleaned_data = []
        for idx_id, idx_data in data["indices"].items():
            new_index_data = {"identifier": idx_id}
            new_index_data["iri"] = idx_data["IRI"]
            new_index_data["label"] = idx_data["label"]
            cleaned_data.append(new_index_data)

        return cleaned_data
