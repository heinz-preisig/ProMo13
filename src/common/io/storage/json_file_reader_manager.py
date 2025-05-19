import pathlib
import typing

from src.common import corelib
from src.common.io import context
from src.common.io.storage import json_file_readers, path_resolver


class JSONFileReaderManager:
    def get_repository_index_options(
        self, context_member: context.IOContextMember, io_context: context.IOContext
    ) -> list[str]:
        file_path = self._get_repository_index_file_path(context_member, io_context)
        if file_path.is_file():
            return self._read_repository_index_file(context_member, io_context)

        return self._check_folders(context_member, io_context)

    def _get_repository_index_file_path(
        self, context_member: context.IOContextMember, io_context: context.IOContext
    ) -> pathlib.Path:
        match context_member:
            case context.IOContextMember.ONTOLOGY:
                template_string = path_resolver.PathTemplateStrings.ONTOLOGY_INDEX_FILE
            case context.IOContextMember.MODEL:
                template_string = path_resolver.PathTemplateStrings.MODEL_INDEX_FILE
            case context.IOContextMember.INSTANTIATION:
                template_string = (
                    path_resolver.PathTemplateStrings.INSTANTIATION_INDEX_FILE
                )

        return path_resolver.resolve(io_context, template_string)

    def _read_repository_index_file(
        self, context_member: context.IOContextMember, io_context: context.IOContext
    ) -> list[str]:
        reader = self._get_repository_index_reader(context_member, io_context)
        options: list[str] = reader.read()
        return options

    # Only for compatibility with repositories without the repository index file
    def _check_folders(
        self, context_member: context.IOContextMember, io_context: context.IOContext
    ) -> list[str]:
        match context_member:
            case context.IOContextMember.ONTOLOGY:
                return self._get_ontology_folder_names(io_context)
            case context.IOContextMember.MODEL:
                return self._get_model_folder_names(io_context)
            case context.IOContextMember.INSTANTIATION:
                return self._get_instantation_file_names(io_context)

    def _get_ontology_folder_names(self, io_context: context.IOContext) -> list[str]:
        template_string = path_resolver.PathTemplateStrings.ONTOLOGY_REPOSITORY_DIR
        parent_folder_path = path_resolver.resolve(io_context, template_string)
        folders = []
        for child in parent_folder_path.iterdir():
            if child.is_dir() and not child.name.startswith("."):
                folders.append(child.name)

        return folders

    def _get_model_folder_names(self, io_context: context.IOContext) -> list[str]:
        template_string = path_resolver.PathTemplateStrings.MODEL_LIBRARY_DIR
        parent_folder_path = path_resolver.resolve(io_context, template_string)
        folders = []
        for child in parent_folder_path.iterdir():
            if child.is_dir() and not child.name.startswith("."):
                folders.append(child.name)

        return folders

    def _get_instantation_file_names(self, io_context: context.IOContext) -> list[str]:
        template_string = path_resolver.PathTemplateStrings.INSTANTIATION_LIBRARY_DIR
        parent_folder_path = path_resolver.resolve(io_context, template_string)
        file_names = []
        for child in parent_folder_path.iterdir():
            if child.is_file() and not child.name.startswith("."):
                file_names.append(child.stem)

        return file_names

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
