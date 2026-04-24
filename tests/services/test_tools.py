from app.services.tools import TOOL_DEFINITIONS, build_system_prompt, execute_tool


def test_tool_definitions_structure():
    assert len(TOOL_DEFINITIONS) == 2
    names = {t["name"] for t in TOOL_DEFINITIONS}
    assert names == {"get_targets", "get_expressions"}


def test_execute_get_targets():
    result = execute_tool("get_targets", {"cancer_name": "lung"})
    assert sorted(result) == ["ALK", "KRAS", "RET", "ROS1", "STK11"]


def test_execute_get_expressions():
    result = execute_tool(
        "get_expressions", {"cancer_name": "lung", "genes": ["KRAS", "ALK"]}
    )
    assert result == {"KRAS": 0.359, "ALK": 0.215}


def test_execute_unknown_tool():
    result = execute_tool("unknown_tool", {})
    assert "error" in result.lower() or "unknown" in result.lower()


def test_execute_dispatches_dynamically():
    """Verify dispatch uses getattr -- no hard-coded if/elif needed."""
    result = execute_tool("get_available_cancers", {})
    assert set(result) == {
        "breast",
        "colorectal",
        "gastric",
        "glioblastoma",
        "lung",
        "melanoma",
        "ovarian",
        "pancreatic",
        "prostate",
        "renal",
    }


def test_system_prompt_contains_all_cancer_types():
    prompt = build_system_prompt()
    for cancer in [
        "breast",
        "colorectal",
        "gastric",
        "glioblastoma",
        "lung",
        "melanoma",
        "ovarian",
        "pancreatic",
        "prostate",
        "renal",
    ]:
        assert cancer in prompt, f"Missing '{cancer}' in system prompt"
    assert "get_targets" in prompt
    assert "get_expressions" in prompt
