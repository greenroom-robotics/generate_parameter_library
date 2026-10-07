# -*- coding: utf-8 -*-
import os
import tempfile

import pytest

from generate_parameter_library_py.generate_rust_module import run as run_rust
from generate_parameter_library_py.parse_yaml import YAMLSyntaxError


def generate(yaml_content):
    with tempfile.TemporaryDirectory() as tmp:
        yaml_file = os.path.join(tmp, 'params.yaml')
        output_file = os.path.join(tmp, 'params.rs')
        with open(yaml_file, 'w') as f:
            f.write(yaml_content)
        run_rust(output_file, yaml_file)
        with open(output_file) as f:
            return f.read()


def test_rust_generation():
    code = generate(
        """ns:
  gains:
    p:
      type: double
      default_value: 1
      validation:
        bounds<>: [0, 10]
  joints:
    type: string_array
    default_value: ["a"]
    validation:
      subset_of<>: [["a", "b"]]
"""
    )
    assert 'pub gains: Gains,' in code
    assert '.default(1.0)' in code
    assert 'bounds(param, 0 as _, 10 as _)' in code
    assert 'lower: Some(0 as _), upper: Some(10 as _)' in code
    assert '.default(Arc::from([Arc::from("a")]))' in code
    assert 'subset_of(param, &["a", "b"])' in code


def test_rust_rejects_mapped_parameters():
    with pytest.raises(YAMLSyntaxError):
        generate(
            """ns:
  joints:
    type: string_array
  __map_joints:
    p:
      type: double
"""
        )
