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
        self.vent_gas_in_progress = False       # Are we venting gas (reducing TG)
        self.vent_gas_start = None              # Venting start time
        self.charging_in_progress = False       # Are we currently charging to the plant
        self.charging_start = None              # Charging start time
        self.charging_duration = None           # Charging duration based on number of pumps.
        self.add_pH = False                     # Flag for adding pH
        self.add_h2 = False                     # Flag for adding hydrogen
        self.degas = False                      # Flag for degas
        self.time_now = 0                       # (minutes) Current simulation time
        self.time_since_safe = 0

        # Parameter Update Flags
        self.pressure_updated = False
        self.temp_updated = False
        self.pH_updated = False
        self.total_gas_updated = False
        self.h2_updated = False
        self.radioactivity_updated = False
        
        
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
            "Injection of Air": [],
            "Injection of Air Degree": [],
            "Resin Overheat": [],
            "Resin Overheat Degree": [],
            "Fuel Element Failure": [],
            "Fuel Element Failure Degree": [],
            "Chemical Addition": [],
            "Vent Gas": []
        }
###########################################################################################################
###########################################################################################################
# The following code will perform the simulation run
###########################################################################################################
###########################################################################################################

    def run_simulation(self, simulation_time = 3*24*60):      # Simulation time of 4320 minutes (3 days)
        """Run the simulation over the specified time range"""

        while self.time_now < simulation_time:
            # Append reactor plant parameters to the dictionary for the previous time step
            self.append_data()

            # Update time for this iteration
            self.time_now += 1

            # Some code to ensure the reactor has been safe for a while before another casualty starts
            if self.status == 0:
                self.time_since_safe += 1
            else:
                self.time_since_safe = 0

            # Reset parameter update flags to false for this iteration            
            self.pressure_updated = False
            self.temp_updated = False
            self.pH_updated = False
            self.total_gas_updated = False
            self.h2_updated = False
            self.radioactivity_updated = False

            # Provide random chance each iteration for a resin overheat or fuel element failure to occur.
            if self.time_since_safe >= 60 and self.status == 0:
                self.casualty()

            # Update remaining reactor plant parameters for this iteration
            self.reactor_plant_parameters()

        # Save the data in a CSV file after all iterations are complete.
        self.save_data("test_file")   

    ###################################################################################################

    def append_data(self):
        """Store the current state of the reactor."""
        # Reactor plant parameters
        self.data_dict["Time"].append(self.time_now)
        self.data_dict["pH"].append(self.pH)
        self.data_dict["Hydrogen"].append(self.h2)
        self.data_dict["Total Gas"].append(self.total_gas)
        self.data_dict["Temperature"].append(self.temp)
        self.data_dict["Pressure"].append(self.pressure)
        self.data_dict["Radioactivity"].append(self.radioactivity)
        self.data_dict["Power"].append(self.power)
        self.data_dict["Reactor Safety"].append(self.status)

        # Casualties and plant operations
        self.data_dict["Injection of Air"].append(self.injection_of_air_flag)
        self.data_dict["Injection of Air Degree"].append(self.injection_of_air_degree)
        self.data_dict["Resin Overheat"].append(self.resin_overheat_flag)
        self.data_dict["Resin Overheat Degree"].append(self.resin_overheat_degree)
        self.data_dict["Fuel Element Failure"].append(self.fuel_element_failure_flag)
        self.data_dict["Fuel Element Failure Degree"].append(self.fuel_element_failure_degree)
        self.data_dict["Chemical Addition"].append(self.charging_in_progress)
        self.data_dict["Vent Gas"].append(self.vent_gas_in_progress)
    
    def save_data(self, filename):
        """Get data for Simulator and save as CSV and return DataFrame"""
        data = pd.DataFrame.from_dict(self.data_dict)
        data.to_csv(filename)
        return pd.DataFrame.from_dict(self.data_dict)

