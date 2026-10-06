"""Checks for every module, whatever its exercise type.

Rules: spec/README.md, spec/content.md, spec/exercises.md. Checks that need
to run code are sent as jobs to the course's environment (see runner.py);
their results come back to check_results().
"""

import json
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from .report import Section

SPEC = Path(__file__).resolve().parents[2] / "spec"

MODULE_FILES = ["module.yaml", "lesson.md", "challenges", "exercise", "tests",
                "quiz.yaml", "recap.md", "solution", "broken"]
LESSON_WORDS = (500, 1200)
CHALLENGE_COUNT = (2, 3)
RECAP_POINTS = 7
RECAP_WORDS = 150

SOURCE_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CITATION = re.compile(r"\(\[([a-z0-9-]+#[^\]\s]+)\]\)")
DEFINITION = re.compile(r'^\[([a-z0-9-]+#[^\]\s]+)\]: (\S+)(?: "([^"]*)")?[ \t]*$', re.M)
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
MENTION = re.compile(r"`([\w./-]+\.\w+)`")
CHALLENGE = re.compile(r"^<!-- challenge id=(\w+) objective=(\d+) -->\n((?:>.*(?:\n|$))+)", re.M)
OBJECTIVE_REF = re.compile(r"\(objective (\d+)\)$")


@dataclass
class Course:
    dir: Path
    language: str
    module_ids: list[str]
    source_ids: set[str]


@dataclass
class Module:
    """What the static checks found out, for the checks that run code."""

    course: Course
    dir: Path
    data: dict  # module.yaml
    examples: list = field(default_factory=list)  # (line, code, expected output)
    quiz_codes: list = field(default_factory=list)  # (question id, code, options, answer)
    challenges: list = field(default_factory=list)  # IDs in lesson order
    learner_files: list = field(default_factory=list)  # relative to the module
    variants: dict = field(default_factory=dict)  # name -> relative paths

    @property
    def language(self):
        return self.data["language"]

    @property
    def objectives(self):
        return len(self.data["objectives"])


# Course


def check_course(course_dir):
    """Check course.yaml, brief.yaml and pyproject.toml. The course is None when
    course.yaml is unusable."""
    section = Section("course files")
    data = load_yaml(course_dir / "course.yaml", section)
    problems = schema_problems("course", data) if data is not None else ["unusable"]
    for problem in problems if data is not None else []:
        section.add(f"course.yaml: {problem}")

    brief = load_yaml(course_dir / "brief.yaml", section)
    source_ids = check_brief(brief, section) if isinstance(brief, dict) else set()
    if brief is not None and not isinstance(brief, dict):
        section.add("brief.yaml: must be a mapping")
    pyproject = course_dir / "pyproject.toml"
    if not pyproject.is_file():
        section.add('pyproject.toml: missing, so the course has no environment '
                    '(spec/README.md, "Course environment")')
    elif isinstance(brief, dict):
        check_pyproject(pyproject, brief, section)
    if problems:
        return section, None

    course = Course(course_dir, data["language"], data["modules"], source_ids)
    for module_id in course.module_ids:
        if not (course_dir / "modules" / module_id).is_dir():
            section.add(f"course.yaml: module {module_id} has no folder modules/{module_id}/")
    modules_dir = course_dir / "modules"
    if modules_dir.is_dir():
        for folder in sorted(modules_dir.iterdir()):
            if folder.is_dir() and not folder.name.startswith(".") \
                    and folder.name not in course.module_ids:
                section.add(f"modules/{folder.name}/ is not listed in course.yaml")
    section.note = f"{len(course.module_ids)} module(s), {len(source_ids)} source(s)"
    return section, course


