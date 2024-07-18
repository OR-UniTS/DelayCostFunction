import os
import pandas as pd
import numpy as np
from typing import Callable


# Costs are expressed in EUR
# see Tables 13 and 14 at page 21/39 of following document
# https://www.beacon-sesar.eu/wp-content/uploads/2022/10/893100-BEACON-D3.2-Industry-briefing-on-updates-to-the-European-cost-of-delay-V.01.01.00-1.pdf
df_hard_reimbursement_rate = pd.read_csv(
    os.path.join(os.path.dirname(__file__), "PassengerReimbursementRates_2019.csv"))
dict_hard_reimbursement_rate = {haul: df_hard_reimbursement_rate[[haul, 'CostType']].set_index('CostType')[haul] for haul in ['ShortHaul', 'MediumHaul', 'LongHaul']}

df_hard_waiting_rate = pd.read_csv(os.path.join(os.path.dirname(__file__), "PassengerWaitingRates_2019.csv"))
dict_hard_waiting_rate = {haul: df_hard_waiting_rate[[haul, 'CostType']].set_index('CostType')[haul] for haul in ['ShortHaul', 'MediumHaul', 'LongHaul']}

df_hard = pd.read_csv(os.path.join(os.path.dirname(__file__), "PassengerTacticalCosts_HARD_2019.csv"))
dict_hard = {haul: df_hard[[haul, 'CostType']].set_index('CostType')[haul] for haul in ['ShortHaul', 'MediumHaul', 'LongHaul']}

df_waiting_passenger_costs = df_hard[['ShortHaul', 'MediumHaul', 'LongHaul']] * df_hard_waiting_rate[['ShortHaul', 'MediumHaul', 'LongHaul']]
df_waiting_passenger_costs['CostType'] = df_hard['CostType']
dict_waiting_passenger_costs = {haul: df_waiting_passenger_costs[haul].sum() for haul in ['ShortHaul', 'MediumHaul', 'LongHaul']}


df_reimbursement_passenger_costs = df_hard[['ShortHaul', 'MediumHaul', 'LongHaul']] * df_hard_reimbursement_rate[['ShortHaul', 'MediumHaul', 'LongHaul']]
df_reimbursement_passenger_costs['CostType'] = df_hard['CostType']
dict_reimbursement_passenger_costs = {haul: df_reimbursement_passenger_costs[haul].sum() for haul in ['ShortHaul', 'MediumHaul', 'LongHaul']}

# from The cost of passenger delay to airlines in Europe, consultation document, UOW 2015
# confirmed in deliverable D3.2 Industry  briefing  on updates  to  the  European cost of delay, Beacon Project, 2019
WAITING_RATE = .8
REIMBURSEMENT_RATE = 0.2

# from The cost of passenger delay to airlines in Europe, consultation document, UOW 2015
WAITING_RATE_LOW_COST = .9
REIMBURSEMENT_RATE_LOW_COST = 0.1


def get_interval(delay, costs, delays):
    if delay < delays[0]:
        return 0
    else:
        for i in range(delays.shape[0] - 1):
            if delays[i] <= delay < delays[i + 1]:
                return costs[i]
        return costs[-1]


def get_hard_costs(passengers: int, scenario: str, haul: str) -> Callable:
    waiting_passengers = passengers * (WAITING_RATE_LOW_COST if scenario == "LowScenario"
                                       else WAITING_RATE)
    reimbursement_passengers = passengers * (REIMBURSEMENT_RATE_LOW_COST if scenario == "LowScenario"
                                             else REIMBURSEMENT_RATE)
    passenger_care_support_list = ["care", "reimbursement_rebooking", "compensation", "accommodation"]
    waiting_passenger_costs = dict_waiting_passenger_costs[haul]
    reimbursement_passenger_costs = dict_reimbursement_passenger_costs[haul]
    total_passenger_costs = (waiting_passengers * waiting_passenger_costs + reimbursement_passengers
                             * reimbursement_passenger_costs)

    delays = np.array([120, 180, 240, 300, 600])

    return lambda delay: get_interval(delay, total_passenger_costs, delays)
