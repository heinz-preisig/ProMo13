import json
import pathlib
import typing

import pytest
import pytest_cases

from src.common import corelib, io
from tests.developer.common.io import helpers

type IOMap = corelib.IndexMap | corelib.VariableMap | corelib.EquationMap

EMPTY_DATA_KEY = "empty"
ONE_ITEM_DATA_KEY = "one_item"
MULTIPLE_ITEMS_DATA_KEY = "multiple_items"
MISSING_REQUIRED_DATA_KEY = "missing_required"
WRONG_ATTRIBUTE_TYPE_DATA_KEY = "wrong_attribute_type"


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
    def __init__(self, full_map_data: dict[str, dict[str, typing.Any]], map_name: str):
        self._fake_storage = helpers.FakeStorage()
        self._full_map_data = full_map_data
        self._map_name = map_name

    def load_fake_storage(self, ontology_name: str, data_key: str) -> None:
        self._add_new_ontology_to_fake_storage(ontology_name)
        self._load_map_data_into_fake_storage(ontology_name, data_key)

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
        self, ontology_name: str, data_key: str
    ) -> None:
        map_data = self._select_map_data(data_key)
        self._fake_storage.set_map_data(ontology_name, map_data)

    def _select_map_data(self, data_key: str) -> dict[str, typing.Any]:
        data_selection_dict = self._get_data_selection_dict(data_key)

        return {
            name: self._full_map_data[name][key]
            for name, key in data_selection_dict.items()
        }

    def _get_data_selection_dict(self, data_key: str) -> dict[str, str]:
        data_selection_dict = {
            name: MULTIPLE_ITEMS_DATA_KEY for name in ["index", "variable", "equation"]
        }
        data_selection_dict[self._map_name] = data_key

        return data_selection_dict

    def get_fake_storage(self) -> helpers.FakeStorage:
        return self._fake_storage

    def get_expected_map(self, ontology_name: str) -> IOMap:
        map_data = self._get_map_data_for_ontology_name(ontology_name)
        return helpers.build_map(self._map_name, map_data)

    def _get_map_data_for_ontology_name(
        self, ontology_name: str
    ) -> dict[str, typing.Any]:
        dummy_context = io.IOContext(ontology_name=ontology_name)
        return {
            "index": self._fake_storage.get_index_data(dummy_context),
            "variable": self._fake_storage.get_variable_data(dummy_context),
            "equation": self._fake_storage.get_equation_data(dummy_context),
        }


@pytest_cases.parametrize(
    data_key=(EMPTY_DATA_KEY, ONE_ITEM_DATA_KEY, MULTIPLE_ITEMS_DATA_KEY),
    ids=("empty", "one item", "multiple items"),
)
@pytest_cases.parametrize(
    map_name=("index", "variable", "equation"), ids=("index", "variable", "equation")
)
@pytest_cases.case(id="")
def case_get_map_correctly(
    full_map_data: dict[str, typing.Any],
    map_name: str,
    data_key: str,
) -> tuple[io.IOManager, IOMap, str]:
    get_map_method_name = f"get_current_{map_name}_map"

    ontology_names = ["VALID_ONTOLOGY"]
    data_keys = [data_key]

    case_setup = prepare_data(map_name, full_map_data, ontology_names, data_keys)

    fake_storage = case_setup.get_fake_storage()
    test_io_manager = configure_io_manager_case_get_map_correctly(
        fake_storage, ontology_names
    )

    expected_map = case_setup.get_expected_map(ontology_names[0])

    return test_io_manager, expected_map, get_map_method_name


def prepare_data(
    map_name: str,
    full_map_data: dict[str, typing.Any],
    ontologies: list[str],
    data_keys: list[str],
) -> SetupGetMap:
    case_setup = SetupGetMap(full_map_data, map_name)

    for ontology_name, data_key in zip(ontologies, data_keys, strict=True):
        case_setup.load_fake_storage(ontology_name, data_key)

    return case_setup


def configure_io_manager_case_get_map_correctly(
    fake_storage: helpers.FakeStorage, ontology_names: list[str]
) -> io.IOManager:
    test_io_manager = io.IOManager(fake_storage)
    test_io_manager.set_repository_location("VALID_REPOSITORY_LOCATION")
    test_io_manager.set_context_member_name(
        io.IOContextMember.ONTOLOGY, ontology_names[0]
    )

    return test_io_manager


@pytest_cases.parametrize_with_cases(
    "test_io_manager, expected_map, get_map_method_name", cases=case_get_map_correctly
)
def test_get_map_correctly(
    test_io_manager: io.IOManager, expected_map: IOMap, get_map_method_name: str
) -> None:
    # GIVEN an IOManager with a fake storage supplying correct map data,
    #  the expected map created from that data
    #  and a get_map method
    get_map_method = getattr(test_io_manager, get_map_method_name)

    # WHEN retrieving the map
    output_map = get_map_method()

    # THEN the output map should match the expected map
    assert expected_map == output_map


@pytest_cases.parametrize(map_name=("index", "variable", "equation"))
@pytest_cases.case(id="")
def case_get_map_correctly_after_switching_context(
    map_name: str,
    full_map_data: dict[str, typing.Any],
) -> tuple[io.IOManager, IOMap, str]:
    get_map_method_name = f"get_current_{map_name}_map"

    ontology_names = ["VALID_ONTOLOGY1", "VALID_ONTOLOGY2"]
    data_keys = [ONE_ITEM_DATA_KEY, MULTIPLE_ITEMS_DATA_KEY]

    case_setup = prepare_data(map_name, full_map_data, ontology_names, data_keys)

    fake_storage = case_setup.get_fake_storage()
    test_io_manager = configure_io_manager_case_switch_context(
        fake_storage, ontology_names
    )

    expected_map = case_setup.get_expected_map(ontology_names[1])

    return test_io_manager, expected_map, get_map_method_name


