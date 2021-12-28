from __future__ import annotations
from copy import deepcopy
from itertools import permutations
from math import ceil, floor
from typing import List, Union


class RNumber:
    def __init__(self, value: int, parent: SFNumber):
        self.value = value
        self.parent = parent

    def __add__(self, other: Union[RNumber, int]):
        return RNumber(self.value + (other if isinstance(other, int) else other.value), self.parent)

    def __iadd__(self, other: Union[RNumber, int]):
        self.value += other if isinstance(other, int) else other.value
        return self

    def __ge__(self, other: Union[RNumber, int]):
        return self.value >= other if isinstance(other, int) else other.value

    def __gt__(self, other: Union[RNumber, int]):
        return self.value > other if isinstance(other, int) else other.value

    def __le__(self, other: Union[RNumber, int]):
        return self.value <= other if isinstance(other, int) else other.value

    def __lt__(self, other: Union[RNumber, int]):
        return self.value < other if isinstance(other, int) else other.value

    def __eq__(self, other: Union[RNumber, int]):
        return self.value == other if isinstance(other, int) else other.value

    def __str__(self):
        return str(self.value)

    def root(self) -> SFNumber:
        return self if self.parent is None else self.parent.root()

    def split(self, parent: SFNumber) -> (RNumber, RNumber):
        return RNumber(floor(self.value / 2), parent), RNumber(ceil(self.value / 2), parent)


