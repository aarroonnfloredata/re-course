# Recap: Extract Method

- Refactoring changes the shape of code so it behaves the same as before.
  Bug fixes and new rules are separate changes. (objective 1)
- A code smell, such as a very long function, is a hint that something may
  be wrong, not a bug. (objective 2)
- Extract Method moves part of a long function into a new function named
  after what the part does, and calls it where the part was. (objective 3)
- Values the part reads become parameters; a value it changes is returned
  and stored by the caller. (objective 3)
- Refactor in small steps and run the tests after each one. If a behaviour
  test fails, undo the last step and try again. (objective 4)
