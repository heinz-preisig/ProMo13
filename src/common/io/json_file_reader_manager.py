import typing

from src.common.io import context, json_file_readers


class JSONFileReader:
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

    def read_index_file(self, io_context: context.IOContext) -> typing.Any:
        reader = json_file_readers.IndexFileReader(io_context)
        data = reader.read()

        return data

    def read_variable_file(self, io_context: context.IOContext) -> typing.Any:
        reader = json_file_readers.VariableFileReader(io_context)
        data = reader.read()

        return data

    def read_equation_file(self, io_context: context.IOContext) -> typing.Any:
        reader = json_file_readers.EquationFileReader(io_context)
        data = reader.read()

        return data
