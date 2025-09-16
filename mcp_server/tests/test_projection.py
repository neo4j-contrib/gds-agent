import os

import pytest
from graphdatascience import GraphDataScience

from neo4j import GraphDatabase

NEO4J_IMAGE = "neo4j:2025.05.0"
NEO4J_BOLT_PORT = 7687
NEO4J_HTTP_PORT = 7474
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "testpassword"


@pytest.mark.asyncio
def test_node_projection_properties(neo4j_container):
    """Import test data into Neo4j."""
    # Set environment variables for the import script
    os.environ["NEO4J_URI"] = neo4j_container
    os.environ["NEO4J_USERNAME"] = NEO4J_USER
    os.environ["NEO4J_PASSWORD"] = NEO4J_PASSWORD

    driver = GraphDatabase.driver(neo4j_container, auth=(NEO4J_USER, NEO4J_PASSWORD))
    existing_count1 = -1
    existing_count2 = -2
    gds = GraphDataScience(driver)
    with driver.session() as session:
        session.run("CREATE (n:Foo {name:'a'})")
        session.run("CREATE (n:Foo {name:'b'})")

        session.run("MATCH (n)  WHERE n.name = 'a' SET n.propInt = 3")
        session.run("MATCH (n)  WHERE n.name = 'a' SET n.propDouble = 3.4")
        session.run("MATCH (n)  WHERE n.name = 'a' SET n.propListDouble = [3.4]")
        session.run("MATCH (n)  WHERE n.name = 'a' SET n.propListInt = [3]")
        session.run("MATCH (n)  WHERE n.name = 'a' SET n.propString = 'foo'")

        session.run("MATCH (n)  WHERE n.name = 'a' SET n.propIntDouble = 3.4")
        session.run("MATCH (n)  WHERE n.name = 'b' SET n.propIntDouble = 3")

        session.run("MATCH (n) WHERE n.name = 'a' SET  n.propListDoubleListInt = [3.4]")
        session.run("MATCH (n) WHERE n.name = 'b' SET  n.propListDoubleListInt = [3]")

        session.run(
            "MATCH (n) WHERE n.name = 'a' SET n.propListDoubleButInvalid = [3.4]"
        )
        session.run("MATCH (n)  WHERE n.name = 'b' SET n.propListDoubleButInvalid = 0")

        res = session.run("MATCH (n) WHERE 'Foo' IN labels(n) RETURN count(n) as count")
        existing_count1 = res.single()["count"]

    from mcp_server.src.mcp_server_neo4j_gds.gds import validate_node_properties

    projection_properties = validate_node_properties(
        gds,
        [
            "propInt",
            "propIntDouble",
            "propDouble",
            "propListDouble",
            "propListInt",
            "propString",
            "propListDoubleListInt",
            "propListDoubleButInvalid",
        ],
    )

    # remove data
    with driver.session() as session:
        session.run("MATCH (n)  REMOVE n.propInt")
        session.run("MATCH (n)  REMOVE n.propIntDouble")
        session.run("MATCH (n)  REMOVE n.propDouble")

        session.run("MATCH (n)  REMOVE n.propListDouble")
        session.run("MATCH (n)  REMOVE n.propListInt")
        session.run("MATCH (n)  REMOVE n.propString")

        session.run("MATCH (n)  REMOVE n.propListDoubleListInt")
        session.run("MATCH (n)  REMOVE n.propListDoubleButInvalid ")
        session.run("MATCH (n:Foo)  DETACH DELETE n")

        res = session.run("MATCH (n) WHERE 'Foo' IN labels(n) RETURN count(n) as count")
        existing_count2 = res.single()["count"]

    driver.close()

    # assertions at the end to ensure failures do not affect other tests
    assert "propString" not in projection_properties
    assert "propListDoubleButInvalid" not in projection_properties
    assert projection_properties["propInt"] == "INTEGER"
    assert projection_properties["propDouble"] == "FLOAT"
    assert projection_properties["propIntDouble"] == "FLOAT"
    assert projection_properties["propListDouble"] == "FLOAT_LIST"
    assert projection_properties["propListInt"] == "INTEGER_LIST"
    assert projection_properties["propListDoubleListInt"] == "FLOAT_LIST"
    assert existing_count1 == 2
    assert existing_count2 == 0


