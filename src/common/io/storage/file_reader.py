import typing

from src.common import corelib
from src.common.io import context
from src.common.io.storage import json_file_readers


class FileReader:
    def get_repository_index_options(
        self, context_member: context.IOContextMember, io_context: context.IOContext
    ) -> list[str]:
        reader = self._get_repository_index_reader(context_member, io_context)
        options: list[str] = reader.read()
        return options

    def _get_repository_index_reader(
        self, context_member: context.IOContextMember, io_context: context.IOContext
    ) -> json_file_readers.BaseJsonFileReader:
        match context_member:
            case context.IOContextMember.ONTOLOGY:
                return json_file_readers.OntologyRepositoryIndexFileReader(io_context)
            case context.IOContextMember.MODEL:
                return json_file_readers.ModelRepositoryIndexFileReader(io_context)
            case context.IOContextMember.INSTANTIATION:
                return json_file_readers.InstantiationRepositoryIndexFileReader(
                    io_context
                )

    def read_core_map_file(
        self, map_variant: corelib.CoreMapVariant, io_context: context.IOContext
    ) -> typing.Any:
        reader = self._get_core_map_file_reader(map_variant, io_context)

        return reader.read()

    def _get_core_map_file_reader(
        self, map_variant: corelib.CoreMapVariant, io_context: context.IOContext
    ) -> json_file_readers.BaseJsonFileReader:
        match map_variant:
            case corelib.CoreMapVariant.INDEX:
                return json_file_readers.IndexFileReader(io_context)
            case corelib.CoreMapVariant.VARIABLE:
                return json_file_readers.VariableFileReader(io_context)
            case corelib.CoreMapVariant.EQUATION:
                return json_file_readers.EquationFileReader(io_context)
