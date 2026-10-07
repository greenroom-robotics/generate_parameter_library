# -*- coding: utf-8 -*-
import json
from typing import Union
from typeguard import typechecked


# ponytail: JSON escaping is a valid Rust literal for everything except raw control chars
def rust_string_literal(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


class RustConversions:
    def __init__(self, defined_type: str):
        self.is_double = defined_type.startswith('double')
        self.defined_type_to_lang_type = {
            'none': lambda defined_type, templates: None,
            'bool': lambda defined_type, templates: 'bool',
            'double': lambda defined_type, templates: 'f64',
            'int': lambda defined_type, templates: 'i64',
            'string': lambda defined_type, templates: 'Arc<str>',
            'bool_array': lambda defined_type, templates: 'Arc<[bool]>',
            'double_array': lambda defined_type, templates: 'Arc<[f64]>',
            'int_array': lambda defined_type, templates: 'Arc<[i64]>',
            'string_array': lambda defined_type, templates: 'Arc<[Arc<str>]>',
        }
        self.yaml_type_to_as_function = {
            yaml_type: 'get()' for yaml_type in self.defined_type_to_lang_type
        }
        self.lang_str_value_func = {
            'none': self.no_code,
            'bool': self.bool_to_str,
            'double': self.float_to_str,
            'int': self.int_to_str,
            'string': self.arc_str_to_str,
            'bool_array': lambda v: self.array_to_str(v, self.bool_to_str),
            'double_array': lambda v: self.array_to_str(v, self.float_to_str),
            'int_array': lambda v: self.array_to_str(v, self.int_to_str),
            'string_array': lambda v: self.array_to_str(v, self.arc_str_to_str),
        }
        self.python_val_to_str_func = {
            "<class 'bool'>": self.bool_to_str,
            "<class 'float'>": self.float_to_str,
            "<class 'int'>": self.int_arg_to_str,
            "<class 'str'>": self.str_to_str,
        }
        self.python_val_to_yaml_type = {
            "<class 'bool'>": 'bool',
            "<class 'float'>": 'double',
            "<class 'int'>": 'int',
            "<class 'str'>": 'str',
        }
        self.python_list_to_yaml_type = {
            "<class 'bool'>": 'bool_array',
            "<class 'float'>": 'double_array',
            "<class 'int'>": 'integer_array',
            "<class 'str'>": 'string_array',
        }

        self.open_bracket = '&['
        self.close_bracket = ']'

    @typechecked
    def get_func_signature(self, function_name: str, base_type: str) -> str:
        return function_name.replace('<>', '')

    @typechecked
    def initialization_fail_validation(self, param_name: str) -> str:
        return ''

    @typechecked
    def initialization_pass_validation(self, param_name: str) -> str:
        return ''

    @typechecked
    def update_parameter_fail_validation(self) -> str:
        return ''

    @typechecked
    def update_parameter_pass_validation(self) -> str:
        return ''

    @typechecked
    def no_code(self, s: Union[None, str]):
        return ''

    @typechecked
    def bool_to_str(self, cond: Union[None, bool]):
        if cond is None:
            return ''
        return 'true' if cond else 'false'

    @typechecked
    def float_to_str(self, num: Union[None, float, int]):
        if num is None:
            return ''
        str_num = str(float(num))
        if str_num == 'nan':
            return 'f64::NAN'
        if str_num == 'inf':
            return 'f64::INFINITY'
        if str_num == '-inf':
            return 'f64::NEG_INFINITY'
        return str_num

    @typechecked
    def int_to_str(self, num: Union[None, int]):
        if num is None:
            return ''
        return str(num)

    # an int argument on a double parameter may be a bound (f64) or a size (usize)
    @typechecked
    def int_arg_to_str(self, num: int):
        return f'{num} as _' if self.is_double else str(num)

    @typechecked
    def str_to_str(self, s: Union[None, str]):
        if s is None:
            return ''
        return rust_string_literal(s)

    @typechecked
    def arc_str_to_str(self, s: Union[None, str]):
        if s is None:
            return ''
        return f'Arc::from({rust_string_literal(s)})'

    @typechecked
    def array_to_str(self, values: Union[None, list], element_to_str):
        if values is None:
            return ''
        return 'Arc::from([' + ', '.join(element_to_str(x) for x in values) + '])'
