# /home/heinz/1_Gits/CAM12/ProMo12/packages/OntologyBuilder/BehaviourLinker_HAP_v0/Controllers/app_state.py

from enum import Enum, auto
from typing import Dict, Callable, Any, Optional
from PyQt5 import QtCore


class AppState(Enum):
  """Application states."""
  IDLE = auto()  # Initial state, nothing selected
  ENTITY_SELECTED = auto()  # Entity is selected in the tree
  EDITING_ENTITY = auto()  # Entity editor is open
  CREATING_ENTITY = auto()  # Creating a new entity
  EDITING_VARIABLE = auto()  # Variable editor is open


class StateMachine(QtCore.QObject):
  """State machine for managing application state."""

  state_changed = QtCore.pyqtSignal(object, dict)  # Emitted when state changes

  def __init__(self, initial_state: AppState = AppState.IDLE):
    super().__init__()
    self._state = initial_state
    self._state_handlers: Dict[AppState, Callable[[dict], None]] = {}
    self._enter_handlers: Dict[AppState, Callable[[dict], None]] = {}
    self._exit_handlers: Dict[AppState, Callable[[dict], None]] = {}

  @property
  def state(self) -> AppState:
    """Get the current state."""
    return self._state

  def on_state(self, state: AppState) -> Callable:
    """Decorator to register a state handler."""

    def decorator(func: Callable[[dict], None]) -> Callable:
      self._state_handlers[state] = func
      return func

    return decorator

  def on_enter(self, state: AppState) -> Callable:
    """Decorator to register an enter state handler."""

    def decorator(func: Callable[[dict], None]) -> Callable:
      self._enter_handlers[state] = func
      return func

    return decorator

  def on_exit(self, state: AppState) -> Callable:
    """Decorator to register an exit state handler."""

    def decorator(func: Callable[[dict], None]) -> Callable:
      self._exit_handlers[state] = func
      return func

    return decorator

  def transition_to(self, new_state: AppState, **kwargs) -> None:
    """Transition to a new state."""
    if self._state == new_state:
      return

    old_state = self._state
    print(f"State transition: {old_state.name} -> {new_state.name}")

    # Call exit handler for old state if it exists
    if old_state in self._exit_handlers:
      self._exit_handlers[old_state](kwargs or {})

    # Update state
    self._state = new_state

    # Call enter handler for new state if it exists
    if new_state in self._enter_handlers:
      self._enter_handlers[new_state](kwargs or {})

    # Emit state changed signal
    self.state_changed.emit(new_state, kwargs or {})

  def handle_event(self, **kwargs) -> None:
    """Handle an event in the current state."""
    if self._state in self._state_handlers:
      self._state_handlers[self._state](kwargs or {})
    else:
      print(f"No handler for state: {self._state.name}")

  def __str__(self) -> str:
    """String representation of the current state."""
    return self._state.name