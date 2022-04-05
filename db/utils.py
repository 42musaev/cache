import json


def get_dump_data(path_file):
    with open(path_file) as json_file:
        data = json.load(json_file)
        data_dict = json.loads(data)
    return data_dict
