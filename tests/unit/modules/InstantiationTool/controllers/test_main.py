import pytest

from PyQt5 import QtWidgets

from packages.Utilities.InstantiationTool.controllers.main import MainController


@pytest.fixture
def main_controller(mocker) -> MainController:
  main_model = mocker.Mock()
  main_view = mocker.Mock()

  return MainController(main_model, main_view)


@pytest.fixture
def mock_list_selector(mocker):
  mock_dialog = mocker.patch(
      "packages.dialogs.views.list_selector.ListSelectorView"
  ).return_value
  mock_dialog.ui.list.currentIndex.return_value.data.return_value = "item1"

  return mock_dialog


@pytest.fixture
def mock_get_available_ontologies(mocker):
  function_mock = mocker.patch(
      "packages.Common.classes.io.get_available_ontologies"
  )
  function_mock.return_value = ["Item1", "Item2", "Item3"]
  return function_mock


@pytest.fixture
def mock_get_available_models(mocker):
  function_mock = mocker.patch(
      "packages.Common.classes.io.get_available_models"
  )
  function_mock.return_value = ["Item1", "Item2", "Item3"]
  return function_mock


class TestSelectOntology:
  """
  Tests for the select_ontology method.
  """

  def test_dialog_accepted(
      self,
      mocker,
      main_controller,
      mock_list_selector,
      mock_get_available_ontologies,
  ):
    """
    ListSelector dialog Accepted
    """
    main_controller.select_model = mocker.Mock(return_value=True)
    mock_list_selector.exec_.return_value = QtWidgets.QDialog.Accepted

    main_controller.select_ontology()
    main_controller.select_model.assert_called()

  def test_dialog_rejected(
      self,
      mocker,
      main_controller,
      mock_list_selector,
      mock_get_available_ontologies,
  ):
    """
    ListSelector dialog Rejected
    """
    main_controller.load_default_data = mocker.Mock()
    mock_list_selector.exec_.return_value = QtWidgets.QDialog.Rejected

    main_controller.select_ontology()
    main_controller.load_default_data.assert_called()


class TestSelectModel:
  """
  Tests for the select_model method.
  """

  def test_dialog_accepted(
      self,
      mocker,
      main_controller,
      mock_list_selector,
      mock_get_available_models,
  ):
    """
    ListSelector dialog Accepted
    """
    mock_list_selector.exec_.return_value = QtWidgets.QDialog.Accepted

    assert main_controller.select_model("ontology_name") is True
    main_controller._model.load_ontology.assert_called()

  def test_dialog_rejected(
      self,
      mocker,
      main_controller,
      mock_list_selector,
      mock_get_available_models,
  ):
    """
    ListSelector dialog Rejected
    """
    main_controller.load_default_data = mocker.Mock()
    mock_list_selector.exec_.return_value = QtWidgets.QDialog.Rejected

    assert main_controller.select_model("ontology_name") is False
