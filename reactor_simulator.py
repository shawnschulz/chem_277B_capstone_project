import numpy as np
import pandas as pd
import random

class NuclearReactorSimulator:
    def __init__(self, pH_0 = 11.0,             # Initial pH
                 power = 100.0,                 # Initial reactor power
                 pressure  = 2100.0,            # Initial pressure
                 temperature = 500,             # Initial temperature
                 h2 = 50,                       # Initial hydrogen concentration
                 total_gas = 60,                # Initial total_gas concentration
                 radioactivity = 10.0,          # Initial radioactivity
                 volume = 20000,                # Initial volume
                 ):
        """Initialize reactor simulator with initial conditions"""
        
        # Reactor plant parameters
        self.pH = pH_0                          # current pH, initially pH0
        self.power = power                      # current reactor power (%)
        self.pressure = pressure                # current pressure (psi)
        self.h2 = h2                            # current hydrogen concentration (cc/kg)
        self.total_gas = total_gas              # current TG concentration (cc/kg)
        self.temp = temperature                 # current temperature (Degrees Fahrenheit)
        self.radioactivity = radioactivity      # current radioactivity (rad)
        #self.volume = volume                   # current volume gallons
        self.status = 0                         # safe

        # Casualty flags
        self.injection_of_air_flag = False          # Flag for injection of air
        self.injection_of_air_degree = False        # Determination for small or large
        self.resin_overheat_flag = False            # Flag for resin overheat
        self.resin_overheat_degree = False          # Determination for small or large
        self.fuel_element_failure_flag = False      # Flag for fuel element failure
        self.fuel_element_failure_degree = False    # Determination for small or large

        # Simulation parameters
        self.monitoring_pressure = True         # Sanity check to avoid overpressure casualty
        self.charging_in_progress = False       # Are we currently charging to the plant
        self.charging_start = None              # Charging start time
        self.charging_duration = None           # Charging duration based on number of pumps.
        self.time_now = 0                       # (minutes) Current simulation time
        self.time_since_safe = None
        
        # Container to store artificial dataset
        self.data_dict = {
            "Time": [],
            "pH": [], 
            "Hydrogen": [], 
            "Total Gas": [],
            "Temperature": [], 
            "Pressure": [], 
            "Radioactivity" : [],
            "Power" : [],
            "Reactor Safety" : [],
        }
    
    def run_simulation(self, simulation_time = 3*24*60):      # Simulation time of 4320 minutes (3 days)
        """Run the simulation over the specified time range"""

        while self.time_now < simulation_time:
            # Update time for this iteration
            self.time_now += 1

            # Some code to ensure the reactor has been safe for a while before another casualty starts
            if self.status == 0:
                self.time_since_safe += 1
            else:
                self.time_since_safe = 0

            # Determine reactor plant parameters for this iteration
            self.reactor_plant_parameters()

            # Provide random chance each iteration for a resin overheat or fuel element failure to occur.
            if self.time_since_safe >= 60 and self.status == 0:
                self.casualty()

            # Append reactor plant parameters to the dictionary at the end of the time step
            self.append_data()

    def append_data(self):
        """Store the current state of the reactor."""
        self.data_dict["Time"].append(self.time_now)
        self.data_dict["pH"].append(self.pH)
        self.data_dict["Hydrogen"].append(self.h2)
        self.data_dict["Total Gas"].append(self.total_gas)
        self.data_dict["Temperature"].append(self.temp)
        self.data_dict["Pressure"].append(self.pressure)
        self.data_dict["Radioactivity"].append(self.radioactivity)
        self.data_dict["Power"].append(self.power)
        self.data_dict["Reactor Safety"].append(self.status)

    def reactor_plant_parameters(self):
        """
        Determine reactor plant parameters for this iteration
        """
        ##########################################################################
        # Calculate current pH as a function of time and reactor power
        self.pH = self.pH - 0.25 * self.time_now * np.exp(self.power / 100)

        ##########################################################################
        def calc_h2():
            """
            Function to calculate hydrogen as a function of pressure and diffusion
            """
            h2_conc_pressure = 1        # Finish this equation
            h2_conc_loss_diffusion = 1  # Finish this equation
            return h2_conc_pressure - h2_conc_loss_diffusion
        self.h2 = calc_h2()

        ###########################################################################
        def calc_total_gas():
             """
             Function to calculate total gas during normal operation and
             injection of air casualty.
             """
             pass
        self.total_gas = calc_total_gas()

        ###########################################################################
        def calc_temperature():
             """
             Function to calculate tmeperature as a fucntion of time.
             """
             pass   # Calculate temperature as a function of time.
        self.temp = calc_temperature()

        ###########################################################################
        def calc_pressure():
            """
            Function to calculate pressure as a function of time and charging.
            """
            if self.charging_in_progress:
                self.plant_maintenance()
            else:
                 pass   # Calculate pressure as a function of time.
        self.pressure = calc_pressure()

        ###########################################################################
        # Set a trigger for plant maintenance to maintain controllable parameters
        # in specification.
        # Note: triggers are offset slightly from the limit to maintain a safety margin.
        if self.pH <= 10.2 or self.total_gas > 70 or self.h2 < 15:
                self.plant_maintenance()

        # Determine if plant maintenance has caused an injection of air casualty.
        if self.injection_of_air_flag == True:
                self.casualty()
                
        ###########################################################################
        # Determine if any of the reactor plant parameters are outside
        # of their operating bands (0 = Rx safe, 1 = Rx not safe).
        if self.pH < 10.0 or self.pH > 11.0:
            self.status = 1
        elif self.power > 100:
            self.status = 1
        elif self.pressure < 2000 or self.pressure > 2200:
            self.status = 1
        elif self.total_gas > 75:
            self.status = 1
        elif self.temp < 485 or self.temp > 515:
            self.status = 1
        elif self.h2 < 10 or self.h2 > 60:
            self.status = 1
        elif self.radioactivity > 15:
            self.status = 1
        else:
            self.status = 0

    def plant_maintenance(self):
        # Give the reactor plant workers an 80% chance of monitoring reactor plant pressure
        # to prevent an overpressure casualty while performing the chemical addition.
        self.monitoring_pressure = random.choices([True, False], weights = [80, 20])[0]

        # If the reactor plant pressure is being monitored, do not charge until pressure is
        # less than 2060 psi, otherwise charge immediately.
        if self.monitoring_pressure == True and self.pressure <= 2060:
            chemical_addition()
        elif not self.monitoring_pressure:
            chemical_addition()

        
        
        def chemical_addition():
            """
            Function to add chemicals for pH or Hydrogen after a casualty
            """
            # Determine how many pumps we will use for the chemical addition.
            pumps = random.choice([1, 2, 3])                
                
            # Case for adding pH chemicals.
            if self.pH < 10.2 and not self.charging_in_progress:        # Cannot add pH while adding hydrogen
                self.charging_in_progress = True                        # Tag for charging is true.
                self.charging_start = self.time_now
                self.charging_duration = {1:30,
                                          2:20,
                                          3:10}[pumps]
                
                # Give some probability of an injection of air casualty occuring during the chemical addition
                self.injection_of_air_flag = random.choices([True, False], weights = [30, 70])[0]


            # Case for adding hydrogen.
            #something for h2
            pass

        def vent_gas(self):
            pass

    def casualty(self):
        """
        Function to handle casualties
        """
        # Determine some random probability each iteration for a casualty to occur
        self.resin_overheat_flag = random.choices([True, False], weights = [5, 95])[0]
        self.fuel_element_failure_flag = random.choices([True, False], weights = [5, 95])[0]

        if self.injection_of_air_flag == True:
            injection_of_air()
        if self.resin_overheat_flag == True:
            resin_overheat()
        if self.fuel_element_failure_flag == True:
            fuel_element_failure()
        
        def injection_of_air():
            # Air is added while charging
            elapsed_time = self.time_now - self.charging_start

            # Determine if it is a small or large air injection (True = small, False = large)
            self.injection_of_air_degree = random.choices([True, False], weights = [60, 40])[0]

            # Small injection of air casualty
            if self.injection_of_air_degree:
                h2_decrease = random.uniform(10, self.pH)        
                self.h2 = h2_decrease * elapsed_time / self.charging_duration
                self.total_gas = calc_total_gas()

                if self.h2 < 10 or self.total_gas > 75:
                    self.status = 1     # Reactor not safe

            # Large injection of air casualty
            else:
                h2_decrease = self.h2       # Drop H2 to zero by the time charging is complete.
                self.h2 = h2_decrease * elapsed_time / self.charging_duration
                self.total_gas = self.calc_total_gas()

                if self.h2 < 10 or self.total_gas > 75:
                    self.status = 1     # Reactor not safe

        def resin_overheat():
            self.resin_overheat_degree = False          # Determination for small or large
            pass

        def fuel_element_failure():
            self.fuel_element_failure_degree = False    # Determination for small or large
            pass

        
            