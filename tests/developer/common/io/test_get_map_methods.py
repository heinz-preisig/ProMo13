import json
import pathlib
import typing
from collections.abc import Callable

import pytest
import pytest_cases

from src.common import corelib, io
from tests.developer.common.io import helpers

EMPTY_DATA_KEY = "empty"
ONE_ITEM_DATA_KEY = "one_item"
MULTIPLE_ITEMS_DATA_KEY = "multiple_items"
MISSING_REQUIRED_DATA_KEY = "missing_required"
WRONG_ATTRIBUTE_TYPE_DATA_KEY = "wrong_attribute_type"
INVALID_REFERENCE_DATA_KEY = "invalid_reference"


@pytest.fixture(scope="module")
def data_dir_path() -> pathlib.Path:
    return pathlib.Path(__file__).parent / "test_data"


@pytest.fixture(scope="module")
def full_map_data(data_dir_path: pathlib.Path) -> dict[str, dict[str, typing.Any]]:
    data_file_path = data_dir_path / "map_data.json"
    with data_file_path.open() as f:
        data: dict[str, dict[str, typing.Any]] = json.load(f)

    return data


class SetupGetMap:
    def __init__(
        self,
        full_map_data: dict[str, dict[str, typing.Any]],
        map_variant_to_test: corelib.CoreMapVariant,
        ontology_names: list[str],
        data_keys: list[str],
    ):
        self._fake_storage = helpers.FakeStorage()
        self._full_map_data = full_map_data
        self._map_variant_to_test = map_variant_to_test
        self._ontology_names = ontology_names
        self._data_keys = data_keys

        self._load_fake_storage()

    def _load_fake_storage(self) -> None:
        for ontology_name, variant_to_test_key in zip(
            self._ontology_names, self._data_keys, strict=True
        ):
            self._add_new_ontology_to_fake_storage(ontology_name)
            self._load_map_data_into_fake_storage(ontology_name, variant_to_test_key)

    def _add_new_ontology_to_fake_storage(self, new_ontology_name: str) -> None:
        dummy_context = io.IOContext()
        current_ontologies = self._fake_storage.get_context_member_options(
            io.IOContextMember.ONTOLOGY, dummy_context
        )
        updated_ontologies = current_ontologies + [new_ontology_name]

        self._fake_storage.set_context_member_options(
            io.IOContextMember.ONTOLOGY, updated_ontologies
        )

    def _load_map_data_into_fake_storage(
        self, ontology_name: str, variant_to_test_key: str
    ) -> None:
        map_data = self._get_map_data(variant_to_test_key)
        self._fake_storage.set_map_data(ontology_name, map_data)

    def _get_map_data(self, variant_to_test_key: str) -> dict[str, typing.Any]:
        variant_key_pairs = self._get_variant_key_pairs(variant_to_test_key)

        return {
            map_variant: self._full_map_data[map_variant][data_key]
            for map_variant, data_key in variant_key_pairs.items()
        }

    def _get_variant_key_pairs(
        self, variant_to_test_key: str
    ) -> dict[corelib.CoreMapVariant, str]:
        DEFAULT_KEY = MULTIPLE_ITEMS_DATA_KEY

        variant_key_pairs = {
            map_variant: DEFAULT_KEY for map_variant in corelib.CoreMapVariant
        }
        variant_key_pairs[self._map_variant_to_test] = variant_to_test_key

        return variant_key_pairs

    def get_fake_storage(self) -> helpers.FakeStorage:
        return self._fake_storage

    def get_expected_map(self, ontology_name: str) -> corelib.CoreMap:
        map_data = self._get_map_data_for_ontology_name(ontology_name)
        return helpers.build_map(self._map_variant_to_test, map_data)

    def _get_map_data_for_ontology_name(
        self, ontology_name: str
    ) -> dict[str, typing.Any]:
        dummy_context = io.IOContext(ontology_name=ontology_name)
        return {
            map_variant: self._fake_storage.get_core_map_data(
                map_variant, dummy_context
            )
            for map_variant in corelib.CoreMapVariant
        }


