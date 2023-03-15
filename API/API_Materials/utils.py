import _io

from typing import Dict

FileDict = Dict[str, _io.BufferedReader]

# Stage -> DataPoint
# Datapoint (required) -> idx_x, idx_y, x, y, z, dis_x, dis_y, dis_z, str_x, str_y, str_major, str_minor, thick_red


# TODO handle repeated stages
def process_test_data(files: FileDict, file_type="aramis"):
    field_names = ["x", "y", "z", "displacement_x", "displacement_y", "displacement_z", "strain_x", "strain_y",
                   "strain_major", "strain_minor", "thickness_reduction"]

    stages = dict()
    for file in files.values():
        stage = None  # TODO handle stage/ts not found
        ts_undef = None
        ts_def = None
        datapoints = dict()
        for line in file:
            line = line.decode()
            if file_type == "aramis":
                if line.startswith("# Stage :"):  # get stage
                    stage = int(float(line.split("-")[1].strip()))  # TODO maybe remove int cast?
                elif line.startswith("# Time  :  undeformt: "): # get timestamp
                    ts_undef = float(line.split()[4])
                elif line.startswith("#            deformt: "):  # get timestamp
                    ts_def = float(line.split()[2])
                elif not line.startswith("#"):  # get datapoint
                    fields = [float(x) for x in line.split()]
                    idx = (fields[0], fields[1])
                    fields = fields[2:5] + fields[8:]
                    if len(fields) == 6 or len(fields) < 11:
                        fields = fields + [None, None, None, None, None]
                    data = dict()
                    for idx2, name in enumerate(field_names):
                        data[name] = fields[idx2]
                    datapoints[idx] = data
                # TODO: AD channels?
            elif file_type == "matchid":
                # TODO
                pass
        stages[(stage, ts_undef, ts_def)] = datapoints
    return stages
