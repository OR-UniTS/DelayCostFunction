import os

import pandas as pd

from CostPackage.Aircraft.aircraft_cluster import get_aircraft_cluster
from CostPackage.Passenger.passenger import get_passengers
from CostPackage.Scenario.scenario import get_fixed_cost_scenario


class Helper:

    def __init__(self):
        self.aircraft = pd.read_csv(os.path.join(os.path.dirname(__file__), "Aircraft/AircraftClustering.csv"))
        self.aircraft_clusters = self.aircraft.AssignedAircraftType.unique()
        self.aircraft_seats = pd.read_csv(os.path.join(os.path.dirname(__file__), "Aircraft/AircraftSeats_2019.csv"))
        self.airports = pd.read_csv(os.path.join(os.path.dirname(__file__), "Airport/airportMore25M.csv"))
        self.hard_costs = pd.read_csv(os.path.join(os.path.dirname(__file__), "Passenger/Hard/PassengerTacticalCosts_HARD_2019.csv"))
        self.hard_reimbursement_pax = pd.read_csv(os.path.join(os.path.dirname(__file__), "Passenger/Hard"
                                                                                          "/PassengerReimbursementRates_2019.csv"))
        self.hard_waiting_pax = pd.read_csv(os.path.join(os.path.dirname(__file__), "Passenger/Hard/PassengerWaitingRates_2019.csv"))
        self.soft = pd.read_csv(os.path.join(os.path.dirname(__file__), "Passenger/Soft/PassengerTacticalCosts_SOFT_2019.csv"))
        self.crew = pd.read_csv(os.path.join(os.path.dirname(__file__), "Crew/CrewTacticalCosts_2019.csv"))
        self.maintenance = pd.read_csv(os.path.join(os.path.dirname(__file__), "Maintenance/MaintenanceTacticalCosts_AT_GATE_2019.csv"))

    """Object containing all info about the data used in the get_delay_cost function. 
        It can be used to correctly formulate the input for the function
        
        aircraft: dataframe containing all aircraft information and their cluster
        aircraft_clusters: array containing all aircraft clusters
        aircraft_seats: aircraft seats dataframe (only clusters)
        airports: dataframe containing all airports considered in the package
        hard_costs: dataframe containing all hard cost considered in the package
        hard_reimbursement_pax: dataframe containing pax reimbursement statistics
        hard_waiting_pax: dataframe containing pax waiting statistics
        soft: dataframe containing soft cost considered in the package
        crew: dataframe containing crew cost considered in the package
        maintenance: dataframe containing maintenance statistics

         get_data_dict(): -> dict
            method to get the dictionary of all dataframes
        
        get_pax_number(is_low_cost: bool, destination: str, aircraft_type: str)  -> int
            method that given the input case return a inferred number of passengers
            
        get_pax_number_from_load_factor(aircraft_type: str, load_factor: float)  -> int
            method that given the input case return a inferred number of passengers
    """
    def get_data_dict(self):
        data_dict = {
            "aircraft": self.aircraft,
            "aircraft_seats": self.aircraft_seats,
            "airports": self.airports,
            "hard": self.hard_costs,
            "hard_reimbursement_pax": self.hard_reimbursement_pax,
            "hard_waiting_pax": self.hard_waiting_pax,
            "crew": self.crew,
            "maintenance": self.maintenance,
            "soft": self.soft
        }

        return data_dict

    @staticmethod
    def get_pax_number(is_low_cost: bool, destination_airport: str, aircraft_type: str):
        aircraft_cluster = get_aircraft_cluster(aircraft_type=aircraft_type)
        cost_scenario = get_fixed_cost_scenario(is_low_cost_airline=is_low_cost,
                                                destination_airport_ICAO=destination_airport)
        return get_passengers(aircraft_cluster, cost_scenario)

    @staticmethod
    def get_pax_number_from_load_factor(aircraft_type: str, load_factor: float):
        aircraft_cluster = get_aircraft_cluster(aircraft_type=aircraft_type)
        df_aircraft_seats = pd.read_csv(os.path.join(os.path.dirname(__file__), "Passengers/AircraftSeats_2019.csv"))
        n_passengers = int(load_factor * df_aircraft_seats[df_aircraft_seats.Aircraft == aircraft_cluster].SeatsLow.iloc[0])
        return n_passengers