@pytest_cases.parametrize(
    variant_to_test_key=(EMPTY_DATA_KEY, ONE_ITEM_DATA_KEY, MULTIPLE_ITEMS_DATA_KEY),
    ids=[f"|data_key: {key}|" for key in ["empty", "one_item", "multiple_items"]],
)
@pytest_cases.parametrize(
    map_variant_to_test=list(corelib.CoreMapVariant),
    ids=[f"|map_variant: {map_variant}|" for map_variant in corelib.CoreMapVariant],
)
def success_standard(
    full_map_data: dict[str, typing.Any],
    map_variant_to_test: corelib.CoreMapVariant,
    variant_to_test_key: str,
) -> tuple[io.IOManager, corelib.CoreMapVariant, corelib.CoreMap]:
    ontology_names = ["VALID_ONTOLOGY"]
    data_keys = [variant_to_test_key]

    case_setup = SetupGetMap(
        full_map_data, map_variant_to_test, ontology_names, data_keys
    )

    fake_storage = case_setup.get_fake_storage()
    test_io_manager = configure_io_manager_for_success_get_map(
        fake_storage, ontology_names
    )

    expected_map = case_setup.get_expected_map(ontology_names[0])

    return test_io_manager, map_variant_to_test, expected_map


def configure_io_manager_for_success_get_map(
    fake_storage: helpers.FakeStorage, ontology_names: list[str]
) -> io.IOManager:
    test_io_manager = io.IOManager(fake_storage)
    test_io_manager.set_repository_location("VALID_REPOSITORY_LOCATION")
    test_io_manager.set_context_member_name(
        io.IOContextMember.ONTOLOGY, ontology_names[0]
    )

    return test_io_manager


@pytest_cases.parametrize(
    map_variant_to_test=list(corelib.CoreMapVariant),
    ids=[f"|map_variant: {map_variant}|" for map_variant in corelib.CoreMapVariant],
)
def success_after_changing_context(
    map_variant_to_test: corelib.CoreMapVariant,
    full_map_data: dict[str, typing.Any],
) -> tuple[io.IOManager, corelib.CoreMapVariant, corelib.CoreMap]:
    ontology_names = ["VALID_ONTOLOGY1", "VALID_ONTOLOGY2"]
    data_keys = [ONE_ITEM_DATA_KEY, MULTIPLE_ITEMS_DATA_KEY]

    case_setup = SetupGetMap(
        full_map_data, map_variant_to_test, ontology_names, data_keys
    )

    fake_storage = case_setup.get_fake_storage()
    test_io_manager = configure_io_manager_for_success_after_changing_context(
        fake_storage, ontology_names
    )

    expected_map = case_setup.get_expected_map(ontology_names[1])

    return test_io_manager, map_variant_to_test, expected_map


def configure_io_manager_for_success_after_changing_context(
    fake_storage: helpers.FakeStorage, ontology_names: list[str]
) -> io.IOManager:
    test_io_manager = io.IOManager(fake_storage)
    test_io_manager.set_repository_location("VALID_REPOSITORY_LOCATION")
    test_io_manager.set_context_member_name(
        io.IOContextMember.ONTOLOGY, ontology_names[0]
    )

    # Change context
    test_io_manager.set_context_member_name(
        io.IOContextMember.ONTOLOGY, ontology_names[1]
    )

    return test_io_manager


@pytest_cases.parametrize(
    map_variant_to_test=list(corelib.CoreMapVariant),
    ids=[f"|map_variant: {map_variant}|" for map_variant in corelib.CoreMapVariant],
)
def success_second_time(
    map_variant_to_test: corelib.CoreMapVariant,
    full_map_data: dict[str, typing.Any],
) -> tuple[io.IOManager, corelib.CoreMapVariant, corelib.CoreMap]:
    ontology_names = ["VALID_ONTOLOGY1", "VALID_ONTOLOGY2"]
    data_keys = [ONE_ITEM_DATA_KEY, MULTIPLE_ITEMS_DATA_KEY]

    case_setup = SetupGetMap(
        full_map_data, map_variant_to_test, ontology_names, data_keys
    )

    fake_storage = case_setup.get_fake_storage()
    test_io_manager = configure_io_manager_for_success_second_time(
        fake_storage, ontology_names, map_variant_to_test
    )

    expected_map = case_setup.get_expected_map(ontology_names[1])

    return test_io_manager, map_variant_to_test, expected_map


