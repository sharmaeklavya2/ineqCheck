#!/usr/bin/env python3

import sys  # noqa
import argparse
import re
from collections.abc import Sequence
from typing import Generic, Literal, NamedTuple, TypeVar

from graph import DiGraph, sccDecomp

# [ Ineq ]======================================================================

IneqType = Literal['<', '≤', '=', '≥', '>']
T = TypeVar('T')


class Ineq(NamedTuple, Generic[T]):
    lhs: T
    op: IneqType
    rhs: T

    def __str__(self) -> str:
        return '{} {} {}'.format(self.lhs, self.op, self.rhs)


class VarGroup(NamedTuple, Generic[T]):
    id: int
    names: tuple[T, ...]

    def __str__(self) -> str:
        return ' = '.join([str(x) for x in self.names])

    def __repr__(self) -> str:
        return '{}({}, {})'.format(self.__class__.__name__, self.id, self.names)


def stdizeIneq(ineq: Ineq[T]) -> Ineq[T]:
    if ineq.op == '>':
        return Ineq(ineq.rhs, '<', ineq.lhs)
    elif ineq.op == '≥':
        return Ineq(ineq.rhs, '≤', ineq.lhs)
    else:
        return ineq


def stdizeIneqs(ineqs: Sequence[Ineq[T]]) -> Sequence[Ineq[T]]:
    return [stdizeIneq(ineq) for ineq in ineqs]


def parseIneqs(lines: Sequence[str]) -> Sequence[Ineq[str]]:
    ineqs: list[Ineq[str]] = []
    for line in lines:
        parts = line.split(':', maxsplit=1)
        if len(parts) == 2:
            label, ineqChain = parts
        else:
            (ineqChain,) = parts
        del parts
        parts2 = re.split(r'([<≤=≥>])', ineqChain)
        n = len(parts2) // 2
        for i in range(n):
            lhs, rawOp, rhs = parts2[2*i: 2*i+3]
            op: IneqType = rawOp  # type: ignore # explicit_cast(str, IneqType)
            ineqs.append(Ineq(lhs.strip(), op, rhs.strip()))
    return stdizeIneqs(ineqs)


# [ process ]===================================================================

def getIneqGraph(ineqs: Sequence[Ineq[T]]) -> DiGraph[T]:
    # inequality u < v becomes edge (u, v)
    V: list[T] = []
    adj: dict[T, list[T]] = {}
    for ineq in ineqs:
        lhs, op, rhs = ineq.lhs, ineq.op, ineq.rhs
        if lhs not in adj:
            adj[lhs] = []
            V.append(lhs)
        if rhs not in adj:
            adj[rhs] = []
            V.append(rhs)
        if op in ('<', '≤'):
            adj[lhs].append(rhs)
        elif op == '=':
            adj[lhs].append(rhs)
            adj[rhs].append(lhs)
        else:
            raise ValueError('Ineq.op was {}'.format(repr(op)))
    return DiGraph(V, adj)


def processIneqs(ineqs: Sequence[Ineq[T]]) -> tuple[bool,
        Sequence[VarGroup[T]], Sequence[Ineq[VarGroup[T]]]]:
    G = getIneqGraph(ineqs)
    # print('G:', G, file=sys.stderr)
    vToCC, CCs, G2 = sccDecomp(G)
    # print('vToCC:', vToCC, file=sys.stderr)
    # print('CCs:', CCs, file=sys.stderr)
    # print('G2:', G2, file=sys.stderr)

    ineqDict: dict[tuple[int, int], bool] = {}  # True means strict inequality
    isValid = True
    for ineq in ineqs:
        u, op, v = ineq.lhs, ineq.op, ineq.rhs
        i, j, isStrict = vToCC[u], vToCC[v], (op == '<')
        if i == j:
            if isStrict:
                isValid = False
        else:
            assert op != '='
            ineqDict[(i, j)] = isStrict or ineqDict.get((i, j), False)

    varGroups = [VarGroup(i, tuple(vars)) for i, vars in enumerate(CCs)]
    newIneqs: list[Ineq[VarGroup[T]]] = []
    for ((i, j), isStrict) in ineqDict.items():
        lhs, op, rhs = varGroups[i], ('<' if isStrict else '≤'), varGroups[j]
        newIneqs.append(Ineq(lhs=lhs, op=op, rhs=rhs))

    return (isValid, varGroups, newIneqs)


# [ main ]======================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ipath', help='path to input file')
    args = parser.parse_args()

    with open(args.ipath) as fp:
        ineqs = parseIneqs(fp.readlines())
    isValid, varGroups, ineqs2 = processIneqs(ineqs)

    if not isValid:
        print('invalid inequalities')
    for ineq in ineqs2:
        print(ineq)


if __name__ == '__main__':
    main()
