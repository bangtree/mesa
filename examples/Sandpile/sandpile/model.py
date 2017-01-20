#
# Sandpile model
# See "How Nature Works" by Per Bak
# Adapted by Neal Thomison github.com/bangtree
#

import random

from collections import Counter

from mesa.time import BaseSchedule
from mesa import Model, Agent
from mesa.space import SimpleGrid

class OneAgentPerStep(BaseSchedule):
    """ One Agent Per Step Scheduler.

    Select an agent at random and call its *step* method.
    """

    def step(self):
        """
        Pick an agent at random, step it, bump counts.
        """

        self.agents[random.randint(self.get_agent_count())].step()
        self.steps += 1
        self.time += 1


class SandCell(Agent):

    def __init__(self, agent_id, model, spill_size):
        """
        Create a cell, in the given state, at the given row, col position.
        The row and col is specified in the agent_id tuple.
        """

        super().__init__(agent_id, model)
        self._row = agent_id[0]
        self._col = agent_id[1]
        self._spill_size = spill_size
        self._grains = 0
        self._spilling = False

    @property
    def spill_size(self):
        """Return cell's grain capacity."""
        return self._spill_size

    @property
    def grains(self):
        """Return cell's current grain count."""
        return self._grains

    @property
    def spilling(self):
        """Return agent's spilling state."""
        return self._spilling

    def step(self):
        """
        Agent has been selected and a grain of sand is added to it. If the cell
        exceeds it capacity it add's itself to the model's spill queue. The model
        handles distributing the spill to adjacent cells.
        """

        self.grains += 1

        if self.grains > self.spill_size:
            print('spill -> ', self.agent_id)
            self.model.spill(self) 

    def advance(self):
        """
        Set the state of the agent to the next state
        """
        self._state = self._next_state

class SandTableModel(Model):
    """
    The "sand table" where grains of sand fall.

    Space: SingleGrid
    Agent: SandCell
    Activation: OneAgentPerStep
    """

    def __init__(self, width, height):
        """
        """

        self._grid = SingleGrid(width, height, torus=False)
        self._schedule = SimultaneousActivation(self)

        # Need to iterate over all cells but don't need contents
        for (_, row, col) in self._grid.coord_iter():
            cell = SandCell((row, col), self, spill_size=3)
            self._grid.place_agent(cell, (row, col))
            self._schedule.add(cell)

        self.running = True
        self.spill_list = []

    def spill(self, agent):
        """Add agent to model's spill queue."""
        self.spill_list.append(agent)

    def _iter_spilling(self):
        while self.spill_list:
            yield spill_list.pop()
        return None

# spill_mask = ?
# call a fcn(agent) which returns effected neighborhood
#
# How do I find the agent's spill method?

    def step(self):
        """
        Process *spill_list* and advance the model one step.
        """
        for c in self.spill_list:
            
        self._schedule.step()

    # the following is a temporary fix for the framework classes accessing
    # model attributes directly
    # I don't think it should
    #   --> it imposes upon the model builder to use the attributes names that
    #       the framework expects.
    #
    # Traceback included in docstrings

    @property
    def grid(self):
        """
        /mesa/visualization/modules/CanvasGridVisualization.py
        is directly accessing Model.grid
             76     def render(self, model):
             77         grid_state = defaultdict(list)
        ---> 78         for y in range(model.grid.height):
             79             for x in range(model.grid.width):
             80                 cell_objects = model.grid.get_cell_list_contents([(x, y)])

        AttributeError: 'ColorPatchModel' object has no attribute 'grid'
        """
        return self._grid

    @property
    def schedule(self):
        """
        mesa_ABM/examples_ABM/color_patches/mesa/visualization/ModularVisualization.py",
        line 278, in run_model
            while self.model.schedule.steps < self.max_steps and self.model.running:
        AttributeError: 'NoneType' object has no attribute 'steps'
        """
        return self._schedule
