from learn import quiz

QUESTION = {
    "prompt": "What does this print?",
    "code": 'print("ab"[1])\n',
    "options": ["a", "b"],
    "answer": 1,
    "explanation": "Index 1 is the second character.",
}


def run(replies):
    replies = iter(replies)
    lines = []
    score = quiz.run([QUESTION], ask=lambda prompt: next(replies), say=lines.append)
    return score, "\n".join(lines)


def test_correct_answer():
    score, out = run(["2"])
    assert score == 1
    assert "✓ Correct." in out
    assert '    print("ab"[1])' in out


def test_wrong_answer_shows_the_right_one():
    score, out = run(["1"])
    assert score == 0
    assert "✗ Not quite. The answer is 2) b" in out
    assert "Index 1 is the second character." in out


def test_invalid_replies_ask_again():
    score, out = run(["x", "5", "", "2"])
    assert score == 1
    assert out.count("Please type a number from 1 to 2.") == 3


def test_wrapping_keeps_quoted_text_together():
    quoted = 'first_word("  hello world")'
    text = "word " * 13 + quoted  # the quoted text crosses the 79th column
    assert quoted in quiz.wrap(text).split("\n")


def test_multiline_option_is_indented():
    question = dict(QUESTION, options=["one", "[a]\n[b]"])
    lines = []
    quiz.run([question], ask=lambda prompt: "2", say=lines.append)
    assert "  2) [a]\n     [b]" in lines