#################################################################################################
#################################################################################################
# The following function will calculate reactor plant parameters and determine the safety
# conditon of the reactor each iteration of the simulation and determine if plant maintenance
# is needed.
#################################################################################################
#################################################################################################

    def reactor_plant_parameters(self):
        """
        Function to update reactor plant parameters for this iteration
        """
        # Calculate reactor plant parameters for this iteration if not already done.
        if not self.pressure_updated:
            self.pressure = self.calc_pressure()    # Pressure must be updated before h2 and total_gas
        
        if not self.temp_updated:
            self.temp = self.calc_temperature()

        if not self.pH_updated:
            self.pH = self.calc_pH()

        if not self.total_gas_updated:    
            self.total_gas = self.calc_total_gas()  # Total gas must be updated before hydrogen

        if not self.h2_updated:
            self.h2 = self.calc_h2()

        if not self.radioactivity_updated:
            self.radioactivity = self.calc_radioactivity()

        ###########################################################################
        # Set a trigger for plant maintenance to maintain controllable parameters
        # in specification during the simulation.
        # Note: triggers are offset slightly from the limit to maintain a safety margin.

        maintenance_triggers = {
            self.pH <= 10.2: "add_pH",
            self.h2 < 15: "add_h2",
            self.total_gas > 70: "degas"
        }

        for condition, action in maintenance_triggers.items():
            if condition:
                setattr(self, action, True)
                
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
            # Update reactor status to 'safe' if parameters return to normal operating bands.
            self.status = 0

    ###################################################################################################
    ###################################################################################################
    # Helper functions to calculate reactor plant parameters at each time step.
    ###################################################################################################
    ###################################################################################################

    def calc_pH(self):
        """
        Function to calculate the value of pH for the current iteration. This function has
        dependencies on the following flags:
            - resin_overheat_flag
            - add_pH and charging_in_progress
        """
        # Small resin overheat casualty
        if self.resin_overheat_flag:
            # Small resin overheat casualty
            if self.resin_overheat_degree:
                pass
            # Large resin overheat casualty
            else:
                pass

        # Charging pH chemicals
        elif self.add_pH and self.charging_in_progress:
            elapsed_time = self.time_now - self.charging_start
            if elapsed_time <= self.charging_duration:
                # Update pH while charging
                self.pH += 0.6 * elapsed_time / self.charging_duration
            else:
                self.add_pH = False
                self.charging_in_progress = False

        # Normal Operation
        else:
            # pH varies as a function of time and reactor power
            self.pH += - 0.25 * self.time_now * np.exp(self.power / 100)

        # Update the parameter flag
        self.pH_updated = True

        return self.pH
    
    #######################################################################################

    def calc_h2(self):
        """
        Function to calculate the value of hydrogen for the current iteration. This function
        has dependencies on the following flags:
            - injection_of_air_flag
            - add_h2 and charging_in_progress
            - vent_gas_in_progress
        """
        
        # Injection of air casualty
        if self.injection_of_air_flag:
            elapsed_time = self.time_now - self.charging_start
            # Hydrogen decreases while charging 
            if elapsed_time <= self.charging_duration:
                # Small injection of air
                if self.injection_of_air_degree:
                    target_h2 = self.h2_before_casualty - self.h2_decrease
                else:
                    target_h2 = 0
                # Update hydrogen while charging based on the degree of the casualty
                self.h2 = self.h2_before_casualty - (self.h2_before_casualty - target_h2) * (elapsed_time / self.charging_duration)
            else:
                self.injection_of_air_flag = False

        # Charging hydrogen
        elif self.add_h2 and self.charging_in_progress:
            elapsed_time = self.time_now - self.charging_start
            if elapsed_time <= self.charging_duration:
                # Update hydrogen while charging.
                self.h2 = self.h2_before_casualty + (50 * elapsed_time / self.charging_duration)
            
            else:
                # End of the charging operation
                self.charging_in_progress = False
                self.add_h2 = False

        # Degas operation
        elif self.vent_gas_in_progress:
            tg_ratio = self.total_gas / self.data_dict["Total Gas"][-1]
            # Reduce hydrogen while degas is in progress
            self.h2 *= tg_ratio

        # Normal operation
        else:
            # Hydrogen varies as a function of pressure (Henrys Law)
            h2_conc_pressure = self.data_dict['Hydrogen'][-1] * ((self.pressure - self.data_dict['Pressure'][-1]) / 2200)
            self.h2 = self.data_dict['Hydrogen'][-1] + h2_conc_pressure 
        
        # Update the parameter flag
        self.h2_updated = True

        return self.h2

    ########################################################################################################
    
    def calc_total_gas(self):
        """
        Function to calculate the value of total gas for the current iteration. This function
        has dependencies on the following flags:
            - injection_of_air_flag
            - vent_gas_in_progress
        """
        # Injection of air casualty
        if self.injection_of_air_flag:
            # Small injection of air casualty
            if self.injection_of_air_degree:
                pass
            # Large injection of air casualty
            else:
                pass
        
        # Degas in progress
        elif self.vent_gas_in_progress:
            self.vent_gas_start = self.time_now
            elapsed_time = self.time_now - self.vent_gas_start
            total_gas_red_rate = 0.5
            # Reduce total gas to 60 from some value greater than 70.
            self.total_gas = self.total_gas - total_gas_red_rate * elapsed_time

            # End the venting of gas after reaching goal.
            if self.total_gas <= 60:
                self.vent_gas_in_progress = False
                self.degas = False
                self.vent_gas_start = None

        # Normal operation
        else:
            # Total gas varies as a function of hydrogen
            pass

        # Update the parameter flag
        self.total_gas_updated = True

        return self.total_gas
    
    ######################################################################################################

    def calc_pressure(self):
        """
        Function to calculate the value of pressure for the current iteration. This function has
        dependencies on the following flags:
            - self.monitoring_pressure (calculated locally)
            - self.add_pH and self.add_h2
            - self.degas
        This function will determine the value of the injection of air casualty flag when the
        charging operation occurs.
        """

        # Give the reactor plant workers an 80% chance of monitoring reactor plant pressure
        # to prevent an overpressure casualty while performing the chemical addition.
        self.monitoring_pressure = random.choices([True, False], weights = [95, 5])[0]

        # Charging operation
        if self.add_pH or self.add_h2:
            # Determine how many pumps we will use for the charging operation.
            pumps = random.choice([1, 2, 3]) 
            self.charging_duration ={1:30, 2:20, 3:10}[pumps]

            # Determine if charging can begin
            if not self.charging_in_progress:
                if self.monitoring_pressure and self.pressure > 2060:
                    return  # Do not charge in this condition
            
                # Commence Charging operation
                self.charging_in_progress = True
                if self.charging_start is None:
                    self.charging_start = self.time_now
                
                # Give some probability of an injection of air casualty occuring during the chemical addition
                self.injection_of_air_flag = random.choices([True, False], weights = [30, 70])[0]
                
                # Handle the casualty if it occurs during charging
                if self.injection_of_air_flag:
                    self.casualty()

                # Update variables linearly during chemical addition.
                elapsed_time = self.time_now - self.charging_start
                if elapsed_time <= self.charging_duration:

                    # Update parameter while charging. 
                    self.pH = self.calc_pH()
                    self.h2 = self.calc_h2()

                    # Update pressure while charging.
                    Q = 30 * pumps          # Charging rate
                    pressure_increase = 3000 * Q * elapsed_time / (20000 + Q * elapsed_time)
                    self.pressure += pressure_increase

                    # End the chemical addition after the duration.
                    if elapsed_time >= self.charging_duration:
                        self.charging_in_progress = False
                        self.add_h2 = False
                        self.add_pH = False
                        self.charging_start = None
                
        # Venting gas operation
        elif self.degas:

            if self.monitoring_pressure and self.pressure <= 2070:
                return # do not vent in this condition (prevent underpressure condition)
            # Perform degas 
            else:
                self.vent_gas_in_progress = True
                # Ensure start time is only calculated once
                if self.vent_gas_start is None:
                    self.vent_gas_start = self.time_now
                elapsed_time = self.time_now - self.vent_gas_start
                pressure_red_rate = 3
                # Reduce pressure while venting
                self.pressure = self.pressure - (pressure_red_rate * elapsed_time)

        # Normal operation
        else:
            pass

        # Update the parameter flag
        self.pressure_updated = True

        return self.pressure

    def calc_temperature(self):
        """
        Function to calculate the value of temperature for the current iteration. This function
        has dependencies on the following flags:
            - resin_overheat_flag
        """
        if self.resin_overheat_flag:
            # Small resin overheat casualty
            if self.resin_overheat_degree:
                pass
            # Large resin overheat casualty
            else:
                pass
        # Normal operation
        else:
            pass

        # Update the parameter flag
        self.temp_updated = True

        return self.temp

    def calc_radioactivity(self):
        """
        Function to calculate the value of radioactivity for the current iteration. This function
        has dependencies on the following flags:
            - fuel_element_failure_flag
        """
        # Fuel element failure casualty
        if self.fuel_element_failure_flag:
            # Small fuel element failure
            if self.fuel_element_failure_degree:
                pass
            # Large fuel element failure
            else:
                pass

        # Large injection of air casualty
        elif self.injection_of_air_flag and not self.injection_of_air_degree:
            pass

        # Normal Operation
        else:
            pass

        # Update the parameter flag
        self.radioactivity_updated = True

        return self.radioactivity

