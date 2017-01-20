from mesa import Agent, Model
from mesa.space import Grid
from mesa.time import BaseScheduler

from mesa.visualization.TextVisualization import TextGrid

import random


class OneAgentPerStep(BaseScheduler):
    """ One Agent Per Step Scheduler.

    Select an agent at random and call its *step* method.
    """

    def step(self):
        """
        Pick an agent at random, step it, bump counts.
        """

        self.agents[random.randint(0, self.get_agent_count()-1)].step()
        self.steps += 1
        self.time += 1


class SandTable(Grid):

    def __init__(self, width, height):
        super().__init__(width, height, torus=False)
        self.viz = TextGrid(self, self.val_converter)
        self.spill_q = []       # agents who are currently 'spilling'
        self.avalanches = []    # [(step, cnt) ... ]

    def val_converter(self, agent):
        return '%1d ' % (agent._grains)

    def render(self):
        print(self.viz.render())

    def spilling(self, cell):
        self.spill_q.append(cell)

    def distribute(self, model):
        cnt = 0
        while self.spill_q:
            agent = self.spill_q.pop()
            x, y = agent.unique_id
            for n in model.grid.neighbor_iter(agent.unique_id, moore=False):
                n.add_a_grain()
            agent._grains -= 4
            if agent._grains < 0:
                print('grains < 0!', agent.unique_id, agent._grains)
                exit()
            agent._spilling = False
            cnt += 1
        self.avalanches.append((model.schedule.time, cnt))


class SandColumn(Agent):

    def __init__(self, unique_id, model, spill_size=3):
        super().__init__(unique_id, model)
        self._spill_size = spill_size
        self._grains = 0
        self._spilling = False

    def __str__(self):
        return str(self.unique_id)

    @property
    def spill_size(self):
        return self._spill_size

    @spill_size.setter
    def spill_size(self, val):
        if not isinstance(val, int) or val < 0:
            raise TypeError('spill_size must be int type 0 or greater!')
        self._spill_size = val

    def add_a_grain(self):
        self._grains += 1
        if self._grains > self._spill_size and not self._spilling:
            # print('Spill: ', self.unique_id, self._grains)
            self._spilling = True
            self.model.grid.spilling(self)

    def step(self):
        # print('Step: ', self.unique_id)
        self.add_a_grain()
        if self._spilling:
            # Have model distribute sand
            self.model.grid.distribute(self.model)


class SandTableModel(Model):

    def __init__(self, width, height):
        super().__init__(seed=42)
        self.num_agents = width * height
        self.running = True
        self.grid = SandTable(width, height)
        self.schedule = OneAgentPerStep(self)

        # Create agents and fill grid
        for x in range(width):
            for y in range(height):
                a = SandColumn((x, y), self)
                self.grid.place_agent(a, (x, y))
                self.schedule.add(a)

    def step(self):
        self.schedule.step()
        # self.grid.render()

    def run_model(self, n):
        for i in range(n):
            self.step()


m = SandTableModel(100, 100)

m.run_model(100000)

print('time, slide size')
for entry in m.grid.avalanches:
    print('%d, %d' % (entry[0], entry[1]))

# m.grid.avalanches.sort(key=lambda pair: pair[1])
# print(m.grid.avalanches)

# s = SandColumn('1', None, 5)
# print(s.spill_size)
# s.spill_size = 3
# print(s.spill_size)

# g.grid[2][2] = 1
# viz = TextGrid(g, my_converter)
# # viz = TextGrid(g, TextGrid.converter)
# print(viz.render())
