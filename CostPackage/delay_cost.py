from CostPackage.Curfew.curfew_costs import check_valid_curfew_costs
from CostPackage.TacticalDelayCosts import *
from CostPackage.cost_object import CostObject


def get_delay_cost(aircraft_type: str,
                   passengers: int | str = None,
                   is_low_cost_airline: bool = None,
                   flight_length: float = None,
                   destination_airport: str = None,
                   crew_costs: float | str = None,
                   maintenance_costs: float | str = None,
                   missed_connection_passengers: List[Tuple] = None,
                   curfew: tuple[float, int] | Union[int, float] = None
                   ) -> CostObject:
    """Generate cost function of delay of a given flight according to the specifics
    Parameters:
        aircraft_type: str
            aircraft(ICAO code)
        passengers: int | str = None
            int is provided means passengers number,
            actual number of passengers boarded on the aircraft,
            when not provided the base scenario for passengers number will be considered
            str is provided means passengers scenario,
            "low" 65% of seats capacity: 
            "base" 80% of seats capacity is the normal scenario (most common)
            "high" 95% of seats capacity
            for wide-body aircraft the capacity is set to 85%
        is_low_cost_airline: bool=None
            boolean value set to true if airline is Low-Cost Carrier (LCC), if true
            sets all the cost scenarios to low
        flight_length: float=None
            Length of flight in kilometers to calculate the type of haul
            (actual fuel costs can be calculated only if provided)
        destination_airport: str=None
            ICAO code of airport of arrival
        crew_costs: float | str =None
            float value means costs of entire crew (pilots and cabin crew) in EUR/min
            str value represents the crew costs scenario which can be either "low", "base" or "high"
            "low" means zero EUR/min costs for the entire crew
            "base" is the normal scenario (most common)
            "high" is the expensive scenario
        maintenance_costs: float | str = None
            float value means costs expressed in EUR/min
            (ATTENTION tactical maintenance costs may be very different at the various flight phases)
            str value represents the maintenance costs scenario which can be either "low", "base" or "high"
            depending on aircraft age, maintenance status etc.
            "low" can be applied for example on newer aircraft or if ordinary maintenance was recently made
            "base"
            "base" is the normal scenario (most common)
            "high" is the expensive scenario (e.g. old aircraft or expensive tactical maintenance)
        missed_connection_passengers: List[Tuple] = None
             list of tuples. Each tuple represents one passenger,
             its composition is (delay threshold, delay perceived).
             The delay threshold is the time at which the passenger misses the connection.
             The delay perceived is the delay at the passenger final destination,
             generally computed considering the next available flight of the same airline which carries
             the passenger to its final destination
        curfew: Tuple[curfew_time: float, n_passenger: int] or float, default None,
             react_curfew: Union[tuple[float, str], tuple[float, int]] = None


        return: CostObject
        """

    # Zero costs lambda if both scenario and exact value are None
    def zero_costs():
        return lambda delay: 0

    # DEFAULT
    haul = "MediumHaul"
    scenario = "BaseScenario"
    passenger_scenario = "BaseScenario"
    regular_passengers = 0
    aircraft_cluster = None
    crew_costs_function = zero_costs()
    maintenance_cost_function = zero_costs()
    total_fuel_costs = zero_costs()
    curfew_costs = zero_costs()
    passengers_hard_costs = zero_costs()
    passengers_soft_costs = zero_costs()

    flight_phase = 'AT_GATE'  # default parameter, to be used in future development

    class FunctionInputParametersError(Exception):
        def __init__(self, conflict_type: str):
            self.conflict_type = conflict_type
            self.message = ("Conflict between exact value and scenario for: " + self.conflict_type
                            + " Cannot both be non None")

        def __repr__(self):
            return "Conflict between exact value and scenario for: " + self.conflict_type + " Cannot both be non None"

    try:
        aircraft_cluster = get_aircraft_cluster(aircraft_type)

        # to calculate passengers hard costs, haul determined according to flight length is needed
        # if flight_length is None a default value could be used to have a Medium Haul e.g. flight_length=2000
        # this could be valid only AT GATE, default flight_length value could disrupt fuel costs in EN ROUTE phase
        # if flight_length is None:
        #   haul = get_haul(fixed_flight_length)

        if flight_length is not None:
            haul = get_haul(flight_length)

        if (destination_airport is not None) and (
                is_valid_airport_icao(airport_icao=destination_airport.strip().upper())):
            destination_airport = destination_airport

        # If airline is LCC sets all costs scenario to low,
        # elif destination airport is in group 1 airports (more than 25 million passengers) set scenario to high
        # else scenario default is base

        if is_low_cost_airline is not None or destination_airport is not None:
            scenario = get_fixed_cost_scenario(is_low_cost_airline=is_low_cost_airline,
                                               destination_airport_ICAO=destination_airport)
            passenger_scenario = scenario if passengers is None or type(passengers) is int else passengers

        # without passengers number input inserted use passengers load factor based on scenario either inserted by user
        # or indirectly obtained by previous if statement
        if passengers is None:
            if type(passengers) is str:
                passenger_scenario = passengers
            else:
                passenger_scenario = scenario

            passengers_number = get_passengers(aircraft_type=aircraft_cluster, scenario=passenger_scenario)
        else:
            passengers_number = passengers

        number_missed_connection_passengers = 0 if missed_connection_passengers is None else len(
            missed_connection_passengers)

        regular_passengers = passengers_number - number_missed_connection_passengers

        # CREW COSTS
        # NO crew costs input, either manage as zero costs or choose a default scenario
        if crew_costs is None:
            crew_costs_function = get_crew_costs(aircraft_cluster=aircraft_cluster, scenario=scenario)
        # Crew costs based on exact value
        elif type(crew_costs) is float:
            crew_costs_function = get_crew_costs_from_exact_value(crew_costs)
        # Crew cost estimation based on scenario
        elif type(crew_costs) is str:
            crew_costs_function = get_crew_costs(aircraft_cluster=aircraft_cluster, scenario=crew_costs)
        else:
            raise FunctionInputParametersError("CREW")

        # MAINTENANCE COSTS
        # NO maintenance costs input,  either manage as zero costs or choose a default scenario
        if maintenance_costs is None:
            maintenance_cost_function = get_maintenance_costs(aircraft_cluster=aircraft_cluster,
                                                            scenario=scenario, flight_phase=flight_phase)
        # Maintenance costs based on exact value
        elif type(maintenance_costs) is float:
            maintenance_cost_function = get_maintenance_costs_from_exact_value(maintenance_costs)
        # Maintenance costs based on scenario
        elif type(maintenance_costs) is str:
            maintenance_cost_function = get_maintenance_costs(aircraft_cluster=aircraft_cluster,
                                                            scenario=maintenance_costs, flight_phase=flight_phase)
        else:
            raise FunctionInputParametersError("MAINTENANCE")

        # CURFEW COSTS
        if curfew is None:
            curfew_costs = zero_costs()
        elif type(curfew) is tuple or type(curfew) in [float, int]:
            curfew_threshold = curfew[0] if type(curfew) is tuple else curfew
            curfew_passengers = curfew[
            1] if type(curfew) is tuple else regular_passengers + number_missed_connection_passengers
            curfew_cost_value = get_curfew_costs(aircraft_cluster=aircraft_cluster, curfew_passengers=curfew_passengers)
            curfew_costs = lambda d: curfew_cost_value if d > curfew_threshold else 0

        else:  # Both parameters are not None, situation managed as a conflict
            raise FunctionInputParametersError("CURFEW")

        # PASSENGER COSTS
        # Soft and Hard costs of passengers who didn't lose the connection
        passengers_hard_costs = get_hard_costs(passengers=regular_passengers, scenario=passenger_scenario, haul=haul)
        passengers_soft_costs = get_soft_costs(passengers=regular_passengers, scenario=passenger_scenario)

        # Soft and Hard costs of passengers with missed connection
        if number_missed_connection_passengers > 0:
            # Hard and soft costs for a single passenger
            missed_connection_passengers_hard_costs = get_hard_costs(passengers=1, scenario=passenger_scenario,
                                                                     haul=haul)
            missed_connection_passengers_soft_costs = get_soft_costs(passengers=1, scenario=passenger_scenario)

            def considered_passenger_costs(delay, passenger, cost_type):
                # Set only care if delay is less than passenger connection threshold
                # Set 0 if delay < passenger connection threshold
                considered_passengers_cost_function = missed_connection_passengers_hard_costs if cost_type == 'hard' \
                    else missed_connection_passengers_soft_costs
                return considered_passengers_cost_function(delay if delay < passenger[0] else passenger[1])

            passengers_costs = lambda delay: passengers_hard_costs(delay) + passengers_soft_costs(delay) + sum(
                considered_passenger_costs(delay, passenger, 'hard') for passenger in
                missed_connection_passengers) + sum(
                considered_passenger_costs(delay, passenger, 'soft') for passenger in
                missed_connection_passengers)
        else:
            passengers_costs = lambda delay: passengers_hard_costs(delay) + passengers_soft_costs(delay)

    except AircraftClusterError as aircraft_cluster_error:
        print(aircraft_cluster_error.message)

    except AirportCodeError as airport_code_error:
        print(airport_code_error.message)

    except HaulError as haul_error:
        print(haul_error.message)

    except ScenarioError as scenario_error:
        print(scenario_error.message)

    except PassengersLoadFactorError as passengers_load_factor_error:
        print(passengers_load_factor_error.message)

    except InvalidCrewCostsValueError as invalid_crew_costs_value_error:
        print(invalid_crew_costs_value_error.message)

    except InvalidMaintenanceCostsValueError as invalid_maintenance_costs_value_error:
        print(invalid_maintenance_costs_value_error.message)

    except InvalidCurfewCostsValueError as invalid_curfew_costs_value_error:
        print(invalid_curfew_costs_value_error.message)

    except FunctionInputParametersError as function_input_parameters_conflict_error:
        print(function_input_parameters_conflict_error.message)

    except Exception as e:
        print(print(f"An unexpected exception occurred: {e}"))

    finally:
        cost_function = lambda delay: (maintenance_cost_function(delay) + crew_costs_function(delay)
                                       + passengers_costs(delay) + curfew_costs(delay))

        cost_object = CostObject(cost_function, aircraft_type,
                                 is_low_cost_airline, flight_length, destination_airport, crew_costs, maintenance_costs,
                                 missed_connection_passengers,
                                 curfew, aircraft_cluster, flight_phase, haul, scenario, passenger_scenario,
                                 regular_passengers, passengers_number,
                                 crew_costs_function, maintenance_cost_function, total_fuel_costs, curfew_costs,
                                 passengers_hard_costs, passengers_soft_costs)

        return cost_object
