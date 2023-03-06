+++
published = 2023-02-27
description = "What did I do last week?"
+++
# 2023Q1 week log
I tend to keep quite a lot of notes on the development related (sometimes at
work, sometimes not) I do on a week-by-week basis, and thought it might be fun
to write up the parts that were public. This
may or may not be of wider interest, but it aims to be a useful aide-mémoire
for my purposes at least. Weeks with few entries might be due to focusing on
downstream work (or perhaps just a less productive week - I am only human!).

## Week of 27th February 2023
* Completed (to the point I was happy to publish at lest) my attempt to
  enumerate the [commercially available RISC-V
  SoCs](/pages/2023q1/commercially-available-risc-v-silicon.md). I'm very
  grateful to have received a whole range of suggested additions and
  clarifications over the weekend, which have all been incorporated.
* Ran the usual biweekly [RISC-V LLVM sync-up
  call](https://discourse.llvm.org/t/risc-v-llvm-sync-up-call-2nd-march-2023/68876).
  Topics included outstanding issues for LLVM 16.x (no major issues now my
  [backport
  request](https://github.com/llvm/llvm-project-release-prs/pull/324#issuecomment-1445012422)
  to fix and LLD regression was merged), an overview off `_Float16` ABI
  lowering fixes, GP relaxation in LLD, my recent RISC-V buildbot, and some
  vectorisation related issues.
* Investigated and largely resolved a issues related to ABI lowering of
  `_Float16` for RISC-V. Primarily, we weren't handling the cases where a
  GPR+FPR or a pair of FPRs are used to pass small structs including
  `_Float16`.
  * Part of this work involved rebasing my
    [previous](https://reviews.llvm.org/D134050)
    [patches](https://reviews.llvm.org/D140400) to refactor our RISC-V ABI
    lowering tests in Clang. Now that a version of my improvements to
    `update_cc_test_check.py --function-signature` (required for the refactor)
    landed as part of [D144963](https://reviews.llvm.org/D144963), this can
    hopefully be completed.
  * Committed a number of simple test improvements related to half floats. e.g.
    [570995e](https://reviews.llvm.org/rG570995eba2f9),
    [81979c3](https://reviews.llvm.org/rG81979c3038de),
    [34b412d](https://reviews.llvm.org/rG34b412dc0efe).
  * Posted [D145070](https://reviews.llvm.org/D145070) to add proper coverage
    for `_Float16` ABI lowering, and
    [D145074](https://reviews.llvm.org/D145074) to fix it. Also
    [D145071](https://reviews.llvm.org/D145071) to set the `HasLegalHalfType`
    property, but the semantics of that are less clear.
  * Posted a [strawman psABI
    patch](https://github.com/riscv-non-isa/riscv-elf-psabi-doc/pull/367) for
    `__bf16`, needed for the RISC-V bfloat16 extension.
* Attended the [Cambridge RISC-V
  Meetup](https://community.riscv.org/events/details/risc-v-international-cambridge-risc-v-group-presents-cheri-risc-v-full-stack-security-using-open-source-hardware-and-software/).
* After seeing the Helix editor [discussed on
  lobste.rs](https://lobste.rs/s/nvoikx/helix_notes), retried my previously
  shared [large Markdown file test
  case](https://github.com/helix-editor/helix/issues/3072#issuecomment-1208133990).
  Unfortunately it's still unusably slow to edit, seemingly due to a
  tree-sitter related issue.
* Cleaned up the static site generator used for this site a bit. e.g. now my
  fixes ([#157](https://github.com/miyuchina/mistletoe/pull/157),
  [#158](https://github.com/miyuchina/mistletoe/pull/158),
  [#159](https://github.com/miyuchina/mistletoe/pull/159)) for the
  `traverse()` helper in [mistletoe](https://github.com/miyuchina/mistletoe)
  where merged upstream, I
  [removed](https://github.com/muxup/muxup-site/commit/52989cf7462d7900bbef5bc2ca9f976af8022ade)
  my downstream version.
* The usual mix of upstream LLVM reviews.
* Had a day off for my birthday.
* Publicly shared this week log for the first time.
* [LLVM Weekly #477](https://llvmweekly.org/issue/477).

## Week of 20th February 2023
* Iterated on [D144353](https://reviews.llvm.org/D144353) (aiming to fix LLD
  regression related to merging RISC-V attributes) based on review feedback
  and committed it.
  * Created [an issue to track this as a
    regression](https://github.com/llvm/llvm-project/issues/60889), aiming for
    a backport into 16.0.0, and [requested that
    backport](https://github.com/llvm/llvm-project-release-prs/pull/324#issuecomment-1445012422).
  * Also some related discussion in ClangBuiltLinux issues
    [#1777](https://github.com/ClangBuiltLinux/linux/issues/1777) and
    [#1808](https://github.com/ClangBuiltLinux/linux/issues/1808).
* Committed [my llvm-zorg patch to add the qemu-user based RISC-V
  builder](https://reviews.llvm.org/D143172), after finalising provisioning
  the machine to run it. The builder is live on the LLVM staging buildmaster
  [as
  clang-rv64gc-qemu-user-single-stage](https://lab.llvm.org/staging/#/builders/241).
  * Worked to resolve remaining test failures and stability issues. One
    recurrent issue was an assert in `___pthread_mutex_lock` when executing
    `ccache`. Setting `inode_cache=false` in the local `ccache` config seems
    to avoid this.
  * Posted a couple of patches - [D144464](https://reviews.llvm.org/D144464)
    and [D144465](https://reviews.llvm.org/D144465) to tweak the LLVM docs on
    setting up a builder, based on my experience doing so.
* Chased for reviews and clarification about pre-commit test requirements for
  my libcxx RISC-V test fix patch,
  [D134158](https://reviews.llvm.org/D143158).
* Committed a couple of further test updates for Wasm in LLVM ahead of some
  upcoming patches. [771261f](https://reviews.llvm.org/rG771261ff0128)
  [1ae8597](https://reviews.llvm.org/rG1ae859753c06).
* Left some quick notes on the [LLVM RFC
  shepherds](https://discourse.llvm.org/t/rfc-rfc-shepherds/68666/8) proposal.
* A variety of upstream LLVM reviews, and received a [useful clarification on
  the RISC-V psABI and the ratification
  lifecycle](https://reviews.llvm.org/D143115#4151994).
* [LLVM Weekly #477](https://llvmweekly.org/issue/477).

## Week of 13th February 2023
* After a fair bit of investigation and thinking about reported compatibility
  issues between GNU and LLVM tools (particularly binutils ld and lld) due to
  RISC-V extension versioning, [posted an RFC outlining the major issues and a
  proposed fix for what I consider to be a regression in
  lld](https://discourse.llvm.org/t/rfc-resolving-issues-related-to-extension-versioning-in-risc-v/68472).
  * Landed a few LLVM patches cleaning up tests related to this.
    [8b50048](https://reviews.llvm.org/rG8b5004864aab)
    [574d0c2](https://reviews.llvm.org/rG574d0c2ec107),
    [d05e1e9](https://reviews.llvm.org/rGd05e1e99b1d6).
  * Posted [D144353](https://reviews.llvm.org/D144353), a proposed fix for the
    LLD regression due to overzealous checking of extensions/versions when
    merging RISC-V attributes.
* Organised agenda for and ran the bi-weekly [RISC-V LLVM contributor
  call](https://discourse.llvm.org/t/risc-v-llvm-sync-up-call-16th-february-2023/68500).
  Key discussion items were the extension versioning related compatibility
  issue mentioned below and support for emulated TLS (where I'd [left some
  comments](https://reviews.llvm.org/D143708#4118468) the previous week).
* Updated my patch ([D143172](https://reviews.llvm.org/D143172)) to register
  and configure a RISC-V qemu-user based builder with LLVM's staging
  buildmaster, based on review feedback.
* A variety of upstream LLVM reviews. Also landed
  [D143407](https://reviews.llvm.org/D143507), marking Zawrs as
  non-experimental.
* [LLVM Weekly #476](https://llvmweekly.org/issue/476).

## Week of 6th February 2023
* Left feedback on the proposed RISC-V psABI
  [patch clarifying treatment of empty structs or unions in the FP calling
  convention](https://github.com/riscv-non-isa/riscv-elf-psabi-doc/pull/365).
  This is a follow-up to the [issue I
  filed](https://github.com/riscv-non-isa/riscv-elf-psabi-doc/issues/358) on
  this issue (where I have [D142327](https://reviews.llvm.org/D142327) queued
  up for LLVM to fix our incorrect handling).
* Responded to a question on LLVM's Discourse [about zicsr and zifencei
  support in
  LLVM](https://discourse.llvm.org/t/support-for-zicsr-and-zifencei-extensions/68369/2).
  As noted, the issue is that we haven't moved RV32I/RV64I 2.1 yet which split
  out Zicsr and Zifencei. Unfortunately this is a backwards-incompatible
  change so requires some care.
* Worked with a colleague trying to reproduce an assertion failure in his
  committed patch [adding support for WebAssembly externref in
  Clang](https://reviews.llvm.org/rGeb66833d19573df97034a81279eda31b8d19815b)
  that appeared only on an MSan buildbot. The [sanitizers project
  guidance](https://github.com/google/sanitizers/wiki/SanitizerBotReproduceBuild)
  is useful for this, but I ended up [rolling a slightly hacky
  script](https://gist.github.com/asb/645a071903f0c3cf9ef6c59a3d3e0810) as I
  stepped through each part of the multi-stage build and test sequence.
* Left my thoughts on a [proposed RISC-V preprocessor define to specify
  support and for and performance of misaligned
  loads/stores](https://github.com/riscv-non-isa/riscv-c-api-doc/issues/32). I
  like the idea of the define, but prefer sticking to the `Zicclsm`
  terminology introduced in the RISC-V profiles.
* Posted patch [D143507](https://reviews.llvm.org/D143507) to mark RISC-V
  Zawrs as non-experimental, after confirming there were no relevant changes
  between the implemented 1.0-rc3 spec and the ratified version.
* A series of WebAssembly GC type related patches remains a work in progress
  downstream, but I landed a couple of related minor test cleanups.
  [604c9a0](https://reviews.llvm.org/rG604c9a07f3a9),
  [3a80dc2](https://reviews.llvm.org/rG3a80dc27ed45).
* Many upstream RISC-V LLVM reviews.
* [LLVM Weekly #475](https://llvmweekly.org/issue/475).

## Article changelog
* 2023-03-06: Added notes for the week of 27th February 2023.
* 2023-02-27: (minor) Added in a forgotten note about trivial buildbot doc
  improvements.
