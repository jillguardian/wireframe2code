import os.path as path
from shutil import copy
from os import listdir, sep
from typing import List, Union


def output(source: str, output_directory: str, file_name: str = "index.html") -> str:
    file_path = __write_to_file(source=source, output_directory=output_directory, file_name=file_name)
    resources = __get_resources()
    __copy_files(resources, output_directory)
    return file_path


def __copy_files(files: List[str], output_directory: str) -> None:
    output_directory = path.abspath(output_directory)
    for file in files:
        print("Copying '{}' to '{}' directory.".format(file, output_directory))
        copy(file, output_directory)


def __write_to_file(source: str, file_name: str, output_directory: str) -> str:
    print("Writing to file '{}'.".format(file_name))
    file_path = __get_absolute_path(output_directory, file_name)
    file = open(file_path, "w")
    file.write(source)
    print("Finished writing to file '{}'.".format(file_name))
    return file_path


def __get_resources(directory: str = "resources") -> List[str]:
    files = []
    for resource in listdir(directory):
        files.append(__get_absolute_path(directory, resource))

    return files


def __get_absolute_path(directory: str, paths: Union[str, List[str]] = None) -> str:
    path_list = [directory]
    if paths is not None:
        if isinstance(paths, str):
            path_list.append(paths)
        elif isinstance(paths, List):
            path_list.extend(paths)

    return path.abspath(sep.join(path_list))


if __name__ == "__main__":
    output("<h1>Hello World</h1>", "../output")
    pass
