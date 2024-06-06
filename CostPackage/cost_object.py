from typing import List

from matplotlib import pyplot as plt


class CostObject:
    """Object containing the result of the cost function computation

    cost_function: lambda
        the lambda function which take as input the delay and returns the cost

    params_dict: dict
        the dictionary containing all parameters of the cost object

    get_params() ->list(str):
        methods which return all parameters included in the cost object

    info():
        methods that prints all parameters of the cost object

    plot(max_delay: int = 300, file_name: str = None, fig_size: tuple = (25, 15), font_size: int = 25)
        methods that plots the cost function from delay=0 to delay=max_delay

    plot_components(components: List[str]= all components, plot args)
        method that plots together the components in input list.
        If no input list is given all components are considered.
        Remaining inputs are the same of method plot
    """
    def __init__(self, cost_function, aircraft_type,
                 is_low_cost_airline, flight_length, destination_airport, crew_costs, maintenance_costs,
                 missed_connection_passengers,
                 curfew, aircraft_cluster, flight_phase, haul, scenario, passenger_scenario,
                 regular_passengers,
                 passengers_number,
                 crew_cost_function, maintenance_cost_function, fuel_costs, curfew_costs,
                 passengers_hard_costs, passengers_soft_costs):


        self.cost_function = cost_function

        self.aircraft_type = aircraft_type
        self.regular_passengers = regular_passengers
        self.passengers_number = passengers_number
        self.passenger_scenario = passenger_scenario
        self.is_low_cost_airline = is_low_cost_airline
        self.flight_length = flight_length
        self.destination_airport = destination_airport
        self.crew_costs = crew_costs
        self.maintenance_costs = maintenance_costs
        self.missed_connection_passengers = missed_connection_passengers
        self.curfew = curfew
        self.aircraft_cluster = aircraft_cluster
        self.flight_phase = flight_phase
        self.haul_type = haul
        self.final_cost_scenario = scenario
        self.final_passenger_scenario = passenger_scenario
        self.adjusted_passengers_number = passengers_number
        self.crew_costs_function = crew_cost_function
        self.maintenance_costs_function = maintenance_cost_function
        self.fuel_costs_function = fuel_costs
        self.curfew_costs_function = curfew_costs
        self.passengers_hard_costs_function = passengers_hard_costs
        self.passengers_soft_costs_function = passengers_soft_costs

        self.params_dict = self.make_params_dict()
        self.components_dict = self.make_components_dict()

    def plot(self, max_delay: int = 300, file_name: str = None, fig_size: tuple = (25, 15), font_size: int = 25):
        x = range(max_delay)
        y = [self.cost_function(x) for x in x]
        plt.rcParams['figure.figsize'] = fig_size
        plt.rcParams['font.size'] = font_size
        plt.xlabel('Delay (min)')
        plt.ylabel('Cost (€)')
        plt.tight_layout()
        plt.plot(x, y)
        if file_name is not None:
            plt.savefig(file_name)
            plt.clf()
            plt.cla()
            plt.close()
        else:
            plt.show()

    def plot_components(self, components: List[str] = None, max_delay: int = 300, file_name: str = None,
                        fig_size: tuple = (25, 15), font_size: int = 25, line_width=4):
        plt.rcParams['figure.figsize'] = fig_size
        plt.rcParams['font.size'] = font_size
        components = components if components is not None else self.components_dict.keys()
        for component in components:
            x = range(max_delay)
            y = [self.components_dict[component](x) for x in x]
            plt.plot(x, y, label=component, linewidth=line_width)
        plt.xlabel('Delay (min)')
        plt.ylabel('Cost (€)')
        plt.legend()
        plt.tight_layout()
        if file_name is not None:
            plt.savefig(file_name)
            plt.clf()
            plt.cla()
            plt.close()
        else:
            plt.show()

    def make_params_dict(self):
        return {
            "input_parameters": {
                "aircraft_type": self.aircraft_type,
                "passengers_number": self.passengers_number,
                "passenger_scenario": self.passenger_scenario,
                "is_low_cost_airline": self.is_low_cost_airline,
                "flight_length": self.flight_length,
                "destination_airport": self.destination_airport,
                "crew_costs": self.crew_costs,
                "maintenance_costs": self.maintenance_costs,
                "missed_connection_passengers": self.missed_connection_passengers,
                "flight_phase": self.flight_phase,
                "curfew": self.curfew
            },
            "derived_parameters": {
                "aircraft_cluster": self.aircraft_cluster,
                "haul_type": self.haul_type,
                "final_cost_scenario": self.final_cost_scenario,
                "final_passenger_scenario": self.passenger_scenario,
                "regular_passengers": self.regular_passengers,

            },
            "cost_functions": {
                "cost_function": self.cost_function,
                "crew_costs_function": self.crew_costs_function,
                "maintenance_costs_function": self.maintenance_costs_function,
                "fuel_costs_function": self.fuel_costs_function,
                "curfew_costs_function": self.curfew_costs_function,
                "passengers_hard_costs_function": self.passengers_hard_costs_function,
                "passengers_soft_costs_function": self.passengers_soft_costs_function
            }
        }

    def make_components_dict(self):
        return {
            "cost_function": self.cost_function,
            "crew_costs_function": self.crew_costs_function,
            "maintenance_costs_function": self.maintenance_costs_function,
            "fuel_costs_function": self.fuel_costs_function,
            "curfew_costs_function": self.curfew_costs_function,
            "passengers_hard_costs_function": self.passengers_hard_costs_function,
            "passengers_soft_costs_function": self.passengers_soft_costs_function

        }

    def get_params(self):

        key_list = list(self.params_dict.keys())
        params = []

        if len(key_list) == 3:
            params.append(key_list[0])

            # Accessing nested dictionary keys and converting them to string
            if isinstance(self.params_dict[key_list[1]], dict):
                params.extend(list(self.params_dict[key_list[1]].keys()))

            if isinstance(self.params_dict[key_list[2]], dict):
                params.extend(list(self.params_dict[key_list[2]].keys()))

        return params

    def info(self):

        top_level_keys = list(self.params_dict.keys())

        print("Input parameters")

        if isinstance(self.params_dict[top_level_keys[0]], dict):
            input_keys = list(self.params_dict[top_level_keys[0]].keys())
            for key in input_keys:
                print(key + ':', self.params_dict[top_level_keys[0]][key])

        print("\nDerived parameters")
        if isinstance(self.params_dict[top_level_keys[1]], dict):
            derived_keys = list(self.params_dict[top_level_keys[1]].keys())
            for key in derived_keys:
                print(key + ':',  self.params_dict[top_level_keys[1]][key])

        print("\nCost function and component functions")
        if isinstance(self.params_dict[top_level_keys[2]], dict):
            derived_keys = list(self.params_dict[top_level_keys[2]].keys())
            for key in derived_keys:
                print(key + ':',  self.params_dict[top_level_keys[2]][key])


