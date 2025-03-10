import json
import logging
import typing
from pathlib import Path

import jsonschema

from . import io_exceptions, json_schemas, path_resolver
from .ontology_context import ContextMember, OntologyContext

logger = logging.getLogger(__name__)


class JSONFileReader:
    def get_index_options(
        self, context_member: ContextMember, context: OntologyContext
    ) -> list[str]:
        content = self._get_index_file_content(context_member, context)
        options = self._process_index_file_content(context_member, content)

        return options

    def _get_index_file_content(
        self, context_member: ContextMember, context: OntologyContext
    ) -> str:
        index_path = self._get_path_to_index_file(context_member, context)

        access_error_msg = f"Can not access {context_member} index"
        file_content = self._get_file_content(index_path, access_error_msg)

        return file_content

    def _get_path_to_index_file(
        self, context_member: ContextMember, context: OntologyContext
    ) -> Path:
        match context_member:
            case ContextMember.ONTOLOGY:
                template = path_resolver.Templates.ONTOLOGY_INDEX_FILE
            case ContextMember.MODEL:
                template = path_resolver.Templates.MODEL_INDEX_FILE
            case ContextMember.INSTANTIATION:
                template = path_resolver.Templates.INSTANTIATION_INDEX_FILE

        index_path = path_resolver.resolve(context, template)
        return index_path

    def _get_file_content(self, index_path: Path, error_msg: str) -> str:
        try:
            with index_path.open("r") as file:
                file_content = file.read()
        except (FileNotFoundError, PermissionError) as err:
            logger.error(err)
            raise io_exceptions.DataIOError(error_msg) from err

        return file_content

    def _process_index_file_content(
        self, context_member: ContextMember, content: str
    ) -> list[str]:
        corrupted_error_msg = f"Corrupted {context_member} index"
        data: list[str] = self._load_json(content, corrupted_error_msg)

        schema = json_schemas.INDEX_FILE
        self._validate_json(data, schema, corrupted_error_msg)

        return data

    def _load_json(self, file_content: str, error_msg: str) -> typing.Any:
        try:
            data = json.loads(file_content)
        except json.JSONDecodeError as err:
            logger.error(err)
            raise io_exceptions.DataIOError(error_msg) from err

        return data

    def _validate_json(
        self, data: typing.Any, schema: typing.Any, error_msg: str
    ) -> None:
        try:
            jsonschema.validate(data, schema)
        except jsonschema.ValidationError as err:
            logger.error(err)
            raise io_exceptions.DataIOError(error_msg) from err
