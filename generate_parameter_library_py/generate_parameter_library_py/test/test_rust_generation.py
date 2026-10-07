# -*- coding: utf-8 -*-
import os
import tempfile

import pytest

from generate_parameter_library_py.generate_cpp_header import run as run_cpp
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


def test_rust_parsed_type():
    code = generate(
        """ns:
  host:
    type: string
    parsed_type: HostName
  ports:
    type: int_array
    parsed_type: Port
    parse: Port::new
"""
    )
    assert 'pub host: HostName,' in code
    assert 'pub ports: Arc<[Port]>,' in code
    assert '<HostName>::try_from(param)' in code
    assert '.map(|value| Port::new(*value)' in code
    assert 'Default' not in code


def test_parse_requires_parsed_type():
    with pytest.raises(YAMLSyntaxError):
        generate(
            """ns:
  host:
    type: string
    parse: HostName::parse
"""
        )


def test_cpp_rejects_parsed_type():
    with tempfile.TemporaryDirectory() as tmp:
        yaml_file = os.path.join(tmp, 'params.yaml')
        with open(yaml_file, 'w') as f:
            f.write('ns:\n  host:\n    type: string\n    parsed_type: HostName\n')
        with pytest.raises(YAMLSyntaxError):
            run_cpp(os.path.join(tmp, 'params.hpp'), yaml_file, '')
