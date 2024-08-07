from CostPackage.Airport.airport import is_group_1_airport


class ScenarioError(Exception):
    def __init__(self, scenario: str):
        self.scenario = scenario
        self.message = "Scenario " + self.scenario + " not found"

    def __repr__(self):
        return "Scenario " + self.scenario + " not found"


dict_scenario = {'low': 'LowScenario',
'base': 'BaseScenario',
'high': 'HighScenario',
'LowScenario': 'LowScenario',
'BaseScenario': 'BaseScenario',
'HighScenario': 'HighScenario'}


def get_scenario(scenario: str):
    try:
        return dict_scenario[scenario]
    except KeyError:
        raise ScenarioError(scenario)


# Cost scenario based on Aircraft Operator Low-Cost Carrier (LCC)
# and destination airport in group 1 (large airports with more than 25 million passengers)
# see page 28/39 of the following report (costs  originally  calculated by RDC aviation)
# https://www.beacon-sesar.eu/wp-content/uploads/2022/10/893100-BEACON-D3.2-Industry-briefing-on-updates-to-the-European-cost-of-delay-V.01.01.00-1.pdf
def get_fixed_cost_scenario(is_low_cost_airline: bool = None, destination_airport_ICAO: str = None) -> str:
    if is_low_cost_airline is not None and is_low_cost_airline:
        return "LowScenario"
    else:
        if destination_airport_ICAO is not None and is_group_1_airport(destination_airport_ICAO):
            return "HighScenario"
    return "BaseScenario"
