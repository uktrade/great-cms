import json
import os
import sys


def print_usage():
    print('Usage: python -m update_params <json file name>')  # noqa T201
    sys.exit(1)


def update_params(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
        for param in data:
            name = param['Name']
            value = param['Value']
            _type = param['Type']
            overwrite = param['Overwrite']
            if overwrite:
                over_str = '--overwrite'
            else:
                over_str = '--no-overwrite'
            cmd = f'aws ssm put-parameter --name "{name}" --type {_type} --value "{value}" {over_str}'
            ret = os.system(cmd)
            print(ret)  # noqa T201


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
    file_name = sys.argv[1]
    update_params(file_name)
