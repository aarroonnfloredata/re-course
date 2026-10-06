"""Checks for outline.yaml, the module plan. Rules: spec/README.md ("outline.yaml")."""

from . import core
from .report import Section


def check_outline(course_dir, source_ids, project_style):
    """Returns (section, plan). The plan maps module ID -> outline entry, in
    order; it is None when outline.yaml is missing or unusable."""
    section = Section("outline.yaml")
    path = course_dir / "outline.yaml"
    if not path.is_file():
        section.add("outline.yaml: missing; run /outline")
        return section, None
    data = core.load_yaml(path, section)
    if data is None:
        return section, None
    problems = core.schema_problems("outline", data)
    for problem in problems:
        section.add(f"outline.yaml: {problem}")
    if problems:
        return section, None

    sources = core.Course(course_dir, "", [], source_ids)
    earlier, introduced, used = [], {}, set()
    for position, module in enumerate(data["modules"], 1):
        module_id = module["id"]
        where = f"outline.yaml: {module_id}"
        if not module_id.startswith(f"{position:02d}-"):
            section.add(f"{where}: is module {position}, so its ID must start with {position:02d}-")
        if module_id in earlier:
            section.add(f"{where}: is listed twice")
        for prerequisite in module["prerequisites"]:
            if prerequisite not in earlier:
                section.add(f"{where}: prerequisite {prerequisite} is not an earlier module")
        for concept in module["introduces"]:
            key = " ".join(concept.lower().split())
            if key in introduced:
                section.add(f"{where}: {concept!r} is already introduced by {introduced[key]}")
            else:
                introduced[key] = module_id
        for citation in module["sources"]:
            used.add(citation)
            problem = core.source_problem(sources, *citation.split("#", 1))
            if problem:
                section.add(f"{where}: {citation}: {problem}")
        earlier.append(module_id)

    left_out = data.get("left_out") or []
    for item in left_out:
        citation = item["section"]
        if citation in used:
            section.add(f"outline.yaml: left_out {citation} is also used by a module")
        problem = core.source_problem(sources, *citation.split("#", 1))
        if problem:
            section.add(f"outline.yaml: left_out {citation}: {problem}")
    if project_style == "cumulative" and not data.get("scenario"):
        section.add("outline.yaml: a cumulative course needs a scenario")

    section.note = f"{len(data['modules'])} module(s), {len(left_out)} section(s) left out"
    return section, {module["id"]: module for module in data["modules"]}
