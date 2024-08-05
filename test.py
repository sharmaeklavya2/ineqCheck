#!/usr/bin/env python3

import sys  # noqa
import unittest
from graph import DiGraph, sccDecomp
from ineqCheck import Ineq, parseIneqs, processIneqs, stdizeIneqs


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
        isValid, varGroups, newIneqs = processIneqs(ineqs)
        self.assertFalse(isValid)
        self.assertEqual(len(varGroups), 1)
        self.assertEqual(len(newIneqs), 0)

    def test2(self) -> None:
        ineqs = stdizeIneqs([Ineq('x', '≤', 'y'), Ineq('x', '≥', 'y')])
        isValid, varGroups, newIneqs = processIneqs(ineqs)
        self.assertTrue(isValid)
        self.assertEqual(len(varGroups), 1)
        self.assertEqual(len(newIneqs), 0)

    def test3(self) -> None:
        ineqs = stdizeIneqs([Ineq('x', '<', 'y')])
        isValid, varGroups, newIneqs = processIneqs(ineqs)
        self.assertTrue(isValid)
        self.assertEqual(len(varGroups), 2)
        self.assertEqual(len(newIneqs), 1)

    def test4(self) -> None:
        ineqs = parseIneqs(['x ≤ y ≤ z ≤ x', 'x < a', 'a = b'])
        isValid, varGroups, newIneqs = processIneqs(ineqs)
        self.assertTrue(isValid)
        self.assertEqual(len(varGroups), 2)
        self.assertEqual(set(varGroups[0].names), set('xyz'))
        self.assertEqual(set(varGroups[1].names), set('ab'))
        self.assertEqual(len(newIneqs), 1)
        rawIneq = (newIneqs[0].lhs.id, newIneqs[0].op, newIneqs[0].rhs.id)
        self.assertEqual(rawIneq, (0, '<', 1))


if __name__ == '__main__':
    unittest.main()
