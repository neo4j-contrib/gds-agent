# /// script
# requires-python = ">=3.11"
# dependencies = ["neo4j>=5", "python-dotenv>=1.0.0"]
# ///
import os
from neo4j import GraphDatabase
import json
import argparse
from dotenv import load_dotenv


def import_tube_data(uri, username, password, data_file, undirected=False):
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    # Load JSON data
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    with driver.session() as session:
        # Create constraints separately
        session.run("""
        CREATE CONSTRAINT underground_station_name IF NOT EXISTS FOR (s:UndergroundStation) REQUIRE s.name IS UNIQUE
        """)
        
        session.run("""
        CREATE CONSTRAINT underground_station_id IF NOT EXISTS FOR (s:UndergroundStation) REQUIRE s.id IS UNIQUE
        """)
        
        session.run("""
        UNWIND $stations AS station
        MERGE (s:UndergroundStation {id: station.id})
        SET s.name = station.name,
            s.display_name = CASE station.display_name 
                         WHEN 'NULL' THEN station.name 
                         ELSE station.display_name 
                         END,
            s.latitude = toFloat(station.latitude),
            s.longitude = toFloat(station.longitude),
            s.zone = CASE 
                  WHEN station.zone CONTAINS '.' THEN toFloat(station.zone)
                  ELSE toInteger(station.zone)
                  END,
            s.total_lines = toInteger(station.total_lines),
            s.rail = toInteger(station.rail)
        """, {'stations': data['stations']})
        
        if undirected:
            # Create bidirectional relationships for undirected graph
            session.run("""
            UNWIND $connections AS conn
            MATCH (s1:UndergroundStation {id: conn.station1})
            MATCH (s2:UndergroundStation {id: conn.station2})
            MERGE (s1)-[r1:LINK {
                line: conn.line,
                time: toInteger(conn.time),
                distance: toInteger(conn.time)
            }]->(s2)
            MERGE (s2)-[r2:LINK {
                line: conn.line,
                time: toInteger(conn.time),
                distance: toInteger(conn.time)
            }]->(s1)
            """, {'connections': data['connections']})
        else:
            # Create directed relationships (default behavior)
            session.run("""
            UNWIND $connections AS conn
            MATCH (s1:UndergroundStation {id: conn.station1})
            MATCH (s2:UndergroundStation {id: conn.station2})
            MERGE (s1)-[r:LINK {
                line: conn.line,
                time: toInteger(conn.time),
                distance: toInteger(conn.time)
            }]->(s2)
            """, {'connections': data['connections']})
    
    driver.close()

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Import London Underground data into Neo4j')
    parser.add_argument('--undirected', action='store_true', 
                       help='Load the graph as undirected (creates bidirectional relationships)')
    args = parser.parse_args()
    
    load_dotenv('.env')
    
    uri = os.environ["NEO4J_URI"]
    username = os.environ["NEO4J_USERNAME"]
    password = os.environ["NEO4J_PASSWORD"]
    data_file = "dataset/london.json"
    
    print(f"Loading graph as {'undirected' if args.undirected else 'directed'}...")
    import_tube_data(uri, username, password, data_file, undirected=args.undirected)
    print("Import completed successfully!")

if __name__ == "__main__":
    main()