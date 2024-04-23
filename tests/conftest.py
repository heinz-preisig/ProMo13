import pytest
import functools


def parametrize(parameters, arguments_dict, **kwargs):
  """
  A nicer pytest parametrization decorator

  Args: 
    parameters: A list of parameter names that will be parametrized
    arguments_dict: A dict that maps between the ID of an argument list
     to the list itself
    kwargs: Additional keyword arguments to be passed to
     pytest.parametrize
  """
  def wrapper(func):
    @functools.wraps(func)
    @pytest.mark.parametrize(
        parameters,
        list(arguments_dict.values()),
        ids=list(arguments_dict.keys()),
        **kwargs
    )
    def wrapped(*func_args, **func_kwargs):
      return func(*func_args, **func_kwargs)
    return wrapped
  return wrapper
