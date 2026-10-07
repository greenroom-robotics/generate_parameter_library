#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import sys

from generate_parameter_library_py.parse_yaml import GenerateCode


def run(output_file, yaml_file, validation_module=''):
    gen_param_struct = GenerateCode('rust')
    gen_param_struct.parse(yaml_file, validation_module)
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(str(gen_param_struct))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('output_rust_file')
    parser.add_argument('input_yaml_file')
    parser.add_argument('validate_module', nargs='?', default='')
    return parser.parse_args()


def main():
    args = parse_args()
    run(args.output_rust_file, args.input_yaml_file, args.validate_module)


if __name__ == '__main__':
    sys.exit(main())
