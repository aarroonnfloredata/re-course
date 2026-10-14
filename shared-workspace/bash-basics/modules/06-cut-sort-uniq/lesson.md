# Cutting, Sorting and Counting

Which clients send the server the most requests? To find out, you take
the IP out of every line, bring equal IPs together, count them and rank
the counts. Three small tools do it: `cut` picks fields out of lines,
`sort` puts lines in order, and `uniq` collapses repeated lines and counts
them. ([tlcl#cut]) ([tlcl#sort]) ([tlcl#uniq]) Joined in one pipeline,
they make logkit's sixth tool, [`exercise/top.sh`](exercise/top.sh).

By the end of this module you can:

1. Pick fields out of each line with `cut`
2. Sort lines as text or as numbers, in either order, with `sort`
3. Count repeated lines with `sort | uniq -c`
4. Rank values with one pipeline and reformat its output with `while read`

**How to work through it:** paste each example whole: pipelines and loops
span several lines. Each example first writes the small files it reads,
so they don't depend on each other.

## Picking fields with `cut`

A log line holds six fields with one space between each.
`cut -d ' ' -f 2` prints field 2 of every line: `-f` chooses the fields
and `-d` names the character between them. ([tlcl#cut]) With no `-d`,
`cut` splits at tabs, which log lines don't have. ([tlcl#cut]) For more
than one field, join their numbers with commas (`4,5`) or give a span
with a dash (`4-6`). ([tlcl#cut]) `cut` reads the files you name, or
text piped into it. ([tlcl#cut])

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" >> access.log
cut -d ' ' -f 2 access.log
cut -d ' ' -f 4,5 access.log
cut -d ' ' -f 4-6 access.log
```
```output
203.0.113.5
198.51.100.7
/index.html 200
/missing.html 404
/index.html 200 512
/missing.html 404 153
```

Three details to know. The fields come out in the order of the line,
whatever the order after `-f`. Without `-d ' '`, a line that holds no tab comes out whole. And
every single space separates two fields, so two spaces in a row hold an
empty field between them: `-d ' '` splits like Python's
`line.split(" ")`, not `line.split()`.

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
cut -d ' ' -f 5,4 access.log
cut -f 2 access.log
echo "GET  /index.html" > spaced.txt
field2=$(cut -d ' ' -f 2 spaced.txt)
field3=$(cut -d ' ' -f 3 spaced.txt)
echo "field 2: [$field2]"
echo "field 3: [$field3]"
```
```output
/missing.html 404
2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
field 2: []
field 3: [/index.html]
```

`-c` picks characters by position instead, with a list of ranges such as
`1-10`. ([tlcl#cut]) Positions count from 1 and a range includes both
ends, so `cut -c 1-10` is Python's `line[0:10]`. On every log line,
characters 1 to 10 are the date. Character 49 is not as steady: IPs and
paths vary in length, so in the two lines below it is a digit of the
status in one and a letter of the path in the other. ([tlcl#cut]) For characters
inside a later field, chain two `cut`s: the first takes field 5, the
status, wherever it sits, and the second takes its first digit with
`-c 1`. ([tlcl#cut])

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T11:02:17 198.51.100.7 GET /missing.html 404 153" >> access.log
cut -c 1-10 access.log
cut -c 49 access.log
cut -d ' ' -f 5 access.log | cut -c 1
```
```output
2026-10-06
2026-10-06
2
m
2
4
```

<!-- challenge id=c1 objective=1 -->
> **Challenge c1:** Open [`challenges/c1.sh`](challenges/c1.sh) and make it
> print the path and the status of every request in LOGFILE, the script's
> first argument, as `PATH STATUS`. For the first example's `access.log`,
> `bash challenges/c1.sh access.log` prints `/index.html 200` and then
> `/missing.html 404`. Check it with `learn check c1`.

## Sorting with `sort`

Unless told otherwise, `sort` orders lines as text, comparing them a
character at a time from the left. Their first characters, `1` and `6`,
put `1024` before `64`. ([tlcl#sort]) With `-n`, it compares the numbers
the lines hold, and `64` goes first. ([tlcl#sort]) `-r` turns either
order around: `sort -r` starts with `64`, and `sort -nr` with the biggest
number, like Python's `sorted(lines, key=int, reverse=True)`. ([tlcl#sort])
Like `cut`, it reads the files you name, or text piped into
it. ([tlcl#sort])

```bash run
echo 512 > bytes.txt
echo 64 >> bytes.txt
echo 1024 >> bytes.txt
echo 153 >> bytes.txt
echo "as text:"
sort bytes.txt
echo "as text, reversed:"
sort -r bytes.txt
echo "as numbers:"
sort -n bytes.txt
echo "as numbers, reversed:"
sort -nr bytes.txt
```
```output
as text:
1024
153
512
64
as text, reversed:
64
512
153
1024
as numbers:
64
153
512
1024
as numbers, reversed:
1024
512
153
64
```

<!-- challenge id=c2 objective=2 -->
> **Challenge c2:** Open [`challenges/c2.sh`](challenges/c2.sh) and make it
> print the bytes of every request in LOGFILE, the script's first argument,
> one number per line, biggest first. For a log whose requests sent 512,
> 153 and 4096 bytes, it prints `4096`, `512` and `153`, in that order.
> Check it with `learn check c2`.

## Counting with `uniq`

`sort | uniq` lists each distinct line once: `sort` puts equal lines next
to each other, and `uniq` turns each run of equal lines into one line.
`uniq` needs `sort` for this, because it only drops a line that equals
the line just above it. ([tlcl#uniq]) Below, the statuses come in the
order of the requests, and `uniq` alone keeps a second `200` and a second
`404`:

```bash run
echo 200 > statuses.txt
echo 200 >> statuses.txt
echo 404 >> statuses.txt
echo 200 >> statuses.txt
echo 404 >> statuses.txt
echo "sort, then uniq:"
sort statuses.txt | uniq
echo "uniq alone:"
uniq statuses.txt
```
```output
sort, then uniq:
200
404
uniq alone:
200
404
200
404
```

With `-c`, `uniq` puts in front of each line it keeps the number of lines
in its run. ([tlcl#uniq]) For these statuses,
`sort statuses.txt | uniq -c` prints two lines, `3 200` and `2 404`, each
padded with spaces before the count. Run it in that example's folder to
see how many spaces your system puts there.

The padding gets in `cut`'s way: when a line starts with a space, its
field 1 is the empty text before that space. `while read -r` skips
spaces at the start of a line, and splits the rest into the count and
the value:

```bash run
echo 404 > statuses.txt
echo 200 >> statuses.txt
echo 404 >> statuses.txt
echo 200 >> statuses.txt
echo 200 >> statuses.txt
first=$(sort statuses.txt | uniq -c | head -n 1 | cut -d ' ' -f 1)
echo "cut's field 1: [$first]"
sort statuses.txt | uniq -c | while read -r count status; do
    echo "$status: $count requests"
done
```
```output
cut's field 1: []
200: 3 requests
404: 2 requests
```

This loop sits at the end of a pipe. That's fine, as it only prints. A
variable it sets is lost when the loop ends, as module 5 warned:

```bash run
echo 404 > statuses.txt
echo 200 >> statuses.txt
last=none
sort statuses.txt | uniq -c | while read -r _ status; do
    last=$status
done
echo "last status after the loop: $last"
```
```output
last status after the loop: none
```

<!-- challenge id=c3 objective=3 -->
> **Challenge c3:** Open [`challenges/c3.sh`](challenges/c3.sh) and make it
> print, for each status in LOGFILE, the script's first argument, the line
> `STATUS COUNT`: the status and how many requests had it, lowest status
> first. For a log with three 200 requests and two 404s, it prints `200 3`
> and then `404 2`. Check it with `learn check c3`.

## Ranking with one pipeline

A ranking is a count, sorted. In each line from `uniq -c`, the count
comes first, after the padding, so `sort -nr` puts the biggest count
first. ([tlcl#sort]) `head -n 3` after it keeps only the first three
lines it gets: the three biggest counts. ([tlcl#sort])
A `while read -r` loop at the end prints each line the way you want it.
A line that ends with `|` goes on in the next one:

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" >> access.log
echo "2026-10-06T10:16:02 203.0.113.5 GET /index.html 200 512" >> access.log
echo "2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 2048" >> access.log
echo "2026-10-06T10:16:48 192.0.2.44 GET /index.html 200 512" >> access.log
echo "2026-10-06T10:17:03 198.51.100.7 GET /missing.html 404 153" >> access.log
cut -d ' ' -f 4 access.log | sort | uniq -c | sort -nr |
    while read -r count path; do
        echo "$path $count"
    done
```
```output
/index.html 3
/missing.html 2
/about.html 1
```

Read it from left to right: `cut` takes the paths, `sort` brings equal
paths together, `uniq -c` counts each one, `sort -nr` puts the biggest
count first, and the loop swaps count and path. Each step needs the one
before it: `uniq -c` counts only repeats next to each other. ([tlcl#uniq])

## What's next

- **Exercise:** write [`exercise/top.sh`](exercise/top.sh), logkit's
  sixth tool, as its header comment describes, then run `learn check`.
  [`exercise/notfound.sh`](exercise/notfound.sh),
  [`exercise/count.sh`](exercise/count.sh),
  [`exercise/countall.sh`](exercise/countall.sh),
  [`exercise/healthcheck.sh`](exercise/healthcheck.sh) and
  [`exercise/summary.sh`](exercise/summary.sh) are the finished tools
  from modules 1 to 5; leave them as they are.
- **Quiz:** run `learn quiz`.
- **Recap:** read [`recap.md`](recap.md).

[tlcl#cut]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=326 "The Linux Command Line, 20 Text Processing: Slicing and Dicing: cut"
[tlcl#sort]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=317 "The Linux Command Line, 20 Text Processing: Revisiting Some Old Friends: sort"
[tlcl#uniq]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=324 "The Linux Command Line, 20 Text Processing: Revisiting Some Old Friends: uniq"
