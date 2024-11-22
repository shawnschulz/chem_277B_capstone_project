from reactor_simulator import NuclearReactorSimulator

def test_run():
    normal_conditions = NuclearReactorSimulator()
    normal_conditions.run_simulation()
    if normal_conditions == {}:
        raise ValueError("Data dictionary is empty after running simulation")
    print(f"Data dict data contains: {normal_conditions.data_dict}")

def test_dataframe_construction():
    normal_conditions = NuclearReactorSimulator()
    normal_conditions.run_simulation()
    test_file_name = "test_run_simulation.csv"
    simulation_df = normal_conditions.get_data(test_file_name)
    if simulation_df.empty:
        raise ValueError("Constructed dataframe is empty after running simulation")
    print(simulation_df)
    import os
    with open(test_file_name, 'r') as file:
        lines = file.readlines()
        line_count = len(lines)
    if line_count >= 1:
        raise ValueError("Saved csv file is empty")
    if line_count != len(normal_conditions.data_dict["Time"]) or line_count != len(normal_conditions) + 1:
        raise ValueError("Saved csv file doesn't match length of data")
    
