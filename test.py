#!/usr/bin/env python3

import sys  # noqa
import unittest
from graph import DiGraph, sccDecomp
from ineqCheck import getGroupedIneqs, Ineq, parseIneqs, processIneqs, stdizeIneqs


class SccTest(unittest.TestCase):
    def test1(self) -> None:
        V = ['x', 'y', 'z', 'a', 'b']
        adj = {'x': ['y', 'a'], 'y': ['z'], 'z': ['x'], 'a': ['b'], 'b': ['a']}
        G = DiGraph(V, adj)
        vToCC, CCs, G2 = sccDecomp(G)
        self.assertEqual(vToCC, {'x': 0, 'y': 0, 'z': 0, 'a': 1, 'b': 1})
        self.assertEqual(CCs, [['x', 'y', 'z'], ['a', 'b']])
        self.assertEqual(G2.V, [0, 1])
        self.assertEqual(G2.adj, {0: [1], 1: []})


class IneqProcessTest(unittest.TestCase):
    def test1(self) -> None:
        ineqs = stdizeIneqs([Ineq('x', '<', 'y'), Ineq('x', '>', 'y')])
        output = processIneqs(ineqs)
        self.assertFalse(output.consistent)
        self.assertEqual(len(output.eqCs), 1)

    def test2(self) -> None:
        ineqs = stdizeIneqs([Ineq('x', '≤', 'y'), Ineq('x', '≥', 'y')])
        output = processIneqs(ineqs)
        self.assertTrue(output.consistent)
        self.assertEqual(len(output.eqCs), 1)

    def test3(self) -> None:
        ineqs = stdizeIneqs([Ineq('x', '<', 'y')])
        output = processIneqs(ineqs)
        self.assertTrue(output.consistent)
        self.assertEqual(len(output.eqCs), 2)

    def test4(self) -> None:
        ineqs = parseIneqs(['x ≤ y ≤ z ≤ x', 'x < a', 'a = b'])
        output = processIneqs(ineqs)
        self.assertTrue(output.consistent)
        self.assertEqual(len(output.eqCs), 2)
        self.assertEqual(set(output.eqCs[0]), set('xyz'))
        self.assertEqual(set(output.eqCs[1]), set('ab'))
        newIneqs = getGroupedIneqs(ineqs, output.varToEqC, output.eqCs)
        self.assertEqual(len(newIneqs), 1)
        rawIneq = (newIneqs[0].lhs.id, newIneqs[0].op, newIneqs[0].rhs.id)
        self.assertEqual(rawIneq, (0, '<', 1))


if __name__ == '__main__':
    unittest.main()
