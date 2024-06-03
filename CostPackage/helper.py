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
    def get_pax_number(is_low_cost: bool, destination: str, aircraft_type: str):
        aircraft_cluster = get_aircraft_cluster(aircraft_type=aircraft_type)
        cost_scenario = get_fixed_cost_scenario(is_low_cost_airline=is_low_cost, destination_airport_ICAO=destination)
        return get_passengers(aircraft_cluster, cost_scenario)

    @staticmethod
    def get_pax_number_from_load_factor(aircraft_type: str, load_factor: float):
        aircraft_cluster = get_aircraft_cluster(aircraft_type=aircraft_type)
        df_aircraft_seats = pd.read_csv(os.path.join(os.path.dirname(__file__), "Passengers/2019-AircraftSeats.csv"))
        n_passengers = int(load_factor * df_aircraft_seats[df_aircraft_seats.Aircraft == aircraft_cluster].SeatsLow.iloc[0])
        return n_passengers
