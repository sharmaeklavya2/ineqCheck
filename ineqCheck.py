#!/usr/bin/env python3

import sys
import argparse
import re
from collections.abc import Mapping, Sequence
from typing import Generic, Literal, NamedTuple, TextIO, TypeVar

from graph import DiGraph, sccDecomp

# [ Ineq ]======================================================================

IneqType = Literal['<', '≤', '=', '≥', '>']
LT = TypeVar('LT')
T = TypeVar('T')


class Ineq(NamedTuple, Generic[LT, T]):
    lhs: T
    op: IneqType
    rhs: T
    label: LT

    def __str__(self) -> str:
        labelStr = str(self.label) + ': ' if self.label is not None else ''
        return '{}{} {} {}'.format(labelStr, self.lhs, self.op, self.rhs)


class VarGroup(NamedTuple, Generic[T]):
    id: int
    names: tuple[T, ...]

    def __str__(self) -> str:
        return ' = '.join([str(x) for x in self.names])

    def __repr__(self) -> str:
        return '{}({}, {})'.format(self.__class__.__name__, self.id, self.names)


def stdizeIneq(ineq: Ineq[LT, T]) -> Ineq[LT, T]:
    if ineq.op == '>':
        return Ineq(ineq.rhs, '<', ineq.lhs, ineq.label)
    elif ineq.op == '≥':
        return Ineq(ineq.rhs, '≤', ineq.lhs, ineq.label)
    else:
        return ineq


def stdizeIneqs(ineqs: Sequence[Ineq[LT, T]]) -> Sequence[Ineq[LT, T]]:
    return [stdizeIneq(ineq) for ineq in ineqs]


def parseIneqs(lines: Sequence[str]) -> Sequence[Ineq[str | None, str]]:
    ineqs: list[Ineq[str | None, str]] = []
    for line in lines:
        parts = line.split(':', maxsplit=1)
        if len(parts) == 2:
            label, ineqChain = parts
        else:
            (ineqChain,) = parts
            label = None
        del parts
        parts2 = re.split(r'([<≤=≥>])', ineqChain)
        n = len(parts2) // 2
        for i in range(n):
            lhs, rawOp, rhs = parts2[2*i: 2*i+3]
            op: IneqType = rawOp  # type: ignore # explicit_cast(str, IneqType)
            ineqs.append(Ineq(lhs.strip(), op, rhs.strip(), label))
    return ineqs


# [ process ]===================================================================

def getIneqGraph(ineqs: Sequence[Ineq[LT, T]]) -> DiGraph[T]:
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
        if op in ('<', '≤', '='):
            adj[lhs].append(rhs)
        if op in ('>', '≥', '='):
            adj[rhs].append(lhs)
    return DiGraph(V, adj)


class IneqProcessOutput(NamedTuple, Generic[LT, T]):
    consistent: bool
    violatedIneqs: Sequence[Ineq[LT, T]]
    varToEqC: Mapping[T, int]
    eqCs: Sequence[Sequence[T]]


def processIneqs(ineqs: Sequence[Ineq[LT, T]]) -> IneqProcessOutput[LT, T]:
    G = getIneqGraph(ineqs)
    # print('G:', G, file=sys.stderr)
    varToEqC, eqCs, G2 = sccDecomp(G)
    # print('G2:', output.G2, file=sys.stderr)

    violatedIneqs = []
    for ineq in ineqs:
        u, op, v = ineq.lhs, ineq.op, ineq.rhs
        if varToEqC[u] == varToEqC[v] and op in ('<', '>'):
            violatedIneqs.append(ineq)

    return IneqProcessOutput(consistent=not violatedIneqs, violatedIneqs=violatedIneqs,
        varToEqC=varToEqC, eqCs=eqCs)


def getGroupedIneqs(ineqs: Sequence[Ineq[LT, T]], varToEqC: Mapping[T, int], eqCs: Sequence[Sequence[T]]
        ) -> Sequence[Ineq[None, VarGroup[T]]]:
    ineqDict: dict[tuple[int, int], bool] = {}  # True means strict inequality
    for ineq in ineqs:
        ineq2 = stdizeIneq(ineq)
        u, op, v = ineq2.lhs, ineq2.op, ineq2.rhs
        i, j, isStrict = varToEqC[u], varToEqC[v], (op == '<')
        if i != j:
            assert op != '='
            ineqDict[(i, j)] = isStrict or ineqDict.get((i, j), False)

    varGroups = [VarGroup(i, tuple(vars)) for i, vars in enumerate(eqCs)]
    newIneqs: list[Ineq[None, VarGroup[T]]] = []
    for ((i, j), isStrict) in ineqDict.items():
        lhs, op, rhs = varGroups[i], ('<' if isStrict else '≤'), varGroups[j]
        newIneqs.append(Ineq(lhs=lhs, op=op, rhs=rhs, label=None))
    return newIneqs


def printGroupedIneqs(ineqs: Sequence[Ineq[LT, VarGroup[T]]], eqCs: Sequence[Sequence[T]], fp: TextIO) -> None:
    seenEqCs = set()
    for ineq in ineqs:
        print(ineq, file=fp)
        seenEqCs.add(ineq.lhs.id)
        seenEqCs.add(ineq.rhs.id)
    for i, eqC in enumerate(eqCs):
        if len(eqC) > 1 and i not in seenEqCs:
            print(' = '.join([str(x) for x in eqC]), file=fp)


# [ main ]======================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ipath', help='path to input file')
    args = parser.parse_args()

    with open(args.ipath) as fp:
        ineqs = parseIneqs(fp.readlines())
    output = processIneqs(ineqs)
    # print('varToEqC:', output.varToEqC, file=sys.stderr)
    # print('eqCs:', output.eqCs, file=sys.stderr)
    newIneqs = getGroupedIneqs(ineqs, output.varToEqC, output.eqCs)

    printGroupedIneqs(newIneqs, output.eqCs, sys.stdout)
    if output.consistent:
        print('inequalities are consistent')
    else:
        print('strictness violated for these inequalities:')
        for ineq in output.violatedIneqs:
            print(ineq)


if __name__ == '__main__':
    main()
