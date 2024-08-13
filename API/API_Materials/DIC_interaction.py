import _io

import numpy as np
import re
import json
from typing import Dict, List

from .DIC_processes import *
from .models import DICStage
from .models_scripts import yield_code, YieldLocus

import logging

logger = logging.getLogger(__name__)

FileDict = Dict[str, _io.BufferedReader]

# Aramis: idx_x, idx_y, x, y, z, dis_x, dis_y, dis_z, str_x, str_y, str_major, str_minor, thick_red
field_names = ["x", "y", "z", "displacement_x", "displacement_y", "displacement_z", "strain_x", "strain_y", "strain_xy",
               "strain_major", "strain_minor", "thickness_reduction"]
# match_id_field_names = ['coor.X.mm', 'coor.Y.mm', 'coor.Z.mm', 'disp.Horizontal.Displacement.U.mm',
#                         'disp.Vertical.Displacement.V.mm', 'disp.Out-Of-Plane.W.mm',
#                         'strain.Strain-global.frame.Exx', 'strain.Strain-global.frame.Eyy',
#                         'strain.Strain-global.frame.Exy', 'strain.Strain-major.E1',
#                         'strain.Strain-minor.E2', 'deltaThick.dThick']
match_id_field_names = ["x", "y", "xy", "displacement_x", "displacement_y", "displacement_xy", "strain_x", "strain_y",
                        "strain_xy", "strain_major", "strain_minor", "thickness_reduction"]

match_id_mapper = {match_id_field_names[i]: field_names[i] for i in range(len(field_names))}


match_id_multiple_files_field_names = ['x_pic', 'y_pic', '', 'u', 'v', '', 'exx', 'eyy', 'exy']
match_id_multiple_files_mapper = {match_id_multiple_files_field_names[i]: field_names[i]
                                  for i in range(len(match_id_multiple_files_field_names))}


