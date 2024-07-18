from typing import Callable
import os
import pandas as pd


# Crew costs in EUR provided directly by user without scenario
def check_valid_curfew_costs(curfew_costs_exact_value: float) -> float:
    if curfew_costs_exact_value < 0:
        raise InvalidCurfewCostsValueError(curfew_costs_exact_value)
    return curfew_costs_exact_value


df_curfew = pd.read_csv(os.path.join(os.path.dirname(__file__), "curfew.csv"))
dict_curfew = df_curfew.set_index('AirCluster')['Cost'].to_dict()


# -------------------------------------------------------------------------------------------------
# ---------- code commented as found in Cost Models inserted for further considerations------------
# Curfew costs
# def get_curfew_value(air_cluster: str, cost_scenario: str, curfew_passengers: int) -> float:
#     if air_cluster in wide_body_list:
#         return curfew_passengers * 254 + 19230
#     elif cost_scenario == "low":
#         return curfew_passengers * 102.75
#     else:
#         return curfew_passengers * 136.59
# to improve
# --------------------------------------------------------------------------------------------------

def get_curfew_costs(aircraft_cluster: str, curfew_passengers: int) -> float:
    return curfew_passengers * 300 + dict_curfew[aircraft_cluster]


class InvalidCurfewCostsValueError(Exception):
    def __init__(self, curfew_costs_exact_value: float):
        self.curfew_costs_exact_value = curfew_costs_exact_value
        self.message = ("Exact curfew costs value " + format(self.curfew_costs_exact_value, '.2f')
                        + " invalid. Value should be >=0")

    def __repr__(self):
        return "Exact curfew costs value " + format(self.curfew_costs_exact_value,
                                                    '.2f') + " invalid. Value should be >=0"