def check_brief(brief, section):
    ids = set()
    sources = brief.get("sources")
    if not isinstance(sources, list) or not sources:
        section.add("brief.yaml: needs a list of sources")
        return ids
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            section.add(f"brief.yaml: sources/{index} must be a mapping")
            continue
        source_id = source.get("id")
        if not isinstance(source_id, str) or not SOURCE_ID.match(source_id):
            section.add(f"brief.yaml: sources/{index}: id must be lowercase letters, "
                        "digits and hyphens")
        elif source_id in ids:
            section.add(f"brief.yaml: source id {source_id!r} is used twice")
        else:
            ids.add(source_id)
        if ("url" in source) == ("path" in source):
            section.add(f"brief.yaml: sources/{index}: needs either a url or a path")
        for optional in ("license", "selector"):
            if optional in source and not (isinstance(source[optional], str) and source[optional].strip()):
                section.add(f"brief.yaml: sources/{index}: {optional} must be text")
    return ids


def check_pyproject(path, brief, section):
    """The course environment lists the runtime and every dependency in the brief."""
    try:
        listed = tomllib.loads(path.read_text(encoding="utf-8")).get("project", {}).get("dependencies", [])
    except tomllib.TOMLDecodeError as error:
        section.add(f"pyproject.toml: not valid TOML: {error}")
        return
    if "re-course-learn" not in listed:
        section.add("pyproject.toml: dependencies must include re-course-learn")
    wanted = brief.get("dependencies") or []
    if not isinstance(wanted, list):
        section.add("brief.yaml: dependencies must be a list")
        return
    for dependency in wanted:
        if dependency not in listed:
            section.add(f"pyproject.toml: doesn't list {dependency!r} from brief.yaml; "
                        "run `uv run python -m forge.dependencies <course>`")


# Module: checks that don't run code


def check_module(course, module_dir):
    """Returns (sections, module). The module is None when module.yaml is unusable."""
    files = Section("files and module.yaml")
    for name in MODULE_FILES:
        if not (module_dir / name).exists():
            files.add(f"{name}: missing")
    if not (module_dir / "module.yaml").is_file():
        return [files], None
    data = load_yaml(module_dir / "module.yaml", files)
    if data is None:
        return [files], None
    problems = schema_problems("module", data)
    for problem in problems:
        files.add(f"module.yaml: {problem}")
    if problems:
        return [files], None

    if data["id"] != module_dir.name:
        files.add(f"module.yaml: id {data['id']!r} doesn't match the folder name")
    if data["language"] != course.language:
        files.add(f"module.yaml: language {data['language']!r} differs from course.yaml")
    position = course.module_ids.index(module_dir.name) if module_dir.name in course.module_ids else 0
    for prerequisite in data["prerequisites"]:
        if prerequisite not in course.module_ids[:position]:
            files.add(f"module.yaml: prerequisite {prerequisite} is not an earlier module")
    if not (SPEC / "exercise-types" / f"{data['exercise_type']}.md").is_file():
        files.add(f"module.yaml: no spec for exercise type {data['exercise_type']!r}")

    module = Module(course, module_dir, data)
    module.learner_files = (
        [f"exercise/{path}" for path in files_under(module_dir / "exercise")]
        + [f"challenges/{path}" for path in files_under(module_dir / "challenges")]
    )
    sections = [files, check_lesson(module), check_quiz(module), check_recap(module),
                check_solutions(module)]
    return sections, module


def check_lesson(module):
    section = Section("lesson")
    path = module.dir / "lesson.md"
    if not path.is_file():
        return section  # reported under files
    text = path.read_text(encoding="utf-8")

    title = module.data["title"]
    if text.split("\n", 1)[0] != f"# {title}":
        section.add(f"lesson.md:1: the first line must be '# {title}'")
    objectives = lesson_objectives(text)
    if objectives is None:
        section.add('lesson.md: no "By the end of this module you can:" list')
    elif [normalize(item) for item in objectives] != [normalize(item) for item in module.data["objectives"]]:
        section.add("lesson.md: the objectives list doesn't match module.yaml")
    if "How to work through it" not in text:
        section.add('lesson.md: no "How to work through it" paragraph')
    headings = re.findall(r"^## (.+)$", text, re.M)
    if not headings or headings[-1].strip() != "What's next":
        section.add("lesson.md: the last ## section must be \"What's next\"")
    else:
        check_whats_next(module, text.rsplit("## What's next", 1)[1], section)
    words = len(prose(text).split())
    low, high = LESSON_WORDS
    if not low <= words <= high:
        section.add(f"lesson.md: {words} words of prose; must be {low}–{high}")

    check_code_blocks(module, text, section)
    citations = check_citations(module, text, section)
    check_links(module, text, section)
    check_challenges(module, text, section)
    section.note = (f"{words} words, {len(module.examples)} runnable examples, "
                    f"{len(module.challenges)} challenges, {citations} citation IDs")
    return section


