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


def process_match_id(file_name: str, file: _io.BufferedReader, match_id_mapper: dict[str, str], bad_format: list,
                     file_identifiers: dict[str, dict], stage: int, stages_points: dict[int, dict]):
    # file_identifiers = {"identifier_name": {"field_name": 0 # N_COL}}

    # Process stage_field dictionary
    if stage not in stages_points:
        stages_points[stage] = {"filename": file_name}
    try:
        content, identifier = check_and_replace_headers(file_name, file, file_identifiers)
        stages_points[stage][identifier] = content

        content.rename(inplace=True, columns=match_id_mapper)
        # datapoints = content.to_dict(orient='records')

    # Bad File (Parser Error)
    except pd.errors.ParserError as e:
        print(f"Bad format exception error: {e}")
        bad_format.append(file_name)


def verify_match_id(stages_points: dict[str, dict], bad_format: list, _3d=False):
    stages = {}

    if _3d:
        required = {'x', 'y', 'xy', 'displacement_x',
                    'displacement_y', 'displacement_xy'}
    else:
        required = {'x', 'y', 'displacement_x',
                    'displacement_y'}

    for stage, stage_identifiers in stages_points.items():
        datapoints = []

        # Stage identifier is "{
        # 		field1: dataframe1,
        # 		field2: dataframe2,
        #       filename: filename
        # 	}"

        stage_content = None
        ts_def = stage_identifiers["ts_def"]
        load = stage_identifiers["load"]
        # Merge identifiers' dataframes of the same stage

        for stage_identifier, content in stage_identifiers.items():
            if stage_identifier in ["filename", "ts_def", "load"]:
                continue

            if stage_content is None:
                stage_content = content
            else:
                stage_content = stage_content.merge(content, how='outer', left_index=True, right_index=True)

        if all([req in stage_content.columns for req in required]):
            present = required
            content = stage_content.filter(items=present)
            datapoints = content.to_dict(orient='records')
            stages[(stage, ts_def, load)] = datapoints
        else:
            print("No all required columns")
            bad_format.append(stage_identifiers["filename"])
            return None

    return stages

    # field = file_name.split("_")[-1].split(".")[0]
    # # Situation for "x_pic" and "y_pic"
    # if field == "pic":
    #     field = file_name.split("_")[-2] + "_pic"
    #
    # if field not in match_id_multiple_files_mapper.keys():
    #     print(f"{field} not in field names.")
    #     bad_format.append(file_name)
    #     return None
    # current_stage = stages[stage]
    # if field in current_stage:
    #     duplicated_fields.append(file_name)
    #     return None
    #
    # # Create datapoints
    # # try:
    # content = pd.read_csv(file, delimiter=';')
    # if not mat_size:
    #     mat_size.append(content.shape[0])
    #     mat_size.append(content.shape[1])
    #
    # current_stage[match_id_multiple_files_mapper[field]] = content

    # try:
    #     content = pd.read_csv(file, delimiter=',')
    #     if content.shape[1] < 4:
    #         file.seek(0, 0)
    #         content = pd.read_csv(file, delim_whitespace=True)
    #         if content.shape[1] < 4:
    #             print(f"bad content shape: {content.shape[1]}")
    #             bad_format.append(file_name)
    #             return None
    # except:
    #     print("Bad format exception error")
    #     bad_format.append(file_name)
    #     return None

    # print(f"{content=}")
    # print(f"{content.columns=}")

    # if _3d:
    #     required = {'coor.X.mm', 'coor.Y.mm', 'coor.Z.mm', 'disp.Horizontal.Displacement.U.mm',
    #                 'disp.Vertical.Displacement.V.mm', 'disp.Out-Of-Plane.W.mm'}
    # else:
    #     required = {'coor.X.mm', 'coor.Y.mm', 'disp.Horizontal.Displacement.U.mm',
    #                 'disp.Vertical.Displacement.V.mm'}
    # if all([req in content.columns for req in required]):
    #     present = required
    #     additional = {'strain.Strain-global.frame.Exx', 'strain.Strain-global.frame.Eyy',
    #                   'strain.Strain-global.frame.Exy', 'strain.Strain-major.E1',
    #                   'strain.Strain-minor.E2', 'deltaThick.dThick'}
    #     for adt in additional:
    #         if adt in content.columns:
    #             present.add(adt)
    #     content = content.filter(items=present)
    #     content.rename(inplace=True, columns=match_id_mapper)
    #     datapoints = content.to_dict(orient='records')
    #     return datapoints
    # else:
    #     print("No all required columns")
    #     bad_format.append(file_name)
    #     return None


def process_match_id_multiple_files(stage: int, file_name: str, file: _io.BufferedReader, stages: dict[int, dict],
                                    match_id_multiple_files_mapper: dict, bad_format: list, duplicated_fields: list,
                                    mat_size: list[int]):
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


# ----- Other Functions -----
def check_and_replace_headers(filename, csv_file, identifiers):
    # Identifiers follow the structure: {
    # 	"identifier_name": {
    # 		"header_name_1": 0, # Integer that represents the column idx in the csv
    #       "header_name_2": 5
    # 	}
    # }

    # Read the CSV file without headers to inspect the first row
    df = pd.read_csv(csv_file, sep=';', header=None)

    # Check if the first row is composed entirely of numbers or NaNs
    # If the first row is all numbers or NaNs, we assume there are no headers
    first_row = df.iloc[0]
    if any(first_row.apply(lambda x: not isinstance(x, (int, float)) and not pd.isna(x))):
        # If headers are detected, read the CSV file again with headers
        csv_file.seek(0)  # Reset the file pointer to allow a re-read
        df = pd.read_csv(csv_file, sep=';')

    # Find the identifier for the current file
    identified_columns = None
    identifier = None
    for identifier_name, columns in identifiers.items():
        if identifier_name in filename:
            identifier = identifier_name
            identified_columns = columns
            break

    if identified_columns is None:
        # TODO: not be a raise
        raise ValueError(f"No identifier found for file: {filename}")

    # Replace only the identified headers
    new_headers = list(df.columns)  # Start with existing headers
    for header_name, col_idx in identified_columns.items():
        if col_idx < len(new_headers):
            new_headers[col_idx] = header_name

    # Assign new headers
    df.columns = new_headers

    # Remove columns not included in identified_columns
    df = df.loc[:, df.columns.isin(list(identified_columns.keys()))]

    return df, identifier