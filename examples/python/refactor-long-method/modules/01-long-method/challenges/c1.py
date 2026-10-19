"""Challenge c1 – see "Extract Method" in lesson.md.

Move the block under the comment into a new function average(scores) that
returns the average of `scores`, and call it from report(). report() keeps
printing exactly what it prints now.
"""


def report(name, scores):
    """Print `name`, how many scores there are and their average.

    report("Ada", [7, 9, 8]) prints "Ada: 3 scores, average 8.0".
    """
    # work out the average
    total = 0
    for score in scores:
        total += score
    mean = total / len(scores)
    print(f"{name}: {len(scores)} scores, average {mean:.1f}")
