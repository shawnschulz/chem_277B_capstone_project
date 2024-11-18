import numpy as np
import pandas as pd

class NuclearReactorSimulator:
    def __init__(self, pH0 = 11.0, power = 100.0, pressure  = 2100.0, temperature = 260.0, radioactivity = 10.0):
        """Initialize reactor simulator with initial conditions"""
        
        self.pH0 = pH0 # initial pH
        self.pH = pH0 # current pH, initially pH0
        self.power = power # (%)
        self.pressure = pressure # (psi)
        self.h2 = self.calc_hydrogen() # current hydrogen concentration (cc/kg)
        self.total_gas = self.calc_total_gas()
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
    
    def air_injection_small(self):
        pass

    def air_injection_large(self):
        pass

    def fuel_element_failure(self, start, end, small = True, gradual = True):
        """Fuel Element Failure
        - radioactivity increases
        - reactor not safe
        - run normal conditions prior to establish baseline
        """
        # 1. Determine radioactivity after failure
        if small: # radiation changes on scale of 10
            increase_rad = np.random.uniform(10, 50)
        else: # radioacticity changes on scale of 100
            increase_rad = np.random.uniform(100, 500)
  
        end_rad = self.radioactivity + increase_rad

        # 2. processes each time step
        for t in range(start, end):
            
            # 2a. increase radioactivity
            if gradual and self.radioactivity < end_rad:
                # radioactivity increases by random amount within predetermined limit
                self.radioactivity += increase_rad / np.random.uniform(10, 50)

            else: # instantaneous increase or plateau
                self.radioactivity = end_rad
   
            # 2b. calculate power and pH based on new radioacitivty
            self.power = 100 * (1 - np.exp(-self.radioactivity / 100)) # radiation and power: exponential relaitonship

            self.pH = self.calc_pH(t) # pH as a function of power and time:

            # 2c. Safety Check
            if self.radioactivity > 15:
                self.status = 1 # not safe
            else:
                self.status = 0 # safe

            # 2d. Add noise to other parameters
            self.pressure = np.random.uniform(-10, 10) # (psi)
            self.h2 = self.calc_hydrogen()
            self.total_gas = self.calc_total_gas()
            self.temp += np.random.uniform(-5, 5)

            # 2e. store data for this timestep
            if small:
                self.set_data(t, 'Fuel Element Failure Small')
            else: 
                self.set_data(t, 'Fuel Element Failure Large')
        
        # # 3. Return stored data
        # return self.get_data(filename)

    def resin_overheating_small(self):
        pass
        
    def resin_overheating_large(self):
        pass 

    def chemical_addition(self):
        pass

    def normal_conditions(self):
        pass
        
    
    def set_data(self, t, condition):
        """Assign data"""
        self.data_dict["Time"].append(t)
        self.data_dict["pH"].append(self.pH)
        self.data_dict["Hydrogen"].append(self.h2)
        self.data_dict["Total Gas"].append(self.total_gas)
        self.data_dict["Pressure"].append(self.pressure)
        self.data_dict["Radioactivity"].append(self.radioactivity)
        self.data_dict["Power"].append(self.power)
        self.data_dict["Reactor Safety"].append(self.status)
        self.data_dict["Condition"].append(condition) 
    
    def get_data(self, filename):
        """Get data for Simulator and save as CSV and return DataFrame"""
        data = pd.DataFrame.from_dict(self.data_dict)
        data.to_csv(filename)
        return pd.DataFrame.from_dict(self.data_dict)
