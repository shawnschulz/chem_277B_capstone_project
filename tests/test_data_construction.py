from scope_1 import NuclearReactorSimulator

def test_run():
    normal_conditions = NuclearReactorSimulator()
    normal_conditions.run_simulation()
    if normal_conditions.data_dict == {}:
        raise ValueError("Data dictionary is empty after running simulation")
    print(f"Data dict data contains: {normal_conditions.data_dict}")

def test_dataframe_construction():
    normal_conditions = NuclearReactorSimulator()
    normal_conditions.run_simulation()
    test_file_name = "test_run_simulation.csv"
    normalized_df = normal_conditions.normalize_values()
    normal_conditions.save_data(test_file_name)
    if normalized_df.empty:
        raise ValueError("Constructed dataframe is empty after running simulation")
    print(normalized_df)
    import os
    with open(test_file_name, 'r') as file:
        lines = file.readlines()
        line_count = len(lines)
    if line_count <= 1:
        raise ValueError("Saved csv file is empty")
    if not (line_count == len(normalized_df["Time"]) or line_count == len(normalized_df) + 1):
        raise ValueError("Saved csv file doesn't match length of data")
    
