# -*- coding: utf-8 -*-
import os
import tempfile

from generate_parameter_library_py.generate_cpp_header import run as run_cpp
from generate_parameter_library_py.generate_python_module import run as run_python


def generate(yaml_content, run):
    """Generate code for a yaml snippet and return it as a string."""
    with tempfile.TemporaryDirectory() as tmp:
        yaml_path = os.path.join(tmp, 'parameters.yaml')
        out_path = os.path.join(tmp, 'out')
        with open(yaml_path, 'w') as f:
            f.write(yaml_content)
        run(out_path, yaml_path, 'test_validate.hpp')
        with open(out_path) as f:
            return f.read()


NESTED_KEY_LIST = """canif_monitor:
  presence:
    devices:
      type: string_array
      default_value: ["sigma_jcu"]
    device:
      __map_devices:
        interface:
          type: string
          default_value: "can0"
"""

ROOT_KEY_LIST = """canif_monitor:
  devices:
    type: string_array
    default_value: ["sigma_jcu"]
  presence:
    device:
      __map_devices:
        interface:
          type: string
          default_value: "can0"
"""


def test_key_list_found_in_enclosing_scope_cpp():
    code = generate(NESTED_KEY_LIST, run_cpp)
    assert 'for (const auto & value_1 : updated_params.presence.devices) {' in code
    # The map member itself is never qualified by the key list's scope.
    assert '.device.devices_map[value_1]' in code


def test_key_list_found_in_enclosing_scope_python():
    code = generate(NESTED_KEY_LIST, run_python)
    assert 'for value_1 in updated_params.presence.devices:' in code


def test_root_key_list_still_resolves_at_root():
    """A nested map keyed on a root-level list keeps working."""
    code = generate(ROOT_KEY_LIST, run_cpp)
    assert 'for (const auto & value_1 : updated_params.devices) {' in code
    assert '.device.devices_map[value_1]' in code


def test_nested_maps_resolve_independently():
    """Two maps at different depths each pick up their nearest key list."""
    code = generate(
        """robot:
  joints:
    type: string_array
    default_value: ["j1"]
  gains:
    dof_names:
      type: string_array
      default_value: ["x"]
    __map_joints:
      __map_dof_names:
        weight:
          type: double
          default_value: 1.0
""",
        run_cpp,
    )
    assert 'for (const auto & value_1 : updated_params.joints) {' in code
    assert 'for (const auto & value_2 : updated_params.gains.dof_names) {' in code
    assert '.joints_map[value_1].dof_names_map[value_2]' in code
