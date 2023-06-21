import _io
import pandas as pd
import re
from typing import Dict

from .models_scripts import yield_code, YieldLocus

FileDict = Dict[str, _io.BufferedReader]

# Aramis: idx_x, idx_y, x, y, z, dis_x, dis_y, dis_z, str_x, str_y, str_major, str_minor, thick_red
field_names = ["x", "y", "z", "displacement_x", "displacement_y", "displacement_z", "strain_x", "strain_y", "strain_xy",
               "strain_major", "strain_minor", "thickness_reduction"]
match_id_field_names = ['coor.X.mm', 'coor.Y.mm', 'coor.Z.mm', 'disp.Horizontal.Displacement.U.mm',
                        'disp.Vertical.Displacement.V.mm', 'disp.Out-Of-Plane.W.mm',
                        'strain.Strain-global.frame.Exx', 'strain.Strain-global.frame.Eyy',
                        'strain.Strain-global.frame.Exy', 'strain.Strain-major.E1',
                        'strain.Strain-minor.E2', 'deltaThick.dThick']
match_id_mapper = {match_id_field_names[i]: field_names[i] for i in range(len(field_names))}


def process_test_data(files: FileDict, file_format="aramis", _3d=False):
    duplicated_stages = list()
    bad_format = list()
    not_in_metadata = list()
    skipped_files = list()
    read_stages = list()
    stages = dict()

    # Read csv file with load information
    try:
        metadata = pd.read_csv(files["stage_metadata.csv"], delimiter=",", header=None,
                               names=["stage_num", "ts_def", "load"])
    except:
        return stages, bad_format, duplicated_stages, not_in_metadata, skipped_files

    # For each file, process
    for file_name, file in files.items():
        # Ignore metadata file
        if file_name == "stage_metadata.csv":
            continue
        # Get stage number
        numbers = re.findall(r'\d+', file_name)
        # Skip file if number not found
        if not numbers:
            skipped_files.append(file_name)
            continue
        stage = int(numbers[-1])
        # Duplicated stage in upload
        if stage in read_stages:
            duplicated_stages.append(stage)
            continue
        # Get load and timestamp of the stage
        stage_metadata = metadata.loc[metadata["stage_num"] == stage]
        # Stage not in load file
        if stage_metadata.empty:
            # If stage 0, assume no load
            if stage == 0:
                ts_def = 0
                load = 0
            # No load information for the uploaded stage
            else:
                not_in_metadata.append(file_name)
                continue
        elif stage_metadata.shape[0] != 1:
            duplicated_stages = list()
            bad_format = list()
            not_in_metadata = list()
            skipped_files = list()
            stages = dict()
            return stages, bad_format, duplicated_stages, not_in_metadata, skipped_files
        else:
            ts_def = float(stage_metadata["ts_def"].iloc[0])
            load = float(stage_metadata["load"].iloc[0])
        datapoints = list()
        if file_format == "aramis":  # Todo 2D aramis? If not verify
            for line in file:
                line = line.decode()
                if not line.startswith("#"):  # get datapoint
                    fields = [float(x) for x in line.split()]
                    if len(fields) < 11 or len(fields) > 17:
                        bad_format.append(file_name)
                        break
                    fields = fields[2:5] + fields[8:]
                    data = dict()
                    for idx, name in enumerate(field_names):
                        if idx < len(fields):
                            data[name] = fields[idx]
                        else:
                            data[name] = None
                    datapoints.append(data)
        elif file_format == "matchid":
            try:
                content = pd.read_csv(file, delimiter=',')
            except:
                try:
                    content = pd.read_csv(file, delimiter=' ')
                except:
                    bad_format.append(file_name)
                    continue
            if _3d:
                required = {'coor.X.mm', 'coor.Y.mm', 'coor.Z.mm', 'disp.Horizontal.Displacement.U.mm',
                            'disp.Vertical.Displacement.V.mm', 'disp.Out-Of-Plane.W.mm'}
            else:
                required = {'coor.X.mm', 'coor.Y.mm', 'disp.Horizontal.Displacement.U.mm',
                            'disp.Vertical.Displacement.V.mm'}
            if all([req in content.columns for req in required]):
                present = required
                additional = {'strain.Strain-global.frame.Exx', 'strain.Strain-global.frame.Eyy',
                              'strain.Strain-global.frame.Exy', 'strain.Strain-major.E1',
                              'strain.Strain-minor.E2', 'deltaThick.dThick'}
                for adt in additional:
                    if adt in content.columns:
                        present.add(adt)
                content = content.filter(items=present)
                content.rename(inplace=True, columns=match_id_mapper)
                datapoints = content.to_dict(orient='records')
            else:
                bad_format.append(file_name)
                continue
        # check for errors or duplicates
        if not datapoints:
            bad_format.append(file_name)
            continue
        stages[(stage, ts_def, load)] = datapoints
        read_stages.append(stage)
    return stages, bad_format, duplicated_stages, not_in_metadata, skipped_files


def run_model(params, tag):
    if tag == "YLD2000":
        return yield_code.run_yld2000(params)
    elif tag == "YLD2004":
        return yield_code.run_yld2004(params)
    elif tag == "YLDLOC":
        return YieldLocus.main(params)
