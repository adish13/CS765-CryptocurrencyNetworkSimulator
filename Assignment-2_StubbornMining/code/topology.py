import numpy as np
from collections import defaultdict

def check_connected(graph, n):
    visited = set()
    queue = [0]

    while queue:
        vertex = queue.pop(0)
        visited.add(vertex)
        queue.extend(graph[vertex] - visited)
    return len(visited) == n

def create_random_graph(n, min_edges, max_edges,adversary_index):
    graph = defaultdict(set)
    while True:
        for i in range(n):
            if (i == adversary_index):
                continue
            num_edges = np.random.randint(min_edges, max_edges)
            while len(graph[i]) < num_edges:
                target = np.random.randint(0, n-1)
                if target != adversary_index and target != i and len(graph[target]) < max_edges:
                    graph[i].add(target)
                    graph[target].add(i)
        if check_connected(graph, n-1):
            return graph