---
id: wiki-refactoring
title: Code refactoring - Wikipedia
url: https://en.wikipedia.org/wiki/Code_refactoring
retrieved: 2026-10-14
license: Wikipedia, CC BY-SA 4.0
---

In [computer programming](https://en.wikipedia.org/wiki/Computer_programming "Computer programming") and [software design](https://en.wikipedia.org/wiki/Software_design "Software design"), **code refactoring** is the process of restructuring existing [source code](https://en.wikipedia.org/wiki/Source_code "Source code")—changing the *[factoring](https://en.wikipedia.org/wiki/Decomposition_(computer_science) "Decomposition (computer science)")*—without changing its external behavior. Refactoring is intended to improve the design, structure, or implementation of the [software](https://en.wikipedia.org/wiki/Software "Software") (its *[non-functional](https://en.wikipedia.org/wiki/Non-functional_requirement "Non-functional requirement")* attributes), while preserving its [functionality](https://en.wikipedia.org/wiki/Functional_requirement "Functional requirement"). Potential advantages of refactoring may include improved code [readability](https://en.wikipedia.org/wiki/Readability "Readability") and reduced [complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity "Cyclomatic complexity"); these can improve the source code's [maintainability](https://en.wikipedia.org/wiki/Maintainability "Maintainability") and create a simpler, cleaner, or more expressive internal [architecture](https://en.wikipedia.org/wiki/Software_architecture "Software architecture") or [object model](https://en.wikipedia.org/wiki/Object_model "Object model") to improve [extensibility](https://en.wikipedia.org/wiki/Extensibility "Extensibility"). Another potential goal for refactoring is improved performance; software engineers face an ongoing challenge to write programs that perform faster or use less memory. Despite the availability of metrics intended to assess such attributes, developers often do not rely on them when making refactoring decisions due to concerns about its practical usefulness.

Typically, refactoring applies a series of standardized basic *micro-refactorings*, each of which is (usually) a tiny change in a computer program's source code that either preserves the behavior of the software, or at least does not modify its conformance to functional requirements. Many [development environments](https://en.wikipedia.org/wiki/Development_environment_(software_development_process) "Development environment (software development process)") provide automated support for performing the mechanical aspects of these basic refactorings. If done well, code refactoring may help software developers discover and fix hidden or dormant [bugs](https://en.wikipedia.org/wiki/Software_bug "Software bug") or [vulnerabilities](https://en.wikipedia.org/wiki/Vulnerability_(computing) "Vulnerability (computing)") in the system by simplifying the underlying logic and eliminating unnecessary levels of complexity. If done poorly, it may fail the requirement that external functionality not be changed, and may thus introduce new bugs.

> By continuously improving the design of code, we make it easier and easier to work with. This is in sharp contrast to what typically happens: little refactoring and a great deal of attention paid to expediently add new features. If you get into the hygienic habit of refactoring continuously, you'll find that it is easier to extend and maintain code.

— Joshua Kerievsky, *Refactoring to Patterns*

## Motivation {#Motivation}

Refactoring is usually motivated by noticing a [code smell](https://en.wikipedia.org/wiki/Code_smell "Code smell"). For example, the method at hand may be very long, or it may be a near [duplicate](https://en.wikipedia.org/wiki/Duplicate_code "Duplicate code") of another nearby method. Once recognized, such problems can be addressed by *refactoring* the source code, or transforming it into a new form that behaves the same as before but that no longer "smells".

For a long routine, one or more smaller subroutines can be extracted. For duplicate routines, the duplication can be removed and replaced with one shared function. Failure to perform refactoring can result in accumulating [technical debt](https://en.wikipedia.org/wiki/Technical_debt "Technical debt"); on the other hand, refactoring is one of the primary means of repaying technical debt.

## Benefits {#Benefits}

There are two general categories of benefits to the activity of refactoring.

1. [Maintainability](https://en.wikipedia.org/wiki/Maintainability "Maintainability"). It is easier to fix bugs because the source code is easy to read and the intent of its author is easy to grasp. This might be achieved by reducing large monolithic routines into a set of individually concise, well-named, single-purpose methods. It might be achieved by moving a method to a more appropriate class or by removing misleading comments.
2. [Extensibility](https://en.wikipedia.org/wiki/Extensibility "Extensibility"). It is easier to extend the capabilities of the application if it uses recognizable [design patterns](https://en.wikipedia.org/wiki/Design_pattern_(computer_science) "Design pattern (computer science)"), and it provides some flexibility where none before may have existed.

[Performance engineering](https://en.wikipedia.org/wiki/Performance_engineering "Performance engineering") can remove inefficiencies in programs, known as software bloat, arising from traditional software-development strategies that aim to minimize an application's development time rather than the time it takes to run. Performance engineering can also tailor [software](https://en.wikipedia.org/wiki/Software "Software") to the [hardware](https://en.wikipedia.org/wiki/Hardware_security_module "Hardware security module") on which it runs, for example, to take advantage of parallel processors and vector units.

## Timing and responsibility {#Timing_and_responsibility}

There are two possible times for refactoring.

1. Preventive refactoring – the original developer of the code makes the code more robust when it is still free of [smells](https://en.wikipedia.org/wiki/Code_smell "Code smell") to prevent the formation of smells in the future.
2. Corrective refactoring – a subsequent developer performs refactoring to correct [code smells](https://en.wikipedia.org/wiki/Code_smell "Code smell") as they occur.

A method that balances preventive and corrective refactoring is "shared responsibility for refactoring".
This approach splits the refactoring action into two stages and two
roles. The original developer of the code just prepares the code for refactoring, and when the [code smells](https://en.wikipedia.org/wiki/Code_smell "Code smell") form, a subsequent developer carries out the actual refactoring action.

## Challenges {#Challenges}

Refactoring requires extracting the software system structure, data models, and intra-application dependencies to get back knowledge of an existing software system.
The turnover of teams implies missing or inaccurate knowledge of the current state of a system and about design decisions made by departing developers. Further code refactoring activities may require additional effort to regain this knowledge.
Refactoring activities generate architectural modifications that deteriorate the structural architecture of a software system. Such deterioration affects architectural properties such as maintainability and comprehensibility, which can lead to a complete re-development of software systems.

## Testing {#Testing}

Automatic [unit tests](https://en.wikipedia.org/wiki/Unit_tests "Unit tests") should be set up before refactoring to ensure routines still behave as expected. Unit tests can bring stability to even large refactors when performed with a single [atomic commit](https://en.wikipedia.org/wiki/Atomic_commit#Revision_control "Atomic commit"). A common strategy to allow safe and atomic refactors spanning multiple projects is to store all projects in a single [repository](https://en.wikipedia.org/wiki/Repository_(version_control) "Repository (version control)"), known as [monorepo](https://en.wikipedia.org/wiki/Monorepo "Monorepo").

With unit testing in place, refactoring is then an iterative cycle of making a small [program transformation](https://en.wikipedia.org/wiki/Program_transformation "Program transformation"), testing it to ensure correctness, and making another small transformation. If at any point a test fails, the last small change is undone and repeated in a different way. Through many small steps the program moves from where it was to where you want it to be. For this very iterative process to be practical, the tests must run very quickly, or the programmer would have to spend a large fraction of their time waiting for the tests to finish. Proponents of [extreme programming](https://en.wikipedia.org/wiki/Extreme_programming "Extreme programming") and other [agile software development](https://en.wikipedia.org/wiki/Agile_software_development "Agile software development") describe this activity as an integral part of the [software development cycle](https://en.wikipedia.org/wiki/Software_development_cycle "Software development cycle"). Refactoring applies to [test code](https://en.wikipedia.org/wiki/Test_code?action=edit&redlink=1 "Test code (page does not exist)") as well as production code; empirical studies show that test refactoring primarily targets low-quality test code exhibiting [test smells](https://en.wikipedia.org/wiki/Test_smell?action=edit&redlink=1 "Test smell (page does not exist)"), and improves test code coupling, cohesion, and size, though it does not necessarily improve code coverage.

## Techniques {#Techniques}

Here are some examples of micro-refactorings; some of these may only apply to certain languages or language types. A longer list can be found in [Martin Fowler](https://en.wikipedia.org/wiki/Martin_Fowler_(software_engineer) "Martin Fowler (software engineer)")'s refactoring book[*[page needed](https://en.wikipedia.org/wiki/Wikipedia:Citing_sources "Wikipedia:Citing sources")*] and website. Many development environments provide automated support for these micro-refactorings. For instance, a programmer could click on the name of a variable and then select the "Encapsulate field" refactoring from a [context menu](https://en.wikipedia.org/wiki/Context_menu "Context menu"). The IDE would then prompt for additional details, typically with sensible defaults and a preview of the code changes. After confirmation by the programmer, it would carry out the required changes throughout the code.

### Static analysis {#Static_analysis}

[Static program analysis](https://en.wikipedia.org/wiki/Static_program_analysis "Static program analysis") (called "linting" when performed on less strict interpreted languages) detects problems in a valid but substandard program.

- [Program dependence graph](https://en.wikipedia.org/wiki/Program_dependence_graph "Program dependence graph") - explicit representation of data and control dependencies
- System dependence graph - representation of procedure calls between PDG
- [Cyclometric complexity](https://en.wikipedia.org/wiki/Cyclometric_complexity "Cyclometric complexity") analysis.
- [Software intelligence](https://en.wikipedia.org/wiki/Software_intelligence "Software intelligence") - reverse engineers the initial state to understand existing intra-application dependencies

### Transformations {#Transformations}

Transformations modify the syntactic representation of a program. Some modifications alter the semantics or structure of the program in a way that improves its flexibility or robustness. Such modifications require knowledge of the problem domain and intended logic, and thus are infeasible to automate. Modifications exist that make the program easier to read and modify, but which do not alter the underlying logic of the program; these transformations can be automated.

- Techniques that allow for more [abstraction](https://en.wikipedia.org/wiki/Abstraction_(computer_science) "Abstraction (computer science)")
  - [Encapsulate field](https://en.wikipedia.org/wiki/Field_encapsulation "Field encapsulation") – force code to access the field with getter and setter methods
  - [Generalize type](https://en.wikipedia.org/wiki/Type_generalization "Type generalization") – create more general types to allow for more code sharing
  - Replace type-checking code with state/strategy
  - Replace conditional with [polymorphism](https://en.wikipedia.org/wiki/Polymorphism_(computer_science) "Polymorphism (computer science)")
- Techniques for breaking code apart into more logical pieces
  - Componentization breaks code down into reusable semantic units that present clear, well-defined, simple-to-use interfaces.
  - [Extract class](https://en.wikipedia.org/wiki/Extract_class "Extract class") moves part of the code from an existing class into a new class.
  - Extract method, to turn part of a larger [method](https://en.wikipedia.org/wiki/Method_(computer_science) "Method (computer science)") into a new method. By breaking down code in smaller pieces, it is more easily understandable. This is also applicable to [functions](https://en.wikipedia.org/wiki/Function_(programming) "Function (programming)").
- Techniques for improving names and location of code
  - Move method or move field – move to a more appropriate [class](https://en.wikipedia.org/wiki/Class_(programming) "Class (programming)") or source file
  - Rename method or rename field – changing the name into a new one that better reveals its purpose
  - Pull up – in [object-oriented programming](https://en.wikipedia.org/wiki/Object-oriented_programming "Object-oriented programming") (OOP), move to a [superclass](https://en.wikipedia.org/wiki/Superclass_(computer_science) "Superclass (computer science)")
  - Push down – in OOP, move to a [subclass](https://en.wikipedia.org/wiki/Subclass_(computer_science) "Subclass (computer science)")
- Automatic [clone detection](https://en.wikipedia.org/wiki/Clone_detection "Clone detection")

## Hardware refactoring {#Hardware_refactoring}

While the term *refactoring* originally referred exclusively to refactoring of software code, in recent years code written in [hardware description languages](https://en.wikipedia.org/wiki/Hardware_description_language "Hardware description language") has also been refactored. The term *hardware refactoring* is used as a shorthand term for refactoring of code in hardware description languages. Since hardware description languages are not considered to be [programming languages](https://en.wikipedia.org/wiki/Programming_language "Programming language") by most hardware engineers, hardware refactoring is to be considered a separate field from traditional code refactoring.

Automated refactoring of analog hardware descriptions (in [VHDL-AMS](https://en.wikipedia.org/wiki/VHDL-AMS "VHDL-AMS")) has been proposed by Zeng and Huss. In their approach, refactoring preserves the simulated behavior of a hardware design. The non-functional measurement that improves is that refactored code can be processed by standard synthesis tools, while the original code cannot. Refactoring of digital hardware description languages, albeit manual refactoring, has also been investigated by [Synopsys](https://en.wikipedia.org/wiki/Synopsys "Synopsys") [fellow](https://en.wikipedia.org/wiki/Fellow "Fellow") Mike Keating. His target is to make complex systems easier to understand, which increases the designers' productivity.

## History {#History}

The terms "factoring" and "factoring out" have been used in the [Forth](https://en.wikipedia.org/wiki/Forth_(programming_language) "Forth (programming language)") programming language community since at least the early 1980s. Chapter Six of [Leo Brodie](https://en.wikipedia.org/wiki/Leo_Brodie_(programmer)?action=edit&redlink=1 "Leo Brodie (programmer) (page does not exist)")'s book *[Thinking Forth](https://en.wikipedia.org/wiki/Thinking_Forth?action=edit&redlink=1 "Thinking Forth (page does not exist)")* (1984) is dedicated to the subject.

[William Opdyke](https://en.wikipedia.org/wiki/William_Opdyke "William Opdyke") and [Ralph Johnson](https://en.wikipedia.org/wiki/Ralph_Johnson_(computer_scientist) "Ralph Johnson (computer scientist)") first used the term "refactoring" in a September 1990 article.
Although refactoring code had been done informally for decades, [William Griswold](https://en.wikipedia.org/wiki/Bill_Griswold "Bill Griswold")'s 1991 Ph.D. dissertation
is one of the first major academic works on refactoring functional and procedural programs, followed by William Opdyke's 1992 dissertation
on the refactoring of object-oriented programs, although all the theory and machinery have long been available as [program transformation](https://en.wikipedia.org/wiki/Program_transformation "Program transformation") systems. All of these resources provide a catalog of common methods for refactoring; a refactoring method has a description of how to apply the [method](https://en.wikipedia.org/wiki/Scientific_method "Scientific method") and indicators for when you should (or should not) apply the method.

[Martin Fowler](https://en.wikipedia.org/wiki/Martin_Fowler_(software_engineer) "Martin Fowler (software engineer)")'s book *Refactoring: Improving the Design of Existing Code* (1999) covers the subject in-depth.

Refactorings can also be reconstructed posthoc to produce concise descriptions of complex software changes recorded in software repositories like [Git](https://en.wikipedia.org/wiki/Git "Git").

## Tools {#Tools}

|  |  |
| --- | --- |
| [icon](https://en.wikipedia.org/wiki/File:Question_book-new.svg) | This section **needs [more citations](https://en.wikipedia.org/wiki/Wikipedia:Verifiability "Wikipedia:Verifiability")**. Please help [improve this section](https://en.wikipedia.org/wiki/Special:EditPage/Code_refactoring "Special:EditPage/Code refactoring") by [adding citations to reliable sources](https://en.wikipedia.org/wiki/Help:Referencing_for_beginners "Help:Referencing for beginners"). Unsourced material may be challenged and [removed](https://en.wikipedia.org/wiki/Wikipedia:Verifiability#Burden_of_evidence "Wikipedia:Verifiability"). *(July 2018)* *([Learn how and when to remove this message](https://en.wikipedia.org/wiki/Help:Maintenance_template_removal "Help:Maintenance template removal"))* |

Many [software development tools](https://en.wikipedia.org/wiki/Software_development_tool "Software development tool") have features for refactoring. Examples include:

[Android Studio](https://en.wikipedia.org/wiki/Android_Studio "Android Studio")
:   Supports refactoring Java and C++.

[AppCode](https://en.wikipedia.org/wiki/AppCode "AppCode")
:   Supports refactoring [Objective-C](https://en.wikipedia.org/wiki/Objective-C "Objective-C"), C and C++.

[Delphi](https://en.wikipedia.org/wiki/Delphi_(software) "Delphi (software)")
:   Supports refactoring [Object Pascal](https://en.wikipedia.org/wiki/Object_Pascal "Object Pascal").

[DMS Software Reengineering Toolkit](https://en.wikipedia.org/wiki/DMS_Software_Reengineering_Toolkit "DMS Software Reengineering Toolkit")
:   Supports large-scale refactoring for [C](https://en.wikipedia.org/wiki/C_(programming_language) "C (programming language)"), [C++](https://en.wikipedia.org/wiki/C++ "C++"), [C#](https://en.wikipedia.org/wiki/C_Sharp_(programming_language) "C Sharp (programming language)"), [COBOL](https://en.wikipedia.org/wiki/COBOL "COBOL"), [Java](https://en.wikipedia.org/wiki/Java_(programming_language) "Java (programming language)"), [PHP](https://en.wikipedia.org/wiki/PHP "PHP") and other languages.

[Eclipse](https://en.wikipedia.org/wiki/Eclipse_(software) "Eclipse (software)")
:   Via plugins, supports refactoring Java and to a lesser extent C++, PHP, [Ruby](https://en.wikipedia.org/wiki/Ruby_(programming_language) "Ruby (programming language)") and [JavaScript](https://en.wikipedia.org/wiki/JavaScript "JavaScript")

[IntelliJ IDEA](https://en.wikipedia.org/wiki/IntelliJ_IDEA "IntelliJ IDEA")
:   Supports refactoring Java.

[JDeveloper](https://en.wikipedia.org/wiki/JDeveloper "JDeveloper")
:   Supports refactoring Java.

[NetBeans](https://en.wikipedia.org/wiki/NetBeans "NetBeans")
:   Supports refactoring Java.

[PhpStorm](https://en.wikipedia.org/wiki/PhpStorm "PhpStorm")
:   Supports refactoring PHP.

[PyCharm](https://en.wikipedia.org/wiki/PyCharm "PyCharm")
:   Supports refactoring Python.

[PyDev](https://en.wikipedia.org/wiki/PyDev "PyDev")
:   Supports refactoring [Python](https://en.wikipedia.org/wiki/Python_(programming_language) "Python (programming language)").

[Smalltalk](https://en.wikipedia.org/wiki/Smalltalk "Smalltalk")
:   Most dialects include powerful refactoring tools. Many use the original refactoring browser produced in the early '90s by [Ralph Johnson](https://en.wikipedia.org/wiki/Ralph_Johnson_(computer_scientist) "Ralph Johnson (computer scientist)").

[Visual Assist](https://en.wikipedia.org/wiki/Visual_Assist "Visual Assist")
:   Supports refactoring C# and C++.

[Visual Studio](https://en.wikipedia.org/wiki/Visual_Studio "Visual Studio")
:   Supports refactoring [.NET](https://en.wikipedia.org/wiki/.NET ".NET") and C++.

[Visual Studio Code](https://en.wikipedia.org/wiki/Visual_Studio_Code "Visual Studio Code")
:   Supports refactoring many languages via plugins

[WebStorm](https://en.wikipedia.org/wiki/WebStorm "WebStorm")
:   Supports refactoring JavaScript.

[Wing IDE](https://en.wikipedia.org/wiki/Wing_IDE "Wing IDE")
:   Supports refactoring Python.

[Xcode](https://en.wikipedia.org/wiki/Xcode "Xcode")
:   Supports refactoring C, Objective-C, and [Swift](https://en.wikipedia.org/wiki/Swift_(programming_language) "Swift (programming language)").

[Qt Creator](https://en.wikipedia.org/wiki/Qt_Creator "Qt Creator")
:   Supports refactoring C++, Objective-C and [QML](https://en.wikipedia.org/wiki/QML "QML")

## See also {#See_also}

- [Amelioration pattern](https://en.wikipedia.org/wiki/Amelioration_pattern "Amelioration pattern")
- [Code review](https://en.wikipedia.org/wiki/Code_review "Code review")
- [Database refactoring](https://en.wikipedia.org/wiki/Database_refactoring "Database refactoring")
- [Decomposition (computer science)](https://en.wikipedia.org/wiki/Decomposition_(computer_science) "Decomposition (computer science)")
- [Modular programming](https://en.wikipedia.org/wiki/Modular_programming "Modular programming")
- [Obfuscated code](https://en.wikipedia.org/wiki/Obfuscated_code "Obfuscated code")
- [Prefactoring](https://en.wikipedia.org/wiki/Prefactoring "Prefactoring")
- [Rewrite (programming)](https://en.wikipedia.org/wiki/Rewrite_(programming) "Rewrite (programming)")
- [Separation of concerns](https://en.wikipedia.org/wiki/Separation_of_concerns "Separation of concerns")
- [Software peer review](https://en.wikipedia.org/wiki/Software_peer_review "Software peer review")
- [Test-driven development](https://en.wikipedia.org/wiki/Test-driven_development "Test-driven development")

## References {#References}

## Further reading {#Further_reading}

- Wake, William C. (2003). *Refactoring Workbook*. Addison-Wesley. [ISBN](https://en.wikipedia.org/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-321-10929-3](https://en.wikipedia.org/wiki/Special:BookSources/978-0-321-10929-3 "Special:BookSources/978-0-321-10929-3").
- Mens, T.; Tourwe, T. (February 2004). ["A survey of software refactoring"](https://zenodo.org/record/848931). *IEEE Transactions on Software Engineering*. **30** (2): 126–139. [Bibcode](https://en.wikipedia.org/wiki/Bibcode_(identifier) "Bibcode (identifier)"):[2004ITSEn..30..126M](https://ui.adsabs.harvard.edu/abs/2004ITSEn..30..126M). [doi](https://en.wikipedia.org/wiki/Doi_(identifier) "Doi (identifier)"):[10.1109/tse.2004.1265817](https://doi.org/10.1109%2Ftse.2004.1265817). [ISSN](https://en.wikipedia.org/wiki/ISSN_(identifier) "ISSN (identifier)") [0098-5589](https://search.worldcat.org/issn/0098-5589). [S2CID](https://en.wikipedia.org/wiki/S2CID_(identifier) "S2CID (identifier)") [206778272](https://api.semanticscholar.org/CorpusID:206778272).
- Feathers, Michael C (2004). *Working Effectively with Legacy Code*. Prentice Hall. [ISBN](https://en.wikipedia.org/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-13-117705-5](https://en.wikipedia.org/wiki/Special:BookSources/978-0-13-117705-5 "Special:BookSources/978-0-13-117705-5").
- Kerievsky, Joshua (2004). *Refactoring To Patterns*. Addison-Wesley. [ISBN](https://en.wikipedia.org/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-321-21335-8](https://en.wikipedia.org/wiki/Special:BookSources/978-0-321-21335-8 "Special:BookSources/978-0-321-21335-8").
- Arsenovski, Danijel (2008). *Professional Refactoring in Visual Basic*. Wrox. [ISBN](https://en.wikipedia.org/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-470-17979-6](https://en.wikipedia.org/wiki/Special:BookSources/978-0-470-17979-6 "Special:BookSources/978-0-470-17979-6").
- Arsenovski, Danijel (2009). *Professional Refactoring in C# and ASP.NET*. Wrox. [ISBN](https://en.wikipedia.org/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-470-43452-9](https://en.wikipedia.org/wiki/Special:BookSources/978-0-470-43452-9 "Special:BookSources/978-0-470-43452-9").
- Ritchie, Peter (2010). *Refactoring with Visual Studio 2010*. Packt. [ISBN](https://en.wikipedia.org/wiki/ISBN_(identifier) "ISBN (identifier)") [978-1-84968-010-3](https://en.wikipedia.org/wiki/Special:BookSources/978-1-84968-010-3 "Special:BookSources/978-1-84968-010-3").

## External links {#External_links}

- [What Is Refactoring?](http://c2.com/cgi/wiki?WhatIsRefactoring) (c2.com article)
- [Martin Fowler's homepage about refactoring](http://refactoring.com/)

Retrieved from "<https://en.wikipedia.org/w/index.php?title=Code_refactoring&oldid=1374831932>"
