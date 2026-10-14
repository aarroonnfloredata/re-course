---
id: wiki-code-smell
title: Code smell - Wikipedia
url: https://en.wikipedia.org/wiki/Code_smell
retrieved: 2026-10-14
license: Wikipedia, CC BY-SA 4.0
---

In [computer programming](https://en.wikipedia.org/wiki/Computer_programming "Computer programming"), a **code smell** is any characteristic of [source code](https://en.wikipedia.org/wiki/Source_code "Source code") that hints at a deeper problem. Determining what a code smell is and is not is subjective, and varies by [language](https://en.wikipedia.org/wiki/Programming_language "Programming language"), developer, and development methodology.

The term was popularized by [Kent Beck](https://en.wikipedia.org/wiki/Kent_Beck "Kent Beck") on [WardsWiki](https://en.wikipedia.org/wiki/WardsWiki "WardsWiki") in the late 1990s. Usage of the term increased after it was featured in the 1999 book *Refactoring: Improving the Design of Existing Code* by [Martin Fowler](https://en.wikipedia.org/wiki/Martin_Fowler_(software_engineer) "Martin Fowler (software engineer)"). It is also a term used by [agile](https://en.wikipedia.org/wiki/Agile_software_development "Agile software development") programmers.

## Definition {#Definition}

One way to look at smells is with respect to principles and quality: "Smells are certain structures in the code that indicate violation of fundamental design principles and negatively impact design quality". Code smells are usually not [bugs](https://en.wikipedia.org/wiki/Software_bug "Software bug"); they are not technically incorrect and do not prevent the program from functioning. Instead, they indicate weaknesses in design that may slow down development or increase the risk of bugs or failures in the future. Bad code smells can be an indicator of factors that contribute to [technical debt](https://en.wikipedia.org/wiki/Technical_debt "Technical debt"). [Robert C. Martin](https://en.wikipedia.org/wiki/Robert_C._Martin "Robert C. Martin") calls a list of code smells a "value system" for software craftsmanship.

Contrary to these severe interpretations, Cunningham's original definition was that a smell is a suggestion that something may be wrong, not evidence that there is already a problem.

Often the deeper problem hinted at by a code smell can be uncovered when the code is subjected to a short [feedback cycle](https://en.wikipedia.org/wiki/Feedback "Feedback"), where it is [refactored](https://en.wikipedia.org/wiki/Code_refactoring "Code refactoring") in small, controlled steps, and the resulting design is examined to see if there are any further code smells that in turn indicate the need for more refactoring. From the point of view of a programmer charged with performing refactoring, code smells are [heuristics](https://en.wikipedia.org/wiki/Heuristic_(computer_science) "Heuristic (computer science)") to indicate when to refactor, and what specific refactoring techniques to use. Thus, a code smell is a driver for refactoring.

Factors such as the understandability of code, how easy it is to be modified, the ease in which it can be enhanced to support functional changes, the code's ability to be reused in different settings, how testable the code is, and code reliability are factors that can be used to identify code smells.

A 2015 study utilizing automated analysis for half a million source code [commits](https://en.wikipedia.org/wiki/Commit_(version_control) "Commit (version control)") and the manual examination of 9,164 commits determined to exhibit "code smells" found that:

- There exists empirical evidence for the consequences of "technical debt", but there exists only anecdotal evidence as to *how*, *when*, or *why* this occurs.
- Common wisdom suggests that urgent maintenance activities and pressure to deliver features while prioritizing time-to-market over code quality are often the causes of such smells.

Tools such as [Checkstyle](https://en.wikipedia.org/wiki/Checkstyle "Checkstyle"), [PMD](https://en.wikipedia.org/wiki/PMD_(software) "PMD (software)"), [FindBugs](https://en.wikipedia.org/wiki/FindBugs "FindBugs"), and [SonarQube](https://en.wikipedia.org/wiki/SonarQube "SonarQube") can automatically identify code smells.

## Examples {#Examples}

|  |  |
| --- | --- |
|  | This section **may contain [original research](https://en.wikipedia.org/wiki/Wikipedia:No_original_research "Wikipedia:No original research")**. Please [improve it](https://en.wikipedia.org/w/index.php?title=Code_smell&action=edit) by [verifying](https://en.wikipedia.org/wiki/Wikipedia:Verifiability "Wikipedia:Verifiability") the claims made and adding [inline citations](https://en.wikipedia.org/wiki/Wikipedia:Citing_sources#Inline_citations "Wikipedia:Citing sources"). Statements consisting only of original research should be removed. *(May 2020)* *([Learn how and when to remove this message](https://en.wikipedia.org/wiki/Help:Maintenance_template_removal "Help:Maintenance template removal"))* |

### Application-level smells {#Application-level_smells}

[Duplicated code](https://en.wikipedia.org/wiki/Duplicate_code "Duplicate code")
:   identical or very similar code that exists in more than one location.

[Shotgun surgery](https://en.wikipedia.org/wiki/Shotgun_surgery "Shotgun surgery")
:   a single change that needs to be applied to multiple classes at the same time.[*[citation needed](https://en.wikipedia.org/wiki/Wikipedia:Citation_needed "Wikipedia:Citation needed")*]

### Class-level smells {#Class-level_smells}

Large class, a.k.a. [god object](https://en.wikipedia.org/wiki/God_object "God object")
:   a [class](https://en.wikipedia.org/wiki/Class_(computer_science) "Class (computer science)") that contains too many types or contains many unrelated methods.[*[citation needed](https://en.wikipedia.org/wiki/Wikipedia:Citation_needed "Wikipedia:Citation needed")*]

Refused bequest
:   a class that [overrides](https://en.wikipedia.org/wiki/Method_overriding_(programming) "Method overriding (programming)") a method of a base class in such a way that the [contract](https://en.wikipedia.org/wiki/Contract_(software) "Contract (software)") of the [base class](https://en.wikipedia.org/wiki/Base_class "Base class") is not honored by the [derived class](https://en.wikipedia.org/wiki/Derived_class "Derived class"), violating the [Liskov substitution principle](https://en.wikipedia.org/wiki/Liskov_substitution_principle "Liskov substitution principle").[*[citation needed](https://en.wikipedia.org/wiki/Wikipedia:Citation_needed "Wikipedia:Citation needed")*]

Excessive use of literals or [magic numbers](https://en.wikipedia.org/wiki/Magic_number_(programming) "Magic number (programming)")
:   these should be coded as named constants, to improve readability and to avoid programming errors. Additionally, [literals](https://en.wikipedia.org/wiki/Literal_(computer_programming) "Literal (computer programming)") can and should be externalized into resource files/scripts, or other data stores such as databases where possible, to facilitate localization of software if it is intended to be deployed in different regions.[*[self-published source](https://en.wikipedia.org/wiki/Wikipedia:Verifiability#Self-published_sources "Wikipedia:Verifiability")*]

[Downcasting](https://en.wikipedia.org/wiki/Downcasting "Downcasting")
:   a type cast which breaks the abstraction model; the abstraction may have to be refactored or eliminated.[*[self-published source](https://en.wikipedia.org/wiki/Wikipedia:Verifiability#Self-published_sources "Wikipedia:Verifiability")*]

[Data clump](https://en.wikipedia.org/wiki/Data_Clump_(Code_Smell) "Data Clump (Code Smell)")
:   Occurs when a group of variables are passed around together in various parts of the program. In general, this suggests that it would be more appropriate to formally group the different variables together into a single object, and pass around only the new object instead.[*[unreliable source?](https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources "Wikipedia:Reliable sources")*]

### Method-level smells {#Method-level_smells}

Too many parameters
:   a long list of parameters is hard to read, and makes calling and testing the function complicated. It may indicate that the purpose of the function is ill-conceived and that the code should be refactored so responsibility is assigned in a more clean-cut way.[*[self-published source](https://en.wikipedia.org/wiki/Wikipedia:Verifiability#Self-published_sources "Wikipedia:Verifiability")*]

## See also {#See_also}

- [Anti-pattern](https://en.wikipedia.org/wiki/Anti-pattern "Anti-pattern") – Solution to a problem that may be commonly used but is generally a bad choice
- [Design smell](https://en.wikipedia.org/wiki/Design_smell "Design smell") – Term in computer programming
- [List of tools for static code analysis](https://en.wikipedia.org/wiki/List_of_tools_for_static_code_analysis "List of tools for static code analysis")
- [Software rot](https://en.wikipedia.org/wiki/Software_rot "Software rot") – Degradation or loss of the use of software over time

## References {#References}

## Further reading {#Further_reading}

- Garousi, Vahid; Küçük, Barış (2018). "Smells in software test code: A survey of knowledge in industry and academia". *Journal of Systems and Software*. **138**: 52–81. [doi](https://en.wikipedia.org/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/j.jss.2017.12.013](https://doi.org/10.1016%2Fj.jss.2017.12.013).
- Sharma, Tushar; [Spinellis, Diomidis](https://en.wikipedia.org/wiki/Diomidis_Spinellis "Diomidis Spinellis") (2018). ["A survey on software smells"](https://zenodo.org/record/1997449). *Journal of Systems and Software*. **138**: 158–173. [doi](https://en.wikipedia.org/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/j.jss.2017.12.034](https://doi.org/10.1016%2Fj.jss.2017.12.034).

## External links {#External_links}

- ["CodeSmell"](https://martinfowler.com/bliki/CodeSmell.html). *martinfowler.com*. Retrieved 2022-03-01.
- Boundy, David, [Software cancer: the seven early warning signs](http://dl.acm.org/citation.cfm?id=156632) or [here](https://www.academia.edu/2303865/Software_cancer_the_seven_early_warning_signs), ACM SIGSOFT Software Engineering Notes, Vol. 18 No. 2 (April 1993), Association for Computing Machinery, New York, NY, USA

Retrieved from "<https://en.wikipedia.org/w/index.php?title=Code_smell&oldid=1379558939>"