def lesson_objectives(text):
    match = re.search(r"^By the end of this module you can:[ \t]*\n\n((?:.+\n?)+)", text, re.M)
    if not match:
        return None
    items = []
    for line in match.group(1).split("\n"):
        if re.match(r"\d+\. ", line):
            items.append(re.sub(r"^\d+\. ", "", line))
        elif line.startswith(" ") and items:
            items[-1] += " " + line.strip()
    return items


def check_whats_next(module, section_text, section):
    links = set(LINK.findall(section_text))
    wanted = [path for path in module.learner_files if path.startswith("exercise/")]
    for path in wanted + ["recap.md"]:
        if path not in links:
            section.add(f"lesson.md: \"What's next\" doesn't link {path}")
    for command in ("learn check", "learn quiz"):
        if f"`{command}`" not in section_text:
            section.add(f"lesson.md: \"What's next\" doesn't name `{command}`")


@dataclass
class Block:
    info: str
    content: str
    start: int  # line of the opening fence
    end: int  # line of the closing fence


def code_blocks(text):
    blocks, lines, index = [], text.split("\n"), 0
    while index < len(lines):
        match = re.match(r"(`{3,})(.*)$", lines[index])
        if match:
            fence, start, content = match.group(1), index, []
            index += 1
            while index < len(lines) and lines[index].strip() != fence:
                content.append(lines[index])
                index += 1
            body = "\n".join(content) + "\n" if content else ""
            blocks.append(Block(match.group(2).strip(), body, start + 1, index + 1))
        index += 1
    return blocks


def check_code_blocks(module, text, section):
    language = module.language
    blocks = code_blocks(text)
    for index, block in enumerate(blocks):
        following = blocks[index + 1] if index + 1 < len(blocks) else None
        previous = blocks[index - 1] if index else None
        if block.info == f"{language} run":
            if following is None or following.info != "output" or following.start != block.end + 1:
                section.add(f"lesson.md:{block.start}: a runnable example must be followed "
                            "directly by an output block")
            else:
                module.examples.append((block.start, block.content, following.content))
        elif block.info.split(" ")[0] == language:
            section.add(f"lesson.md:{block.start}: {language} code must be a "
                        f"`{language} run` block")
        elif block.info == "output" and (previous is None or previous.info != f"{language} run"):
            section.add(f"lesson.md:{block.start}: an output block must follow a "
                        f"`{language} run` block")


def check_citations(module, text, section):
    cited = set(CITATION.findall(text))
    defined = set()
    for citation_id, url, title in DEFINITION.findall(text):
        if citation_id in defined:
            section.add(f"lesson.md: {citation_id} is defined twice")
        defined.add(citation_id)
        if not url.startswith(("http://", "https://")):
            section.add(f"lesson.md: {citation_id} needs a URL")
        if not title:
            section.add(f'lesson.md: {citation_id} needs a "title"')
    for citation_id in sorted(cited - defined):
        section.add(f"lesson.md: {citation_id} is cited but not defined")
    for citation_id in sorted(defined - cited):
        section.add(f"lesson.md: {citation_id} is defined but never cited")
    if cited != set(module.data["sources"]):
        section.add(f"lesson.md: the cited IDs {sorted(cited)} don't match module.yaml "
                    f"sources {sorted(module.data['sources'])}")
    for citation_id in sorted(cited):
        problem = source_problem(module.course, *citation_id.split("#", 1))
        if problem:
            section.add(f"lesson.md: {citation_id}: {problem}")
    return len(cited)


