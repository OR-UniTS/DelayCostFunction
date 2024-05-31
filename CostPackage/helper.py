import os

import pandas as pd

from CostPackage.Aircraft.aircraft_cluster import get_aircraft_cluster
from CostPackage.Passenger.passenger import get_passengers
from CostPackage.Scenario.scenario import get_fixed_cost_scenario


class Helper:

    def __init__(self):
        self.aircraft = pd.read_csv(os.path.join(os.path.dirname(__file__), "Cluster/aircraftClustering.csv")),
        self.aircraft_seats = pd.read_csv(os.path.join(os.path.dirname(__file__), "Passengers/2019-AircraftSeats.csv")),
        self.airports = pd.read_csv(os.path.join(os.path.dirname(__file__), "CostScenario/airportMore25M.csv")),
        self.hard = pd.read_csv(os.path.join(os.path.dirname(__file__), "Hard/2019-PassengerHardCostsBaseScenarioAverage.csv")),
        self.crew = pd.read_csv(os.path.join(os.path.dirname(__file__), "MaintenanceCrew/2019-TacticalCrewCosts.csv")),
        self.maintenance = pd.read_csv(os.path.join(os.path.dirname(__file__), "MaintenanceCrew/2019-TacticalMaintenanceCosts.csv")),
        self.soft = pd.read_csv(os.path.join(os.path.dirname(__file__), "Soft/2019-PassengerSoftCosts.csv"))

    def get_data_dict(self):
        data_dict = {
            "aircraft": self.aircraft,
            "aircraft_seats": self.aircraft_seats,
            "airports": self.airports,
            "hard": self.hard,
            "crew": self.crew,
            "maintenance": self.maintenance,
            "soft": self.soft
        }

        return data_dict

    @staticmethod
    def get_pax_number(is_low_cost: bool, destination: str, aircraft_type: str):
        aircraft_cluster = get_aircraft_cluster(aircraft_type=aircraft_type)
        cost_scenario = get_fixed_cost_scenario(is_LCC_airline=is_low_cost, destination_airport_ICAO=destination)
        return get_passengers(aircraft_cluster, cost_scenario)

    @staticmethod
    def get_pax_number_from_load_factor(aircraft_type: str, load_factor: float):
        aircraft_cluster = get_aircraft_cluster(aircraft_type=aircraft_type)
        df_aircraft_seats = pd.read_csv(os.path.join(os.path.dirname(__file__), "Passengers/2019-AircraftSeats.csv"))
        n_passengers = int(load_factor * df_aircraft_seats[df_aircraft_seats.Aircraft == aircraft_cluster].SeatsLow.iloc[0])
        return n_passengers