def configure_io_manager_for_success_second_time(
    fake_storage: helpers.FakeStorage,
    ontology_names: list[str],
    map_variant_to_test: corelib.CoreMapVariant,
) -> io.IOManager:
    test_io_manager = io.IOManager(fake_storage)
    test_io_manager.set_repository_location("VALID_REPOSITORY_LOCATION")
    test_io_manager.set_context_member_name(
        io.IOContextMember.ONTOLOGY, ontology_names[0]
    )
    test_io_manager.get_core_map(map_variant_to_test)

    # Change context
    test_io_manager.set_context_member_name(
        io.IOContextMember.ONTOLOGY, ontology_names[1]
    )

    return test_io_manager


@pytest_cases.parametrize_with_cases(
    "test_io_manager, map_variant_to_test, expected_map", cases=".", prefix="success_"
)
def test_get_map_correctly(
    test_io_manager: io.IOManager,
    map_variant_to_test: corelib.CoreMapVariant,
    expected_map: corelib.CoreMap,
) -> None:
    # GIVEN an IOManager with a fake storage supplying correct map data,
    #  the expected map created from that data
    #  and the map variant to test

    # WHEN retrieving the map for the variant to test
    output_map = test_io_manager.get_core_map(map_variant_to_test)

    # THEN the output map should match the expected map
    assert expected_map == output_map


@pytest_cases.parametrize(
    data_key=(
        MISSING_REQUIRED_DATA_KEY,
        WRONG_ATTRIBUTE_TYPE_DATA_KEY,
        INVALID_REFERENCE_DATA_KEY,
    ),
    ids=[
        f"|error_type: {key}|"
        for key in ["missing_required", "wrong_attribute_type", "invalid_reference"]
    ],
)
@pytest_cases.parametrize(
    map_variant_to_test=list(corelib.CoreMapVariant),
    ids=[f"|map_variant: {map_variant}|" for map_variant in corelib.CoreMapVariant],
)
@pytest_cases.case(id="")
def case_exception_on_invalid_data(
    map_variant_to_test: corelib.CoreMapVariant,
    full_map_data: dict[str, typing.Any],
    data_key: str,
) -> tuple[io.IOManager, corelib.CoreMapVariant]:
    ontology_names = ["VALID_ONTOLOGY"]
    data_keys = [data_key]

    case_setup = SetupGetMap(
        full_map_data, map_variant_to_test, ontology_names, data_keys
    )

    fake_storage = case_setup.get_fake_storage()
    test_io_manager = configure_io_manager_for_case_exception_on_invalid_data(
        fake_storage, ontology_names
    )

    return test_io_manager, map_variant_to_test


def configure_io_manager_for_case_exception_on_invalid_data(
    fake_storage: helpers.FakeStorage, ontology_names: list[str]
) -> io.IOManager:
    test_io_manager = io.IOManager(fake_storage)
    test_io_manager.set_repository_location("VALID_REPOSITORY_LOCATION")
    test_io_manager.set_context_member_name(
        io.IOContextMember.ONTOLOGY, ontology_names[0]
    )

    return test_io_manager


@pytest_cases.parametrize_with_cases(
    "test_io_manager, map_variant_to_test",
    cases=case_exception_on_invalid_data,
)
def test_exception_on_invalid_data(
    test_io_manager: io.IOManager,
    map_variant_to_test: corelib.CoreMapVariant,
    current_cases: dict[str, tuple[str, Callable[..., None], dict[str, typing.Any]]],
) -> None:
    # Skip case
    _, _, params = current_cases["test_io_manager"]
    if (
        params["data_key"] == INVALID_REFERENCE_DATA_KEY
        and params["map_variant_to_test"] == "index"
    ):
        pytest.skip("Index map does not have any references")

    # GIVEN an IOManager with a fake storage supplying incorrect map data,
    #  the expected error message
    #  and a the map variant to test
    error_message = f"Corrupted {map_variant_to_test} data"

    # WHEN retrieving the map
    # THEN the expected error message should be raised
    with pytest.raises(io.IOBuilderError, match=error_message):
        test_io_manager.get_core_map(map_variant_to_test)
