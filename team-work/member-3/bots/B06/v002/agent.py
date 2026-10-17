"""B06 v002: visible opponent threats and strict bonus-race evaluation."""
from member3_core import Policy


class Agent(Policy):
    def __init__(self):
        super().__init__('threat')