def configure_io_manager_case_switch_context(
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


@pytest_cases.parametrize_with_cases(
    "test_io_manager, expected_map, get_map_method_name",
    cases=case_get_map_correctly_after_switching_context,
)
def test_get_map_correctly_after_switching_context(
    test_io_manager: io.IOManager, expected_map: IOMap, get_map_method_name: str
) -> None:
    # GIVEN an IOManager with a fake storage supplying correct map data for two
    #  different contexts after switching to the second context,
    #  the expected map created from that data
    #  and a get_map method
    get_map_method = getattr(test_io_manager, get_map_method_name)

    # WHEN retrieving the map
    output_map = get_map_method()

    # THEN the output map should match the expected map
    assert expected_map == output_map


@pytest_cases.parametrize(map_name=("index", "variable", "equation"))
@pytest_cases.case(id="")
def case_get_map_correctly_second_time(
    map_name: str,
    full_map_data: dict[str, typing.Any],
) -> tuple[io.IOManager, IOMap, str]:
    get_map_method_name = f"get_current_{map_name}_map"

    ontology_names = ["VALID_ONTOLOGY1", "VALID_ONTOLOGY2"]
    data_keys = [ONE_ITEM_DATA_KEY, MULTIPLE_ITEMS_DATA_KEY]

    case_setup = prepare_data(map_name, full_map_data, ontology_names, data_keys)

    fake_storage = case_setup.get_fake_storage()
    test_io_manager = configure_io_manager_case_switch_context(
        fake_storage, ontology_names
    )

    expected_map = case_setup.get_expected_map(ontology_names[1])

    return test_io_manager, expected_map, get_map_method_name


def configure_io_manager_case_second_time(
    fake_storage: helpers.FakeStorage, ontology_names: list[str]
) -> io.IOManager:
    test_io_manager = io.IOManager(fake_storage)
    test_io_manager.set_repository_location("VALID_REPOSITORY_LOCATION")
    test_io_manager.set_context_member_name(
        io.IOContextMember.ONTOLOGY, ontology_names[0]
    )
    test_io_manager.get_current_index_map()

    # Change context
    test_io_manager.set_context_member_name(
        io.IOContextMember.ONTOLOGY, ontology_names[1]
    )

    return test_io_manager


@pytest_cases.parametrize_with_cases(
    "test_io_manager, expected_map, get_map_method_name",
    cases=case_get_map_correctly_second_time,
)
def test_get_map_correctly_second_time(
    test_io_manager: io.IOManager, expected_map: IOMap, get_map_method_name: str
) -> None:
    # GIVEN an IOManager with a fake storage supplying correct map data for two
    #  different contexts after building the map for the first context and switching
    #  to the second context,
    #  the expected map created from that data
    #  and a get_map method
    get_map_method = getattr(test_io_manager, get_map_method_name)

    # WHEN retrieving the map
    output_map = get_map_method()

    # THEN the output map should match the expected map
    assert expected_map == output_map


@pytest_cases.parametrize(
    data_key=(MISSING_REQUIRED_DATA_KEY, WRONG_ATTRIBUTE_TYPE_DATA_KEY)
)
@pytest_cases.parametrize(map_name=("index", "variable", "equation"))
@pytest_cases.case(id="")
def case_exception_on_invalid_data(
    map_name: str, full_map_data: dict[str, typing.Any], data_key: str
) -> tuple[io.IOManager, str, str]:
    get_map_method_name = f"get_current_{map_name}_map"

    ontology_names = ["VALID_ONTOLOGY"]
    data_keys = [data_key]

    case_setup = prepare_data(map_name, full_map_data, ontology_names, data_keys)

    fake_storage = case_setup.get_fake_storage()
    test_io_manager = configure_io_manager_case_exception_on_invalid_data(
        fake_storage, ontology_names
    )

    error_msg = f"Corrupted {map_name} data"

    return test_io_manager, error_msg, get_map_method_name


def configure_io_manager_case_exception_on_invalid_data(
    fake_storage: helpers.FakeStorage, ontology_names: list[str]
) -> io.IOManager:
    test_io_manager = io.IOManager(fake_storage)
    test_io_manager.set_repository_location("VALID_REPOSITORY_LOCATION")
    test_io_manager.set_context_member_name(
        io.IOContextMember.ONTOLOGY, ontology_names[0]
    )

    return test_io_manager


@pytest_cases.parametrize_with_cases(
    "test_io_manager, error_message, get_map_method_name",
    cases=case_exception_on_invalid_data,
)
def test_exception_on_invalid_data(
    test_io_manager: io.IOManager, error_message: str, get_map_method_name: str
) -> None:
    # GIVEN an IOManager with a fake storage supplying incorrect map data,
    #  the expected error message
    #  and a get_map method
    get_map_method = getattr(test_io_manager, get_map_method_name)

    # WHEN retrieving the map
    # THEN the expected error message should be raised
    with pytest.raises(io.IOBuilderError, match=error_message):
        get_map_method()


# # Test when the reference for an item in a map is not found
