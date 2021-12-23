from numpy import array
from re import match


class Probe:
    def __init__(self, position=None, velocity=None):
        self.position = position if position is not None else array([0, 0])
        self.velocity = velocity if velocity is not None else array([0, 0])
        self.max_y = self.position[1]


class Target:
    def __init__(self, xmin, xmax, ymin, ymax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

    def is_inside(self, p: Probe) -> bool:
        return (self.xmin <= p.position[0] <= self.xmax) and (self.ymin <= p.position[1] <= self.ymax)

    def is_past(self, p: Probe) -> bool:
        return p.position[1] < self.ymin


def simulate_step(p: Probe) -> Probe:
    p.position += p.velocity
    if p.velocity[0] != 0:
        p.velocity[0] = p.velocity[0] - 1 if p.velocity[0] > 0 else p.velocity[0] + 1
    p.velocity[1] -= 1
    if p.position[1] > p.max_y:
        p.max_y = p.position[1]
    return p


def simulate_until_target(p: Probe, t: Target) -> bool:
    while not t.is_past(p):
        simulate_step(p)
        if t.is_inside(p):
            return True
    return False


def find_highest_max_y(t: Target) -> int:
    best_y = 0
    for y in range(1, 100):
        for x in range(1,100):
            p = Probe(velocity=array([x, y]))
            if simulate_until_target(p, t) and p.max_y > best_y:
                best_y = p.max_y
    return best_y


def find_successful_velocities(t: Target) -> [(int, int)]:
    vs = []
    for y in range(-100, 100):
        for x in range(1, 300):
            p = Probe(velocity=array([x, y]))
            if simulate_until_target(p, t):
                vs.append(tuple(p.velocity))
    return vs


def parse_input(filename: str) -> Target:
    with open(filename, "r") as file:
        line = file.readline()
        m = match(r'^target area: x=(.*)\.\.(.*), y=(.*)\.\.(.*)$', line)
        return Target(
            xmin=int(m.group(1)),
            xmax=int(m.group(2)),
            ymin=int(m.group(3)),
            ymax=int(m.group(4))
        )


t = parse_input("SolutionInput.txt")
p1 = find_highest_max_y(t)
p2 = len(find_successful_velocities(t))