def source_problem(course, source_id, section_id):
    if source_id not in course.source_ids:
        return f"source {source_id!r} is not in brief.yaml"
    path = course.dir / "sources" / f"{source_id}.md"
    if not path.is_file():
        return f"sources/{source_id}.md is missing"
    text = path.read_text(encoding="utf-8")
    front = re.match(r"---\n(.*?)\n---\n", text, re.S)
    try:
        front_id = (yaml.safe_load(front.group(1)) or {}).get("id") if front else None
    except yaml.YAMLError:
        front_id = None
    if front_id != source_id:
        return f"sources/{source_id}.md needs front matter with id: {source_id}"
    if not re.search(r"^#+ .*\{#" + re.escape(section_id) + r"\}[ \t]*$", text, re.M):
        return f"sources/{source_id}.md has no section {{#{section_id}}}"
    return None


def check_links(module, text, section):
    text = prose(text)
    targets = set()
    for target in LINK.findall(text):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        targets.add(target)
        if not (module.dir / target).exists():
            section.add(f"lesson.md: links to {target}, which doesn't exist")
    for mention in sorted(set(MENTION.findall(text))):
        if (module.dir / mention).is_file() and mention not in targets:
            section.add(f"lesson.md: mentions {mention} without linking it")


def check_challenges(module, text, section):
    found = CHALLENGE.findall(text)
    if len(re.findall(r"<!-- challenge ", text)) != len(found):
        section.add("lesson.md: every <!-- challenge ... --> comment must be followed "
                    "directly by a blockquote")
    for position, (challenge_id, objective, quote) in enumerate(found, 1):
        module.challenges.append(challenge_id)
        where = f"lesson.md: challenge {challenge_id}"
        if challenge_id != f"c{position}":
            section.add(f"{where}: should be c{position} (IDs go c1, c2, … in order)")
        if not 1 <= int(objective) <= module.objectives:
            section.add(f"{where}: objective {objective} doesn't exist")
        body = normalize(re.sub(r"^> ?", "", quote, flags=re.M))
        if not body.startswith(f"**Challenge {challenge_id}:**"):
            section.add(f"{where}: must start with **Challenge {challenge_id}:**")
        if f"](challenges/{challenge_id}." not in body:
            section.add(f"{where}: must link its file in challenges/")
        if not body.endswith(f"Check it with learn check {challenge_id}."):
            section.add(f"{where}: must end with \"Check it with `learn check {challenge_id}`.\"")
    low, high = CHALLENGE_COUNT
    if not low <= len(found) <= high:
        section.add(f"lesson.md: {len(found)} challenges; must be {low}–{high}")
    files = {Path(path).stem for path in files_under(module.dir / "challenges")}
    for challenge_id in module.challenges:
        if challenge_id not in files:
            section.add(f"challenges/{challenge_id}.*: missing for challenge {challenge_id}")
    for stem in sorted(files - set(module.challenges)):
        section.add(f"challenges/{stem}: no challenge {stem} in the lesson")


def check_quiz(module):
    section = Section("quiz")
    path = module.dir / "quiz.yaml"
    if not path.is_file():
        return section  # reported under files
    quiz = load_yaml(path, section)
    if quiz is None:
        return section
    problems = schema_problems("quiz", quiz)
    for problem in problems:
        section.add(f"quiz.yaml: {problem}")
    if problems:
        return section

    covered = set()
    for position, question in enumerate(quiz, 1):
        question_id = question["id"]
        if question_id != f"q{position}":
            section.add(f"quiz.yaml: {question_id} should be q{position}")
        if question["objective"] > module.objectives:
            section.add(f"quiz.yaml: {question_id}: objective {question['objective']} doesn't exist")
        covered.add(question["objective"])
        if question["answer"] >= len(question["options"]):
            section.add(f"quiz.yaml: {question_id}: answer {question['answer']} is not an "
                        "option (counted from 0)")
        elif question["type"] == "predict-output":
            module.quiz_codes.append(
                (question_id, question["code"], question["options"], question["answer"]))
    for objective in range(1, module.objectives + 1):
        if objective not in covered:
            section.add(f"quiz.yaml: no question for objective {objective}")
    if len({question["answer"] for question in quiz}) == 1:
        section.add("quiz.yaml: the answer is in the same position in every question")
    section.note = f"{len(quiz)} questions"
    return section