#####################################################################################################
#####################################################################################################

    def casualty(self):
        """
        Function to handle casualties.

        The safe time for resin overheat and fuel element failure are determined in the
        run simulation function
        """
        # Check if injection of air casualty is ocurring before calculating other casualties.
        if self.injection_of_air_flag == True and self.status == 0 and self.time_since_safe > 60:
            self.injection_of_air_degree = random.choices([True, False], weights = [40, 60])[0]
            self.h2_before_casualty = self.h2

            # Small injection of air
            if self.injection_of_air_degree:
                self.h2_decrease = random.uniform(5, self.h2_before_casualty)
                self.injection_of_air()
            else:
                self.h2_decrease = self.h2_before_casualty
                self.injection_of_air()

        # Determine some random probability each iteration for a casualty to occur
        casualties = ['resin_overheat', 'fuel_element_failure']
        select_casualty = random.choices(casualties + [None], weights = [5, 5, 90])[0]
        
        if select_casualty == 'resin_overheat'and not self.injection_of_air_flag:
            self.resin_overheat_flag = True
            self.resin_overheat_degree = random.choices([True, False], weights = [30, 70])[0]
            self.resin_overheat()
        elif select_casualty == 'fuel_element_failure'and not self.injection_of_air_flag:
            self.fuel_element_failure_flag = True
            self.fuel_element_failure_degree = random.choices([True, False], weights = [20, 80])[0]
            self.fuel_element_failure()

    #################################################################################################
    #################################################################################################
    # Helper functions to handle casualties
    #################################################################################################
    #################################################################################################
        
    def injection_of_air(self):
        """
        The calc_pressure() function has determined that an injection of air casualty is ocurring
        during a charging operation.

        The casualty() function has determined the degree of the casualty.

        The following functions have dependencies with the injection of air flag:
            - calc_pressure(), pressure must be updated before calculated hydrogen and total gas
            - calc_h2() 
            - calc_total_gas()
            - calc_radioactivity()

        These parameters are dependent on eachother and must be calculated in a specific order.
        """
        self.calc_pressure()    # Pressure must be updated before h2 and total gas
        self.calc_total_gas()   # Total gas must be updated before h2
        self.calc_h2()
        self.calc_radioactivity()

    def resin_overheat(self):
        """
        The call to the casualty() function this iteration has determined that a resin overheat
        casualty is ocurring and determined the degree of the casualty. The following functions
        have dependencies with the resin overheat flag:
            - calc_pH()
            - calc_temperature()
            - calc_radioactivity()

        These parameters are independent of eachother and can be calculated in any order.
        """
        self.calc_pH()
        self.calc_temperature()
        self.calc_radioactivity()

    def fuel_element_failure(self):
        """
        The call to the casualty() function this iteration has determined that a fuel element
        failure casualty is ocurring and determined the degree of the casualty. The following
        functions have dependencies with the fuel element failure flag:
            - calc_radioactivity()
        """
        self.calc_radioactivity()
        self.radioactivity_updated = True


        
            