datapoints_non_nullable_fields = ["x", "y", "displacement_x", "displacement_y"]
def process_dic_data(files: FileDict, file_format="aramis", _3d =False, file_identifiers_str=""):
    duplicated_stages = list()
    duplicated_fields = list()
    bad_format = list()
    not_in_metadata = list()
    skipped_files = list()
    read_stages = list()
    stages = dict()

    logger.debug(f"files: {files}")

    # {stage_num: {ts_def: val, load: val, field_name: points, x: points, ...}} if variables in a stage_num (aka the
    # keys of its dict) != minimum required, it fails. Also ts_def and load are "extra" variables
    multiple_stages = {}
    # {stage_num: {ts_def: val, load: val, file_identifier1: dataframe1 (points), file_identifier2: dataframe2, ...}}
    multiple_identifiers_stages = {}
    mat_size = []  # [x, y]

    # Read csv file with load information
    # May be ignored
    try:
        metadata = pd.read_csv(files["stage_metadata.csv"], delimiter=";")
    except:
        metadata = None

    # List of the id_number that are still missing another identifier to be completed (used in matchid)
    missing_identifiers = []

    file_identifiers = {}
    if file_format == "matchid":
        # Verify file_identifiers
        try:
            file_identifiers = json.loads(file_identifiers_str)
        except json.JSONDecodeError:
            bad_format.append("Not a valid json for file_identifiers!")
            return stages, bad_format, duplicated_stages, not_in_metadata, skipped_files

    # For each file, process
    for file_name, file in files.items():
        logger.debug(f"file: {file_name}")
        # Ignore metadata file
        if file_name == "stage_metadata.csv":
            continue
        # Get stage number
        numbers = re.findall(r'\d+', file_name)
        # Skip file if number not found
        if not numbers:
            skipped_files.append(file_name)
            continue
        stage = int(numbers[-1]) if file_format != "matchid_multiple_files" else int(numbers[-2])
        # Duplicated stage in upload
        if stage in read_stages and not file_format == "matchid_multiple_files":
            duplicated_stages.append(stage)
            continue

        # Get load and timestamp of the stage
        stage_metadata = metadata.loc[metadata["Time"] == stage] if metadata else None # May be None if not any metadata

        # Stage not in load file
        if not stage_metadata or stage_metadata.empty:
            # Assume no load
            # if stage == 0:
            ts_def = 0
            load = 0

        elif stage_metadata.shape[0] != 1:
            duplicated_stages = list()
            bad_format = list()
            not_in_metadata = list()
            skipped_files = list()
            stages = dict()
            return stages, bad_format, duplicated_stages, not_in_metadata, skipped_files

        else:
            ts_def = float(stage_metadata["TimeStamp"].iloc[0])
            load = float(stage_metadata[" Force [N]"].iloc[0])

        datapoints = list()
        if file_format == "aramis":  # TODO 2D aramis? If not verify
            datapoints = process_aramis(file_name, file, field_names, bad_format)
        elif file_format == "matchid":
            datapoints = process_match_id(file_name, file, match_id_mapper, bad_format,
                                          file_identifiers, stage, multiple_identifiers_stages)
            multiple_identifiers_stages[stage]["ts_def"] = ts_def
            multiple_identifiers_stages[stage]["load"] = load
            # if datapoints is None:
            #     continue
        elif file_format == "matchid_multiple_files":
            datapoints = process_match_id_multiple_files(stage, file_name, file, multiple_stages,
                                                         match_id_multiple_files_mapper, bad_format,
                                                         duplicated_fields, mat_size)
            multiple_stages[stage]["ts_def"] = ts_def
            multiple_stages[stage]["load"] = load

        # check for errors or duplicates
        if file_format == "matchid":
            continue

        if file_format != "matchid_multiple_files" and not datapoints:
            print("No datapoints?")
            bad_format.append(file_name)
            continue

        stages[(stage, ts_def, load)] = datapoints
        read_stages.append(stage)

    # Process stages if multiple files or matchid
    logger.debug("end first cycle")
    if file_format not in ["matchid_multiple_files", "matchid"]:
        return stages, bad_format, duplicated_stages, not_in_metadata, skipped_files

    if file_format == "matchid":
        stages = verify_match_id(multiple_identifiers_stages, bad_format, _3d)
        return stages, bad_format, duplicated_stages, not_in_metadata, skipped_files

    if file_format == "matchid_multiple_files":
        for stage, data in multiple_stages.items():
            ts_def = data.pop("ts_def")
            load = data.pop("load")
            datapoints = list()
            for x in range(mat_size[0]):
                for y in range(mat_size[1]):
                    skip_current = False
                    datapoint = dict()
                    for field, points in data.items():
                        point = points.iloc[x, y]
                        if np.isnan(point) and field in datapoints_non_nullable_fields:
                            skip_current = True
                            break
                        datapoint[field] = point
                    if skip_current:
                        continue
                    datapoints.append(datapoint)
            stages[(stage, ts_def, load)] = datapoints

        return stages, bad_format, duplicated_stages, not_in_metadata, skipped_files




def update_metadata(metadata_file : _io.BufferedReader, dic_stages : List[DICStage]):
    # Read csv file with load information
    # May be ignored
    not_in_metadata = list()
    invalid_metadata = False
    try:
        metadata = pd.read_csv(metadata_file, delimiter=";")
    except: # TODO: Check for specific exception
        invalid_metadata = True
        return not_in_metadata, invalid_metadata, dic_stages
        # return stages, bad_format, duplicated_stages, not_in_metadata, skipped_files

    for dic_stage in dic_stages:
        stage_num = dic_stage.stage_num
        # Get load and timestamp of the stage
        stage_metadata = metadata.loc[metadata["Time"] == stage_num]

        # Stage not in load file
        if stage_metadata.empty:
            # If stage 0, assume no load
            if stage_num == 0:
                ts_def = 0
                load = 0

            # No load information for the uploaded stage
            else:
                not_in_metadata.append(dic_stage)
                continue

        # File in metadata :D
        else:
            ts_def = float(stage_metadata["TimeStamp"].iloc[0])
            load = float(stage_metadata[" Force [N]"].iloc[0])

        dic_stage.timestamp_def = ts_def
        dic_stage.load = load

    return not_in_metadata, invalid_metadata, dic_stages



def run_model(params, tag):
    if tag == "YLD2000":
        return yield_code.run_yld2000(params)
    elif tag == "YLD2004":
        return yield_code.run_yld2004(params)
    elif tag == "YLDLOC":
        return YieldLocus.main(params)