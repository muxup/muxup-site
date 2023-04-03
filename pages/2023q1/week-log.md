+++
published = 2023-02-27
description = "What did I do last week?"
+++
# 2023Q1 week log
I tend to keep quite a lot of notes on the development related (sometimes at
work, sometimes not) I do on a week-by-week basis, and thought it might be fun
to write up the parts that were public. This may or may not be of wider
interest, but it aims to be a useful aide-mémoire for my purposes at least.
Weeks with few entries might be due to focusing on downstream work (or perhaps
just a less productive week - I am only human!).

## Week of 27th March 2023
* Submitted a [backport request to
  16.0.1](https://github.com/llvm/llvm-project-release-prs/pull/406) for my
  recent fixes to `llvm-objdump` (and related tools) when encountering
  unrecognised RISC-V base or ISA extension versions, or unrecognised ISA
  extension names.
* Landed a tweak to the RISC-V ISA manual to [make it clear that HINT
  encodings aren't
  "reserved"](https://github.com/riscv/riscv-isa-manual/pull/1001) in terms of
  being part of the defined "reserved instruction-set category". Thanks to
  Andrew Waterman for suggesting a simpler fix than my first attempt.
* I'm now on Mastodon, at [@asb@fosstodon.org](https://fosstodon.org/@asb) and
  [@llvmweekly@fosstodon.org](https://fosstodon.org/@llvmweekly).
* Proposed [alternate wording for the RISC-V LLVM doc updates reflecting
  recent ISA versioning
  discussions](https://reviews.llvm.org/D147183#4233360).
* Set agenda for and ran the usual biweekly [RISC-V LLVM contributor sync up
  call](https://discourse.llvm.org/t/risc-v-llvm-sync-up-call-30th-march-2023-note-daylight-savings-time-impact/69635).
* Added the Renesas R9A06G150 to my [commercially available RISC-V silicon
  list](/pages/2023q1/commercially-available-risc-v-silicon.md).
* Posted and landed patches to implement MC layer and codegen support for the
  experimental `Zicond` (integer conditional operations) extension
  ([D146946](https://reviews.llvm.org/D146946),
  [D147147](https://reviews.llvm.org/D147147)). This is essentially the same
  as the `XVentanaCondOps` extension.
* Advertised the ongoing discussion about changing the shadow call stack
  register on RISC-V [through an
  RFC](https://discourse.llvm.org/t/rfc-psa-changing-the-shadow-call-stack-register-on-risc-v/69537).
* It was pointed out to me that the expansion of `seq_cst` atomic ops to
  RISC-V lr/sc loops was slightly stronger than required by the mapping table
  in the ISA manual. Specifically, `sc.{w|d}.rl` is sufficient rather than
  `sc.{w|d}.aqrl`. Fixed with [D146933](https://reviews.llvm.org/D146933).
* Filed issue about the [fcvt.bf16.s instruction encoding colliding with
  fround.h](https://github.com/riscv/riscv-bfloat16/issues/33) (instructions
  from `zfbfmin` and `zfa` respectively).
* Usual mix of upstream LLVM reviews. We were now able to
  [bump](https://reviews.llvm.org/D147179) the versions of the standard ISA
  extensions LLVM claims to support. As noted in my [previous
  RFC](https://discourse.llvm.org/t/rfc-resolving-issues-related-to-extension-versioning-in-risc-v/68472),
  LLVM was reporting the wrong version information for the A/F/D extensions.
* [LLVM Weekly #482](https://llvmweekly.org/issue/482).

## Week of 20th March 2023
* Landed patches to fix RISC-V ISA extension versioning related issues in
  llvm-objdump and related tools ([D146070](https://reviews.llvm.org/D146070),
  [D146113](https://reviews.llvm.org/D146113), and
  [D146114](https://reviews.llvm.org/D146114)). Also patches to fix an ABI bug
  with `_Float16` lowering on RISC-V
  ([D142326](https://reviews.llvm.org/D142326),
  [D145074](https://reviews.llvm.org/D145074)).
* Opened a few issues on the [aichat](https://github.com/sigoden/aichat)
  (command line ChatGPT client) repo: one for [maximum line
  width](https://github.com/sigoden/aichat/issues/97), another for [word
  wrapping](https://github.com/sigoden/aichat/issues/99), and a [suggestion on
  converting one-shot questions to
  conversations](https://github.com/sigoden/aichat/issues/88#issuecomment-1484132478).
* Added the HPM6750 to my [commercially available RISC-V silicon
  list](/pages/2023q1/commercially-available-risc-v-silicon.md).
* My tutorial and lightning talk proposals were accepted for EuroLLVM!
* Some bits and pieces related to the RISC-V bfloat16 spec and also Zfh.
  * [Drafted](https://github.com/riscv/riscv-bfloat16/pull/31) a Zfbfinxmin
    extension definition (primarily for symmetry with the existing
    `z*inx[min]` extensions.
  * [Fixing](https://reviews.llvm.org/D146435) a missed predicate for
    `PseudoQuietFCMP`.
  * [Minor clarification](https://github.com/riscv/riscv-bfloat16/pull/29) to
    the riscv-bfloat16 spec.
* Usual mix of upstream LLVM reviews.
* [LLVM Weekly #481](https://llvmweekly.org/issue/481).

## Week of 13th March 2023
* Most importantly, added
  [some](https://github.com/muxup/muxup-site/commit/7159a2400e6535a288c78dfd4d71c1b544ddf51e#diff-196dde1107e14fd35d571db219211acb6853813d95a5c7faee5ac09e058f9203)
  [more](https://github.com/muxup/muxup-site/commit/a1cb4d4256815bcfa8a6a4c5174a03ae077ee8c6#diff-4e9f5b15205b49dff89e5050a5a899e63213f1f015daeca45b76270bb2c009dd)
  footer images for this site from the Quick Draw dataset. Thanks to my son
  (Archie, 5) for the assistance.
* Reviewed submissions for [EuroLLVM](https://llvm.org/devmtg/2023-05/) (I'm
  on the program committee).
* Added note to the [commercially available RISC-V silicon
  post](/pages/2023q1/commercially-available-risc-v-silicon.md) about a
  hardware bug in the Renesas RZ/Five.
* Finished writing and published [what's new for RISC-V in LLVM 16
  article](/pages/2023q1/whats-new-for-risc-v-in-llvm-16.md) and took part in
  some of the discussions in the
  [HN](https://news.ycombinator.com/item?id=35215826) and [Reddit
  threads](https://old.reddit.com/r/RISCV/comments/11veftz/whats_new_for_riscv_in_llvm_16/)
  (it's [on lobste.rs
  too](https://lobste.rs/s/qcu7fc/what_s_new_for_risc_v_llvm_16), but that
  didn't generate any comments).
* Investigated an issue where inline asm with the `m` constraint was
  generating worse code on LLVM vs GCC, finding that LLVM conservatively
  lowers this to a single register, while GCC treats `m` as reg+imm, relying
  on users indicating `A` when using a memory operand with an instruction that
  can't take an immediate offset. Worked with a colleague who posted
  [D146245](https://reviews.llvm.org/D146245) to fix this.
* Set
  [agenda](https://discourse.llvm.org/t/risc-v-llvm-sync-up-call-16th-march-2023-note-daylight-savings-impact/69244)
  for and ran the biweekly RISC-V LLVM contributor sync call as usual.
* Bisected reported LLVM bug
  [#61412](https://github.com/llvm/llvm-project/issues/61412), which
  as it happens was fixed that evening by
  [D145474](https://reviews.llvm.org/D145474) being committed. We hope to
  backport this to 16.0.1.
* Did some digging on a regression (compiler crash) for `-Oz`, bisecting it to
  the commit that enabled machine copy propagation by default. I found the
  issue was due to machine copy propagation running after the machine
  outliner, and incorrectly determining that some register writes in outlined
  functions were not live-out. I posted and
  landed [D146037](https://reviews.llvm.org/D146037) to fix this by running
  machine copy propagation earlier in the pipeline, though a more principled
  fix would be desirable.
* Filed a PR against the riscv-isa-manual to [disambiguate the use of the term
  "reserved" for HINT
  instructions](https://github.com/riscv/riscv-isa-manual/pull/990). I've also
  been looking at the proposed bfloat16 extension recently and filed an
  [issue](https://github.com/riscv/riscv-bfloat16/issues/27) to clarify if
  Zfbfinxmin will be defined (as all the other floating point extensions so
  far have an `*inx` twin.
* Almost finished work to resolve issues related to overzealous error checking
  on RISC-V ISA naming strings (with llvm-objdump and related tools being the
  final piece).
  * Landed [D145879](https://reviews.llvm.org/D145879) and
    [D145882](https://reviews.llvm.org/D145882) to expand `RISCVISAInfo` test
    coverage and fix an issue that surfaced through that.
  * Posted a pair of patches that makes llvm-objdump and related tools
    tolerant of unrecognised versions of ISA extensions.
    [D146070](https://reviews.llvm.org/D146070) resolves this for the base ISA
    in a minimally invasive way, while
    [D146114](https://reviews.llvm.org/D146114) solves this for other
    extensions, moving the parsing logic to using the
    `parseNormalizedArchString` function I introduced to fix a similar issue
    in LLD. This built on some directly committed work to [expand
    testing](https://reviews.llvm.org/rG0ae8f5ac08ae).
* The usual assortment of upstream LLVM reviews.
* [LLVM Weekly #480](https://llvmweekly.org/issue/480).

## Week of 6th March 2023
* Had a really useful meeting with a breakout group from the [RISC-V LLVM
  sync-up
  calls](https://docs.google.com/document/d/1G3ocHm2zE6AYTS2N3_3w2UxFnSEyKkcF57siLWe-NVs/edit)
  about the long-standing issues related to ISA extension versioning, error
  handling for this, and other related issues.
  * Related to this, posted [D145879](https://reviews.llvm.org/D145879) and
    [D145882](https://reviews.llvm.org/D145882) to flesh out testing of
    `RISCVISAInfo::parseArchString` ahead of further improvements, and to
    start to fix identified issues.
* Incorporated more clarifications submitted to me about the [commercially
  available RISC-V
  SoCs](/pages/2023q1/commercially-available-risc-v-silicon.md) post,
  particularly around SiFive cores.
* Shared [some
  thoughts](https://discourse.llvm.org/t/diversity-inclusion-strategic-planning-march-6-7/68794/8)
  on attracting more people to the LLVM Foundation strategic planning
  sessions.
* Posted and committed an LLVM patch to [migrate the RISC-V backend to using
  shared MCELFStreamer code for attribute
  emission](https://reviews.llvm.org/D145570). The initial implementation was
  largely derived from Arm's version of the same feature but a later
  refactoring managed to move this logic to common code, which we can now
  reuse.
* Some small tasks related to the RISC-V LLVM build-bot: trying to find a path
  forwards for a [simple patch to enable RISC-V support in
  libcxx](https://reviews.llvm.org/D143158), and [clarifying how often the
  staging buildmaster configuration is
  updated](https://reviews.llvm.org/D144465).
* Posted a docs patch to [clarify
  Clang's `-fexceptions`](https://reviews.llvm.org/D145564) in follow-up to
  discussion in [issue
  61216](https://github.com/llvm/llvm-project/issues/61216).
* Did some final preparations for the LLVM 16.0.0 release - committing some
  [cleaned up release notes](https://reviews.llvm.org/rGae37edf1486d).
* A variety of upstream LLVM reviews, and left some thoughts on [using
  sub-modules for RVV intrinsics
  tests](https://github.com/llvm/llvm-project/issues/61179).
* [LLVM Weekly #479](https://llvmweekly.org/issue/479).


## Week of 27th February 2023
* Completed (to the point I was happy to publish at least) my attempt to
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
* [LLVM Weekly #478](https://llvmweekly.org/issue/478).

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
* 2023-04-03: Added notes for the week of 27th March 2023.
* 2023-03-27: Added notes for the week of 20th March 2023.
* 2023-03-20: Added notes for the week of 13th March 2023.
* 2023-03-13: Added notes for the week of 6th March 2023.
* 2023-03-06: Added notes for the week of 27th February 2023.
* 2023-02-27: (minor) Added in a forgotten note about trivial buildbot doc
  improvements.
