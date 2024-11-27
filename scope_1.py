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
        self.injection_of_air_flag = None          # Flag for injection of air
        self.injection_of_air_degree = None        # Determination for small or large
        self.resin_overheat_flag = None            # Flag for resin overheat
        self.resin_overheat_degree = None          # Determination for small or large
        self.fuel_element_failure_flag = None      # Flag for fuel element failure
        self.fuel_element_failure_degree = None    # Determination for small or large

        # Simulation parameters
        self.monitoring_pressure = True         # Sanity check to avoid overpressure casualty
        self.vent_gas_in_progress = False       # Are we venting gas (reducing TG)
        self.vent_gas_start = None              # Venting start time
        self.charging_in_progress = False       # Are we currently charging to the plant
        self.charging_start = None              # Charging start time
        self.resin_overheat_start = None        # Resin overheat start time
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
# The following code will perform the simulation run.
###########################################################################################################
###########################################################################################################

    def run_simulation(self, simulation_time = 3*24*60):      # Simulation time of 4320 minutes (3 days)
        """
        Function to run the simulation.

        How to interpret the code:
            - The data is appended to the dictionary at the start of the iteration.
            - The 'parameter update' flags are reset for this iteration.
            - If the logic to induce a casualty is met there is a call to the casualty() function.
                - The casualty function will only allow one casualty to occur at a time and set
                  the corresponding casualty flag to true.
                - The casualty function will make a call to the respective casualty function to
                  calculate reactor plant paramters for this iteration.
                - Once a parameter has been calculated it's update flag is set to 'True'.
            - Once the parameters have been calculated by the respective casualty function
              we return to the run simulation function to call the reactor_plant_parameters() function.
                - The reactor plant parameters function will calculate any remaining parameters that
                  have not been calculated this iteration.
            - Once the simulation loop is complete the dictionary is converted to a csv file.
        
        Note: The probability of an injection of air casualty ocurring is determined inside of
        the function to calculate pressure. The reactor plant parameters function has triggers
        built in to insert a charging operation if pH or hydrogen concentration is low. An injection
        of air casualty can only occur during a charging operation.

        Note: There are dependencies on the order of which some variables must be calculated.
        Specifically, pressure must be calculated before total gas, and total gas must be
        calculated before hydrogen.
        """
        # Populate initial values into the dictionary
        self.append_data()

        while self.time_now < simulation_time:
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

            # Only allow calls to the casualty function if a casualty is ocurring or if sufficient
            # time has elapsed to allow the reactor to stabilize parameters.
            if self.time_since_safe >= 180 or\
                    self.injection_of_air_flag or\
                    self.resin_overheat_flag or\
                    self.fuel_element_failure_flag:
                self.casualty()

            # Update remaining reactor plant parameters for this iteration
            self.reactor_plant_parameters()

            # Append reactor plant parameters to the dictionary for this iteration
            self.append_data()

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
        data.to_csv(filename, index = False)
        

