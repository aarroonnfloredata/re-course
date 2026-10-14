"""Helpers for refactor exercises: behaviour tests and structural checks.

Behaviour tests pin down what the legacy code did; when one fails, the
refactoring changed the behaviour. Structural checks read the learner's code
with `ast` and test properties (length, complexity, nesting, comments, ...),
never one particular design. Every failure is a plain-language message.
"""

import ast
import io
import re
import textwrap
import tokenize
from contextlib import redirect_stdout
from pathlib import Path

import pytest

MODULE_DIR = Path(__file__).resolve().parent.parent

BLOCKS = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith, ast.Try,
          ast.TryStar, ast.Match)
NESTED_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)


# Behaviour tests


def keeps(func, args, before, kwargs=None):
    """Fail unless func(*args, **kwargs) still returns `before`, what the
    legacy code returned."""
    call = describe(func, args, kwargs)
    try:
        result = func(*args, **(kwargs or {}))
    except Exception as error:
        fail(f"Behaviour changed: {call} returned {before!r} before the refactoring, "
             f"but now raises {type(error).__name__}: {error}")
    if result != before:
        fail(f"Behaviour changed: {call} returned {before!r} before the refactoring, "
             f"but now returns {result!r}.")


def keeps_output(func, args, before, kwargs=None):
    """Fail unless func(*args, **kwargs) still prints `before`, what the
    legacy code printed."""
    call = describe(func, args, kwargs)
    printed = io.StringIO()
    try:
        with redirect_stdout(printed):
            func(*args, **(kwargs or {}))
    except Exception as error:
        fail(f"Behaviour changed: {call} now raises {type(error).__name__}: {error}")
    if printed.getvalue() != before:
        fail(f"Behaviour changed: before the refactoring, {call} printed:\n"
             f"{indent(before)}\nbut now it prints:\n{indent(printed.getvalue())}")


def keeps_raising(func, args, error_type, kwargs=None):
    """Fail unless func(*args, **kwargs) still raises `error_type`."""
    call = describe(func, args, kwargs)
    try:
        result = func(*args, **(kwargs or {}))
    except error_type:
        return
    except Exception as error:
        fail(f"Behaviour changed: {call} raised {error_type.__name__} before the "
             f"refactoring, but now raises {type(error).__name__}: {error}")
    fail(f"Behaviour changed: {call} raised {error_type.__name__} before the refactoring, "
         f"but now returns {result!r}.")


# Structural checks


