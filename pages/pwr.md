+++
published = 2024-07-01
description = "Paced web reader (pwr) - an esoteric feed reader and workflow for keeping up to date online."
+++

# pwr

## Summary

[pwr](https://github.com/muxup/pwr) (paced web reader) is a script and
terminal-centric workflow I use for keeping up to date with various sources
online, shared on the off chance it's useful to you too.

## Motivation

The internet is (mostly) a wonderful thing, but it's kind of a lot. It can be
distracting and I thnk we all know the unhealthy loops of scrolling and
refreshing the same sites. `pwr` provides a structured workflow for keeping up
to date with a preferred set of sites in an incremental fashion (willpower
required). It takes some inspiration from [a widely reported
workflow](https://web.archive.org/web/20150708111216/http://article.gmane.org/gmane.os.openbsd.misc/134979)
that involved sending a URL to a server and having it returned via email to be
read in a batch later. `pwr` adopts the delayed gratification aspect of this
but doesn't involve downloading for offline reading.

## The pwr flow

One-time setup:
* Configure the `pwr` script so it supports your desired feed sources (RSS or
  using hand-written extractors for those that don't have a good feed).

Regular workflow (just run `pwr` with no arguments to initiate this sequence
in one invocation):
* Run `pwr read` to open any URLs that were previously queued for reading.
* Run `pwr fetch` to get any new URLs from the configured sources.
* Run `pwr filter` to open an editor window where you can quickly mark which
  retrieved articles to queue for reading.

In my preferred usage, the above is run once a day as a replacement for
unstructured web browsing. This flow means you're always reading items that
were identified the previous day. Although comments on sites such as Hacker
News or Reddit are much maligned, I do find they can be a source of additional
insight, and this flow means that by the time you're reading a post ~24 hours
after initially found, discussion has died down so there's little reason to
keep refreshing.

`pwr filter` is the main part requiring active input, and involves the editor
in a way that is somewhat inspired by `git rebase -i`. For instance, at the
time of writing it produces the following output (and you would simply replace
the `d ` prefix with `r ` for any you want to queue to read:

```
------------------------------------------------------------
Filter file generated at 2024-07-01 08:51:54 UTC
DO NOT DELETE OR MOVE ANY LINES
To mark an item for reading, replace the 'd' prefix with 'r'
Exit editor with non-zero return code (:cq in vim) to abort
------------------------------------------------------------

# Rust Internals
d [Discussion] Hybrid borrow (0 replies)

# Swift Evolution
d [Pitch #2] Safe Access to Contiguous Storage (27 replies)
d [Re-Proposal] Type only Unions (69 replies)

# HN
d Programmers Should Never Trust Anyone, Not Even Themselves
d Unification in Elixir
d Quaternions in Signal and Image Processing

# lobste.rs
d Code Reviews Do Find Bugs
d Integrated assembler improvements in LLVM 19
d Cubernetes
d Grafana security update: Grafana Loki and unintended data write attempts to Amazon S3 buckets
d regreSSHion: RCE in OpenSSH's server, on glibc-based Linux systems (CVE-2024-6387)
d Elaboration of the PostgreSQL sort cost model

# /r/programminglanguages
d Rate my syntax (Array Access)
```

## Making it your own

Ultimately `pwr` is a tool that happens to scratch an itch for me. It's out
there in case any aspect of it is useful to you. It's very explicitly written
a script, where the expected usage is that you take a copy and make what
modifications you need for yourself (changing sources, new fetchers, or other
improvements).
