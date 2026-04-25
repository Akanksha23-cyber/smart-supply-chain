"""Graph-based routing engine with Dijkstra and A* algorithms."""
import heapq
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from math import sqrt
import logging

logger = logging.getLogger(__name__)


@dataclass
class Node:
    """Graph node representation."""
    id: str
    lat: float = 0.0
    lon: float = 0.0
    properties: Dict = None

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.id < other.id


@dataclass
class Edge:
    """Graph edge representation."""
    from_node: str
    to_node: str
    distance: float
    time: float = None
    risk: float = 0.0

    def __lt__(self, other):
        return self.distance < other.distance


class RoutingEngine:
    """Advanced routing engine using graph algorithms."""

    def __init__(self):
        """Initialize routing engine."""
        self.graph: Dict[str, List[Edge]] = {}
        self.nodes: Dict[str, Node] = {}

    def add_node(self, node_id: str, lat: float = 0.0, lon: float = 0.0, **properties):
        """Add a node to the graph."""
        self.nodes[node_id] = Node(
            id=node_id,
            lat=lat,
            lon=lon,
            properties=properties
        )
        if node_id not in self.graph:
            self.graph[node_id] = []

    def add_edge(
        self,
        from_node: str,
        to_node: str,
        distance: float,
        time: float = None,
        risk: float = 0.0
    ):
        """Add an edge to the graph."""
        if from_node not in self.graph:
            self.add_node(from_node)
        if to_node not in self.graph:
            self.add_node(to_node)

        time = time or (distance / 80.0)  # Estimate time if not provided
        edge = Edge(
            from_node=from_node,
            to_node=to_node,
            distance=distance,
            time=time,
            risk=risk
        )
        self.graph[from_node].append(edge)

    def dijkstra(
        self,
        source: str,
        destination: str,
        weight: str = "distance"
    ) -> Tuple[Optional[List[str]], Optional[float]]:
        """
        Find shortest path using Dijkstra's algorithm.

        Args:
            source: Source node ID
            destination: Destination node ID
            weight: Weight property ('distance', 'time', or 'risk')

        Returns:
            Tuple of (path, total_weight) or (None, None) if no path exists
        """
        if source not in self.graph or destination not in self.graph:
            logger.error(f"Node not found: {source} or {destination}")
            return None, None

        # Distance dictionary
        distances = {node: float('inf') for node in self.graph}
        distances[source] = 0

        # Parent dictionary for path reconstruction
        parent = {node: None for node in self.graph}

        # Priority queue: (distance, node)
        pq = [(0, source)]

        while pq:
            current_dist, current_node = heapq.heappop(pq)

            if current_dist > distances[current_node]:
                continue

            if current_node == destination:
                # Reconstruct path
                path = []
                node = destination
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return path, distances[destination]

            # Check neighbors
            for edge in self.graph[current_node]:
                # Get edge weight based on property
                if weight == "distance":
                    edge_weight = edge.distance
                elif weight == "time":
                    edge_weight = edge.time
                elif weight == "risk":
                    edge_weight = edge.risk
                else:
                    edge_weight = edge.distance

                new_dist = current_dist + edge_weight
                if new_dist < distances[edge.to_node]:
                    distances[edge.to_node] = new_dist
                    parent[edge.to_node] = current_node
                    heapq.heappush(pq, (new_dist, edge.to_node))

        logger.warning(f"No path found from {source} to {destination}")
        return None, None

    def a_star(
        self,
        source: str,
        destination: str,
        heuristic: str = "euclidean"
    ) -> Tuple[Optional[List[str]], Optional[float]]:
        """
        Find shortest path using A* algorithm.

        Args:
            source: Source node ID
            destination: Destination node ID
            heuristic: Heuristic type ('euclidean' or 'manhattan')

        Returns:
            Tuple of (path, total_cost) or (None, None) if no path exists
        """
        if source not in self.graph or destination not in self.graph:
            logger.error(f"Node not found: {source} or {destination}")
            return None, None

        def heuristic_func(node_id: str) -> float:
            """Calculate heuristic distance to destination."""
            if node_id not in self.nodes or destination not in self.nodes:
                return 0.0

            node = self.nodes[node_id]
            dest_node = self.nodes[destination]

            if heuristic == "euclidean":
                return sqrt(
                    (node.lat - dest_node.lat) ** 2 +
                    (node.lon - dest_node.lon) ** 2
                ) * 111  # Approximate km per degree
            else:  # manhattan
                return (
                    abs(node.lat - dest_node.lat) +
                    abs(node.lon - dest_node.lon)
                ) * 111

        # g_score: cost from start to node
        g_score = {node: float('inf') for node in self.graph}
        g_score[source] = 0

        # f_score: g_score + heuristic
        f_score = {node: float('inf') for node in self.graph}
        f_score[source] = heuristic_func(source)

        parent = {node: None for node in self.graph}

        # Priority queue: (f_score, node)
        pq = [(f_score[source], source)]

        while pq:
            _, current_node = heapq.heappop(pq)

            if current_node == destination:
                # Reconstruct path
                path = []
                node = destination
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return path, g_score[destination]

            # Check neighbors
            for edge in self.graph[current_node]:
                tentative_g = g_score[current_node] + edge.distance
                if tentative_g < g_score[edge.to_node]:
                    parent[edge.to_node] = current_node
                    g_score[edge.to_node] = tentative_g
                    f_score[edge.to_node] = tentative_g + heuristic_func(edge.to_node)
                    heapq.heappush(pq, (f_score[edge.to_node], edge.to_node))

        logger.warning(f"No path found from {source} to {destination}")
        return None, None

    def find_k_shortest_paths(
        self,
        source: str,
        destination: str,
        k: int = 3,
        weight: str = "distance"
    ) -> List[Tuple[List[str], float]]:
        """
        Find k shortest paths using modified Dijkstra.

        Args:
            source: Source node ID
            destination: Destination node ID
            k: Number of paths to find
            weight: Weight property to optimize

        Returns:
            List of (path, cost) tuples
        """
        paths = []
        visited_edges = set()

        for _ in range(k):
            # Temporarily remove used edges
            temp_removed = []
            for edge_key in visited_edges:
                from_node, to_node = edge_key
                for i, edge in enumerate(self.graph[from_node]):
                    if edge.to_node == to_node:
                        temp_removed.append((from_node, i, edge))
                        self.graph[from_node].pop(i)
                        break

            # Find shortest path
            path, cost = self.dijkstra(source, destination, weight)

            # Restore edges
            for from_node, idx, edge in temp_removed:
                self.graph[from_node].insert(idx, edge)

            if path is None:
                break

            paths.append((path, cost))

            # Mark edges as visited
            for i in range(len(path) - 1):
                visited_edges.add((path[i], path[i + 1]))

        return paths

    def calculate_route_metrics(self, path: List[str]) -> Dict:
        """Calculate comprehensive metrics for a path."""
        if len(path) < 2:
            return {}

        total_distance = 0.0
        total_time = 0.0
        risk_score = 0.0
        edge_count = 0

        for i in range(len(path) - 1):
            from_node = path[i]
            to_node = path[i + 1]

            # Find edge
            for edge in self.graph.get(from_node, []):
                if edge.to_node == to_node:
                    total_distance += edge.distance
                    total_time += edge.time or (edge.distance / 80.0)
                    risk_score += edge.risk
                    edge_count += 1
                    break

        avg_risk = risk_score / edge_count if edge_count > 0 else 0.0

        return {
            "distance": round(total_distance, 2),
            "time_hours": round(total_time, 2),
            "risk_score": round(avg_risk, 3),
            "edge_count": edge_count,
        }


# Global routing engine instance
routing_engine = RoutingEngine()
