+++
published = 2024-01-01
description = "Some thoughts on LLVM Weekly after 10 years of uninterrupted publishing"
+++

# Reflections on ten years of LLVM Weekly

Today, with [Issue #522](https://llvmweekly.org/issue/522) I'm marking ten
years of authoring [LLVM Weekly](https://llvmweekly.org/), a newsletter
summarising developments on projects under the LLVM umbrella (LLVM, Clang,
MLIR, Flang, libcxx, compiler-rt, lld, LLDB, ...). Somehow I've managed to
keep up an unbroken streak, publishing every single Monday since the first
issue back on [Jan 6th 2014](https://llvmweekly.org/issue/1) (the first Monday
of 2014 - you can also see the format hasn't changed much!). With a milestone
like that, now is the perfect moment to jot down some reflections on the
newsletter and thoughts for the future.

## Motivation and purpose

Way back when I started [LLVM Weekly](https://llvmweekly.org/), I'd been
working with LLVM for a few years as part of developing and supporting a
downstream compiler for a novel
research architecture. This was a very educational yet somewhat lonely
experience, and I sought to more closely follow upstream LLVM development
to keep better abreast of changes that might impact or help my work, to
learn more about parts of the compiler I wasn't actively using, and also to
feel more of a connection to the wider LLVM community given my compiler work
was a solo effort. The calculus for kicking off an LLVM development newsletter
was dead simple: I found value in tracking development anyway, the
incremental effort to write up and share with others wasn't _too_ great, and I
felt quite sure others would benefit as well.

Looking back at my notes (I have a huge Markdown file with daily notes going back
to 2011 - a file of this rough size and format is also a good
[stress](https://github.com/mawww/kakoune/issues/4685#issuecomment-1208129806)
[test](https://github.com/helix-editor/helix/issues/3072#issuecomment-1208133990)
for text editors!) it seems I thought seriously about the idea of starting
something up at the beginning of December 2013. I brainstormed the format,
looked at other newsletters I might want to emulate, and went ahead and just
did it starting in the new year. It really was as simple as that. I figured
better to give it a try and stop it if it gets no traction rather than waste
lots of time putting out feelers on level of interest and format. As a
sidenote, I was delighted to see many of the newsletters I studied at the time
are still going: [This Week in Rust](https://this-week-in-rust.org/)
[Perl Weekly](https://perlweekly.com/) (I'll admit this surprised me!),
[Ubuntu Weekly News](https://discourse.ubuntu.com/c/uwn/124), [OCaml Weekly
News](https://alan.petitepomme.net/cwn/index.html), and [Haskell Weekly
News](https://wiki.haskell.org/Haskell_Weekly_News).

## Readership and content

The basic format of LLVM Weekly is incredibly simple - highlight relevant news
articles and blog posts, pick out some forum/mailing discussions (sometimes
trying to summarise complex debates - but this is very challenging and time
intensive), and highlight some noteworthy commits from across the project.
More recently I've taken to advertising the scheduled [online
sync-ups](https://llvm.org/docs/GettingInvolved.html#online-sync-ups) and
[office hours](https://llvm.org/docs/GettingInvolved.html#office-hours) for
the week. Notably absent are any kind of ads or paid content. I respect that
others have made successful businesses in this kind of space, but although I've
always written LLVM Weekly on my own personal time I've never felt comfortable
trying to monetise other people's attention or my relationship with the
community in this way.

The target audience is really anyone with an interest in keeping track of LLVM
development, though I don't tend to expand every acronym or give a
from-basics explanation for every term, so some familiarity with the project
is assumed if you want to understand every line. The newsletter is posted to
LLVM's Discourse, to [llvmweekly.org](https://llvmweekly.org/), and delivered
direct to people's inboxes. I additionally post [on
Twitter](https://twitter.com/llvmweekly) and [on
Mastodon](https://fosstodon.org/@llvmweekly) linking to each issue. I don't
attempt to track open rates or have functioning analytics, so only have a
rough idea of readership. There are ~3.5k active subscribers directly to the
mailing list, ~7.5k Twitter followers, ~180 followers on Mastodon (introduced
much more recently), and an unknown number of people reading via
llvmweekly.org or RSS. I'm pretty confident that I'm not just shouting in the
void at least.

There are some gaps or blind spots of course. I make no attempt to try to link
to patches that are under-review, even though many might have interesting
review discussions because it would simply be too much work to sort through
them and if the discussion is particularly contentious or requires input
from a wider cross-section of the LLVM community you'd expect an RFC
to be posted anyway. Although I do try to highlight MLIR threads or commits,
as it's not an area of LLVM I'm working right now I probably miss some things.
Thankfully Javed Absar has taken up writing an [MLIR
newsletter](https://discourse.llvm.org/c/mlir/mlir-news-mlir-newsletter/37)
that helps plug those gaps. I'm also not currently trawling through repos
under the [LLVM GitHub organisation](https://github.com/llvm/) other than the
main llvm-project monorepo, though perhaps I should...

I've shied away from reposting job posts as the overhead is just too high.  I
found dealing with requests to re-advertise (and considering if this is useful
to the community) or determining if ads are sufficiently LLVM related just
wasnt a good use of time when there's a good alternative. People can [check
the job post
category on LLVM
discourse](https://discourse.llvm.org/c/community/job-postings/) or search for
LLVM on their favourite jobs site.

## How it works

There are really two questions to be answered here: how I go about writing it
each week, and what tools and services are used. In terms of writing:

* I have a checklist I follow just to ensure nothing gets missed and help dive
  back in quickly if splitting work across multiple days.
* `tig --since=$LAST_WEEK_DATE $DIR` to step through commits in the past week
  for each sub-project within the monorepo.
  [Tig](https://jonas.github.io/tig/) is a fantastic text interface for git,
  and I of course have an ugly script that I bind to a key that generates the
  `[shorthash](github_link)` style links I insert for each chosen commit.
* I make a judgement call as to whether I think a commit might be of interest
  to others. This is bound to be somewhat flawed, but hopefully better than
  ramdom selection! I always really appreciate feedback if you think I missed
  something important, or tips on things you think I should include next week.
  * There's a cheat that practically guarantees a mention in LLVM Weekly
    without even needing to drop me a note though - write documentation! It's
    very rare I see a commit that adds more docs and fail to highlight it.
* Similarly, I scan through [LLVM Discourse](https://discourse.llvm.org/)
  posts over the past week and pick out discussions I think readers may be
  interested in. Most RFCs will be picked up as part of this. In some cases if
  there's a lengthy discussion I might attempt to summarise or point to key
  messages, but honestly this is rarer than I'd like as it can be incredibly
  time consuming. I try very hard to remain a neutral voice and no to insert
  personal views on technical discussions.
* Many ask how long it takes to write, and the answer is of course that it
  varies. It's easy to spend a lot of time trying to figure out the importance
  of commits or discussions in parts of the compiler I don't work with much,
  or to better summarise content. The amount of activity can also vary a lot
  week to week (especially on Discourse). It's mostly in the 2.5-3.5h range
  (very rarely any more than 4 hours) to write, copyedit, and send.

There's not much to be said on the tooling said, except that I could probably
benefit from refreshing my helper scripts. Mail sending is handled by
[Mailgun](https://www.mailgun.com/), who have changed ownership three times
since I started. I handle double opt-in via a simple Python script on the
server-side and mail sending costs me $3-5 a month. Otherwise, I generate the
static HTML with some scripts that could do with a bit more love. The only
other running costs are the domain name fees and a VPS that hosts some other
things as well, so quite insignificant compared to the time commitment.

## How you can help

I cannot emphasise enough that I'm not an expert on all parts of LLVM, and I'm
also only human and can easily miss things. If you did something you think
people may be interested in and I failed to cover it, I almost certainly
didn't explicitly review it and deem it not worthy. Please do continue to help
me out by dropping links and suggestions. Writing commit messages that make it
clear if a change has wider impact also helps increase the chance I'll pick it
up.

I noted above that it is particularly time consuming to summarise back and
forth in lengthy RFC threads. Sometimes people step up and do this and I
always try to link to it when this happens. The person who initiated a thread
or proposal is best placed write such a summary, and it's also a useful tool
to check that you interpreted people's suggestions/feedback correctly, but it
can still be helpful if others provide a similar service.

Many people have fed back they find LLVM Weekly useful to stay on top of LLVM
developments. This is gratifying, but also a pretty huge responsibility. If
you have thoughts on things I could be doing differently to serve the
community even better without a big difference in time commitment, I'm always
keen to hear ideas and suggestions.

## Miscellaneous thoughts

To state the obvious, ten years is kind of a long time. A lot has happened
with me in that time - I've got married, had a son, co-founded and helped grow a
company, and then moved on from that, kicked off the upstream RISC-V LLVM
backend, and much more. One of the things I love working with compilers is
that there's always new things to learn, and writing LLVM Weekly helps me
learn at least a little more each week in areas outside of where I'm currently
working.  There's been a lot of changes in LLVM as well. Off the top off my
head: there's been the move from SVN to Git, moving the Git repo to GitHub,
moving from Phabricator to GitHub PRs, Bugzilla to GitHub issues, mailing
lists to Discourse, relicensing to Apache 2.0 with LLVM exception, the wider
adoption of office hours and area-specific sync-up calls, and more. I think
even the LLVM Foundation was set up a little bit after LLVM Weekly started.
It's comforting to see the [llvm.org website design remains unchanged
though!](https://web.archive.org/web/20140102034931/http://llvm.org/)

It's also been a time period where I've become increasingly involved in LLVM.
Upstream work - most notably initiating the RISC-V LLVM backend, organising an
LLVM conference, many talks, serving on various program committees for LLVM
conferences, etc etc. When I started I felt a lot like someone outside the
community looking in and documenting what I saw. That was probably accurate
too, given the majority of my work was downstream. While I don't feel like an
LLVM "insider" (if such a thing exists?!), I certainly feel a lot more part of
the community than I did way back then.

An obvious question is whether there are other ways of pulling together the
newsletter that are worth pursuing. My experience with large language models
so far has been that they haven't been very helpful in reducing the effort for
the more time consuming aspects of producing LLVM Weekly, but perhaps that
will change in the future. If I could be automated away then that's great -
perhaps I'm misjudging how much of my editorial input is signal rather than
just noise, but I don't think we're there yet for AI. More collaborative
approaches to producing content would be another avenue to explore. For the
current format, the risk is that the communication overhead and stress of
seeing if various contributions actually materialise before the intended
publication date is quite high. If I did want to spread the load or hand it
over, then a rotating editorship would probably be most interesting to me.
Even if multiple people contribute, each week a single would act as a backstop
to make sure something goes out.

The unbroken streak of LLVM Weekly editions each Monday has become a bit
totemic. It's certainly not always convenient having this fixed commitment,
but it can also be nice to have this rhythm to the week. Even if it's a bad
week, at least it's something in the bag that people seem to appreciate.
Falling into bad habits and frequently missing weeks would be good for nobody,
but I suspect that a schedule that allowed the odd break now and then would be
just fine. Either way, I feel a sense of relief having hit the 10 year
unbroken streak. I don't intend to start skipping weeks, but should life get
in the way and the streak gets broken I'll feel rather more relaxed about it
having hit that arbitrary milestone.

## Looking forwards and thanks

So what's next? LLVM Weekly continues, much as before. I don't know of I'll
still be writing it in another 10 years time, but I'm not planning to stop
soon. If it ceases to be a good use of my time, ceases to have values for
others, or I find there's a better way of generating similar impact then it
would only be logical to move on. But for now, onwards and upwards.

Many thanks are due. Thank you to the people who make LLVM
what it is - both technically and in terms of its community that I've learned
so much from. Thank you to [Igalia](https://www.igalia.com/) where I work for
creating an environment where I'm privileged enough to be paid to contribute
upstream to LLVM ([get in touch](https://www.igalia.com/contact/) if you have
LLVM needs!). Thanks to my family for ongoing support and
of course putting up with the times my LLVM Weekly commitment is inconvenient.
Thank you to everyone who has been reading LLVM Weekly and especially those
sending in feedback or tips or suggestions for future issues.

On a final note, if you've got this far you should make sure you are
[subscribed](https://llvmweekly.org/) to LLVM Weekly and [follow on
Mastodon](https://fosstodon.org/@llvmweekly) or [on
Twitter](https://twitter.com/llvmweekly).
