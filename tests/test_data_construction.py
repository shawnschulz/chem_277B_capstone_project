from reactor_simulator import NuclearReactorSimulator

def test_run():
    normal_conditions = NuclearReactorSimulator()
    normal_conditions.run_simulation()
    assert normal_conditions.data_dict != {}, "Data dictionary is empty after running simulation"
    print(f"Data dict data contains: {normal_conditions.data_dict}")
