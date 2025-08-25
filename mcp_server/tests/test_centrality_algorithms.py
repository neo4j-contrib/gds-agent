import pytest


@pytest.mark.asyncio
async def test_article_rank(mcp_client):
    # Test basic
    baseline_result = await mcp_client.call_tool(
        "article_rank",
        {
            "nodeIdentifierProperty": "name",
            "dampingFactor": 0.85,
            "maxIterations": 20,
            "tolerance": 1e-6,
            "nodeLabels": ["UndergroundStation"],
        },
    )

    assert len(baseline_result) == 1
    baseline_text = baseline_result[0]["text"]

    assert "nodeId" in baseline_text
    assert "score" in baseline_text
    assert "nodeName" in baseline_text

    baseline_lines = baseline_text.strip().split("\n")
    baseline_data_lines = [line for line in baseline_lines[1:] if line.strip()]
    assert len(baseline_data_lines) == 302

    # Test with node filtering
    result = await mcp_client.call_tool(
        "article_rank",
        {
            "nodes": ["Covent Garden", "Southwark"],
            "nodeIdentifierProperty": "name",
            "dampingFactor": 0.85,
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]
    assert "nodeId" in result_text
    assert "score" in result_text
    assert "nodeName" in result_text

    lines = result_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) <= 2  # Should not exceed the number of filtered nodes

    # Test basic (no node names)
    basic_result = await mcp_client.call_tool(
        "article_rank",
        {
            "dampingFactor": 0.85,
        },
    )

    assert len(basic_result) == 1
    basic_text = basic_result[0]["text"]

    assert "nodeId" in basic_text
    assert "score" in basic_text
    assert "nodeName" not in basic_text

    # Test personalized article rank with sourceNodes
    personalized_result = await mcp_client.call_tool(
        "article_rank",
        {
            "sourceNodes": ["Covent Garden", "Southwark"],
            "nodeIdentifierProperty": "name",
            "dampingFactor": 0.85,
            "maxIterations": 20,
        },
    )

    assert len(personalized_result) == 1
    personalized_text = personalized_result[0]["text"]
    assert "nodeId" in personalized_text
    assert "score" in personalized_text
    assert "nodeName" in personalized_text

    personalized_lines = personalized_text.strip().split("\n")
    personalized_data_lines = [line for line in personalized_lines[1:] if line.strip()]
    assert len(personalized_data_lines) == 302

    # Extract scores for source nodes from both baseline and personalized results
    # to verify that personalization is working
    def extract_score_for_station(text, station_name):
        lines = text.strip().split("\n")
        for line in lines[1:]:
            if station_name in line:
                import re

                parts = re.split(r"\s+", line.strip())
                if len(parts) >= 3:
                    try:
                        score_candidates = []
                        for i in range(1, min(4, len(parts))):
                            try:
                                score_candidates.append((i, float(parts[i])))
                            except ValueError:
                                continue

                        if len(score_candidates) >= 2:
                            return score_candidates[1][1]
                        elif len(score_candidates) >= 1:
                            return score_candidates[0][1]
                    except (ValueError, IndexError):
                        continue
        return None

    print("DEBUG - Baseline first 3 lines:")
    baseline_lines_debug = baseline_text.strip().split("\n")[:3]
    for i, line in enumerate(baseline_lines_debug):
        print(f"  {i}: {repr(line)}")

    print("DEBUG - Personalized first 3 lines:")
    personalized_lines_debug = personalized_text.strip().split("\n")[:3]
    for i, line in enumerate(personalized_lines_debug):
        print(f"  {i}: {repr(line)}")

    baseline_pad_score = extract_score_for_station(baseline_text, "Paddington")
    personalized_pad_score = extract_score_for_station(personalized_text, "Paddington")

    assert baseline_pad_score is not None and personalized_pad_score is not None
    pad_diff = abs(baseline_pad_score - personalized_pad_score)

    assert pad_diff == baseline_pad_score, (
        f"Personalized ArticleRank should turn the score of Paddington to zero because it is unreachable (diff: {pad_diff})"
    )

    # Test combining sourceNodes with nodes filtering
    combined_result = await mcp_client.call_tool(
        "article_rank",
        {
            "sourceNodes": ["Covent Garden"],
            "nodes": ["Covent Garden", "Southwark", "London Bridge"],
            "nodeIdentifierProperty": "name",
            "dampingFactor": 0.85,
        },
    )

    assert len(combined_result) == 1
    combined_text = combined_result[0]["text"]

    assert "nodeId" in combined_text
    assert "score" in combined_text
    assert "nodeName" in combined_text

    combined_lines = combined_text.strip().split("\n")
    combined_data_lines = [line for line in combined_lines[1:] if line.strip()]
    assert len(combined_data_lines) <= 3

    combined_full_text = " ".join(combined_data_lines)
    assert (
        "Covent Garden" in combined_full_text
        and "Southwark" in combined_full_text
        and "London Bridge" in combined_full_text
    )


@pytest.mark.asyncio
async def test_articulation_points(mcp_client):
    result_with_names = await mcp_client.call_tool(
        "articulation_points", {"nodeIdentifierProperty": "name"}
    )

    assert len(result_with_names) == 1
    result_with_names_text = result_with_names[0]["text"]
    assert "nodeId" in result_with_names_text
    assert "resultingComponents" in result_with_names_text
    assert "nodeName" in result_with_names_text


