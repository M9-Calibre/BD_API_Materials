import _io
import pandas as pd


def process_aramis(file_name: str, file: _io.BufferedReader, field_names: list[str],
                   bad_format: list):
    datapoints = list()
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
    return datapoints


def process_match_id(file_name: str, file: _io.BufferedReader, match_id_mapper: dict[str, str], bad_format: list, _3d=False):
    try:
        content = pd.read_csv(file, delimiter=',')
        if content.shape[1] < 4:
            file.seek(0, 0)
            content = pd.read_csv(file, delim_whitespace=True)
            if content.shape[1] < 4:
                print(f"bad content shape: {content.shape[1]}")
                bad_format.append(file_name)
                return None
    except:
        print("Bad format exception error")
        bad_format.append(file_name)
        return None
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
        return datapoints
    else:
        print("No all required columns")
        bad_format.append(file_name)
        return None

def process_match_id_multiple_files(stage: int, file_name: str, file: _io.BufferedReader, stages: dict[int, dict],
                                    match_id_multiple_files_mapper : dict, bad_format: list, duplicated_fields: list, mat_size: list[int]):
    # Process stage_field dictionary
    if stage not in stages:
        stages[stage] = {}
    field = file_name.split("_")[-1].split(".")[0]
    # Situation for "x_pic" and "y_pic"
    if field == "pic":
        field = file_name.split("_")[-2] + "_pic"

    if field not in match_id_multiple_files_mapper.keys():
        print(f"{field} not in field names.")
        bad_format.append(file_name)
        return None
    current_stage = stages[stage]
    if field in current_stage:
        duplicated_fields.append(file_name)
        return None


    # Create datapoints
    # try:
    content = pd.read_csv(file, delimiter=';')
    if not mat_size:
        mat_size.append(content.shape[0])
        mat_size.append(content.shape[1])

    current_stage[match_id_multiple_files_mapper[field]] = content

    return content

