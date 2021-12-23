from typing import Union
from math import prod


class Operator:
    def __init__(self, version, typeid, children):
        self.version = version
        self.typeid = typeid
        self.children = children


class Literal:
    def __init__(self, version, value):
        self.version = version
        self.value = value


def get_packet_version(binstr: str) -> int:
    return int(binstr[0:3], 2)


def get_packet_type(binstr: str) -> int:
    return int(binstr[3:6], 2)


def get_packet_typeid(binstr: str) -> int:
    return int(binstr[6], 2)


def is_literal_packet(binstr: str) -> bool:
    return get_packet_type(binstr) == 4


def parse_literal_packet(binstr: str) -> (Literal, str):
    if not is_literal_packet(binstr):
        raise Exception("Cannot parse operator packet as literal packet")

    value_binstr = ""
    ptr = 6
    while ptr < len(binstr):
        header = binstr[ptr]
        value_binstr += binstr[ptr + 1:ptr + 5]
        ptr += 5
        if header == '0':
            break

    return Literal(version=get_packet_version(binstr), value=int(value_binstr, 2)), binstr[ptr:]


def parse_operator_packet(binstr: str) -> (Operator, str):
    if is_literal_packet(binstr):
        raise Exception("Cannot parse literal packet as operator packet")

    length_type = get_packet_typeid(binstr)

    operator = Operator(
        version=get_packet_version(binstr),
        typeid=get_packet_type(binstr),
        children=[]
    )

    if length_type == 0:
        length_bits = int(binstr[7:22], 2)
        remaining_binstr = binstr[22:22 + length_bits]

        while len(remaining_binstr) > 6:
            if is_literal_packet(remaining_binstr):
                result = parse_literal_packet(remaining_binstr)
            else:
                result = parse_operator_packet(remaining_binstr)
            operator.children.append(result[0])
            remaining_binstr = result[1]

        return operator, binstr[22 + length_bits:]
    else:
        number_of_children = int(binstr[7:18], 2)
        remaining_binstr = binstr[18:]

        for _ in range(0, number_of_children):
            if is_literal_packet(remaining_binstr):
                result = parse_literal_packet(remaining_binstr)
            else:
                result = parse_operator_packet(remaining_binstr)
            operator.children.append(result[0])
            remaining_binstr = result[1]

        return operator, remaining_binstr


def hexstr_to_binstr(hexstr: str) -> str:
    return "".join(["{0:b}".format(int(hexchar, 16)).zfill(4) for hexchar in hexstr])


def sum_of_versions(root) -> int:
    if isinstance(root, Literal):
        return root.version
    return root.version + sum([sum_of_versions(child) for child in root.children])


def eval_packet_expr(root: Union[Operator, Literal]) -> int:
    if isinstance(root, Literal):
        return root.value
    elif root.typeid == 0:
        return sum([eval_packet_expr(child) for child in root.children])
    elif root.typeid == 1:
        return prod([eval_packet_expr(child) for child in root.children])
    elif root.typeid == 2:
        return min([eval_packet_expr(child) for child in root.children])
    elif root.typeid == 3:
        return max([eval_packet_expr(child) for child in root.children])
    elif root.typeid == 5:
        return 1 if eval_packet_expr(root.children[0]) > eval_packet_expr(root.children[1]) else 0
    elif root.typeid == 6:
        return 1 if eval_packet_expr(root.children[0]) < eval_packet_expr(root.children[1]) else 0
    elif root.typeid == 7:
        return 1 if eval_packet_expr(root.children[0]) == eval_packet_expr(root.children[1]) else 0
    else:
        raise Exception("Unknown operator type ID")


with open("SolutionInput.txt") as file:
    line = file.readline()
    P1 = sum_of_versions(parse_operator_packet(hexstr_to_binstr(line))[0])
    print("Part 1: ", P1)
    P2 = eval_packet_expr(parse_operator_packet(hexstr_to_binstr(line))[0])
    print("Part 2: ", P2)
