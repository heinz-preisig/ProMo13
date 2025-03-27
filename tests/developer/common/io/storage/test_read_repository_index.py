import pathlib

import pytest
import pytest_cases

from src.common import io
from src.common.io import storage


@pytest.fixture
def ok_context(base_path: pathlib.Path) -> io.IOContext:
    ok_location = str(base_path / "repositoryOK")
    ok_ontology = "ontologyOK"
    ok_model = "modelOK"
    ok_instantiation = "instantiationOK"
    return io.IOContext(ok_location, ok_ontology, ok_model, ok_instantiation)


def replace_context_attribute(
    member: io.IOContextMember,
    io_context: io.IOContext,
    content: str,
    path: pathlib.Path,
) -> io.IOContext:
    match member:
        case io.IOContextMember.ONTOLOGY:
            location = str(path / content)
            io_context.repository_location = location
        case io.IOContextMember.MODEL:
            io_context.ontology_name = content
        case io.IOContextMember.INSTANTIATION:
            io_context.model_name = content

    return io_context


@pytest_cases.parametrize(
    "test_member, repo_prefix",
    [
        (io.IOContextMember.ONTOLOGY, "repository"),
        (io.IOContextMember.MODEL, "ontology"),
        (io.IOContextMember.INSTANTIATION, "model"),
    ],
    ids=("ontology", "model", "instantiation"),
)
class CasesReadRepositoryIndex:
    @pytest_cases.case(id="")
    def valid_repository_index(
        self,
        ok_context: io.IOContext,
        test_member: io.IOContextMember,
        repo_prefix: str,
    ) -> tuple[io.IOContextMember, io.IOContext]:
        return test_member, ok_context

    def invalid_missing_file(
        self,
        ok_context: io.IOContext,
        base_path: pathlib.Path,
        test_member: io.IOContextMember,
        repo_prefix: str,
    ) -> tuple[io.IOContextMember, io.IOContext, str]:
        repository_name = f"{repo_prefix}1"

        test_context = replace_context_attribute(
            test_member, ok_context, repository_name, base_path
        )

        error_msg = f"Can not access {test_member} repository index"

        return test_member, test_context, error_msg

    @pytest_cases.parametrize(
        repo_id=("2", "3"), ids=("invalid json", "invalid json schema")
    )
    def invalid_json_problem(
        self,
        ok_context: io.IOContext,
        base_path: pathlib.Path,
        test_member: io.IOContextMember,
        repo_prefix: str,
        repo_id: str,
    ) -> tuple[io.IOContextMember, io.IOContext, str]:
        repository_name = f"{repo_prefix}{repo_id}"
        test_context = replace_context_attribute(
            test_member, ok_context, repository_name, base_path
        )

        error_msg = f"Corrupted {test_member} repository index"

        return test_member, test_context, error_msg

    @pytest_cases.case(id="")
    def incomplete_context(
        self,
        test_member: io.IOContextMember,
        repo_prefix: str,
    ) -> tuple[io.IOContextMember, io.IOContext, str]:
        test_context = io.IOContext()
        error_msg = "Insufficient data in IOContext"

        return test_member, test_context, error_msg


class TestReadRepositoryIndex:
    @pytest_cases.parametrize_with_cases(
        "test_member, test_context", cases=CasesReadRepositoryIndex, prefix="valid"
    )
    def test_read_repository_index_ok(
        self,
        test_storage: storage.GenericStorage,
        test_member: io.IOContextMember,
        test_context: io.IOContext,
    ) -> None:
        expected = [
            f"{test_member}{content_id}" for content_id in ["1", "2", "3", "OK"]
        ]

        output = test_storage.get_context_member_options(test_member, test_context)

        assert sorted(expected) == sorted(output)

    @pytest_cases.parametrize_with_cases(
        "test_member, test_context, error_msg",
        cases=CasesReadRepositoryIndex,
        prefix="invalid",
    )
    def test_exception_on_invalid_index(
        self,
        test_storage: storage.GenericStorage,
        test_member: io.IOContextMember,
        test_context: io.IOContext,
        error_msg: str,
    ) -> None:
        with pytest.raises(io.DataIOError, match=error_msg):
            test_storage.get_context_member_options(test_member, test_context)

    @pytest_cases.parametrize_with_cases(
        "test_member, test_context, error_msg",
        cases=CasesReadRepositoryIndex,
        prefix="incomplete",
    )
    def test_exception_on_read_repository_index_with_empty_context(
        self,
        test_storage: storage.GenericStorage,
        test_member: io.IOContextMember,
        test_context: io.IOContext,
        error_msg: str,
    ) -> None:
        with pytest.raises(io.IOContextError, match=error_msg):
            test_storage.get_context_member_options(test_member, test_context)