class SFNumber:
    @staticmethod
    def __extract_literal_pair__(lit: str) -> (Union[str, int], int):
        """
        >>> SFNumber.__extract_literal_pair__("[1,2]")
        ('[1,2]', 7)
        >>> SFNumber.__extract_literal_pair__("[3,4],[1,2]")
        ('[3,4]', 7)
        >>> SFNumber.__extract_literal_pair__("[[3,4],[5,6]],[2,1]")
        ('[[3,4],[5,6]]', 15)
        """
        if lit[0] != "[":
            comma_index = len(lit) if lit.find(",") == -1 else lit.index(",")
            return int(lit[0:comma_index]), comma_index + 2
        else:
            remaining_open_pair = 1
            index = 1
            for char in lit[1:]:
                if char == "[":
                    remaining_open_pair += 1
                elif char == "]":
                    remaining_open_pair -= 1

                if remaining_open_pair == 0:
                    break
                else:
                    index += 1
            return lit[:index + 1], index + 3

    @staticmethod
    def parse(lit: str, parent: Union[SFNumber, None] = None) -> SFNumber:
        """
        >>> isinstance(SFNumber.parse("[[1,2],[[3,4],5]]"), SFNumber)
        True
        >>> str(SFNumber.parse("[[1,2],[[3,4],5]]"))
        '[[1,2],[[3,4],5]]'
        """
        left_lit, right_start_index = SFNumber.__extract_literal_pair__(lit[1:])
        right_lit, _ = SFNumber.__extract_literal_pair__(lit[right_start_index:len(lit) - 1])

        number = SFNumber(parent=parent)
        number.left = RNumber(left_lit, number) if isinstance(left_lit, int) else SFNumber.parse(left_lit, number)
        number.right = RNumber(right_lit, number) if isinstance(right_lit, int) else SFNumber.parse(right_lit, number)

        return number

    @staticmethod
    def parse_all(data: str, delim: str = "\n"):
        return [SFNumber.parse(line) for line in data.split(delim)]

    @staticmethod
    def sum(numbers: List[SFNumber]) -> SFNumber:
        """
        >>> a0 = SFNumber.sum(
        ...     SFNumber.parse_all("\\n".join([
        ...         "[1,1]",
        ...         "[2,2]",
        ...         "[3,3]",
        ...         "[4,4]"
        ...     ]))
        ... )
        >>> str(a0)
        '[[[[1,1],[2,2]],[3,3]],[4,4]]'
        >>> a1 = SFNumber.sum(
        ...     SFNumber.parse_all("\\n".join([
        ...         "[1,1]",
        ...         "[2,2]",
        ...         "[3,3]",
        ...         "[4,4]",
        ...         "[5,5]"
        ...     ]))
        ... )
        >>> str(a1)
        '[[[[3,0],[5,3]],[4,4]],[5,5]]'
        >>> a2 = SFNumber.sum(
        ...     SFNumber.parse_all("\\n".join([
        ...         "[1,1]",
        ...         "[2,2]",
        ...         "[3,3]",
        ...         "[4,4]",
        ...         "[5,5]",
        ...         "[6,6]"
        ...     ]))
        ... )
        >>> str(a2)
        '[[[[5,0],[7,4]],[5,5]],[6,6]]'
        >>> a3 = SFNumber.sum(
        ...     SFNumber.parse_all("\\n".join([
        ...         "[[[0,[4,5]],[0,0]],[[[4,5],[2,6]],[9,5]]]",
        ...         "[7,[[[3,7],[4,3]],[[6,3],[8,8]]]]",
        ...         "[[2,[[0,8],[3,4]]],[[[6,7],1],[7,[1,6]]]]",
        ...         "[[[[2,4],7],[6,[0,5]]],[[[6,8],[2,8]],[[2,1],[4,5]]]]",
        ...         "[7,[5,[[3,8],[1,4]]]]",
        ...         "[[2,[2,2]],[8,[8,1]]]",
        ...         "[2,9]",
        ...         "[1,[[[9,3],9],[[9,0],[0,7]]]]",
        ...         "[[[5,[7,4]],7],1]",
        ...         "[[[[4,2],2],6],[8,7]]",
        ...     ]))
        ... )
        >>> str(a3)
        '[[[[8,7],[7,7]],[[8,6],[7,7]]],[[[0,7],[6,6]],[8,7]]]'
        """
        result = numbers[0]
        for number in numbers[1:]:
            result += number
        return result

    def __init__(self, left: Union[SFNumber, RNumber, None] = None, right: Union[SFNumber, RNumber, None] = None, parent: Union[SFNumber, None] = None):
        self.left = left
        self.right = right
        self.parent = parent

    def __add__(self, other: SFNumber) -> SFNumber:
        """
        >>> a = SFNumber.parse("[[[[4,3],4],4],[7,[[8,4],9]]]")
        >>> b = SFNumber.parse("[1,1]")
        >>> c = a + b
        >>> str(c)
        '[[[[0,7],4],[[7,8],[6,0]]],[8,1]]'
        >>> a.parent is c
        True
        >>> b.parent is c
        True
        >>> a0 = SFNumber.parse("[[[0,[4,5]],[0,0]],[[[4,5],[2,6]],[9,5]]]")
        >>> b0 = SFNumber.parse("[7,[[[3,7],[4,3]],[[6,3],[8,8]]]]")
        >>> c0 = a0 + b0
        >>> str(c0)
        '[[[[4,0],[5,4]],[[7,7],[6,0]]],[[8,[7,7]],[[7,9],[5,0]]]]'
        >>> a1 = SFNumber.parse("[[[[4,0],[5,4]],[[7,7],[6,0]]],[[8,[7,7]],[[7,9],[5,0]]]]")
        >>> b1 = SFNumber.parse("[[2,[[0,8],[3,4]]],[[[6,7],1],[7,[1,6]]]]")
        >>> c1 = a1 + b1
        >>> str(c1)
        '[[[[6,7],[6,7]],[[7,7],[0,7]]],[[[8,7],[7,7]],[[8,8],[8,0]]]]'
        >>> a2 = SFNumber.parse("[[[[6,7],[6,7]],[[7,7],[0,7]]],[[[8,7],[7,7]],[[8,8],[8,0]]]]")
        >>> b2 = SFNumber.parse("[[[[2,4],7],[6,[0,5]]],[[[6,8],[2,8]],[[2,1],[4,5]]]]")
        >>> c2 = a2 + b2
        >>> str(c2)
        '[[[[7,0],[7,7]],[[7,7],[7,8]]],[[[7,7],[8,8]],[[7,7],[8,7]]]]'
        >>> a3 = SFNumber.parse("[[[[7,0],[7,7]],[[7,7],[7,8]]],[[[7,7],[8,8]],[[7,7],[8,7]]]]")
        >>> b3 = SFNumber.parse("[7,[5,[[3,8],[1,4]]]]")
        >>> c3 = a3 + b3
        >>> str(c3)
        '[[[[7,7],[7,8]],[[9,5],[8,7]]],[[[6,8],[0,8]],[[9,9],[9,0]]]]'
        """
        root = SFNumber(self, other)
        self.parent = root
        other.parent = root
        root.reduce()
        return root

    def __str__(self):
        return '[{},{}]'.format(str(self.left), str(self.right))

    def root(self) -> SFNumber:
        return self if self.parent is None else self.parent.root()

    def rightmost_rnumber(self):
        """
        >>> str(SFNumber.parse("[[1,2],[[3,4],[5,[6,7]]]]").rightmost_rnumber())
        '7'
        """
        return self.right if isinstance(self.right, RNumber) else self.right.rightmost_rnumber()

    def leftmost_rnumber(self):
        """
        >>> str(SFNumber.parse("[[1,2],[[3,4],[5,[6,7]]]]").leftmost_rnumber())
        '1'
        """
        return self.left if isinstance(self.left, RNumber) else self.left.leftmost_rnumber()

    def prev_adj_rnumber(self):
        """
        >>> str(SFNumber.parse("[[1,2],[[3,4],[5,[6,7]]]]").left.prev_adj_rnumber())
        'None'
        >>> str(SFNumber.parse("[[1,2],[[3,4],[5,[6,7]]]]").right.left.prev_adj_rnumber())
        '2'
        >>> str(SFNumber.parse("[[1,2],[[3,4],[5,[6,7]]]]").right.right.prev_adj_rnumber())
        '4'
        >>> str(SFNumber.parse("[[6,[5,[4,[3,2]]]],1]").left.right.right.right.prev_adj_rnumber())
        '4'
        >>> str(SFNumber.parse("[[6,[5,[[3,2],4]]],1]").left.right.right.left.prev_adj_rnumber())
        '5'
        >>> str(SFNumber.parse("[[6,[[2,1],[[3,2],4]]],1]").left.right.right.left.prev_adj_rnumber())
        '1'
        >>> str(SFNumber.parse("[[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]]").left.right.right.right.prev_adj_rnumber())
        '1'
        """
        if self.parent and self.parent.left is self:
            return None if self.parent.parent is None else self.parent.prev_adj_rnumber()
        else:
            return self.parent.left.rightmost_rnumber() if isinstance(self.parent.left, SFNumber) else self.parent.left

    def next_adj_rnumber(self):
        """
        >>> str(SFNumber.parse("[[1,2],[[3,4],[5,[6,7]]]]").left.next_adj_rnumber())
        '3'
        >>> str(SFNumber.parse("[[1,2],[[3,4],[5,[6,7]]]]").right.left.next_adj_rnumber())
        '5'
        >>> str(SFNumber.parse("[[1,2],[[3,4],[5,[6,7]]]]").right.right.next_adj_rnumber())
        'None'
        >>> str(SFNumber.parse("[[6,[5,[4,[3,2]]]],1]").left.right.right.right.next_adj_rnumber())
        '1'
        >>> str(SFNumber.parse("[[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]]").left.right.right.right.next_adj_rnumber())
        '6'
        """
        if self.parent and self.parent.right is self:
            return None if self.parent.parent is None else self.parent.next_adj_rnumber()
        else:
            return self.parent.right.leftmost_rnumber() if isinstance(self.parent.right, SFNumber) else self.parent.right

    def explode(self) -> SFNumber:
        """
        >>> str(SFNumber.parse("[[[[[9,8],1],2],3],4]").left.left.left.left.explode().root())
        '[[[[0,9],2],3],4]'
        >>> str(SFNumber.parse("[7,[6,[5,[4,[3,2]]]]]").right.right.right.right.explode().root())
        '[7,[6,[5,[7,0]]]]'
        >>> str(SFNumber.parse("[[6,[5,[4,[3,2]]]],1]").left.right.right.right.explode().root())
        '[[6,[5,[7,0]]],3]'
        >>> str(SFNumber.parse("[[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]]").left.right.right.right.explode().root())
        '[[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]]'
        >>> str(SFNumber.parse("[[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]]").right.right.right.right.explode().root())
        '[[3,[2,[8,0]]],[9,[5,[7,0]]]]'
        >>> str(SFNumber.parse("[[[[0,7],4],[[7,8],[0,[6,7]]]],[1,1]]").left.right.right.right.explode().root())
        '[[[[0,7],4],[[7,8],[6,0]]],[8,1]]'
        """
        if isinstance(self.left, SFNumber) or isinstance(self.right, SFNumber):
            raise Exception("Can only reduce a SFNumber containing RNumber objects")

        prev_adj_rnumber = self.prev_adj_rnumber()
        next_adj_rnumber = self.next_adj_rnumber()

        if prev_adj_rnumber is not None:
            prev_adj_rnumber += self.left
        if next_adj_rnumber is not None:
            next_adj_rnumber += self.right

        if self.parent.left is self:
            self.parent.left = RNumber(0, self.parent)
        else:
            self.parent.right = RNumber(0, self.parent)

        return self.parent

    def explode_next(self) -> bool:
        remaining = [(self, 0)]
        while len(remaining) > 0:
            number, depth = remaining.pop()
            if depth == 4 and isinstance(number.left, RNumber) and isinstance(number.right, RNumber):
                number.explode()
                return True
            if isinstance(number.right, SFNumber):
                remaining.append((number.right, depth + 1))
            if isinstance(number.left, SFNumber):
                remaining.append((number.left, depth + 1))
        return False

    def split_next(self) -> bool:
        remaining = [self]
        while len(remaining) > 0:
            number = remaining.pop()
            if isinstance(number, SFNumber):
                remaining.append(number.right)
                remaining.append(number.left)
            if isinstance(number, RNumber) and number >= 10:
                new_number = SFNumber(parent=number.parent)
                left, right = number.split(parent=new_number)
                new_number.left = left
                new_number.right = right
                if number.parent.left is number:
                    number.parent.left = new_number
                else:
                    number.parent.right = new_number
                return True
        return False

    def reduce(self) -> SFNumber:
        """
        >>> str(SFNumber.parse("[[[[[4,3],4],4],[7,[[8,4],9]]],[1,1]]").reduce())
        '[[[[0,7],4],[[7,8],[6,0]]],[8,1]]'
        """
        while True:
            did_split = False
            did_explode = self.explode_next()
            if not did_explode:
                did_split = self.split_next()
            if not did_explode and not did_split:
                return self

    def magnitude(self) -> int:
        """
        >>> SFNumber.parse("[[1,2],[[3,4],5]]").magnitude()
        143
        >>> SFNumber.parse("[[[[0,7],4],[[7,8],[6,0]]],[8,1]]").magnitude()
        1384
        >>> SFNumber.parse("[[[[1,1],[2,2]],[3,3]],[4,4]]").magnitude()
        445
        >>> SFNumber.parse("[[[[3,0],[5,3]],[4,4]],[5,5]]").magnitude()
        791
        >>> SFNumber.parse("[[[[5,0],[7,4]],[5,5]],[6,6]]").magnitude()
        1137
        >>> SFNumber.parse("[[[[8,7],[7,7]],[[8,6],[7,7]]],[[[0,7],[6,6]],[8,7]]]").magnitude()
        3488
        """
        result = 0
        if isinstance(self.left, RNumber):
            result += 3 * self.left.value
        else:
            result += 3 * self.left.magnitude()
        if isinstance(self.right, RNumber):
            result += 2 * self.right.value
        else:
            result += 2 * self.right.magnitude()
        return result