@pytest.mark.asyncio
async def test_betweenness_centrality(mcp_client):
    result_filtered = await mcp_client.call_tool(
        "betweenness_centrality",
        {
            "nodes": ["King's Cross St. Pancras", "Oxford Circus"],
            "nodeIdentifierProperty": "name",
        },
    )

    assert len(result_filtered) == 1
    result_filtered_text = result_filtered[0]["text"]
    assert "nodeId" in result_filtered_text
    assert "score" in result_filtered_text
    assert "nodeName" in result_filtered_text


@pytest.mark.asyncio
async def test_bridges(mcp_client):
    result_with_names = await mcp_client.call_tool(
        "bridges", {"nodeIdentifierProperty": "name"}
    )

    assert len(result_with_names) == 1
    result_with_names_text = result_with_names[0]["text"]
    assert "from" in result_with_names_text
    assert "to" in result_with_names_text
    assert "remainingSizes" in result_with_names_text
    assert "fromName" in result_with_names_text
    assert "toName" in result_with_names_text


@pytest.mark.asyncio
async def test_celf(mcp_client):
    result_with_names = await mcp_client.call_tool(
        "CELF", {"seedSetSize": 3, "nodeIdentifierProperty": "name"}
    )

    assert len(result_with_names) == 1
    result_with_names_text = result_with_names[0]["text"]
    assert "nodeId" in result_with_names_text
    assert "spread" in result_with_names_text
    assert "nodeName" in result_with_names_text


@pytest.mark.asyncio
async def test_closeness_centrality(mcp_client):
    result_filtered = await mcp_client.call_tool(
        "closeness_centrality",
        {
            "nodes": ["King's Cross St. Pancras", "Oxford Circus"],
            "nodeIdentifierProperty": "name",
        },
    )

    assert len(result_filtered) == 1
    result_filtered_text = result_filtered[0]["text"]
    assert "nodeId" in result_filtered_text
    assert "score" in result_filtered_text
    assert "nodeName" in result_filtered_text


@pytest.mark.asyncio
async def test_degree_centrality(mcp_client):
    result_filtered = await mcp_client.call_tool(
        "degree_centrality",
        {
            "nodes": ["King's Cross St. Pancras", "Oxford Circus"],
            "nodeIdentifierProperty": "name",
            "orientation": "NATURAL",
            "relationshipWeightProperty": "distance",
        },
    )

    assert len(result_filtered) == 1
    result_filtered_text = result_filtered[0]["text"]
    assert "nodeId" in result_filtered_text
    assert "score" in result_filtered_text
    assert "nodeName" in result_filtered_text


@pytest.mark.asyncio
async def test_eigenvector_centrality(mcp_client):
    result_combined = await mcp_client.call_tool(
        "eigenvector_centrality",
        {
            "sourceNodes": ["Covent Garden"],
            "nodes": ["Covent Garden", "Southwark", "London Bridge"],
            "nodeIdentifierProperty": "name",
            "maxIterations": 15,
        },
    )

    assert len(result_combined) == 1
    result_combined_text = result_combined[0]["text"]
    assert "nodeId" in result_combined_text
    assert "score" in result_combined_text
    assert "nodeName" in result_combined_text

    # Parse results to verify filtering worked
    combined_lines = result_combined_text.strip().split("\n")
    combined_data_lines = [line for line in combined_lines[1:] if line.strip()]
    assert len(combined_data_lines) <= 3  # Should not exceed filtered nodes

    combined_full_text = " ".join(combined_data_lines)
    assert (
        "Covent Garden" in combined_full_text
        and "Southwark" in combined_full_text
        and "London Bridge" in combined_full_text
    )


@pytest.mark.asyncio
async def test_pagerank(mcp_client):
    result_combined = await mcp_client.call_tool(
        "pagerank",
        {
            "sourceNodes": ["Covent Garden"],
            "nodes": ["Covent Garden", "Southwark", "London Bridge"],
            "nodeIdentifierProperty": "name",
            "dampingFactor": 0.85,
        },
    )

    assert len(result_combined) == 1
    result_combined_text = result_combined[0]["text"]
    assert "nodeId" in result_combined_text
    assert "score" in result_combined_text
    assert "nodeName" in result_combined_text

    # Parse results to verify filtering worked
    combined_lines = result_combined_text.strip().split("\n")
    combined_data_lines = [line for line in combined_lines[1:] if line.strip()]
    assert len(combined_data_lines) <= 3  # Should not exceed filtered nodes

    combined_full_text = " ".join(combined_data_lines)
    assert (
        "Covent Garden" in combined_full_text
        and "Southwark" in combined_full_text
        and "London Bridge" in combined_full_text
    )


@pytest.mark.asyncio
async def test_harmonic_centrality(mcp_client):
    result_filtered = await mcp_client.call_tool(
        "harmonic_centrality",
        {
            "nodes": ["King's Cross St. Pancras", "Oxford Circus"],
            "nodeIdentifierProperty": "name",
        },
    )

    assert len(result_filtered) == 1
    result_filtered_text = result_filtered[0]["text"]
    assert "nodeId" in result_filtered_text
    assert "score" in result_filtered_text
    assert "nodeName" in result_filtered_text


@pytest.mark.asyncio
async def test_hits(mcp_client):
    result_filtered = await mcp_client.call_tool(
        "HITS",
        {
            "nodes": ["King's Cross St. Pancras", "Oxford Circus"],
            "nodeIdentifierProperty": "name",
        },
    )

    assert len(result_filtered) == 1
    result_filtered_text = result_filtered[0]["text"]
    assert "nodeId" in result_filtered_text
    assert "values" in result_filtered_text
    assert "nodeName" in result_filtered_text
