"""Matched common-evaluator control: no beam and no visible-threat layer."""
from member3_core import Policy


class Agent(Policy):
    def __init__(self):
        super().__init__('greedy')
