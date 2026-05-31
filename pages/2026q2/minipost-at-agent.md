+++
published = 2026-05-31
description = "No-hassle feedback to agents via in-line comments."
+++

# at-agent

## Motivation

Like most people, I've been playing with agents to see where they're helpful,
where they're not, and what kind of workflows are a good match for me. One
area I've found friction is in iterating on a piece of code - written by me or
otherwise. I _can_ describe the relevant section and my question/request in
command line chat, but it would be better to do so directly inline and have
the LLM pick it up.
[`at-agent`](https://github.com/muxup/medley/blob/main/at-agent) is a super
minimal approach for picking out such directives from your worktree and
processing them.

This is very much a "worse is better" approach. A separate structured channel
for attaching questions or requests to spans of code would have advantages.
But that requires an interface for creating and editing such annotations as
well as logic for handling edits after the annotation was made. Sticking
`@agent` comments directly inline means it's trivial to intermingle manual
edits with requests for action, it's trivial to keep comments attached to the
region they were intended for, and reviewing and editing them at the file or
repository level is easy through `git diff` and your text editor of choice.

You _could_ get away with just asking your LLM of choice to "find all
comments prefixed with @agent in this codebase, treat them as directions to
you, action them, and then remove them". But I still believe in building on
solid primitives, and limited as this little script is, I'd rather lean on its
deterministic behaviour and reduce the number of round trips and tool calls
the LLM needs to handle successfully. So far it's been helpful for some kinds
of tasks and a handy tool to have in the toolbelt.

There are surely no end of IDE-integrated solutions and vim plugins that offer
something similar. `aider` also [supports 'AI'
comments](https://aider.chat/docs/usage/watch.html) but relies on the model to
remove them after the fact.

## Interface

`at-agent` doesn't try to understand language-specific comment syntax. It looks
for a whole line that starts with optional whitespace, then at least two
punctuation characters such as `//`, `##`, or `///`, then whitespace and
`@agent`. A following `!` marks an action request rather than a question, and
the rest of the line is the request text. Subsequent lines with the same
comment prefix are consumed as part of the same `@agent` directive.

What this means is that you might write something like this:

```
Example: // @agent explain why std::vector isn't used here. How does the
Example: // custom vector compare in terms of reallocation strategy?
```

The `Example:` prefix is only there to keep this blog post from containing live
annotations. Without it, running `at-agent` over the Markdown file would treat
the example itself as a real request and remove it.

Or for an action request:

```
Example: ## @agent! split this into a helper and update the two other callers
```

`@agent` is a comment/explanation request, and `@agent!` is a request to make
an edit. Only whole-line annotations are supported. If you want to nest a
request inside a long comment, just tweak the prefix appropriately, e.g.:

```
Example: // This is a multi-line comment. We want to place a directive in it.
Example: /// @agent explain the paragraph below, with a worked example
         /// alongside appropriate source code snippets.
Example: // Normal comment continues here.
```

Running the tool removes the annotation lines from the working tree and emits
something like:

```
The user manually added these annotations for you, the agent, to react to.
They are either comment/explanation requests, which ask you to explain nearby
code or answer the user's question without editing files, or action requests,
which ask you to investigate and make the requested code change.

The @agent remark lines have already been removed from the working tree.
Relevant line numbers refer to the files after remark removal.

1. example.cc
   kind: comment/explanation request
   relevant line number: 42
   text:
     @agent explain why std::vector isn't used here. How does the
     custom vector compare in terms of reallocation strategy?
   nearby context before removal:
     ...
```

## Usage

`at-agent` can be pointed at specific files listed in command line arguments
(passing files selects args mode automatically), or via `--discover=rg`
recursively grep the current working directory, or via
`--discover=inodes` (or indeed, no args) walk the current working directory
recursively to find inodes flagged as being modified recently and potentially
containing `@agent` directives. For that default mode, the idea is you set
your text editor to append to that list of inodes as you edit files and leave
`@agent` directives in them. This is particularly helpful to avoid expensive
greps on large trees. There is also `--dry-run`, which reports directives
without removing annotation lines.

The use of inode numbers rather than path names means that this works
comfortably in the scenario where you are editing files in your normal
environment, but an agent is running [in a sandbox](/pages/shandbox.md) and so
may have paths mounted at a different location.

You can just add something like this to your `.vimrc` (the filter is
imprecise, but this doesn't matter as `at-agent` will just do nothing for
files that have no valid directives):

```vim
let s:at_agent_dir = expand('~/.local/state/at-agent')

function! s:NoteAtAgentInode() abort
  let l:file = expand('%:p')
  if empty(l:file) || !isdirectory(s:at_agent_dir) || search('\s@agent', 'nw') == 0
    return
  endif

  call system(
        \ 'stat -c %i -- ' . shellescape(l:file) .
        \ ' >> ' . shellescape(s:at_agent_dir . '/inodes'))
endfunction

augroup at_agent
  autocmd!
  autocmd BufWritePost * call s:NoteAtAgentInode()
augroup END
```

So a simple flow would be:

1. Leave notes in the files while editing.
2. Save as normal in vim.
3. Run `at-agent` from the repository root in the agent session.

There are all kinds of ways this could be integrated into a harness, but I
have a fondness for no integration at all, meaning it's easy to switch between
different options. e.g. just give a prompt such as "Run `at-agent` and action
its output.".

If using `shandbox` or similar, the list of inodes that potentially contain
directives needs to be exposed at the expected location. You can add something
like this to `.shandbox_meta/init` (or `~/.config/shandbox/default-init`):

```sh
#!/bin/sh
host_at_agent_dir="$HOME/.local/state/at-agent"
mkdir -p "$host_at_agent_dir"

"$SHANDBOX_SELF" add-mount --read-write \
  "$host_at_agent_dir" \
  ".local/state/at-agent"
```