def check_recap(module):
    section = Section("recap")
    path = module.dir / "recap.md"
    if not path.is_file():
        return section  # reported under files
    lines = path.read_text(encoding="utf-8").split("\n")
    if not lines[0].startswith("# Recap: "):
        section.add("recap.md:1: must start with '# Recap: <short title>'")
    points = []
    for line in lines[1:]:
        if line.startswith("- "):
            points.append(line[2:].strip())
        elif line.startswith("  ") and points:
            points[-1] += " " + line.strip()
        elif line.strip():
            section.add(f"recap.md: line outside the list: {line.strip()[:40]}")
    words = len(" ".join(points).split())
    if len(points) > RECAP_POINTS:
        section.add(f"recap.md: {len(points)} points; at most {RECAP_POINTS}")
    if words > RECAP_WORDS:
        section.add(f"recap.md: {words} words; at most {RECAP_WORDS}")
    covered = set()
    for point in points:
        match = OBJECTIVE_REF.search(point)
        if not match:
            section.add(f"recap.md: point doesn't end with (objective N): {point[:40]}…")
        elif not 1 <= int(match.group(1)) <= module.objectives:
            section.add(f"recap.md: objective {match.group(1)} doesn't exist")
        else:
            covered.add(int(match.group(1)))
    for objective in range(1, module.objectives + 1):
        if objective not in covered:
            section.add(f"recap.md: no point for objective {objective}")
    section.note = f"{len(points)} points, {words} words"
    return section


def check_solutions(module):
    section = Section("solutions and variants")
    learner = set(module.learner_files)
    solution = set(files_under(module.dir / "solution"))
    for path in sorted(learner - solution):
        section.add(f"solution/{path}: missing")
    for path in sorted(solution - learner):
        section.add(f"solution/{path}: there is no learner file {path}")
    broken = module.dir / "broken"
    for variant in sorted(broken.iterdir()) if broken.is_dir() else []:
        if not variant.is_dir() or variant.name.startswith("."):
            continue
        paths = files_under(variant)
        module.variants[variant.name] = paths
        if not paths:
            section.add(f"broken/{variant.name}/: empty")
        for path in paths:
            if not path.startswith("exercise/") or path not in learner:
                section.add(f"broken/{variant.name}/{path}: variants may only change "
                            "existing files in exercise/")
            elif "Broken variant:" not in (variant / path).read_text(encoding="utf-8").split("\n", 1)[0]:
                section.add(f"broken/{variant.name}/{path}: the first line must be a "
                            "'Broken variant: <what is wrong>' comment")
    if not module.variants:
        section.add("broken/: no variants")
    section.note = f"{len(module.variants)} broken variants"
    return section


# Module: checks that run code


def jobs(module):
    language = module.language
    codes = [code for _, code, _ in module.examples] + [code for _, code, _, _ in module.quiz_codes]
    found = {
        "starter": {"kind": "tests", "module": str(module.dir)},
        "objectives": {"kind": "objectives", "module": str(module.dir)},
        "snippets": {"kind": "snippets", "language": language, "codes": codes},
    }
    for path in module.learner_files:
        if path.startswith("exercise/"):
            found[f"stubs:{path}"] = {"kind": "stubs", "language": language,
                                      "file": str(module.dir / path)}
    for variant, paths in module.variants.items():
        for path in paths:
            original = module.dir / "solution" / path
            if path in module.learner_files and original.is_file():
                found[f"changed:{variant}:{path}"] = {
                    "kind": "changed", "language": language, "original": str(original),
                    "changed": str(module.dir / "broken" / variant / path),
                }
    return found


def check_results(module, results):
    return [check_examples(module, results["snippets"]),
            check_tests(module, results),
            check_variant_coverage(module, results)]


