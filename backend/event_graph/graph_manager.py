from neo4j import GraphDatabase
import networkx as nx
import logging
import os
import json

class GraphManager:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self._connected = False
        
        # In-memory graph for simulations and fallback
        self.memory_graph = nx.DiGraph()
        self.last_event_id = None
        
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.driver.verify_connectivity()
            self._connected = True
            logging.info("Connected to Neo4j Event Graph")
        except Exception as e:
            logging.warning(f"Could not connect to Neo4j: {e}. Using NetworkX memory-only graph.")

    def close(self):
        if self.driver:
            self.driver.close()

    def update_graph(self, event: dict):
        """
        Update the event graph:
        1. Node: Event
        2. Edge: Source -> PRODUCED -> Event
        3. Edge: PrevEvent -> NEXT -> Event (Temporal)
        """
        source_name = event.get('source')
        event_type = event.get('event_type')
        event_id = str(event.get('id', 'unknown'))
        payload = event.get('payload', {})
        
        print(f"[GRAPH] Relating {event_type} to {source_name} (Temporal Chain)...")

        # Update Memory Graph (NetworkX)
        self.memory_graph.add_node(event_id, type=event_type, source=source_name, **payload)
        self.memory_graph.add_edge(source_name, event_id, relation="PRODUCED")
        if self.last_event_id:
            self.memory_graph.add_edge(self.last_event_id, event_id, relation="NEXT")

        # Update Neo4j
        if self._connected:
            with self.driver.session() as session:
                session.execute_write(self._create_event_node, source_name, event_type, event_id, payload, self.last_event_id)
        
        # Update trace pointer
        self.last_event_id = event_id

    def create_causal_link(self, cause_id: str, effect_id: str, weight: float = 1.0):
        """Explicitly link two events with a causal relationship."""
        # Memory Graph
        if self.memory_graph.has_node(cause_id) and self.memory_graph.has_node(effect_id):
            self.memory_graph.add_edge(cause_id, effect_id, relation="CAUSED_BY", weight=weight)
            
        # Neo4j
        if self._connected:
            with self.driver.session() as session:
                session.run("""
                    MATCH (a:Event {id: $cause}), (b:Event {id: $effect})
                    MERGE (a)-[r:CAUSED_BY {weight: $weight}]->(b)
                """, cause=cause_id, effect=effect_id, weight=weight)

    def get_visualization_data(self, limit=20):
        """Return graph data in D3.js compatible format directly for the Dashboard."""
        nodes = []
        links = []
        
        if self._connected:
            # Fetch from Neo4j
            with self.driver.session() as session:
                result = session.run(f"""
                    MATCH (n)-[r]->(m)
                    RETURN n, r, m LIMIT {limit}
                """)
                seen_nodes = set()
                for record in result:
                    n, r, m = record['n'], record['r'], record['m']
                    
                    # Add nodes if new
                    for node in [n, m]:
                        label = list(node.labels)[0] if hasattr(node, 'labels') else 'Node'
                        props = dict(node)
                        node_id = props.get('id', props.get('name', str(node.id)))  # Fallback to internal ID
                        if node_id not in seen_nodes:
                            nodes.append({"id": node_id, "group": label, "properties": props})
                            seen_nodes.add(node_id)
                    
                    # Add link
                    source_id = dict(n).get('id', dict(n).get('name', str(n.id)))
                    target_id = dict(m).get('id', dict(m).get('name', str(m.id)))
                    links.append({"source": source_id, "target": target_id, "type": r.type})
        else:
            # Fetch from NetworkX
            # Simple simulation of D3 structure from generic graph
            for n, attrs in list(self.memory_graph.nodes(data=True))[-limit:]:
                group = "Event" if "type" in attrs else "Source"
                nodes.append({"id": n, "group": group, "properties": attrs})
            
            for u, v, attrs in list(self.memory_graph.edges(data=True))[-limit:]:
                links.append({"source": u, "target": v, "type": attrs.get("relation", "LINKED")})

        return {"nodes": nodes, "links": links}

    def simulate_what_if(self, start_event_id: str, hypothetical_action: str) -> dict:
        """
        Simulate a 'what-if' scenario on the event graph.
        Projects a future branch from the given event ID.
        Returns the projected impact path.
        """
        print(f"[GRAPH] Simulating outcome for action '{hypothetical_action}' from {start_event_id}...")
        
        # Simple projection logic using NetworkX
        # In a real system, this would use a Graph Neural Network or causal inference model
        if start_event_id not in self.memory_graph:
            return {"error": "Event not found in memory graph"}
            
        successors = list(self.memory_graph.successors(start_event_id))
        
        return {
            "scenario": hypothetical_action,
            "origin_node": start_event_id,
            "immediate_impact": successors,
            "projected_risk": len(successors) * 0.15,  # Heuristic risk
            "path_length": nx.shortest_path_length(self.memory_graph, start_event_id) if successors else 0
        }

    @staticmethod
    def _create_event_node(tx, source_name, event_type, event_id, payload, prev_event_id):
        # Create Source node
        tx.run("MERGE (s:Source {name: $source_name})", source_name=source_name)
        
        # Create Event node with PRODUCED relationship
        tx.run("""
            MATCH (s:Source {name: $source_name})
            CREATE (e:Event {id: $event_id, type: $event_type, timestamp: datetime()})
            MERGE (s)-[:PRODUCED]->(e)
            SET e += $payload
        """, source_name=source_name, event_id=event_id, event_type=event_type, payload=payload)
        
        # Create Temporal NEXT relationship
        if prev_event_id:
            tx.run("""
                MATCH (prev:Event {id: $prev_id})
                MATCH (curr:Event {id: $curr_id})
                MERGE (prev)-[:NEXT]->(curr)
            """, prev_id=prev_event_id, curr_id=event_id)
