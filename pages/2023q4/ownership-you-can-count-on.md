+++
published = 2023-12-20
description = "The never (academically) cited 2007 memory management paper that's had more influence than you might expect"
+++

# Ownership you can count on

## Introduction
I came across the paper [Ownership You Can Count
On](https://web.archive.org/web/20220111001720/https://researcher.watson.ibm.com/researcher/files/us-bacon/Dingle07Ownership.pdf)
(by Adam Dingle and David F. Bacon, seemingly written in 2007) some years ago
and it stuck with me as being an interesting variant on traditional reference
counting. Since then I've come across references to it multiple times in the
programming language design and implementation community and thought it might
be worth jotting down some notes on the paper itself and the various attempts
to adopt its ideas.

## Ownership you can count on and the Gel language

The basic idea is very straight-forward. Introduce the idea of an owning
pointer type (not dissimilar to `std::unique_ptr` in C++) where each object
may have only a single owning pointer and the object is freed when that
pointer goes out of scope. In addition to that allow an arbitrary number of
non-owning pointers to the object, but require that all non-owning pointers
have been destroyed by the time the object is freed. This requirement
prevents use-after-free and is implemented using run-time checks.
A reference count is incremented or decremented whenever a non-owning pointer
is created or destroyed (referred to as alias counting in the paper). That
count is checked when the object is freed and if it still has non-owning
references (i.e. the count is non-zero), then the program exits with an error.

Contrast this with a conventional reference counting system, where objects are
freed when their refcount reaches zero. In the alias counting scheme, the
refcount stored on the object is simply decremented when a non-owning
reference goes out of scope, and this refcount needs to be compared to 0 only
upon the owning pointer going out of scope rather than upon every decrement
(as an object is never freed as a result of the non-owning pointer count
reaching zero). Additionally, refcount manipulation is never needed when
passing around the owning pointer. The paper also describes an analysis
that allows many refcount operations to be elided in regions where there
aren't modifications to owned pointers of the owned object's
subclass/class/superclass (which guarantees the pointed-to object can't be
destructed in this region). The paper also claims support for destroying data
structures with pointer cycles that can't be automatically destroyed with
traditional reference counting. The authors suggest for cases where you might
otherwise reach for multiple ownership, (e.g. an arbitrary graph) to allocate
an array of owning pointers to hold your nodes, then use non-owning pointers
between them.

The paper describes a C# derived language called Gel which only requires two
additional syntactic constructs to support the alias counting model: owned
pointers indicated by a `^` (e.g. `Foo ^f = new Foo();` and a `take` operator
to take ownership of a value from an owning field. Non-owning pointers are
written just as `Foo f`. They also achieve a rather neat _erasure_
property, whereby if you take a Gel program and remove all `^` and `take`
you'll have a C# program that is valid as long as the original Gel program was
valid.

That all sounds pretty great, right? Does this mean we can have it all: full
memory safety, deterministic destruction, low runtime and annotation overhead? As you'd
expect, there are some challenges:

* The usability in practice is going to depend a lot on how easy it is for a
  programmer to maintain the invariant that no unowned pointers outlive the
  owned pointer, especially as failure to do so results in a runtime crash.
  * Several languages have looked at integrating the idea, so there's some
    information later in this article on their experiences.
* Although data structures with pointer cycles that couldn't be automatically
  destroyed by reference counting an be handled, there are also significant
  limitations. Gel can't destroy graphs containing non-owning pointers to
  non-ancestor nodes unless the programmer writes logic to null out those
  pointers. This could be frustrating and error-prone to handle.
  * The authors present a multi-phase object destruction mechanism aiming to
    address these limitations, though the cost (potentially recursively
    descending the graph of the ownership tree 3 times) depends on how much
    can be optimised away.
* Although it's not a fundamental limitation of the approach, Gel doesn't yet
  provide any kind of polymorphism between owned and unowned references. This
  would be necessary for any modern language with support for generics.
* The reference count elimination optimisation described in the paper assumes
  single-threaded execution.
  * Though as noted there, thread escape analysis or structuring groups of
    objects into independent regions (also see [recent work on
    Verona](https://dl.acm.org/doi/10.1145/3622846)) could provide a solution.

So in summary, an interesting idea that is meaningfully different to
traditional reference counting, but the largest program written using this
scheme is the Gel compiler itself and many of the obvious questions require
larger scale usage to judge the practicality of the scheme.

## Influence and adoption of the paper's ideas

Ownership You Can Count On was written around 2007 and as far as I can tell
never published in the proceedings of a conference or workshop, or in a
journal. Flicking through the [Gel language
repository](https://code.google.com/archive/p/gel2/source/default/source) and
applying some world-class logical deduction based on the directory name
holding a draft version of the paper leads to me suspect it was submitted to
PLDI though. Surprisingly it has no academic citations, despite being shared
publicly on David F. Bacon's site (and Bacon has a range of widely cited
papers related to reference counting / garbage collection). Yet, the work
has been used as the basis for memory management in one language
([Inko](https://inko-lang.org/)) and was seriously evaluated (partially
implemented?) for both [Nim](https://nim-lang.org/) and
[Vale](https://vale.dev/).

Inko started out with a garbage collector, but its creator Yorick Peterse
announced in 2021 [a plan to adopt the scheme from Ownership You Can Count
on](https://yorickpeterse.com/articles/friendship-ended-with-the-garbage-collector/),
who then [left his job to work on Inko
full-time](https://yorickpeterse.com/articles/im-leaving-gitlab-to-work-on-inko-full-time/)
and [successfully transitioned to the new memory management scheme in the
Inko 0.10.0
release](https://inko-lang.org/news/inko-0-10-0-released/#header-what-happened-since-the-last-release)
about a year later. Inko as a language is more ambitious than Gel - featuring
parametric polymorphism, lightweight processes for concurrency, and more. Yet
it's still early days and it's not yet, for instance, good for drawing
conclusions about performance on modern systems as [optimisations aren't
currently
applied](https://github.com/jinyus/related_post_gen/pull/440#issuecomment-1816583612).
Dusty Phillips wrote a blog post earlier this year [explaining Inko's memory
management through some example data
structures](https://dusty.phillips.codes/2023/06/26/understanding-inko-memory-management-through-data-structures/),
which also includes some thoughts on the usability of the system and some
drawbacks. Some of the issues may be more of a result of the language being
young, e.g. the author notes it took a lot of trial and error to figure out
some of the described techniques (perhaps this will be easier once common
patterns are better documented and potentially supported by library functions
or syntax?), or that debuggability is poor when the program exits with a
dangling reference error.

Nim was at one point going to move to Gel's scheme (see the [blog
post](https://nim-lang.org/araq/ownedrefs.html) and
([RFC](https://github.com/nim-lang/RFCs/issues/144)). I haven't been able to
find a detailed explanation for the reasons why it was rejected, though
Andreas Rumpf (Nim language creator) commented on a [Dlang forum discussion
thread](https://forum.dlang.org/post/ejvshljmezqovmfprkww@forum.dlang.org)
about the paper that "Nim tried to use this in production before moving to ORC
and I'm not looking back, 'ownership you can count on' was actually quite a
pain to work with...". Nim has since [adopted a more conventional non-atomic
reference counted
scheme](https://nim-lang.org/blog/2020/10/15/introduction-to-arc-orc-in-nim.html)
(ARC), with an optional cycle collector (ORC). 

Vale was [previously adopting the Gel / Ownership You Can Count On
scheme](https://verdagon.dev/blog/raii-next-steps) (calling the unowned
references "constraint references"), but has since changed path slightly and
now uses "[generational
references](https://verdagon.dev/blog/generational-references)" Rather than a
reference count, each allocation includes a generation counter which is
incremented each time it is reused. Fat pointers that include the expected
value of the generation counter are used, and checked before dereferencing. If
they don't match, that indicates the memory location was since reallocated and
the program will fault. This also puts restrictions on the allocator's
ability to reuse freed allocations without compromising safety. Vale's memory
management scheme retains similarities to Gel: the language is still based
around single ownership and this is exploited to elide checks on owning
references/pointers.

# Conclusion and other related work

Some tangentially related things that didn't make it into the main body of
text above:
* A language that references Gel in its design but goes in a slightly
  different direction is Wouter van Oortmerssen's
  [Lobster](https://strlen.com/lobster/).  Its [memory management
  scheme](https://aardappel.github.io/lobster/memory_management.html) attempts
  to infer ownership (and optimise in the case where single ownership can be
  inferred) rather than requiring single ownership like the languages listed
  above.
* One of the discussions on Ownership You Can Count On referenced this
  [Pointer Ownership
  Model](https://insights.sei.cmu.edu/documents/351/2013_019_001_55008.pdf)
  paper as having similarities. It chooses to categorise pointers as either
  "responsible" or "irresponsible" - cute!

And, that's about it. If you're hoping for a definitive answer on whether
alias counting is a winning idea or not I'm sorry to disappoint, but I've at
least succeeded in collecting together the various places I've seen it
explored and am looking forward to seeing how Inko's adoption of it evolves.
I'd be very interested to hear any experience reports of adopting alias
counting or using a language like Inko that tries to use it.