def check_examples(module, result):
    section = Section("runnable examples")
    if job_failed(result, section):
        return section
    lesson_runs, quiz_runs = result[:len(module.examples)], result[len(module.examples):]
    for (line, _, expected), run in zip(module.examples, lesson_runs):
        if run["returncode"] != 0:
            section.add(f"lesson.md:{line}: the example fails: {last_line(run['stderr'])}")
        elif run["stdout"] != expected:
            section.add(f"lesson.md:{line}: prints {run['stdout']!r}, but the output block "
                        f"says {expected!r}")
    for (question_id, _, options, answer), run in zip(module.quiz_codes, quiz_runs):
        printed = run["stdout"].rstrip("\n")
        if run["returncode"] != 0:
            section.add(f"quiz.yaml: {question_id}: the code fails: {last_line(run['stderr'])}")
        elif printed != options[answer]:
            section.add(f"quiz.yaml: {question_id}: the code prints {printed!r}, but the marked "
                        f"answer is {options[answer]!r}")
    section.note = (f"{len(module.examples)} lesson examples, "
                    f"{len(module.quiz_codes)} predict-output answers")
    return section


def check_tests(module, results):
    section = Section("tests")
    starter, objectives = results["starter"], results["objectives"]
    if job_failed(starter, section) or job_failed(objectives, section):
        return section
    if not starter:
        section.add("tests/: no tests found")
        return section

    functions = sorted({f"{result['file']}::{result['name'].split('[')[0]}" for result in starter})
    covered = set()
    for function in functions:
        numbers = objectives.get(function, [])
        if not numbers:
            section.add(f"{function}: declares no objective")
        for number in numbers:
            if not 1 <= number <= module.objectives:
                section.add(f"{function}: objective {number} doesn't exist")
            covered.add(number)
    for objective in range(1, module.objectives + 1):
        if objective not in covered:
            section.add(f"no test checks objective {objective}")

    parts = {result["part"] for result in starter}
    for challenge_id in module.challenges:
        if challenge_id not in parts:
            section.add(f"challenge {challenge_id} has no test_{challenge_id}_* test "
                        "in test_challenges")
    for part in sorted(parts - set(module.challenges) - {"exercise"}):
        section.add(f"tests for {part}: there is no challenge {part} in the lesson")
    if "exercise" not in parts:
        section.add("no exercise tests")
    section.note = f"{len(starter)} tests in {len(functions)} test functions"
    return section


def check_variant_coverage(module, results):
    section = Section("variant coverage")
    units, changed_by = [], {}
    for name, result in results.items():
        if name.startswith("stubs:") and not job_failed(result, section):
            units += result
        elif name.startswith("changed:") and not job_failed(result, section):
            _, variant, path = name.split(":", 2)
            if not result:
                section.add(f"broken/{variant}/{path}: changes no function of the solution")
            for unit in result:
                changed_by.setdefault(unit, []).append(variant)
    if not units:
        section.add("exercise/: no stubs found; each unit the learner writes must be a stub")
    for unit in units:
        if unit not in changed_by:
            section.add(f"{unit}() has no broken variant")
    section.note = f"{len(units)} units in exercise/"
    return section


# Helpers


def load_yaml(path, section):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        section.add(f"{path.name}: missing")
    except yaml.YAMLError as error:
        section.add(f"{path.name}: not valid YAML: {error}")
    return None


def schema_problems(name, data):
    schema = json.loads((SPEC / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8"))
    problems = []
    for error in Draft202012Validator(schema).iter_errors(data):
        where = "/".join(str(part) for part in error.absolute_path)
        problems.append(f"{where}: {error.message}" if where else error.message)
    return problems


def files_under(folder):
    """Relative paths of the files under `folder`, without caches and hidden files."""
    if not folder.is_dir():
        return []
    paths = []
    for path in folder.rglob("*"):
        relative = path.relative_to(folder)
        if path.is_file() and "__pycache__" not in relative.parts \
                and not any(part.startswith(".") for part in relative.parts):
            paths.append(relative.as_posix())
    return sorted(paths)


def prose(text):
    """The lesson without code blocks, citation definitions and HTML comments."""
    text = re.sub(r"^(`{3,}).*?^\1[ \t]*$", "", text, flags=re.S | re.M)
    text = DEFINITION.sub("", text)
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def normalize(text):
    return " ".join(text.replace("`", "").split())


def job_failed(result, section):
    if isinstance(result, dict) and "error" in result:
        section.add(f"could not run: {result['error']}")
        return True
    return False


def last_line(text):
    lines = text.strip().split("\n")
    return lines[-1] if lines else ""
