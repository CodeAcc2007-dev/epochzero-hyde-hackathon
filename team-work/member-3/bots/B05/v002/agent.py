"""B05 v002: bounded deterministic same-turn purchase-completion search."""
from member3_core import Policy


class Agent(Policy):
    def __init__(self):
        super().__init__('beam')