@pytest.mark.asyncio
def test_node_projection_properties_with_node_labels(neo4j_container):
    """Import test data into Neo4j."""
    # Set environment variables for the import script
    os.environ["NEO4J_URI"] = neo4j_container
    os.environ["NEO4J_USERNAME"] = NEO4J_USER
    os.environ["NEO4J_PASSWORD"] = NEO4J_PASSWORD

    driver = GraphDatabase.driver(neo4j_container, auth=(NEO4J_USER, NEO4J_PASSWORD))
    existing_count1 = -1
    existing_count2 = -2
    gds = GraphDataScience(driver)
    with driver.session() as session:
        session.run("CREATE (n:Foo {prop: 'IGNORE_ME'})")
        session.run("CREATE (n:Bar {prop: 1})")
        res = session.run(
            "MATCH (n) WHERE 'Foo' IN labels(n) OR 'Bar' IN labels(n) RETURN count(n) as count"
        )
        existing_count1 = res.single()["count"]

    # do validations
    from mcp_server.src.mcp_server_neo4j_gds.gds import validate_node_properties

    projection_properties_foo = validate_node_properties(gds, ["prop"], ["Foo"])
    projection_properties_bar = validate_node_properties(gds, ["prop"], ["Bar"])

    # remove data
    with driver.session() as session:
        session.run("MATCH (n:Foo)  DETACH DELETE n")
        session.run("MATCH (n:Bar)  DETACH DELETE n")

        res = session.run(
            "MATCH (n) WHERE 'Foo' IN labels(n) OR 'Bar' IN labels(n) RETURN count(n) as count"
        )
        existing_count2 = res.single()["count"]

    driver.close()

    # assertions at the end to ensure failures do not affect other tests
    assert existing_count1 == 2
    assert existing_count2 == 0
    assert projection_properties_bar["prop"] == "INTEGER"
    assert "prop" not in projection_properties_foo


@pytest.mark.asyncio
def test_rel_projection_properties(neo4j_container):
    """Import test data into Neo4j."""
    # Set environment variables for the import script
    os.environ["NEO4J_URI"] = neo4j_container
    os.environ["NEO4J_USERNAME"] = NEO4J_USER
    os.environ["NEO4J_PASSWORD"] = NEO4J_PASSWORD

    driver = GraphDatabase.driver(neo4j_container, auth=(NEO4J_USER, NEO4J_PASSWORD))
    existing_count1 = -1
    existing_count2 = -2
    gds = GraphDataScience(driver)
    with driver.session() as session:
        session.run("CREATE (:Foo)-[:R{ prop_ok1: 2.0}]->(:Foo)")
        session.run("CREATE (:Foo)-[:R{ prop_ok2: 2}]->(:Foo)")
        session.run("CREATE (:Foo)-[:R{ prop_bad: 2.0}]->(:Foo)")
        session.run("CREATE (:Foo)-[:R{ prop_bad: 'Foo'}]->(:Foo)")

        res = session.run("MATCH (n) WHERE 'Foo' IN labels(n) RETURN count(n) as count")
        existing_count1 = res.single()["count"]

    # do validations
    from mcp_server.src.mcp_server_neo4j_gds.gds import validate_rel_properties

    projection_properties = validate_rel_properties(
        gds, ["prop_ok1", "prop_ok2", "prop_bad"]
    )

    # remove data
    with driver.session() as session:
        session.run("MATCH (n:Foo)  DETACH DELETE n")

        res = session.run("MATCH (n) WHERE 'Foo' IN labels(n) RETURN count(n) as count")
        existing_count2 = res.single()["count"]

    driver.close()

    # assertions at the end to ensure failures do not affect other tests
    assert existing_count1 == 8
    assert existing_count2 == 0
    assert "prop_ok1" in projection_properties
    assert "prop_ok2" in projection_properties
    assert "prop_bad" not in projection_properties