#################################################################################################
#################################################################################################
# The following function will calculate reactor plant parameters if they have not already been
# calculated. Triggers are implemented in this function to normalize pH, hydrogen, and total gas
# during the simulation during normal operation and between casualties. If any of the calculated
# parameters out out of their normal operating band for this iteration, the reactor is not safe.
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
            self.temp = self.calc_temperature()     # Temperature must be calculated before pH

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
            - resin_overheat_start
            - add_pH and charging_in_progress
        """
        # Resin overheat casualty
        if self.resin_overheat_start is not None:
            # Small resin overheat casualty
            if self.resin_overheat_degree:
                factor = 0.1       # Maximum possible pH increase of ~0.41
            # Large resin overheat casualty
            else:
                factor = 0.2        # Maximum possible pH increase of ~0.82

            elapsed_time = self.time_now - self.resin_overheat_start
            self.ph = self.initial_pH + factor * elapsed_time * (self.temp / 515)

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
            self.pH += - 0.0025 * self.time_now * np.exp(self.power / 100)

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

            if self.data_dict['Pressure'][-1] is None:
                self.h2 = 49.5
            else:
                # Hydrogen varies as a function of pressure (Henrys Law)
                h2_conc_pressure = self.h2 * ((self.pressure - self.data_dict['Pressure'][-1]) / 2200)
                self.h2 += h2_conc_pressure 
        
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
        def charging_operation():
            # Determine how many pumps we will use for the charging operation.
            pumps = random.choice([1, 2, 3]) 
            self.charging_duration ={1:30, 2:20, 3:10}[pumps]

            # Determine if charging can begin
            if not self.charging_in_progress:
                if self.monitoring_pressure and self.pressure > 2060:
                    normal_operation()
            
                # Commence Charging operation
                self.charging_in_progress = True
                if self.charging_start is None:
                    self.charging_start = self.time_now
                
                # Give some probability of an injection of air casualty occuring during the chemical addition
                if self.injection_of_air_flag is None and self.time_since_safe > 60:
                    self.injection_of_air_flag = random.choices([True, False], weights = [30, 70])[0]
                    self.injection_of_air_degree = random.choices([True, False], weights = [60, 40])[0]
                    self.h2_before_casualty = self.h2

                # Update variables linearly during chemical addition.
                elapsed_time = self.time_now - self.charging_start
                if elapsed_time <= self.charging_duration:

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
                        self.injection_of_air_flag = None
                        self.injection_of_air_degree = None
        
        def degas():
            if self.monitoring_pressure and self.pressure <= 2070:
                normal_operation()
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
        def normal_operation():
            # To Support the first time step
            if self.time_now == 1:
                self.pressure = 2099
                # Initialize phase
                self.phase = 0
            # To deal with pressure above or below normal oscillations during normal operation
            elif self.pressure > 2195:
                self.pressure -= 1
            elif self.pressure < 2005:
                self.pressure += 1
            # To Support every time step after the first step
            else:
                # Constants for oscillating pressure
                mid = 2100
                amp = 95
                period = 60
                press_diff = self.data_dict['Pressure'][-2] - self.data_dict['Pressure'][-1]

                # Determine where we are in phase
                if press_diff < 0:
                    # Adjust the phase for falling temperature
                    self.phase = np.pi - np.arcsin((self.pressure - mid) / amp)
                elif press_diff > 0:
                    # Adjust the phase for rising temperature
                    self.phase = np.arcsin((self.pressure - mid) / amp)

                # Update temperature based on the phase
                self.phase += 2 * np.pi / period
                self.pressure = mid + amp * np.sin(self.phase)
            
        
        # Give the reactor plant workers an 80% chance of monitoring reactor plant pressure
        # to prevent an overpressure casualty while performing the chemical addition.
        self.monitoring_pressure = random.choices([True, False], weights = [95, 5])[0]

        # Charging operation
        if self.add_pH or self.add_h2:
            charging_operation()
        # Venting gas operation
        elif self.degas and not self.charging_in_progress:
            degas()
        # Normal Operation
        else:
            normal_operation()
        
        # Update the parameter flag
        self.pressure_updated = True

        return self.pressure

    def calc_temperature(self):
        """
        Function to calculate the value of temperature for the current iteration. This function
        has dependencies on the following flags:
            - resin_overheat_flag
        """
        # Resin overheat casualty
        if self.resin_overheat_flag:
            # Start raising temperature to the limit
            if self.temp < 515:
                self.temp += 1
                
            # Resin overheat start when temperature is greater than 515.
            elif self.resin_overheat_start is not None:
                elapsed_time = self.time_now - self.resin_overheat_start
                # Temperature changes IAW sinusoidal half period while above upper limit.
                if elapsed_time <= self.time_above_limit:
                    # Degree of casualty is determined by target_temp in casualty function
                    self.temp = 515 + (self.target_temp - 515) * np.sin((np.pi/self.time_above_limit)*elapsed_time)
                # The casualty is over after the half period
                else:
                    # Set temp within band to avoid error in phase calculation
                    self.temp = 513.5
                    # Reset flags and state parameter
                    self.resin_overheat_flag = None
                    self.resin_overheat_degree = None
                    self.resin_overheat_start = None

        # Normal operation
        else:
            # To Support the first time step
            if self.time_now == 1:
                self.temp = 499.5
                # Initialize phase
                self.phase = 0
            # To Support every time step after the first step
            else:
                # Constants for oscillating temperature
                mid = 500
                amp = 14
                period = 60
                temp_diff = self.data_dict['Temperature'][-2] - self.data_dict['Temperature'][-1]

                # Determine where we are in phase
                if temp_diff < 0:
                    # Adjust the phase for falling temperature
                    self.phase = np.pi - np.arcsin((self.temp - mid) / amp)
                elif temp_diff > 0:
                    # Adjust the phase for rising temperature
                    self.phase = np.arcsin((self.temp - mid) / amp)

                # Update temperature based on the phase
                self.phase += 2 * np.pi / period
                self.temp = mid + amp * np.sin(self.phase)

        # Update the parameter flag
        self.temp_updated = True

        return self.temp

    def calc_radioactivity(self):
        """
        Function to calculate the value of radioactivity for the current iteration. This function
        has dependencies on the following flags:
            - fuel_element_failure_flag
            - injection_of_air_flag and injection_of_air_degree
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
        
        # Large resin overheat casualty
        elif self.resin_overheat_start is not None and not self.resin_overheat_degree:
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
        # This is redundant programming. Injection of air will handle itself regardless of
        # the call to the casualty function. 
        if self.injection_of_air_flag:               
            self.injection_of_air()

        # Determine some random probability each iteration this function is called
        # for a casualty to occur, unless a casualty is already ocurring.
        if self.injection_of_air_flag is None and\
                self.resin_overheat_flag is None and\
                self.fuel_element_failure_flag is None:
            casualties = ['resin_overheat', 'fuel_element_failure']
            select_casualty = random.choices(casualties + [None], weights = [5, 5, 90])[0]

            if select_casualty == 'resin_overheat':
                self.resin_overheat_flag = True
            elif select_casualty == 'fuel_element_failure':
                self.fuel_element_failure_flag = True

        # Resin overheat casualty   
        if self.resin_overheat_flag:
            # Ensure the degree is only calculated once per casualty
            if self.resin_overheat_degree is None:
                self.resin_overheat_degree = random.choices([True, False], weights = [30, 70])[0]
                # Determine how long the casualty is ocurring for
                self.time_above_limit = random.randint(4, 8)
                # Obtain some random target temperature for the casualty above the limit
                if self.resin_overheat_degree:
                    self.target_temp = random.randint(520, 520)
                else:
                    self.target_temp = random.randint(540, 550)
            # Changes in pH start to happen above 515 degrees
            if self.temp > 515 and self.resin_overheat_start is None:
                self.resin_overheat_start = self.time_now
                self.initial_pH = self.pH
            self.resin_overheat()

        # Fuel element failure casualty
        elif self.fuel_element_failure_flag:
            # Ensure the degree is only calculated once per casualty
            if self.fuel_element_failure_degree is None:
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
        self.calc_temperature()
        self.calc_pH()
        self.calc_radioactivity()

    def fuel_element_failure(self):
        """
        The call to the casualty() function this iteration has determined that a fuel element
        failure casualty is ocurring and determined the degree of the casualty. The following
        functions have dependencies with the fuel element failure flag:
            - calc_radioactivity()
        """
        self.calc_radioactivity()


        
            