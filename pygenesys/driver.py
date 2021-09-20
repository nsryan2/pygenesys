#! /usr/bin/env python

import numpy as np
import importlib
import inspect
import argparse
import os
import sys
import sqlite3

# custom imports
from pygenesys import model_info
from pygenesys.technology.technology import Technology
from pygenesys.commodity.commodity import *

def name_from_path(infile_path):
    """
    Returns just the base of the filename from the path.

    Parameters
    ----------
    infile_path : string
        The path to PyGenesys input file
        (absolute, relative, or missing extensions are okay)

    Returns
    -------
    file_name_base : string
        The base name without the extension or path
    """
    file_dir = os.path.dirname(infile_path)
    sys.path.append(file_dir)
    file_name = os.path.basename(infile_path)
    file_name_base = os.path.splitext(file_name)[0]
    return file_name_base


def load_infile(infile_path):
    """
    Loads the input file as a python package import based on the path.

    Parameters
    ----------
    infile_path : string
        The path to the PyGenesys input file.

    Returns
    -------
    infile : Python module
        The PyGenesys input file imported as a python
        module.
    """
    file_name = name_from_path(infile_path)
    infile = importlib.import_module(file_name)
    return infile


def collect_technologies(module_name):
    """
    Collects the technologies from the PyGenesys input file.

    Parameters
    ----------
    module_name : python module
        The PyGenesys input file once imported. Should be "infile."
    """
    technologies = []

    for member, attrib in inspect.getmembers(module_name):
        try:
            string_attr = str(attrib)
        except BaseException:
            string_attr = ''

        if 'Technology' in string_attr:
            print(f"{member} is Technology")
            technologies.append(getattr(module_name, member))
            print(f"using isinstance: {isinstance(attrib, Technology)}")

    return technologies


def _collect_commodities(technology_list):
    """
    Collects the unique commodities from the PyGenesys input file.
    """

    demand = {}
    resource = {}
    emission = {}

    for tech in technology_list:
        for region in tech.regions:
            input_comm = tech.input_comm[region]
            output_comm = tech.output_comm[region]
            emissions = tech.emissions[region]

            # check the input commodity type
            if isinstance(input_comm, Commodity):
                # resource
                pass
            elif isinstance(input_comm, DemandCommodity):
                print(f"Warning: Input commodity of {tech.tech_name}" \
                      f"is a Demand Commodity.")
                # demand
                pass
            elif isinstance(input_comm, EmissionCommodity):
                # emission
                print(f"Warning: Input commodity of {tech.tech_name}" \
                      f"is an Emission Commodity.")
                pass

            if isinstance(output_comm, Commodity):
                # resource
                pass
            elif isinstance(output_comm, DemandCommodity):
                # demand
                pass
            elif isinstance(output_comm, EmissionCommodity):
                # emission
                print(f"Warning: Output commodity of {tech.tech_name}" \
                      f"is an Emission Commodity. Skipped.")
                pass



    return commodities


def main():

    # Read commandline arguments
    ap = argparse.ArgumentParser(description='PyGenesys Parameters')
    ap.add_argument('--infile', help='the name of the input file')
    args = ap.parse_args()
    print(f"Reading input from {args.infile} \n")

    infile = load_infile(args.infile)
    out_db = infile.database_filename
    try:
        out_path = infile.curr_dir + "/" + out_db
    except BaseException:
        out_path = "./" + out_db

    # get infile technologies
    technology_list = collect_technologies(infile)

    # create the model object
    model = model_info.ModelInfo(output_db=out_path,
                                 scenario_name=infile.scenario_name,
                                 start_year=infile.start_year,
                                 end_year=infile.end_year,
                                 N_years=infile.N_years,
                                 N_seasons=infile.N_seasons,
                                 N_hours=infile.N_hours,
                                 demands=infile.demands_list,
                                 resources=infile.resources_list,
                                 emissions=infile.emissions_list,
                                 technologies=technology_list,
                                 reserve_margin=infile.reserve_margin,
                                 global_discount=infile.discount_rate
                                 )
    print(f"Database will be exported to {model.output_db} \n")

    # print('=========================\n')
    # print(f"{technology_list}")
    # print('=========================\n')

    print(f"The years simulated by the model are \n {model.time_horizon} \n")

    # Should check if the model is to be written to a sql or sqlite database
    model._write_sqlite_database()

    print("Input file written successfully.\n")

    return
