+++
published = 2024-05-12
description = "Why I enjoy following Carbon development and what I learned from the panel session about it at EuroLLVM this year"
+++

# Notes from the Carbon panel session at EuroLLVM 2024

Last month I had the pleasure of attending EuroLLVM which featured a panel
session on the [Carbon programming
language](https://github.com/carbon-language/carbon-lang). It was recorded and
of course we all know automated transcription can be stunningly accurate these days, yet I still
took fairly extensive notes throughout. I often take notes (or near
transcriptions) as I find it helps me process. I'm not sure whether I'm adding
any value by writing this up, or just contributing entropy but here it goes.
You should of course assume factual mistakes or odd comments are errors in my
transcription or interpretation, and if you keep an eye on the [LLVM YouTube
channel](https://www.youtube.com/@LLVMPROJ/videos) you should find the session
recording uploaded there in the coming months.

First, a bit of background on the session, Carbon, and my interest in it.
Carbon is a programming language started by Google aiming to be used in many
cases where you would currently use C++ (billed as "an experimental successor
to C++"). The [Carbon
README](https://github.com/carbon-language/carbon-lang/blob/trunk/README.md)
gives a great description of its goals and purpose, but one point I'll
highlight is that ease of interoperability with C++ is a key design
goal and constraint. The project recognises that this limits the options for
the language to such a degree that it explicitly recommends that if you are
able to make use of a modern language like Go, Swift, Kotlin, or Rust, then
you should. Carbon is intended to be there for when you need that C++
interoperability. Of course, (and as mentioned during the panel) there are
parallel [efforts to improve Rust's ability to interoperate with
C++](https://security.googleblog.com/2024/02/improving-interoperability-between-rust-and-c.html).

Whatever other benefits the Carbon project is able to deliver, I think there's
huge value in the artefacts being produced as part of the design and decision
making process so far. This has definitely been true of languages like Swift
and especially Rust, where going back through the development history there's
masses of discussion on difficult decisions e.g. (in the case of Rust) green
threads, the removal of typestate, or internal vs external iterators. The
[Swift Evolution](https://forums.swift.org/c/evolution/18) and [Rust
Internals](https://internals.rust-lang.org/) forums are still a great read,
but obviously there's little ability to revisit fundamental decisions at this
point. I try to follow Carbon's development due to a combination of its
openness, the fact it's early stage enough to be making big decisions (e.g.
[lambdas in
Carbon](https://github.com/carbon-language/carbon-lang/pull/3848)), and also
because they're exploring different design trade-offs than those other
languages (e.g. the [Carbon approach to definition-checked
generics](https://www.youtube.com/watch?v=FKC8WACSMP0)). I follow because I'm
a fan of programming language design discussion, not necessarily
because of the language itself, which may or may not turn out to be something
I'm excited to program in. As a programming language development lurker I like
to imagine I'm learning something by osmosis if nothing else - but perhaps
it's just a displacement activity...

If you want to keep up with Carbon, then [check out their recently started
newsletter](https://github.com/carbon-language/carbon-lang/discussions/categories/announcements),
issues/PRs/discussions [on
GitHub](https://github.com/carbon-language/carbon-lang) and there's a lot
going on on Discord too (I find group chat distracting so don't really follow
there). The current [Carbon
roadmap](https://github.com/carbon-language/carbon-lang/blob/trunk/docs/project/roadmap.md)
is of course worth a read too. In case I wasn't clear enough already, I have
no affiliation to the project. From where I'm standing, I'm impressed by the
way it's being designed and developed out in the open, more than (rightly or
wrongly) you might assume given the Google origin.

## Notes from the panel session

The panel "Carbon: An experiment in different tradeoffs" took place on April
11th at EuroLLVM 2024. It was moderated by Hana Dusíková and the panel members
were Chandler Carruth, Jon Ross-Perkins, and Richard Smith. Rather than go
through each question in the order they were asked I've tried to group
together questions I saw as thematically linked. Anything in quotes should be
a close approximation of what was said, but I can't guarantee I didn't
introduce errors.

### Background and basics of Carbon

This wasn't actually the first question, but I think a good starting point is
'how would you sell Carbon to a C++ user?'. Per Chandler, "we can provide a
better language, tooling, and ecosystem without needing to leave everything
you built up in C++ (both existing code and the training you had). The cost of
leveraging carbon should have as simple a ramp as possible. Sometimes you need
performance, we can give more advanced tools to help you get the most
performance from your code. In other cases, it's security and we'll be able to
offer more tools here than C++. It's having the ability to unlock improvements
in the language without having to walk away from your investments in C++, that
of course isn't going anywhere."

When is it going to be done? Chandler: "When it's ready! We're trying to put
our roadmap out there publicly where we can. It's a long term project. Our
goal for this year is to get the toolchain caught up with the language design,
get into building practical C++ interop this year. There are many unknowns in
terms of how far we'll get this year, but next year I think you'll see a
toolchain that works and you can do interesting stuff with and evaluate in a
more concrete context."

As for the size of the team and how many companies are contributing, the
conclusion was that Google is definitely the main backer right now but there
are others starting to take a look. There are probably about 5-10 people
active on Carbon in any different week, but it varies so this can be a
different set of people from week to week.

Given we've established that Google are still the main backer, one line of
questioning was about what Google see in it and how management were convinced
to back it. Richard commented "I think we're always interested in exploring
new possibilities for how to deal with our existing C++ codebase, which is a
hugely valuable asset for us. That includes both looking at how we can keep
the C++ language itself happy and our tools for it being good and
maintainable, but also places we might take it in the future. For a long time
we've been talking about if we can build something that works better for our
use case than existing tools, and had an opportunity to explore that and went
with it."

A fun question that followed later aimed to establish the favourite thing
about Carbon from each of the panel members (of course, it's nice that much of
this motivation overlaps with the reasons for my own interest!):
* Jon: For me it's unlocking the ability to improve the developer experience.
  Improving the language syntax, making things more understandable. Also C++
  is very slow to compile and we're hoping for 1/3rd of the compile time for a
  typical file vs Clang.
* Richard: from a language design perspective, being able to go through and
  systematically evaluate every decision and look at them again using things
  that have been learned since then.
* Chandler: It's not so much the systematic review for me. We're building this
  with an eye to C++, and to integrate with C++ need a fairly big complex
  language (generics, inheritance, overloading etc etc). But when we look at
  this stuff, we keep finding principled and small/focused designs that we can
  use to underpin the sort of language functionality that is in C++ but fits
  together in a coherent and principled way. And we write this down.  I think
  a lot of people don't realise that Carbon is writing down all the design as
  we go rather than having some mostly complete starting point and then making
  changes to that using something like an RFC process.

Finally, (for this section) there was also some intriguing discussion about
Carbon's design tradeoffs. This is covered mostly elsewhere, but I think
Chandler's answer focusing on the philosophy of Carbon rather than technical
implementation details fits well here: "One of the philosophical goals of our
language design is we don't try to solve hard problems in the compiler. [In
other languages] there's often a big problem and the compiler has to solve it,
freeing the programmer from worrying about it. Instead we provide the syntax
and ask the programmer to tell us. e.g. for type inference, you could imagine
having Hindley-Milner type inference. That's a hard problem, even if it makes
ergonomics better in some cases. So we use a simpler and more direct type
system. You see this crop up all over the language design."

### Carbon governance

The first question related to organisation of the project and its governance
was about what has been done to make it easier for contributors to get
involved. My interpretation of the responses is that although they've had some
success in attracting new contributors, the feeling is that there's more that
could be done here. e.g. from Jon "Things like maintaining the project
documentation, writing a start guide on how to build. We're making some
different infrastructure choices, e.g. bazel, but in general we're trying to
use things people are familiar with: GitHub, GH actions etc. There's probably
still room for improvement.  Listening to the LLVM newcomers session a couple
of days ago gave me some ideas. Right now there's probably a lot of challenge
learning how the different model works in Carbon."

The governance model for Carbon in general was something Chandler had a lot to
say about:
* On getting it in place early: "I was keen we start off with it, seeing
  challenges with C++ or even LLVM where as a project gets big the governance
  model that worked well at the beginning might not work so well and changing
  it at that point can be really hard. So I wanted to set up something that
  could scale, and can be changed if needed.
* Initial mistakes: "The initial model was terrible. It was very elaborate, a
  large core team of people that pulled in people that weren't even involved
  in the project. We'd have weekly/biweekly meetings, a complex consensus
  process. In some ways it worked, we were being intentional and it was clear
  there was a governance project. But its was so inefficient, so people tried
  to avoid it. So we revamped it and simplified it, distilling it to something
  a little closer to the benevolent dictator for life model with minimal
  patches. Three leads rather than one to add some redundancy, one top-level
  governance body, will eventually have a rotation there."
* The model now: "It's not that we'll try to agree on everything - if a change
  is uncontroversial then any one of the leads can approve, which gives us 3x
  bandwidth. Except for the cases if there is controversy, then the three of
  us step back and discuss. I had my personal pet favourite feature of carbon
  overturned by this governance model. The model allows us to make decisions
  quickly and easily, and most decisions are reversible if they turn out to be
  wrong. So we don't try to optimise for getting to the best outcome, rather
  to minimise cost for getting to an outcome. We're still early - we have a
  plan for scaling but that's more in the future."

Further questioning led to additional points being made about the governance
model, such as the fact there are now several community members unaffiliated
to Google with commit privileges, that the [project goals are
documented](https://github.com/carbon-language/carbon-lang/blob/trunk/docs/project/goals.md)
which helps contributors understand if a proposal is likely to be aligned with
Carbon or not, and that these goals are potentially changeable if people come
in with good arguments as to why they should be updated.

### Carbon vs other languages

Naturally, there were multiple questions related to Carbon vs Rust. In terms
of high-level comparisons, the panel members were keen to point out that Rust
is a great language and is mature, while Carbon remains at an early stage.
There are commonalities in terms of the aim to provide modern type system
features to systems programmers, but the focus on C++ interoperability as a
goal driving the language design is a key differentiator.

Thoughts about Rust naturally lead to questions about Carbon's memory safety
story, and whether Carbon plans to have something like Rust's borrow checker.
Richard commented "I think it's possible to get something like that. We're not
sure exactly what it will look like yet, we're planning to look at this more
between the 0.1 and 0.2 milestone. Borrow checking is an interesting option to
pursue but there are some others to explore."

Concerns were also raised about whether given that C++ interop is such a core
goal of Carbon, it may have problems as C++ continues to evolve (perhaps with
features that clash with features add in Carbon). Chandler's response was "As
long as clang gets new C++ features, we'll get them. Similar to how swift's
interop works, linking the toolchain and using that to understand the
functionality. If C++ starts moving in ways addressing the safety concerns etc
that would be fantastic.  We could shut down carbon! I don't think that's very
likely. In terms of functionality that would make interop not work well that's
a bit of a concern, but of course if C++ adds something they need it to
interop with existing C++ code so we face similar constraints. While Richard
commented "C++ modules is a big one we need to keep an eye on. But at the
moment as modules adoption hasn't taken off in a big way yet, we're still
targeting header files." There was also a brief exchange about what if Carbon
gets reflection before C++, with the hope that if it did happen it could help
with the design process by giving another example for C++ to learn from (just
as Carbon learns from Rust, Swift, Go, C++, and others).

### Compiler implementation questions

EuroLLVM is of course a compilers conference, so there was a lot of curiousity
about the implementation of the Carbon toolchain itself. In discussing
trade-offs in the design, Jon leapt into a discussion of this "to go for SemIR
vs a traditional AST. In Clang the language is represented by an AST, which is
what you're typically taught about how compilers work. We have a semantic IR
model where we produce lex tokens, then a parse tree (slightly different to an
AST) an then it becomes SemIR. This is very efficient and fast to process,
lowers to LLVM IR very easily, but it's a different model and a different way
to think about writing a compiler. To the earlier point about newcomers, it's
something people have to learn and a bit of a barrier because of that. We try
to address it, but it is a trade-off." Jon since provided more insight on
Carbon's implementation approach in a [recent /r/ProgrammingLanguages
thread](https://old.reddit.com/r/ProgrammingLanguages/comments/1co8qpv/flat_ast_and_states_machine_over_recursion_is/l3fyrga/).

Given what Carbon devs have learned about applying data oriented design to
optimise the frontend (see talks like [Modernizing Compiler Design for Carbon
Toolchain](https://www.youtube.com/watch?v=ZI198eFghJk)), could the same ideas
be applied to the backend? Chandler commented on the tradeoff he sees "By
necessity with data-oriented design you have to specialise a lot. We think we
can benefit from this a lot with the frontend at the cost of reusability. The
trade-off might be different within LLVM."

When asked about whether the Carbon frontend may be reusable for other tools
(reducing duplicated effort writing parsers for Carbon), Jon responded "I'm
pretty confident at least through the parse tree it will be reusable. I'm more
hesitant to make that claim through to SemIR. It may not be the best choice
for everyone, and in some cases you may want more of an AST. But providing
these tools as part of the language project like a formatter, migration tool
[for language of API changes], something like clang-tidy, we're going to be
taking on these costs ourselves which is going to incentivise us to find ways
of amortising this and finding the right balance."

## Article changelog
* 2024-05-13: (minor) Various phrasing tweaks and fixed improper heading
  nesting.
