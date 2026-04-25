"""Neo4j graph database operations for routing."""
from neo4j import GraphDatabase, Driver
from typing import List, Dict, Any, Optional, Tuple
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class GraphDB:
    """Neo4j graph database wrapper for network routing."""

    def __init__(self):
        """Initialize Neo4j connection."""
        try:
            self.driver: Optional[Driver] = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_username, settings.neo4j_password),
                connection_timeout=10
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Neo4j connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self.driver = None

    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()

    def create_node(self, node_id: str, label: str = "City", properties: Optional[Dict] = None) -> bool:
        """Create a graph node."""
        try:
            if self.driver is None:
                return False
            with self.driver.session() as session:
                props = properties or {}
                session.run(
                    f"CREATE (n:{label} {{id: $id, ...props}})",
                    id=node_id,
                    props=props
                )
            return True
        except Exception as e:
            logger.error(f"Failed to create node: {e}")
            return False

    def create_relationship(
        self,
        from_node: str,
        to_node: str,
        rel_type: str = "ROUTE",
        properties: Optional[Dict] = None
    ) -> bool:
        """Create a relationship between nodes."""
        try:
            if self.driver is None:
                return False
            with self.driver.session() as session:
                props = properties or {}
                session.run(
                    f"""MATCH (a {{id: $from}}) MATCH (b {{id: $to}})
                       CREATE (a)-[r:{rel_type} {{...props}}]->(b)""",
                    **{
                        "from": from_node,
                        "to": to_node,
                        **props
                    }
                )
            return True
        except Exception as e:
            logger.error(f"Failed to create relationship: {e}")
            return False

    def find_shortest_path(
        self,
        source: str,
        destination: str,
        weight_property: str = "distance"
    ) -> Optional[List[str]]:
        """Find shortest path between two nodes using Dijkstra."""
        try:
            if self.driver is None:
                return None
            with self.driver.session() as session:
                result = session.run(
                    f"""MATCH (source {{id: $source}}), (dest {{id: $destination}})
                       CALL apoc.algo.dijkstra(source, dest, 'ROUTE', '{weight_property}')
                       YIELD path
                       RETURN nodes(path) as nodes""",
                    source=source,
                    destination=destination
                )
                record = result.single()
                if record:
                    nodes = record["nodes"]
                    return [node["id"] for node in nodes]
            return None
        except Exception as e:
            logger.error(f"Failed to find shortest path: {e}")
            return None

    def find_paths_with_costs(
        self,
        source: str,
        destination: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Find multiple paths with cost information."""
        try:
            if self.driver is None:
                return []
            with self.driver.session() as session:
                result = session.run(
                    """MATCH (source {id: $source}), (dest {id: $destination})
                       CALL apoc.algo.allSimplePaths(source, dest, 'ROUTE', 5)
                       YIELD path
                       WITH path, reduce(cost = 0, r IN relationships(path) | cost + r.distance) as total_distance,
                            reduce(time = 0, r IN relationships(path) | time + r.time) as total_time
                       RETURN nodes(path) as nodes, relationships(path) as edges, total_distance, total_time
                       LIMIT $limit""",
                    source=source,
                    destination=destination,
                    limit=limit
                )
                paths = []
                for record in result:
                    nodes = record["nodes"]
                    path_data = {
                        "nodes": [node["id"] for node in nodes],
                        "distance": record["total_distance"] or 0,
                        "time": record["total_time"] or 0,
                    }
                    paths.append(path_data)
                return paths
        except Exception as e:
            logger.error(f"Failed to find paths: {e}")
            return []

    def get_node_properties(self, node_id: str) -> Optional[Dict]:
        """Get all properties of a node."""
        try:
            if self.driver is None:
                return None
            with self.driver.session() as session:
                result = session.run(
                    "MATCH (n {id: $id}) RETURN properties(n) as props",
                    id=node_id
                )
                record = result.single()
                return record["props"] if record else None
        except Exception as e:
            logger.error(f"Failed to get node properties: {e}")
            return None

    def is_connected(self) -> bool:
        """Check if Neo4j is connected."""
        try:
            if self.driver is None:
                return False
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            logger.error(f"Neo4j connection check failed: {e}")
            return False


# Global Neo4j instance
graph_db = GraphDB()
