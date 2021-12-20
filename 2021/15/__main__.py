import array

import numpy as np
from networkx import *
from numpy import *

COMPASS = [
    array([1, 0]),
    array([0, 1]),
    array([-1, 0]),
    array([0, -1])
]


def parse_matrix(fn):
    with open(fn, "r") as file:
        rows = []
        for line in file:
            columns = []
            for char in line.strip():
                columns.append(int(char))
            rows.append(columns)
        return matrix(rows)


def check_bounds(matrix, i: int, j: int) -> bool:
    max_i, max_j = shape(matrix)
    return 0 <= i < max_i and 0 <= j < max_j


def build_graph(matrix) -> DiGraph:
    max_i, max_j = shape(matrix)
    graph = DiGraph()
    for j in range(0, max_j):
        for i in range(0, max_i):
            for coord in [array([j, i]) + direction for direction in COMPASS]:
                if not check_bounds(matrix, coord[0], coord[1]):
                    continue
                graph.add_edge(tuple([j, i]), tuple(coord), weight=matrix[coord[0], coord[1]])
    return graph


def shortest_path_risk(graph: DiGraph, matrix) -> int:
    max_i, max_j = shape(matrix)
    path = shortest_path(graph, source=(0, 0), target=(max_j - 1, max_i - 1), weight="weight")
    return sum([matrix[coord] for coord in path]) - matrix[0, 0]


def vectorized_shift_value(count):
    def shift_value(m):
        return where(count < 1, m, np.mod(np.add(m, count + 9), 9))

    return shift_value


def extend_matrix(m):
    for j in range(0, 5):
        for i in range(0, 5):
            m_2 = vectorized_shift_value(i + j)(m)
            m_2[m_2 < 1] = 9
            if i == 0:
                m_row = m_2
            else:
                m_row = concatenate((m_row, m_2), axis=1)
        if j == 0:
            m_all = m_row
        else:
            m_all = concatenate((m_all, m_row))
    return m_all


M1 = parse_matrix("SolutionInput.txt")
G1 = build_graph(M1)
R1 = shortest_path_risk(G1, M1)
print("Part 1: ", R1)

M2 = extend_matrix(M1)
G2 = build_graph(M2)
R2 = shortest_path_risk(G2, M2)
print("Part 2: ", R2)