def solve_p1(data: str):
    """
    >>> solve_p1("[[[[4,3],4],4],[7,[[8,4],9]]]\\n[1,1]")
    1384
    """
    numbers = SFNumber.parse_all(data)
    return SFNumber.sum(numbers).magnitude()


def solve_p2(data: str):
    """
    >>> data = "\\n".join([
    ...     "[[[0,[5,8]],[[1,7],[9,6]]],[[4,[1,2]],[[1,4],2]]]",
    ...     "[[[5,[2,8]],4],[5,[[9,9],0]]]",
    ...     "[6,[[[6,2],[5,6]],[[7,6],[4,7]]]]",
    ...     "[[[6,[0,7]],[0,9]],[4,[9,[9,0]]]]",
    ...     "[[[7,[6,4]],[3,[1,3]]],[[[5,5],1],9]]",
    ...     "[[6,[[7,3],[3,2]]],[[[3,8],[5,7]],4]]",
    ...     "[[[[5,4],[7,7]],8],[[8,3],8]]",
    ...     "[[9,3],[[9,9],[6,[4,9]]]]",
    ...     "[[2,[[7,7],7]],[[5,8],[[9,3],[0,2]]]]",
    ...     "[[[[5,2],5],[8,[3,7]]],[[5,[7,5]],[4,4]]]",
    ... ])
    >>> solve_p2(data)
    3993
    """
    numbers = SFNumber.parse_all(data)
    magnitudes = []
    for a, b in permutations(numbers, 2):
        magnitudes.append((deepcopy(a) + deepcopy(b)).magnitude())
    return max(magnitudes)


with open("Input.txt", "r") as file:
    data = file.read()
    p1 = solve_p1(data)
    print("Part 1: ", p1)
    p2 = solve_p2(data)
    print("Part 2: ", p2)
