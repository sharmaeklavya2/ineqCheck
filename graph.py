from __future__ import annotations
import sys  # noqa
from collections.abc import Mapping, Sequence
from typing import Generic, TypeVar

T = TypeVar('T')


class DiGraph(Generic[T]):
    def __init__(self, V: Sequence[T], adj: Mapping[T, Sequence[T]]):
        self.V = V
        self.adj = adj

    def getEdges(self) -> Sequence[tuple[T, T]]:
        return [(u, v) for u in self.V for v in self.adj[u]]

    @staticmethod
    def fromEdges(edges: Sequence[tuple[T, T]]) -> DiGraph[T]:
        V: list[T] = []
        adj: dict[T, list[T]] = {}
        for (u, v) in edges:
            if u not in adj:
                adj[u] = []
                V.append(u)
            if v not in adj:
                adj[v] = []
                V.append(v)
            adj[u].append(v)
        return DiGraph(V, adj)

    def __str__(self) -> str:
        return 'DiGraph(V={}, E={})'.format(self.V, self.getEdges())


def sccDecomp(G: DiGraph[T]) -> tuple[Mapping[T, int], Sequence[Sequence[T]], DiGraph[int]]:
    visited: set[T] = set()
    VRTopo: list[T] = []

    radj: Mapping[T, list[T]] = {v: [] for v in G.V}
    for u in G.V:
        for v in G.adj[u]:
            radj[v].append(u)

    def dfs1(u: T) -> None:
        if u not in visited:
            visited.add(u)
            for v in G.adj[u]:
                dfs1(v)
            VRTopo.append(u)

    for u in G.V:
        dfs1(u)
    # print('VTopo:', list(reversed(VRTopo)), file=sys.stderr)

    visited.clear()
    vToCC: dict[T, int] = {}

    def dfs2(u: T, ccid: int) -> None:
        if u not in visited:
            visited.add(u)
            for v in radj[u]:
                dfs2(v, ccid)
            vToCC[u] = ccid

    nCC = 0
    for u in reversed(VRTopo):
        if u not in visited:
            dfs2(u, nCC)
            nCC += 1
    CCs: list[list[T]] = [[] for i in range(nCC)]
    for u in reversed(VRTopo):
        CCs[vToCC[u]].append(u)
    # print('nCC: {}, vToCC: {}'.format(nCC, vToCC), file=sys.stderr)

    V2 = list(range(nCC))
    adj2: dict[int, list[int]] = {i: [] for i in range(nCC)}
    for u in G.V:
        i = vToCC[u]
        seenVIds = {i}
        for v in G.adj[u]:
            j = vToCC[v]
            if j not in seenVIds:
                seenVIds.add(j)
                adj2[i].append(j)

    return (vToCC, CCs, DiGraph(V2, adj2))
