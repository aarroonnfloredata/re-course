# Regular Expressions with grep

Some requests in a log look like attacks: paths with `..` in them, paths
ending in `.php` or `.env`, failed logins. A fixed string like `" 404 "`
can't describe them. A regular expression can: it is a notation for
patterns in text. ([tlcl#what-are-regular-expressions]) With regular
expressions, you add [`exercise/suspicious.sh`](exercise/suspicious.sh) to logkit.

By the end of this module you can:

1. Anchor a pattern to the start or end of a line, and match any character
   or one of a set
2. Repeat parts of a pattern with `*`, `+`, `?` and `{ }`
3. Match alternatives and groups with `|` and `( )` in `grep -E`
4. Leave out matching lines and ignore case with `grep -v` and `-i`

**How to work through it:** patterns are in single quotes; the first
section says why.

## Patterns, not just text

In `grep [options] regex [file...]`, each line of the files is printed if
the regex matches some part of it, as with Python's
`re.search()`. ([tlcl#grep]) `" 404 "`
is a regular expression too: each of its characters is a
literal, which matches itself. ([tlcl#metacharacters-and-literals])
grep, like most command-line tools, uses POSIX regular
expressions. ([tlcl#what-are-regular-expressions]) ([tlcl#posix-basic-vs-extended-regular-expressions])
POSIX (Portable Operating System Interface) is a set of standards for
Unix-like systems. ([tlcl#posix-basic-vs-extended-regular-expressions])

The metacharacters, which have special meanings, are `\`, `.`, `*`, `^`,
`$`, `[ ]` and `-`, and also `+ ? { } ( ) |`. ([tlcl#metacharacters-and-literals])
Unescaped, those last seven are special only with `-E`, the way this
module writes them, and `-` only inside
`[ ]`. ([tlcl#posix-basic-vs-extended-regular-expressions]) ([tlcl#bracket-expressions-and-character-classes])
Many metacharacters are special to the shell too, so quote every
pattern. ([tlcl#metacharacters-and-literals]) `echo` shows what a command
receives:

```bash run
status=404
echo unquoted: \.php
echo double-quoted: "\.php$" "$status"
echo single-quoted: '\.php$' '$status'
```
```output
unquoted: .php
double-quoted: \.php$ 404
single-quoted: \.php$ $status
```

Without quotes, the backslash is lost. Double quotes keep `\.` and a
final `$` but expand `$status`; single quotes keep everything as typed, so
this module uses them; double quotes suit a pattern with a variable.

## Any character and anchors

`.` matches any one character. ([tlcl#the-any-character]) So `.php` needs
a character before `php`, which can be the `/` of
`/phpinfo`. ([tlcl#the-any-character]) Write `\.` for a real dot: the
backslash takes away the dot's special meaning. ([tlcl#metacharacters-and-literals])

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /phpinfo 404 153" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /wp-login.php 404 153" >> access.log
echo "2026-10-06T10:16:02 192.0.2.44 GET /index.html 200 512" >> access.log
grep '.php' access.log
echo "---"
grep '\.php' access.log
```
```output
2026-10-06T10:15:32 203.0.113.5 GET /phpinfo 404 153
2026-10-06T10:15:40 198.51.100.7 GET /wp-login.php 404 153
---
2026-10-06T10:15:40 198.51.100.7 GET /wp-login.php 404 153
```

`^` makes a pattern match only at the start of a line, and `$` only at
its end. `^$` matches an empty line. ([tlcl#anchors]) In logkit's logs,
`^` points at the time and `$` at the bytes:

```bash run
echo "2026-10-05T23:59:58 192.0.2.44 GET /index.html 200 512" > access.log
echo "2026-10-06T00:00:03 203.0.113.5 GET /reports/2026-10-05.html 200 1020" >> access.log
echo "2026-10-06T00:00:09 198.51.100.7 GET /favicon.ico 304 0" >> access.log
grep '2026-10-05' access.log
echo "---"
grep '^2026-10-05' access.log
echo "---"
grep '0$' access.log
echo "---"
grep ' 0$' access.log
```
```output
2026-10-05T23:59:58 192.0.2.44 GET /index.html 200 512
2026-10-06T00:00:03 203.0.113.5 GET /reports/2026-10-05.html 200 1020
---
2026-10-05T23:59:58 192.0.2.44 GET /index.html 200 512
---
2026-10-06T00:00:03 203.0.113.5 GET /reports/2026-10-05.html 200 1020
2026-10-06T00:00:09 198.51.100.7 GET /favicon.ico 304 0
---
2026-10-06T00:00:09 198.51.100.7 GET /favicon.ico 304 0
```

Without `^`, the date in the second line's path matches too. `0$` finds
bytes ending in 0; `' 0$'` needs the last field to be 0.

## Sets of characters

A bracket expression, `[...]`, matches one character from the set inside
it. A `-` between two characters gives a range: `[0-9]` is any
digit. ([tlcl#bracket-expressions-and-character-classes]) Right after `[`,
a `^` turns the set around: `[^2]` is one character other than 2, so the
line must have a character in that place. ([tlcl#negation]) Other
metacharacters are plain inside the brackets: `[.*]` is a dot or a
star. ([tlcl#bracket-expressions-and-character-classes])

POSIX character classes name common sets, such as `[:digit:]`,
`[:alpha:]`, `[:upper:]`, `[:lower:]` and `[:space:]`. ([tlcl#posix-character-classes])
A class goes inside a bracket expression, so one digit is
`[[:digit:]]`. ([tlcl#match-an-element-zero-or-more-times]) Prefer
`[[:upper:]]` to `[A-Z]`: in some locales a glob's `[A-Z]` also matches
lowercase letters, and other programs can behave the same way. ([tlcl#posix-character-classes])

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /old.html 301 0" >> access.log
echo "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64" >> access.log
echo "2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0" >> access.log
echo "failed:"
grep ' [45][0-9][0-9] ' access.log
echo "not 2xx:"
grep ' [^2][[:digit:]][[:digit:]] ' access.log
```
```output
failed:
2026-10-06T10:16:02 203.0.113.5 POST /login 401 64
2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0
not 2xx:
2026-10-06T10:15:40 198.51.100.7 GET /old.html 301 0
2026-10-06T10:16:02 203.0.113.5 POST /login 401 64
2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0
```

<!-- challenge id=c1 objective=1 -->
> **Challenge c1:** Open [`challenges/c1.sh`](challenges/c1.sh) and make it
> print the requests in LOGFILE, its first argument, whose time starts
> with `2026-10-05`, `2026-10-06` or `2026-10-07`. A request from
> 2026-10-08 for `/reports/2026-10-06.html` is not printed. Check it with
> `learn check c1`.

## Extended patterns with `grep -E`

grep reads a basic regular expression unless you give it `-E`; then it
reads an extended one. These are the two POSIX kinds, and only the
extended kind gives `+ ? { } ( ) |` their meaning without a
backslash. ([tlcl#posix-basic-vs-extended-regular-expressions]) Without `-E`,
the `{3}` below, "three times", is plain text that no line holds:

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
grep ' [0-9]{3} ' access.log
echo "basic: status $?"
grep -E ' [0-9]{3} ' access.log
```
```output
basic: status 1
2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
```

`\(` matches a `(` in an extended pattern, and `\.` a dot; escaping works
for every metacharacter there. ([tlcl#posix-basic-vs-extended-regular-expressions])
Examples below use `grep -E` for any pattern with `+ ? { } ( ) |`.

## Repeating with `*`, `+`, `?` and `{ }`

A quantifier says how many times the element just before it may
occur. ([tlcl#quantifiers]) The element is one character, one bracket
expression, or a group (a later section). ([tlcl#match-an-element-zero-or-one-time]) ([tlcl#match-an-element-zero-or-more-times]) ([tlcl#match-an-element-one-or-more-times])
Python's `re` uses the same symbols. Its `\d`, `\w`, `\s` and `\b` aren't
POSIX, so not every grep has them: write `[0-9]` or
`[[:digit:]]`. ([tlcl#what-are-regular-expressions])

- `?`: zero times or once, so the element is
  optional. ([tlcl#match-an-element-zero-or-one-time])
- `*`: zero or more times. ([tlcl#match-an-element-zero-or-more-times])
- `+`: one or more times. ([tlcl#match-an-element-one-or-more-times])
- `{n}`: exactly n times; `{n,m}`: n to m times; `{n,}`: n or more
  times. ([tlcl#match-an-element-a-specific-number-of-times])

```bash run
echo "/" > paths.txt
echo "/admin" >> paths.txt
echo "/admin/" >> paths.txt
echo "/admin/users" >> paths.txt
echo "? optional slash:"
grep -E '^/admin/?$' paths.txt
echo "* zero or more letters:"
grep -E '^/[[:lower:]]*$' paths.txt
echo "+ one or more letters:"
grep -E '^/[[:lower:]]+$' paths.txt
```
```output
? optional slash:
/admin
/admin/
* zero or more letters:
/
/admin
+ one or more letters:
/admin
```

In a glob, `*` is any text and `?` any one character.
In a regular expression, `*` repeats the element before it and `?` makes
it optional; any text is `.*`. `[[ ]]` matches globs:

```bash run
echo "/api/users" > paths.txt
echo "/apis" >> paths.txt
[[ /api/users = /api* ]] && echo "glob /api*: /api/users"
[[ /apis = /api? ]] && echo "glob /api?: /apis"
echo "regex ^/api*$:"
grep -E '^/api*$' paths.txt
echo "regex ^/api?$:"
grep -E '^/api?$' paths.txt
echo "regex ^/api.*$:"
grep -E '^/api.*$' paths.txt
```
```output
glob /api*: /api/users
glob /api?: /apis
regex ^/api*$:
regex ^/api?$:
regex ^/api.*$:
/api/users
/apis
```

```bash run
echo 0 > bytes.txt
echo 64 >> bytes.txt
echo 512 >> bytes.txt
echo 2048 >> bytes.txt
echo "exactly 3 digits:"
grep -E '^[0-9]{3}$' bytes.txt
echo "2 to 3 digits:"
grep -E '^[0-9]{2,3}$' bytes.txt
echo "3 or more digits:"
grep -E '^[0-9]{3,}$' bytes.txt
echo "3 digits, no anchors:"
grep -E '[0-9]{3}' bytes.txt
```
```output
exactly 3 digits:
512
2 to 3 digits:
64
512
3 or more digits:
512
2048
3 digits, no anchors:
512
2048
```

Without anchors, a pattern matches part of a longer number too.

<!-- challenge id=c2 objective=2 -->
> **Challenge c2:** Open [`challenges/c2.sh`](challenges/c2.sh) and make it
> print the requests in LOGFILE, its first argument, that sent 1000 bytes
> or more. A request whose bytes field is `1024` is printed; one with
> `999` is not, even when its path is `/reports/2026.html`. Check it with
> `learn check c2`.

## Leaving lines out and ignoring case

`-v` inverts the match: grep prints every line that doesn't match. With
`-c` as well, it counts those lines. `-i` ignores case. ([tlcl#grep])
Options combine, also with `-E`:

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /Admin 403 64" >> access.log
echo "2026-10-06T10:16:02 192.0.2.44 GET /ADMIN/users 403 64" >> access.log
echo "2026-10-06T10:16:20 192.0.2.44 GET /admin 200 2048" >> access.log
echo "-i:"
grep -i ' /admin' access.log
echo "-v:"
grep -v ' 200 ' access.log
echo "-v -c -E:"
grep -v -c -E ' 2[0-9]{2} ' access.log
```
```output
-i:
2026-10-06T10:15:40 198.51.100.7 GET /Admin 403 64
2026-10-06T10:16:02 192.0.2.44 GET /ADMIN/users 403 64
2026-10-06T10:16:20 192.0.2.44 GET /admin 200 2048
-v:
2026-10-06T10:15:40 198.51.100.7 GET /Admin 403 64
2026-10-06T10:16:02 192.0.2.44 GET /ADMIN/users 403 64
-v -c -E:
2
```

<!-- challenge id=c3 objective=4 -->
> **Challenge c3:** Open [`challenges/c3.sh`](challenges/c3.sh) and make it
> print every request in LOGFILE, its first argument, except those for
> the path `/health`, in any mix of upper- and lowercase: `/health`,
> `/Health` and `/HEALTH` are left out, `/healthz` and `/api/health` are
> printed. Check it with
> `learn check c3`.

## Alternatives and groups

In `(GET|HEAD) /index\.html`, `|` separates two alternatives, so the
pattern matches a GET or a HEAD request for `/index.html`. ([tlcl#alternation])
The parentheses keep the alternatives inside them; without them, `|`
splits the whole pattern. ([tlcl#alternation]) Without `-E`, `|` is a
plain character, and without quotes the shell reads it as a
pipe. ([tlcl#alternation]) ([tlcl#posix-basic-vs-extended-regular-expressions])

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 HEAD /index.html 200 0" >> access.log
echo "2026-10-06T10:16:20 192.0.2.44 GET /logo.png 200 4096" >> access.log
echo "without ( ):"
grep -E ' GET|HEAD /index\.html' access.log
echo "with ( ):"
grep -E ' (GET|HEAD) /index\.html' access.log
```
```output
without ( ):
2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
2026-10-06T10:15:40 198.51.100.7 HEAD /index.html 200 0
2026-10-06T10:16:20 192.0.2.44 GET /logo.png 200 4096
with ( ):
2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
2026-10-06T10:15:40 198.51.100.7 HEAD /index.html 200 0
```

Without parentheses, the alternatives are ` GET` and
`HEAD /index\.html`, and every GET request holds ` GET`.

Fields are separated by single spaces, so a space after a group marks the
end of the path:

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /logo.png 200 4096" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /logo.png.bak 404 153" >> access.log
echo "2026-10-06T10:16:02 192.0.2.44 GET /png 404 153" >> access.log
echo "2026-10-06T10:16:20 192.0.2.44 GET /photo.jpg 200 8192" >> access.log
grep -E '\.(png|jpg) ' access.log
```
```output
2026-10-06T10:15:32 203.0.113.5 GET /logo.png 200 4096
2026-10-06T10:16:20 192.0.2.44 GET /photo.jpg 200 8192
```

A group counts as one element, so a quantifier after it repeats the whole
group. ([tlcl#match-an-element-one-or-more-times])
Here `([0-9]{1,3}\.){3}` is three numbers, each followed by a dot:

```bash run
echo "203.0.113.5" > ips.txt
echo "198.51.100" >> ips.txt
echo "192.0.2.4444" >> ips.txt
grep -E '^([0-9]{1,3}\.){3}[0-9]{1,3}$' ips.txt
```
```output
203.0.113.5
```

<!-- challenge id=c4 objective=3 -->
> **Challenge c4:** Open [`challenges/c4.sh`](challenges/c4.sh) and make it
> print the requests in LOGFILE whose path is `/admin` or `/login`, or
> starts with `/admin/` or `/login/`. `/admin/users` and `/login/reset`
> count; `/administrator`, `/login.php` and `/api/login` don't. Check it
> with `learn check c4`.

## What's next

- **Exercise:** write [`exercise/suspicious.sh`](exercise/suspicious.sh),
  logkit's seventh tool, then run `learn check`. [`exercise/notfound.sh`](exercise/notfound.sh),
  [`exercise/count.sh`](exercise/count.sh),
  [`exercise/countall.sh`](exercise/countall.sh),
  [`exercise/healthcheck.sh`](exercise/healthcheck.sh),
  [`exercise/summary.sh`](exercise/summary.sh) and
  [`exercise/top.sh`](exercise/top.sh) are the finished tools from
  modules 1 to 6; leave them unchanged.
- **Quiz:** run `learn quiz`.
- **Recap:** read [`recap.md`](recap.md).

[tlcl#what-are-regular-expressions]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=291 "The Linux Command Line, 19 Regular Expressions: What are Regular Expressions?"
[tlcl#grep]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=291 "The Linux Command Line, 19 Regular Expressions: grep"
[tlcl#metacharacters-and-literals]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=294 "The Linux Command Line, 19 Regular Expressions: Metacharacters and Literals"
[tlcl#the-any-character]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=294 "The Linux Command Line, 19 Regular Expressions: The Any Character"
[tlcl#anchors]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=295 "The Linux Command Line, 19 Regular Expressions: Anchors"
[tlcl#bracket-expressions-and-character-classes]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=296 "The Linux Command Line, 19 Regular Expressions: Bracket Expressions and Character Classes"
[tlcl#negation]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=297 "The Linux Command Line, 19 Regular Expressions: Bracket Expressions and Character Classes: Negation"
[tlcl#posix-character-classes]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=298 "The Linux Command Line, 19 Regular Expressions: Bracket Expressions and Character Classes: POSIX Character Classes"
[tlcl#posix-basic-vs-extended-regular-expressions]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=302 "The Linux Command Line, 19 Regular Expressions: POSIX Basic vs. Extended Regular Expressions"
[tlcl#alternation]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=303 "The Linux Command Line, 19 Regular Expressions: Alternation"
[tlcl#quantifiers]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=304 "The Linux Command Line, 19 Regular Expressions: Quantifiers"
[tlcl#match-an-element-zero-or-one-time]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=304 "The Linux Command Line, 19 Regular Expressions: Quantifiers: ? Match an Element Zero or One Time"
[tlcl#match-an-element-zero-or-more-times]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=305 "The Linux Command Line, 19 Regular Expressions: Quantifiers: * Match an Element Zero or More Times"
[tlcl#match-an-element-one-or-more-times]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=306 "The Linux Command Line, 19 Regular Expressions: Quantifiers: + Match an Element One or More Times"
[tlcl#match-an-element-a-specific-number-of-times]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=306 "The Linux Command Line, 19 Regular Expressions: Quantifiers: { } Match an Element a Specific Number of Times"
