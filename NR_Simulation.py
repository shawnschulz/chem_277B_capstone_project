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
        self.monitoring_pressure = None         # Sanity check to avoid overpressure casualty
        self.vent_gas_in_progress = False       # Are we venting gas (reducing TG)
        self.vent_gas_start = None              # Venting start time
        self.charging_in_progress = False       # Are we currently charging to the plant
        self.charging_start = None              # Charging start time
        self.resin_overheat_start = None        # Resin overheat start time
        self.charging_duration = None           # Charging duration based on number of pumps.
        self.degas_duration = None              # degas duration based on tg concentration 
        self.add_pH = False                     # Flag for adding pH (plant maintenance)
        self.add_h2 = False                     # Flag for adding hydrogen (plant maintenance)
        self.degas = False                      # Flag for degas (plant maintenance)
        self.time_now = 0                       # (minutes) Current simulation time
        self.time_since_safe = 0                # Amount of time reactor status 0
        self.pH_start = None                    # Used for injection of air casualty and charging pH
        self.h2_start = None                    # Used for injection of air casualty and charging h2
        self.total_gas_start = None             # Used for injection of air casualty
        self.dissolved_nitrogen = 10            # Used for injection of air casualty
        self.dissolved_oxygen = 0               # Used for injection of air casualty.
        self.delta_oxygen = None                # Used for injection of air casualty
        self.extra_oxygen = None                # Used for injection of air casualty
        self.baseline_radioactivity = 10        # Used for fuel element failure casualty
        self.initial_radioactivity = None       # Used for resin overheat casualty
        self.fuel_element_failure_start = None  # Used for fuel element failure casualty
        self.p_transition_start = None          # Used for smoothing pressure change after charging
        self.p_transition_start_pressure = None # Used for smoothing pressure change after charging
        self.p_transition_duration = None       # Used for smoothing pressure change after charging
        
        
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

    def run_simulation(self, simulation_time = 14*24*60):      #3*24*60 Simulation time of 4320 minutes (3 days)
        """
        Function to run the simulation.

        How to interpret the code:
            - Time is incremented by one and the 'parameter update' flags are reset each iteration.
            - A call to the casualty() method is made:
                - The probability of a casualty ocurring is randomly determined each iteration.
                - Only one casualty can occur at a time.
                - The probability of an injection of air casualty ocurring is only calculated if
                  a charging operation is in progress.
                - If a parameter is updated, its update flag is set to true. Once all of the parameters
                  affected by the casualty are updated we return to the simulation loop.
            - A call to the reactor_plant_parameters() function is made:
                - The reactor plant parameters function will calculate any remaining parameters that
                  have not been calculated this iteration.
            - The data is appended to the dictionary at the end of the iteration.
            - Once the simulation loop is complete the dictionary is converted to a csv file.
        
        Note: The reactor plant parameters function has triggers built in to insert a charging operation
        if pH or hydrogen concentration is low. An injection of air casualty can only occur during a
        charging operation.

        Note: There are dependencies on the order of which some variables must be calculated.
        Specifically, pressure must be calculated before hydrogen, and hydrogen must be calculated
        before total gas.
        """
        # Populate initial values into the dictionary
        self.append_data()

        while self.time_now < simulation_time:
            # Update time for this iteration
            self.time_now += 1

            # Reset parameter update flags to false for this iteration            
            self.pressure_updated = False
            self.temp_updated = False
            self.pH_updated = False
            self.total_gas_updated = False
            self.h2_updated = False
            self.radioactivity_updated = False

            # Determine if a casualty is ocurring this iteration
            self.casualty()

            # Update remaining reactor plant parameters for this iteration
            self.reactor_plant_parameters()

            # Append reactor plant parameters to the dictionary for this iteration
            self.append_data()

        # Save the data in a CSV file after all iterations are complete.
        self.save_data("Sim_two_weeks_all_casualties")   

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
        # Determine if triggers for plant maintenance are met. This will maintain parameters
        # within their normal bands during the simulation and between casualties.
        # Note: triggers are offset slightly from the limit to maintain a safety margin.

        if self.pH <= 10.2:
            self.add_pH = True
        if self.h2 < 15:
            self.add_h2 = True
        if self.total_gas > 70:
            self.degas = True
        
        # Degas Operation
        if self.degas and not self.charging_in_progress:
            self.vent_gas()

        # Charging operation
        if self.p_transition_start is None:
            if (self.add_pH or self.add_h2) and not self.vent_gas_in_progress:
                self.charging_operation()
        
        
        ##################################################################################
        # Calculate reactor plant parameters for this iteration if not already done.

        if not self.pressure_updated:
            self.pressure = self.calc_pressure()    # Pressure must be updated before hydrogen
        
        if not self.temp_updated:
            self.temp = self.calc_temperature()     

        if not self.pH_updated:
            self.pH = self.calc_pH()
        
        if not self.h2_updated:
            self.h2 = self.calc_h2()                # Hydrogen must be updated before total gas.

        if not self.total_gas_updated:    
            self.total_gas = self.calc_total_gas()  

        if not self.radioactivity_updated:
            self.radioactivity = self.calc_radioactivity()
      
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
        elif self.radioactivity > self.baseline_radioactivity + 5:
            self.status = 1
        else:
            # Update reactor status to 'safe' if parameters return to normal operating bands.
            self.status = 0

    ########################################################################################################
    ########################################################################################################

    def charging_operation(self):
        if self.injection_of_air_flag is not None:
            return     
          
        if self.monitoring_pressure is None:
            # Give the reactor plant workers an 80% chance of monitoring reactor plant pressure
            # to prevent an overpressure casualty while performing the chemical addition.
            self.monitoring_pressure = random.choices([True, False], weights = [100, 0])[0]

        # Determine if charging can begin
        if not self.charging_in_progress:
            if self.monitoring_pressure and self.pressure > 2060:
                # Update parameters normally
                return 
            elif self.monitoring_pressure and self.pressure < 2060: 
                # Commence Charging operation
                self.charging_in_progress = True
                           
        if self.charging_in_progress:
            if self.charging_duration is None:
                # Determine how many pumps we will use for the charging operation.
                pumps = random.choice([1, 2, 3]) 
                self.charging_duration ={1:30, 2:20, 3:10}[pumps]

            # Obtain starting values for reference
            if self.charging_start is None:
                self.charging_start = self.time_now
                self.pH_start = self.pH
                self.h2_start = self.h2

            # Update variables linearly during chemical addition.
            elapsed_time = self.time_now - self.charging_start
            if elapsed_time <= self.charging_duration - 1:
                    
                # Update Pressure
                step_increase_pressure = 100 / self.charging_duration
                self.pressure += step_increase_pressure
                self.pressure_updated = True

                # Update pH
                if self.add_pH:
                    step_increase_pH = (10.8 - self.pH_start) / self.charging_duration
                    self.pH += step_increase_pH
                    self.pH_updated = True
                    
                # Update hydrogen
                if self.add_h2:
                    target_h2 = 50
                    delta_h2 = target_h2 - self.h2_start
                    step_increase_h2 = delta_h2 / self.charging_duration
                    self.h2 += step_increase_h2
                    self.h2_updated = True

            # End the chemical addition after the duration.
            else:
                self.monitoring_pressure = None
                self.charging_in_progress = False
                self.charging_start = None
                self.charging_duration = None
                self.pH_start = None
                self.add_pH = False
                self.add_h2 = False
                self.h2_start = None
                self.p_transition_duration = self.calc_pressure_smoothing()
                self.p_transition_start = self.time_now          
                self.p_transition_start_pressure = self.pressure
                self.pressure = self.calc_pressure()                    
        
    ########################################################################################################

    def vent_gas(self):
        """
        Function to update hydrogen, total gas, and pressure during degas operation.
        """
        # Determine if we have met our target.
        if self.total_gas <= 60:
            return
        
        if self.monitoring_pressure is None:
            # Give the reactor plant workers an 80% chance of monitoring reactor plant pressure
            # to prevent an overpressure casualty while performing the chemical addition.
            self.monitoring_pressure = random.choices([True, False], weights = [100, 0])[0]
        
        # Determine if charging can begin
        if not self.vent_gas_in_progress:
            if self.monitoring_pressure and self.pressure < 2175:
                # Update parameters normally
                return 
            elif self.monitoring_pressure and self.pressure >= 2175: 
                # Commence Charging operation
                self.vent_gas_in_progress = True
        
        # Wait until pressure is high in band to perform degas.
        if self.vent_gas_in_progress:
            if self.vent_gas_start is None:
                self.vent_gas_start = self.time_now
                self.total_gas_start = self.total_gas

            # Determine amount of time required to reduce total gas to target
            total_gas_red_rate = 0.5 
            delta_total_gas  = self.total_gas_start - 60
            self.degas_duration = delta_total_gas / total_gas_red_rate
            elapsed_time = self.time_now - self.vent_gas_start

            if elapsed_time < self.degas_duration - 1:
                # Update total gas and hydrogen
                self.dissolved_nitrogen *= (self.total_gas - total_gas_red_rate) / self.total_gas
                self.dissolved_oxygen *= (self.total_gas - total_gas_red_rate) / self.total_gas
                self.h2 *= (self.total_gas - total_gas_red_rate) / self.total_gas
                self.h2_updated = True
                self.total_gas -= total_gas_red_rate
                self.total_gas_updated = True

                # Update pressure
                pressure_red_rate = 1.2
                self.pressure -= pressure_red_rate
                self.pressure_updated = True
            
            if elapsed_time >= self.degas_duration - 1:
                self.vent_gas_in_progress = False
                self.vent_gas_start = None
                self.total_gas_start = None
                self.degas_duration = None
                self.degas = False
            

    ###################################################################################################
    ###################################################################################################
    # Helper functions to calculate reactor plant parameters at each time step.
    ###################################################################################################
    ###################################################################################################

    def calc_pressure_smoothing(self):
        """
        Function to calculate the smoothing duration for pressure after conducting a charging
        operation.
        """

        period = 120
        angular_frequency = (2 * np.pi) / period

        # Determine the current phase
        current_phase = (angular_frequency * self.time_now) % (2 * np.pi)

        # Determine when pressure will cross the middle value of oscillation again based on current phase
        next_mid_crossing = ((2 * np.pi) - current_phase) % (2 * np.pi) / angular_frequency

        return int(next_mid_crossing)

    def calc_pressure(self):
        """
        Function to calculate the value of pressure for the current iteration.
        """                                  
        
        # Constants for oscillating pressure
        mid = 2100
        amp = 95
        period = 120
        angular_frequency = (2 * np.pi) / period

        normal_pressure = mid + amp * np.sin(angular_frequency * self.time_now)
        
        # Smooth pressure after charging back to normal pressure
        if self.p_transition_start is not None:
            elapsed_time = self.time_now - self.p_transition_start

            if elapsed_time < self.p_transition_duration:
                t = elapsed_time / self.p_transition_duration
                self.pressure = (1 -t) * self.p_transition_start_pressure + t * normal_pressure
            else:
                self.pressure = normal_pressure
                self.p_transition_duration = None
                self.p_transition_start = None
                self.p_transition_start_pressure = None

        # Normal operation
        else:
            self.pressure = normal_pressure
        
        # Update the parameter flag
        self.pressure_updated = True

        return self.pressure

    ########################################################################################################
    
    def calc_pH(self):
        """
        Function to calculate the value of pH for the current iteration.
        """     
        # pH varies as a function of time since charging and reactor power
        self.pH -= 0.002 * (self.power / 100)

        # Update the parameter flag
        self.pH_updated = True

        return self.pH
    
    #######################################################################################

    def calc_h2(self):
        """
        Function to calculate the value of hydrogen for the current iteration.
        """
        # Hydrogen varies as a function of pressure (Henrys Law)
        h2_conc_pressure = self.h2 * ((self.pressure - self.data_dict['Pressure'][-1]) / 2200)
        self.h2 += h2_conc_pressure 
        
        # Update the parameter flag
        self.h2_updated = True

        return self.h2

    ########################################################################################################
    
    def calc_total_gas(self):
        """
        Function to calculate the value of total gas for the current iteration.
        """        
        self.total_gas = self.h2 + self.dissolved_nitrogen + self.dissolved_oxygen

        # Update the parameter flag
        self.total_gas_updated = True

        return self.total_gas
    
    ######################################################################################################

    def calc_temperature(self):
        """
        Function to calculate the value of temperature for the current iteration. This function
        has dependencies on the following flags:
            - resin_overheat_flag
        """
        # Constants for oscillating pressure
        mid = 500
        amp = 14
        period = 120
        angular_frequency = (2 * np.pi) / period
        normal_temp = mid + amp * np.sin(angular_frequency * self.time_now)

        self.temp = normal_temp

        # Update the parameter flag
        self.temp_updated = True

        return self.temp

    def calc_radioactivity(self):
        """
        Function to calculate the value of radioactivity for the current iteration.
        """
        
        if self.time_since_safe > 180 and self.radioactivity > self.baseline_radioactivity:
            self.baseline_radioactivity = self.radioactivity

        # Filter radioactivity from CRUD bursts and resin overheat
        if self.radioactivity > self.baseline_radioactivity:
            filter_efficiency = 0.95
            self.radioactivity *= filter_efficiency
        
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
        # Calculate the amount of time the reactor has been safe.
        if self.status == 0:
            self.time_since_safe += 1
        else:
            self.time_since_safe = 0
        
        # Allow the reactor to be safe for some amount of time before inserting another casualty.
        if self.time_since_safe > 180:
            # Determine if an injection of air casualty is ocurring.
            if self.charging_in_progress and self.charging_start is not None:
                # An injection of air casualty will not occur while restoring hydrogen.
                if self.injection_of_air_flag is None and not self.add_h2:
                    # Determine probability of an injection of air occurring
                    prob_inj_of_air = random.choices([True, False], weights = [40, 60])[0]
                    if prob_inj_of_air:
                        self.injection_of_air_flag = random.choices([True, False], weights = [60, 40])[0]
                        self.injection_of_air_degree = random.choices([True, False], weights = [60, 40])[0]
                        
            # Determine if a resin overheat or fuel element failure casualty is ocurring.               
            else:
                casualties = ['resin_overheat', 'fuel_element_failure']
                # Determine probability of resin overheat or fuel element failure occurring.
                select_casualty = random.choices(casualties + [None], weights = [15, 15, 70])[0]

                if select_casualty == 'resin_overheat':
                    self.resin_overheat_flag = True
                elif select_casualty == 'fuel_element_failure':
                    self.fuel_element_failure_flag = True

        # Make a call to the casualty function if a casualty is in progress
        if self.injection_of_air_flag is not None:
            self.injection_of_air()
        elif self.resin_overheat_flag is not None:
            self.resin_overheat()
        elif self.fuel_element_failure_flag is not None:
            self.fuel_element_failure()

    ###################################################################################################
    def injection_of_air(self):
        """
        It has been determined that an injection of air casualty is ocurring during the
        charging operation which is currently in progress as determined by the
        calc_pressure() function.

        Pressure has already been calculated for this iteration and marked as updated.

        The following parameters are affected by an injection of air casualty and must be
        calculated and marked as updated:
            - h2                
            - total_gas
            - pH
            - radioactivity
            
        Note: h2 must be updated before total gas during this casualty.
        """
        # Determine how much hydrogen is present at the beginning of the casualty
        if self.h2_start is None:
            self.h2_start = self.h2
        
        if self.extra_oxygen is None:
            self.extra_oxygen = random.randint(2, 10)
        
        # Determine amount of oxygen added
        if self.delta_oxygen is None:
            # Small injection of air casualty
            if self.injection_of_air_degree:
                self.delta_oxygen = random.uniform(5, self.h2_start)
            # Large injection of air casualty
            else:
                self.delta_oxygen = self.h2_start + self.extra_oxygen

        # Limit the contribution of nitrogen to total gas
        delta_nitrogen = self.delta_oxygen * (0.78 / 0.22) * 0.075
        step_increase_n2 = delta_nitrogen / self.charging_duration

        # Charging is in progress
        elapsed_time = self.time_now - self.charging_start
        # Hydrogen decreases while charging 
        if elapsed_time < self.charging_duration - 1:

            # Update Pressure
            step_increase_pressure = 100 / self.charging_duration
            self.pressure += step_increase_pressure
            self.pressure_updated = True

            # Update pH
            if self.add_pH:
                step_increase_pH = (10.8 - self.pH_start) / self.charging_duration
                self.pH += step_increase_pH
                self.pH_updated = True

            # Small injection of air (h2 and total gas)
            if self.injection_of_air_degree: 

                # Update hydrogen
                step_decrease_h2 = self.delta_oxygen / self.charging_duration
                self.h2 -= step_decrease_h2
                self.h2_updated = True

                # Update total gas
                self.dissolved_nitrogen += step_increase_n2
                self.total_gas = self.h2 + self.dissolved_oxygen + self.dissolved_nitrogen
                self.total_gas_updated = True

            # Large injection of air (h2, total gas, pH, radioactivity)
            else:
                # Increase the pH while charging is in progress proportional to the amount of
                # extra oxygen.
                pH_increase = 1.5 * (self.extra_oxygen / 10)
                step_increase_pH = pH_increase / self.charging_duration
                self.pH += step_increase_pH
                self.pH_updated = True

                # Increase radioactivity proportional to the CRUD burst caused by the chemical shock.
                rad_increase = 50 * (self.extra_oxygen / 10)
                step_increase_rad = rad_increase / self.charging_duration
                self.radioactivity += step_increase_rad
                self.radioactivity_updated = True
                
                # Update hydrogen and total gas proportional to time.
                time_proportion = (self.h2_start / (self.delta_oxygen + self.extra_oxygen + self.h2_start)) * self.charging_duration
                # Time for hydrogen to decrease to zero.
                if elapsed_time <= time_proportion:
                    # Update hydrogen
                    step_decrease_h2 = self.h2_start / time_proportion
                    self.h2 -= step_decrease_h2
                    self.h2_updated = True

                    # Update total gas
                    self.dissolved_nitrogen += step_increase_n2
                    self.total_gas = self.h2 + self.dissolved_oxygen + self.dissolved_nitrogen
                    self.total_gas_updated = True

                # Time for dissolved oxygen to increase.
                else:
                    # Update hydrogen
                    self.h2 = 0
                    self.h2_updated = True
                    
                    # Update total gas
                    step_increase_o2 = self.extra_oxygen / (self.charging_duration - time_proportion)
                    self.dissolved_oxygen += step_increase_o2
                    self.dissolved_nitrogen += step_increase_n2
                    self.total_gas = self.h2 + self.dissolved_oxygen + self.dissolved_nitrogen
                    self.total_gas_updated = True

        else: 
            # End the chemical addition after the duration.
            self.monitoring_pressure = None
            self.charging_in_progress = False
            self.charging_start = None
            self.charging_duration = None
            self.pH_start = None
            self.add_pH = False
            self.add_h2 = False
            self.h2_start = None
            self.injection_of_air_flag = None
            self.injection_of_air_degree = None
            self.h2_start = None
            self.delta_oxygen = None
            self.extra_oxygen = None  
            self.p_transition_duration = self.calc_pressure_smoothing()
            self.p_transition_start = self.time_now          
            self.p_transition_start_pressure = self.pressure
            self.pressure = self.calc_pressure()
        
    ################################################################################################
                    
    def resin_overheat(self):
        """
        It has been determined that a resin overheat casualty is ocurring this iteration.

        The following parameters are affected by an resin overheat casualty and must be
        calculated and marked as updated.
            - temperature
            - pH
            - radioactivity
        """
        # Ensure the degree is only calculated once per casualty
        if self.resin_overheat_degree is None:
            self.resin_overheat_degree = random.choices([True, False], weights = [50, 50])[0]
            # Determine how long the casualty is ocurring for
            self.time_above_limit = random.randint(8, 24)
            # Obtain some random target temperature for the casualty above the limit
            if self.resin_overheat_degree:
                self.target_temp = random.randint(520, 530)
            else:
                self.target_temp = random.randint(540, 550)
        
        # Start increasing temperature.
        if self.temp < 515:
            self.temp += 1
            self.temp_updated = True
            return  # Calculate the rest of the variables normally
        
        if self.temp >= 515:
            if self.resin_overheat_start is None:
                self.resin_overheat_start = self.time_now
                self.initial_pH = self.pH
                self.initial_rad = self.radioactivity

        elapsed_time = self.time_now - self.resin_overheat_start
        if elapsed_time < self.time_above_limit - 1:
            
            # Update temperature on a sinusoidal quarter period.
            self.temp = 515 + (self.target_temp - 515) * np.sin((np.pi/self.time_above_limit)*elapsed_time)
            self.temp_updated = True
            
            # Create a factor to represent resin exhaustion proportional to temperature.
            factor = 0.002 * (self.temp / 515)
            # Update pH
            self.pH += self.initial_pH * factor
            self.pH_updated = True

            # Large resin overheat casualty
            if not self.resin_overheat_degree:
                
                # Update radioactivity
                rad_factor = 0.15 * (self.temp / 515)
                self.radioactivity += self.initial_rad * rad_factor
                self.radioactivity_updated = True

        else: 
            # Set temp within band to avoid error in phase calculation
            self.temp = 513.5
            # Reset flags and state parameter
            self.resin_overheat_flag = None
            self.resin_overheat_degree = None
            self.resin_overheat_start = None
            self.initial_pH = None
            self.initial_radioactivity = None
            self.time_above_limit = None

    ######################################################################################################

    def fuel_element_failure(self):
        """
        It has been determined that a fuel element failure casualty is ocurring this iteration.

        The following parameters are affected by a fuel element failure casualty and
        must be calculated and marked as updated:
            - radioactivity
        """
        # Ensure the degree is only calculated once per casualty
        if self.fuel_element_failure_degree is None:
            self.fuel_element_failure_degree = random.choices([True, False], weights = [50, 50])[0]
        
        if self.initial_radioactivity is None:
            if self.fuel_element_failure_degree:
                self.initial_radioactivity = random.randint(15, 50)
            else:
                self.initial_radioactivity = random.randint(75, 100)

        if self.fuel_element_failure_degree:

            if self.radioactivity < self.initial_radioactivity + self.baseline_radioactivity:
                self.radioactivity += 3
                self.radioactivity_updated = True
            else:
                self.radioactivity = self.radioactivity
                self.radioactivity_updated = True
        else: 
            if self.radioactivity < self.initial_radioactivity + self.baseline_radioactivity:
                self.radioactivity += 6
                self.radioactivity_updated = True
            else:
                self.radioactivity = self.radioactivity
                self.radioactivity_updated = True
        
        if self.fuel_element_failure_start is None:
            self.fuel_element_failure_start = self.time_now
        
        elapsed_time = self.time_now - self.fuel_element_failure_start
        if elapsed_time > 100:
            self.baseline_radioactivity = self.radioactivity
            self.fuel_element_failure_flag = None
            self.fuel_element_failure_degree = None
            self.initial_radioactivity = None
            self.fuel_element_failure_start = None
        

    


        
            