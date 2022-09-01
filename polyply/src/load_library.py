# Copyright 2020 University of Groningen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pathlib
import vermouth
from vermouth.gmx.rtp import read_rtp
from vermouth.citation_parser import read_bib
from vermouth.log_helpers import StyleAdapter, get_logger
from polyply import DATA_PATH
from .ff_parser_sub import read_ff
from .build_file_parser import read_build_file
from .polyply_parser import read_polyply
from .topology import Topology

LOGGER = StyleAdapter(get_logger(__name__))
FORCE_FIELD_PARSERS = {'rtp': read_rtp, 'ff': read_ff, 'itp': read_polyply, 'bib': read_bib}


def _resolve_lib_paths(lib_names, data_path, allowed_extensions):
    """
    select the appropiate files from data_path
    according to library names given.

    Parameters
    ----------
    lib_names: list[`os.path`]
        list of library names
    data_path:
        location of library files
    allowed_extensions: list[str]
         list of allowed file extensions
    """
    files = []
    for name in lib_names:
        directory = os.path.join(data_path, name)
        for _file in os.listdir(directory):
            _, file_extension = os.path.splitext(_file)
            if file_extension in allowed_extensions:
                _file = os.path.join(directory, _file)
                files.append(_file)
    return files


def read_ff_from_files(paths, force_field):
    """
    read the input files for the defintion of blocks and links.

    Parameters
    ----------
    paths: list[`os.path`]
           List of valid file paths
    force_field: class:`vermouth.force_field.ForceField`

    Returns
    -------
    force_field: class:`vermouth.force_field.ForceField`
       updated forcefield

    """

    def wrapper(parser, path, force_field):
        with open(path, 'r') as file_:
            lines = file_.readlines()
            parser(lines, force_field=force_field)

    for path in paths:
        path = pathlib.Path(path)
        file_extension = path.suffix.casefold()[1:]

        parser = FORCE_FIELD_PARSERS[file_extension]
        wrapper(parser, path, force_field)

    return force_field


def load_ff_library(name, lib_names, extra_files):
    """
    Load libraries and extra-files into vermouth
    force-field.

    Parameters
    ----------
    name: str
      Force-field name
    lib_names: list[`os.path`]
      List of lirbary names
    extra_files: list[`os.path`]
      List of extra files to include

    Returns
    -------
    :class:`vermouth.forcefield.Forcefield`
    """
    force_field = vermouth.forcefield.ForceField(name)
    if lib_names and extra_files:
        lib_files = _resolve_lib_paths(lib_names, DATA_PATH,
                                       FORCE_FIELD_PARSERS.keys())
        all_files = lib_files + extra_files
    elif lib_names:
        all_files = _resolve_lib_paths(lib_names, DATA_PATH,
                                       FORCE_FIELD_PARSERS.keys())
    elif extra_files:
        all_files = extra_files

    read_ff_from_files(all_files, force_field)
    return force_field


def read_from_build_files(paths, topology):
    """
    read the input files for the build file options.

    Parameters
    ----------
    paths: list[`os.path`]
           List of valid file paths
    force_field: class:`vermouth.force_field.ForceField`

    Returns
    -------

    """
    for path in paths:
        with open(path, 'r') as file_:
            lines = file_.readlines()
            read_build_file(lines, topology.molecules, topology)


def load_build_options(topology, build_file, lib_names):
    """
    Load build file options and molecule templates into topology.

    Parameters
    ----------
    topology: :class:`polyply.src.topology`
    build_file: str
        List of build files to parse
    lib_names: list[str]
        List of library names for which to load templates

    Returns
    -------

    """
    if lib_names and build_files:
        lib_files = _resolve_lib_paths(lib_names, DATA_PATH, ['bld'])
        all_files = lib_files + [build_file]
    elif lib_names:
        all_files = _resolve_lib_paths(lib_names, DATA_PATH, ['bld'])
    elif build_file:
        all_files = [build_file]
    else:
        return

    read_from_build_files(all_files, topology)
