import logging
import pathlib
import stat

from src.common.io import context
from src.common.io.storage import exceptions, path_resolver

logger = logging.getLogger(__name__)


class FolderRepositoryValidator:
    def __init__(self, location: str):
        self._location = location
        self._path = self._build_repository_path()

    def _build_repository_path(self) -> pathlib.Path:
        PATH_TEMPLATE = path_resolver.PathTemplateStrings.ONTOLOGY_REPOSITORY_DIR
        new_context = context.IOContext(self._location)
        return path_resolver.resolve(new_context, PATH_TEMPLATE)

    def validate_repository_location(self) -> None:
        if self._path.is_dir():
            self._check_permissions()
        else:
            self._log_missing_dir_error()
            self._raise_invalid_repository_error()

    def _log_missing_dir_error(self) -> None:
        log_error_msg = f"The directory does not exist: {self._location}"
        logger.error(log_error_msg)

    def _raise_invalid_repository_error(self) -> None:
        exception_msg = f"Invalid repository location: {self._location}"
        raise exceptions.DataIOError(exception_msg)

    def _check_permissions(self) -> None:
        directory_info = self._path.stat()
        directory_permissions = directory_info.st_mode
        READ_MODE = stat.S_IRUSR
        WRITE_MODE = stat.S_IWUSR
        for permission_type in [READ_MODE, WRITE_MODE]:
            self._check_single_permission(directory_permissions, permission_type)

    def _check_single_permission(
        self, directory_permissions: int, permission_type: int
    ) -> None:
        has_mode_permissions = bool(directory_permissions & permission_type)
        if not has_mode_permissions:
            self._log_permission_error(permission_type)
            self._raise_invalid_repository_error()

    def _log_permission_error(self, permission_type: int) -> None:
        log_error_msg = {
            f"You don't have the necessary permissions ({oct(permission_type)}):"
            f"{self._location}."
        }
        logger.error(log_error_msg)
