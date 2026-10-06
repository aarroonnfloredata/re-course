# Greetings

A fixture for testing the bash plugin. Its lesson is short on purpose.

By the end of this module you can:

1. Read a script's arguments with `$1` and `$#`
2. Write functions and call them with arguments
3. Send output to files, and errors to stderr with an exit status

How to work through it: read each section, run the examples, and do each
challenge when you reach it.

## Arguments

A script's arguments are its positional parameters: `$1` is the first, and
`$#` is how many there are. ([bashref#Positional-Parameters])

```bash run
set -- apple banana
echo "$# arguments; the first is $1"
```
```output
2 arguments; the first is apple
```

<!-- challenge id=c1 objective=1 -->
> **Challenge c1:** Finish [`challenges/c1.sh`](challenges/c1.sh) so it
> prints how many arguments it got: `bash challenges/c1.sh a b c` prints
> `3`. Check it with `learn check c1`.

## Functions

A function groups commands under one name. ([bashref#Shell-Functions])

```bash run
greet() {
    echo "Hello, $1!"
}
greet Ada
```
```output
Hello, Ada!
```

<!-- challenge id=c2 objective=2 -->
> **Challenge c2:** Finish `twice` in [`challenges/c2.sh`](challenges/c2.sh)
> so it prints its argument twice: `twice hi` prints `hi hi`. Check it with
> `learn check c2`.

## Files and errors

`>` sends output to a file, and `>&2` sends it to stderr.
([bashref#Redirections])

```bash run
echo "saved" > note.txt
cat note.txt
echo "this goes to stderr" >&2
```
```output
saved
```

## What's next

Write [`exercise/greet.sh`](exercise/greet.sh) and the functions in
[`exercise/text.sh`](exercise/text.sh) until `learn check` passes, then take
`learn quiz` and read [`recap.md`](recap.md).

[bashref#Positional-Parameters]: https://www.gnu.org/software/bash/manual/bash.html#Positional-Parameters "Bash Reference Manual, 3.4.1 Positional Parameters"
[bashref#Shell-Functions]: https://www.gnu.org/software/bash/manual/bash.html#Shell-Functions "Bash Reference Manual, 3.3 Shell Functions"
[bashref#Redirections]: https://www.gnu.org/software/bash/manual/bash.html#Redirections "Bash Reference Manual, 3.6 Redirections"
