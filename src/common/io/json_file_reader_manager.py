import typing

from . import json_file_readers
from .context import IOContext, IOContextMember


class JSONFileReader:
    def get_repository_index_options(
        self, context_member: IOContextMember, context: IOContext
    ) -> list[str]:
        reader = self._get_repository_index_reader(context_member, context)
        options: list[str] = reader.read()
        return options

    def _get_repository_index_reader(
        self, context_member: IOContextMember, context: IOContext
    ) -> json_file_readers.BaseJsonFileReader:
        match context_member:
            case IOContextMember.ONTOLOGY:
                return json_file_readers.OntologyRepositoryIndexFileReader(context)
            case IOContextMember.MODEL:
                return json_file_readers.ModelRepositoryIndexFileReader(context)
            case IOContextMember.INSTANTIATION:
                return json_file_readers.InstantiationRepositoryIndexFileReader(context)

    def read_index_file(self, context: IOContext) -> typing.Any:
        reader = json_file_readers.IndexFileReader(context)
        data = reader.read()

        return data

    def read_variable_file(self, context: IOContext) -> typing.Any:
        reader = json_file_readers.VariableFileReader(context)
        data = reader.read()

        return data
