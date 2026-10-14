---
name: exercise-refactor
description: "How to write a refactor exercise for re-course - believable legacy starter code, the task statement, behaviour tests, structural checks, refactored solutions and the two kinds of broken variant. Use when writing or fixing any of these for a module with `exercise_type: refactor`."
---

# Refactor exercises

The rules are in `spec/exercise-types/refactor.md`; read it first. This skill
is about doing them well. How to write each part in a given language is in
`.claude/skills/lang-<language>/SKILL.md` ("Refactor modules").

Reference module: `examples/python/refactor-long-method/modules/01-long-method/`.
When in doubt, do what it does.

## Legacy starter code

The starter is the product here: if it doesn't feel real, nothing else
works.

- **Believable domain, accumulated mess.** Code that grew through changing
  requirements: a rule added here, a special case there, a comment
  explaining a block nobody dared to split. Avoid code that is cartoonishly
  bad (single-letter names everywhere, obvious nonsense) and code that is
  secretly clean.
- **The module's smells, clearly present.** Each smell the module teaches
  appears where a learner can find it. Other smells may be present in
  moderation, but the task only asks about the module's own.
- **It works.** Every documented behaviour is correct as written, including
  odd cases the legacy code handles in a surprising way (an empty order still
  pays shipping). Odd cases are good material for behaviour tests; they are
  not bugs to fix in this module.
- **Small enough to refactor in one sitting.** One area, usually one to
  three long functions. The rest of the file, in a cumulative course, is the
  previous module's solution and stays as it is.
- Use only what the lesson and earlier modules taught.

## The task statement

The exercise file's module docstring states the task. Agents write tests and
solutions from it, so it must be complete:

1. What this code is and why it needs work (one or two sentences).
2. What to do: "refactor it with Extract Method, without changing what it
   does".
3. The interface that must stay: function names and parameters that other
   code calls.
4. The targets, as measurable properties: "no function in this file is
   longer than 10 lines, not counting docstrings, blank lines and comments";
   "can_borrow() has a cyclomatic complexity of at most 4"; "no function in
   this file assigns a new value to one of its parameters".
5. A new requirement to add afterwards, if the module has one, stated as
   precisely as an `implement` stub's documentation.
6. How to check: `learn check`, behaviour tests pass from the start.

Pick targets the starter clearly misses and a good refactoring clearly meets,
with some room: if the solution's longest function has 8 lines, a limit of 10
is better than 8. Don't name functions the learner should create unless the
task needs a name (a requirement, or an interface other code calls); then
name them in the task.

## Behaviour tests

- Pin down what the starter does through the interface that must stay. Get
  the expected values by running the starter, never by reasoning about it.
- Cover each path the refactoring could break: each branch of the logic,
  boundary values (exactly at a threshold, just below), empty input, the odd
  cases. Each refactoring mistake a learner could make should change at least
  one pinned result.
- Name each case after the behaviour it pins
  (`shipping-counted-after-discount`), so a failure tells the learner where
  to look.

## Structural checks

- One test per target in the task. Each fails on the starter with a message
  that names the property, the measured value and the target.
- Test properties, never one particular design: line counts, complexity,
  nesting, parameter counts, comments, which named function calls which.
  Two different good refactorings must both pass.
- Name only functions the task names.

## Solution

The refactoring a careful practitioner would do: small, well-named
functions, each doing one thing, using the techniques the module teaches and
nothing the lesson hasn't covered. Docstrings of the interface stay the same.
It meets every target with some room.

## Broken variants

At least one of each kind, each one plausible:

- **behaviour**: a refactoring step that slipped, e.g. an extracted function
  gets the value before the discount instead of after, a threshold is lost
  while moving a condition, a changed variable isn't returned. A behaviour
  test must catch it.
- **smell**: the code behaves the same but the work isn't done, e.g. part of
  the long function is still inline, comments were moved along instead of
  becoming names. It must pass every behaviour test and fail a structural
  check.

A smell variant that breaks behaviour or a behaviour variant only the
structural checks catch shows a mistake in the variant or in the tests; the
validator reports which.

## Challenges

Challenges are small refactorings of a few lines each, in the module's
technique: extract this block, flatten this condition. Each challenge file is
working code whose docstring states the task, naming the function to create
when the check needs one. Its one check tests the new structure first, then
that the behaviour stayed the same.