class Function:
    """One function or method of a learner file, as the checks see it."""

    def __init__(self, name, node, lines):
        self.name = name  # "total" or "Invoice.total"
        self.node = node
        self._lines = lines  # the file's lines

    def __str__(self):
        return f"{self.name}()"

    @property
    def length(self):
        """Lines of code in the body: not counting the docstring, blank lines
        or lines that hold only a comment."""
        body = self.node.body
        if docstring_node(self.node) is not None:
            body = body[1:]
        if not body:
            return 0
        lines = self._lines[body[0].lineno - 1:self.node.end_lineno]
        return sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))

    @property
    def complexity(self):
        """Cyclomatic complexity: 1, plus 1 for each if, elif, conditional
        expression, for, while, except, with, assert, comprehension `for` or
        `if` and match case, plus 1 for each extra operand of `and` and `or`.
        Nested functions and classes count on their own."""
        total = 1
        for node in walk(self.node):
            if isinstance(node, (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While,
                                 ast.With, ast.AsyncWith, ast.Assert, ast.ExceptHandler,
                                 ast.match_case)):
                total += 1
            elif isinstance(node, ast.comprehension):
                total += 1 + len(node.ifs)
            elif isinstance(node, ast.BoolOp):
                total += len(node.values) - 1
        return total

    @property
    def nesting(self):
        """How deep blocks (if, for, while, with, try, match) sit inside each
        other; an elif doesn't count as a level of its own."""
        def depth(statements, level):
            deepest = level
            for statement in statements:
                if isinstance(statement, NESTED_SCOPES):
                    continue
                inner = level + 1 if isinstance(statement, BLOCKS) else level
                for children in child_blocks(statement):
                    elif_chain = (isinstance(statement, ast.If) and children is statement.orelse
                                  and len(children) == 1 and isinstance(children[0], ast.If))
                    deepest = max(deepest, depth(children, level if elif_chain else inner))
                deepest = max(deepest, inner)
            return deepest
        return depth(self.node.body, 0)

    @property
    def parameters(self):
        """Parameter names, without self and cls."""
        arguments = self.node.args
        names = [arg.arg for arg in arguments.posonlyargs + arguments.args + arguments.kwonlyargs]
        names += [arg.arg for arg in (arguments.vararg, arguments.kwarg) if arg is not None]
        return [name for name in names if name not in ("self", "cls")]

    @property
    def comments(self):
        """The comments inside the function, without their #."""
        text = textwrap.dedent("\n".join(self._lines[self.node.lineno - 1:self.node.end_lineno])) + "\n"
        found = []
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.COMMENT:
                found.append(token.string.lstrip("#").strip())
        return found

    @property
    def calls(self):
        """Names of the functions and methods it calls: `total` for
        total(...) and for self.total(...)."""
        names = set()
        for node in walk(self.node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    names.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    names.add(node.func.attr)
        return names

    @property
    def reassigned(self):
        """Local names given a new value with `=` more than once (loop
        variables and augmented assignments like += don't count)."""
        counts = {}
        for node in walk(self.node):
            targets = []
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                targets = [node.target]
            for target in targets:
                for name in assigned_names(target):
                    counts[name] = counts.get(name, 0) + 1
        return sorted(name for name, count in counts.items() if count > 1)

    @property
    def assigned_parameters(self):
        """Parameters the body assigns a new value to."""
        assigned = set()
        for node in walk(self.node):
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                for target in getattr(node, "targets", [getattr(node, "target", None)]):
                    assigned.update(assigned_names(target))
        return [name for name in self.parameters if name in assigned]


def functions(relative_path):
    """The functions and methods of a learner file, by name ("Class.method"
    for methods). Functions nested in other functions are left out."""
    path = MODULE_DIR / relative_path
    try:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
    except FileNotFoundError:
        fail(f"{relative_path} is missing.")
    except SyntaxError as error:
        fail(f"{relative_path} could not be loaded: SyntaxError: {error.msg} (line {error.lineno})")
    lines = text.split("\n")
    found = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found[node.name] = Function(node.name, node, lines)
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    name = f"{node.name}.{item.name}"
                    found[name] = Function(name, item, lines)
    return found


def function(relative_path, name):
    """One function or method of a learner file; fails if it is missing."""
    found = functions(relative_path)
    if name not in found:
        fail(f"{relative_path} has no {name}(); the task says to keep it.")
    return found[name]


def max_length(relative_path, limit, names=None):
    """Fail unless every function (or each of `names`) has at most `limit`
    lines of code in its body."""
    selected = select(relative_path, names)
    too_long = [f"{function} has {function.length} lines" for function in selected
                if function.length > limit]
    if too_long:
        fail(listing(too_long, f"the task asks for no function longer than {limit} lines "
                               "(not counting docstrings, blank lines and comments)"))


def max_complexity(relative_path, limit, names=None):
    """Fail unless every function (or each of `names`) has a cyclomatic
    complexity of at most `limit`."""
    selected = select(relative_path, names)
    too_complex = [f"{function} has a cyclomatic complexity of {function.complexity}"
                   for function in selected if function.complexity > limit]
    if too_complex:
        fail(listing(too_complex, f"the task asks for a complexity of at most {limit}"))


def max_nesting(relative_path, limit, names=None):
    """Fail unless blocks in every function (or each of `names`) are nested
    at most `limit` deep."""
    selected = select(relative_path, names)
    too_deep = [f"{function} nests blocks {function.nesting} deep" for function in selected
                if function.nesting > limit]
    if too_deep:
        fail(listing(too_deep, f"the task asks for blocks nested at most {limit} deep"))


def max_parameters(relative_path, limit, names=None):
    """Fail unless every function (or each of `names`) takes at most `limit`
    parameters, not counting self and cls."""
    selected = select(relative_path, names)
    too_many = [f"{function} takes {len(function.parameters)} parameters" for function in selected
                if len(function.parameters) > limit]
    if too_many:
        fail(listing(too_many, f"the task asks for at most {limit} parameters"))


def no_comments(relative_path, names=None):
    """Fail if any function (or one of `names`) still has comments inside."""
    selected = [function for function in select(relative_path, names) if function.comments]
    if selected:
        found = "\n".join(f"{function}: # {text}" for function in selected
                          for text in function.comments)
        fail("The task asks for names instead of comments inside functions, but these "
             f"comments are still there:\n{indent(found)}")


def fail(message):
    pytest.fail(message, pytrace=False)


# Internals


def select(relative_path, names):
    found = functions(relative_path)
    if names is None:
        return list(found.values())
    for name in names:
        if name not in found:
            fail(f"{relative_path} has no {name}(); the task says to keep it.")
    return [found[name] for name in names]


def listing(items, target):
    if len(items) == 1:
        return f"{items[0]}; {target}."
    return f"Some functions miss the target; {target}:\n" + indent("\n".join(items))


def walk(function_node):
    """The nodes inside a function, without entering nested functions or classes."""
    stack = list(function_node.body)
    while stack:
        node = stack.pop()
        yield node
        for child in ast.iter_child_nodes(node):
            if not isinstance(child, NESTED_SCOPES):
                stack.append(child)


def child_blocks(statement):
    for field in ("body", "orelse", "finalbody"):
        block = getattr(statement, field, None)
        if block:
            yield block
    for handler in getattr(statement, "handlers", []):
        yield handler.body
    for case in getattr(statement, "cases", []):
        yield case.body


def assigned_names(target):
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        return [name for element in target.elts for name in assigned_names(element)]
    return []


def docstring_node(node):
    first = node.body[0] if node.body else None
    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) \
            and isinstance(first.value.value, str):
        return first
    return None


def describe(func, args, kwargs):
    shown = [repr(arg) for arg in args] + [f"{key}={value!r}" for key, value in (kwargs or {}).items()]
    return f"{func.__name__}({', '.join(shown)})"


def indent(text):
    return re.sub(r"(?m)^", "    ", text.rstrip("\n"))