@pytest.mark.asyncio
def test_rel_projection_properties_with_node_labels(neo4j_container):
    """Import test data into Neo4j."""
    # Set environment variables for the import script
    os.environ["NEO4J_URI"] = neo4j_container
    os.environ["NEO4J_USERNAME"] = NEO4J_USER
    os.environ["NEO4J_PASSWORD"] = NEO4J_PASSWORD

    driver = GraphDatabase.driver(neo4j_container, auth=(NEO4J_USER, NEO4J_PASSWORD))
    existing_count1 = -1
    existing_count2 = -2
    gds = GraphDataScience(driver)
    with driver.session() as session:
        session.run("CREATE (:Foo)-[:REL1{ prop: 2.0}] ->(:Foo)")
        session.run("CREATE (:Bar)-[:REL2{ prop:'foo'}]->(:Bar)")

        res = session.run(
            "MATCH (n) WHERE 'Foo' IN labels(n) OR 'Bar' IN labels(n) RETURN count(n) as count"
        )
        existing_count1 = res.single()["count"]

    # do validations
    from mcp_server.src.mcp_server_neo4j_gds.gds import validate_rel_properties

    projection_properties_foo = validate_rel_properties(gds, ["prop"], ["Foo"])
    projection_properties_bar = validate_rel_properties(gds, ["prop"], ["Bar"])

    # remove data
    with driver.session() as session:
        session.run("MATCH (n:Foo)  DETACH DELETE n")
        session.run("MATCH (n:Bar)  DETACH DELETE n")

        res = session.run(
            "MATCH (n) WHERE 'Foo' IN labels(n) OR 'Bar' IN labels(n) RETURN count(n) as count"
        )
        existing_count2 = res.single()["count"]

    driver.close()

    # assertions at the end to ensure failures do not affect other tests
    assert existing_count1 == 4
    assert existing_count2 == 0
    assert "prop" in projection_properties_foo
    assert "prop" not in projection_properties_bar


@pytest.mark.asyncio
def test_rel_projection_properties_with_rel_types(neo4j_container):
    """Import test data into Neo4j."""
    # Set environment variables for the import script
    os.environ["NEO4J_URI"] = neo4j_container
    os.environ["NEO4J_USERNAME"] = NEO4J_USER
    os.environ["NEO4J_PASSWORD"] = NEO4J_PASSWORD

    driver = GraphDatabase.driver(neo4j_container, auth=(NEO4J_USER, NEO4J_PASSWORD))
    existing_count1 = -1
    existing_count2 = -2
    gds = GraphDataScience(driver)
    with driver.session() as session:
        session.run("CREATE (:Foo)-[:REL1{ prop: 2.0}] ->(:Foo)")
        session.run("CREATE (:Foo)-[:REL2{ prop: 'foo'}]->(:Foo)")

        res = session.run("MATCH (n) WHERE 'Foo' IN labels(n) RETURN count(n) as count")
        existing_count1 = res.single()["count"]

    # do validations
    from mcp_server.src.mcp_server_neo4j_gds.gds import validate_rel_properties

    projection_properties_rel1 = validate_rel_properties(gds, ["prop"], [], ["REL1"])
    projection_properties_rel2 = validate_rel_properties(gds, ["prop"], [], ["REL2"])

    # remove data
    with driver.session() as session:
        session.run("MATCH (n:Foo)  DETACH DELETE n")

        res = session.run("MATCH (n) WHERE 'Foo' IN labels(n) RETURN count(n) as count")
        existing_count2 = res.single()["count"]

    driver.close()

    # assertions at the end to ensure failures do not affect other tests
    assert existing_count1 == 4
    assert existing_count2 == 0
    assert "prop" in projection_properties_rel1
    assert "prop" not in projection_properties_rel2
