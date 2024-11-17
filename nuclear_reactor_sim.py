import numpy as np
import pandas as pd

class NuclearReactorSimulator:
    def __init__(self, pH0 = 11.0, power = 100.0, pressure  = 2100.0, temperature = 260.0, radioactivity = 10.0):
        """Initialize reactor simulator with initial conditions"""
        
        self.pH0 = pH0 # initial pH
        self.pH = pH0 # current pH, initially pH0
        self.h2 = self.calc_hydrogen() # current hydrogen concentration (cc/kg)
        self.total_gas = self.calc_total_gas()
        self.power = power # (%)
        self.pressure = pressure # (psi)
        self.temp = temperature # (C)
        self.radioactivity = radioactivity # (rad)
        self.time_step = 1 # (days)
        self.status = 0 # safe

        self.data_dict = {
            "Time": [],
            "pH": [], 
            "Hydrogen": [], 
            "Total Gas": [], 
            "Pressure": [], 
            "Radioactivity" : [],
            "Power" : [],
            "Reactor Safety" : [],
            "Condition": []
        }
    
    def calc_pH(self, time):
        """calculate pH  
        PARAMETERS: time(days), power(%), pH0  
        RETURN: pH
        """
        return self.pH0 - 0.25 * time * np.exp(self.power / 100)
    
    def calc_hydrogen(self):
        """Calculate hydrogen cconcentration 
        - range (10 - 60), midpoint: 35 
        RETURN: Hydrogen concentration (cc/kg)
        """
        return 0.01667 * self.pressure
    
    def calc_total_gas(self):
        """Sum of all gasses in coolant (H2, O2, N2, Ar)
        For simplicity, assume total air concentration is proportional to [H2]
        """
        return self.h2 * 2
    
    def air_injection_small(self, t):
        pass

    def air_injection_large(self, t):
        pass

    def fuel_element_failure_small(self, t):
        pass
        
    def fuel_element_failure_large(self, t):
        pass

    def resin_overheating_small(self, t):
        pass
        
    def resin_overheating_large(self, t):
        pass 

    def chemical_addition(self, t):
        pass

    def normal_conditions(self, t):
        pass
        
    def simulate_scenario(self, scenario, start, end):
        """Run Simulation
        Parameters:
        -----------
        scenario : str
            pertubation to system

        start : int
            time at which the scenario start (for continuous data)
        
        end : int
            time at which the scenario end (for continuous data)
            
        """
        
        for t in range(start, end):

            if scenario == "small_air_injection":
                self.air_injection_small(t)
            elif scenario == "large_air_injection":
                self.air_injection_large(t)
            elif scenario == "fuel_failure_small":
                self.fuel_element_failure_small(t)
            elif scenario == "fuel_failure_large":
                self.fuel_element_failure_large(t)
            elif scenario == "resin_overheating_small":
                self.resin_overheating_small(t)
            elif scenario == "resin_overheating_large":
                self.resin_overheating_large(t)
            elif scenario == "chemical_addition":
                self.chemical_addition(t)

            self.data_dict["Time"].append(t)
            self.data_dict["pH"].append(self.pH)
            self.data_dict["Hydrogen"].append(self.h2)
            self.data_dict["Total Gas"].append(self.total_gas)
            self.data_dict["Pressure"].append(self.pressure)
            self.data_dict["Radioactivity"].append(self.radioactivity)
            self.data_dict["Power"].append(self.power)
            self.data_dict["Reactor Safety"].append(self.status)
            self.data_dict["Condition"].append(scenario)

        print(f"{scenario} simulation complete")

        return 
    
    def get_data(self, filename):
        """Get data for Simulator and save as CSV and return DataFrame"""
        data = pd.DataFrame.from_dict(self.data_dict)
        data.to_csv(filename)
        return pd.DataFrame.from_dict(self.data_dict)
