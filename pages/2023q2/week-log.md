+++
published = 2023-04-10
description = "What did I do last week?"
+++
# 2023Q2 week log
I tend to keep quite a lot of notes on the development related (sometimes at
work, sometimes not) I do on a week-by-week basis, and thought it might be fun
to write up the parts that were public. This may or may not be of wider
interest, but it aims to be a useful aide-mémoire for my purposes at least.
Weeks with few entries might be due to focusing on downstream work (or perhaps
just a less productive week - I am only human!).

## Week of 29th May 2023
* Posted [D151663](https://reviews.llvm.org/D151663), implementing support for
  bf16 truncate/extend of hard FP targets.
* Responded to user query about [gating of
  CSRs](https://discourse.llvm.org/t/csrs-defined-in-sstc-extension/70824/2).
* Filed [issue](https://gitlab.xfce.org/apps/xfce4-terminal/-/issues/244)
  about shift and right-click and xfce4-terminal (after migrating to it due to
  frustration with gnome-terminal [not supporting setting the urgent hint upon
  receiving a terminal
  bell](https://gitlab.gnome.org/GNOME/gnome-terminal/-/issues/6698)).
* [Spread the word](https://fosstodon.org/@asb/110475298100440985) about my
  keynote about LLVM next week at the RISC-V Summit Europe.
* A few reviews on RISC-V psABI or ASM manual PRs (e.g. [atomics
  ABI](https://github.com/riscv-non-isa/riscv-elf-psabi-doc/pull/378),
  [floating point in the asm
  manual](https://github.com/riscv-non-isa/riscv-asm-manual/pull/86)).
* Less activity this week due to being on holiday.
* [LLVM Weekly #491](https://llvmweekly.org/issue/491).

## Week of 22nd May 2023
* Posted a [patch](https://reviews.llvm.org/D151434) to generalise  the
  shouldExtendTypeInLibcall hook so it applies to half and bfloat16.
* Updated [bfloat16 psABI
  PR](https://github.com/riscv-non-isa/riscv-elf-psabi-doc/pull/367), which
  has now been merged.
* Posted [D151363](https://reviews.llvm.org/D151563) a patch to implement soft
  FP legalisation for bf16 FP_EXTEND and BF16_TO_FP after abandoning [patch to
  add an extenbfsf2 libcall](https://reviews.llvm.org/D151436) (which would
  match libgcc, but add no real value).
* Identified a bug in the ABI used for half FP libcalls and [posted a
  patch](https://reviews.llvm.org/D151284) to fix it.
* Some misc small cleanups like [making zfbfmin imply the F
  extension](https://reviews.llvm.org/D151096), cleaning up bfloat16 tests
  ([1](https://reviews.llvm.org/rGf3202b9da663),
  [2](https://reviews.llvm.org/rGa6e2b1ee49f5)).
* Prepared agenda for an ran biweekly [RISC-V LLVM sync-up
  call](https://discourse.llvm.org/t/risc-v-llvm-sync-up-call-may-25th-2023/70873).
* [LLVM Weekly #490](https://llvmweekly.org/issue/490).

## Week of 15th May 2023
* Corrected Clang codegen support for half FP types when the zhinx extension
  is available ([D150777](https://reviews.llvm.org/D150777).
* Rebased and committed patches to implement MC layer support for the bfloat16
  extensions (unblocked now a new PDF was posted in the riscv-bfloat16 repo).
  [Zfbfmin](https://reviews.llvm.org/D147610),
  [zvfbfmin](https://reviews.llvm.org/D147611),
  [zvfbfwma](https://reviews.llvm.org/D147612). Also made a [trivial typo fix
  to the spec](https://github.com/riscv/riscv-bfloat16/pull/48).
* Looked at cleaning up the usage of `report_fatal_error` in the RISC-V
  backend and also [fixed a bug encountered while looking at
  this](https://reviews.llvm.org/D150669).
  [D150674](https://reviews.llvm.org/D150674).
* Participated in the ongoing discussion about [adding atomics lowering to the
  RISC-V
  psABI](https://github.com/riscv-non-isa/riscv-elf-psabi-doc/pull/378#issuecomment-1549250676),
  including a slightly altered lowering of some primitives in order to allow
  for forwards compatibility with "table A.7".
* Usual mix of upstream LLVM reviews, and a number of RISC-V psABI or ASM
  manual reviews.
* [LLVM Weekly #489](https://llvmweekly.org/issue/489).
* Missed some weeks - busy with EuroLLVM etc.

## Week of 17th April 2023
* Still [pinging](https://github.com/riscv/riscv-bfloat16/issues/33) for an
  updated riscv-bfloat1y spec version that incorporates the `fcvt.bf16.s`
  encoding fix.
* Bumped the version of the experimental Zfa RISC-V extension supported by
  LLVM to 0.2 ([D146834](https://reviews.llvm.org/D148634)). This was very
  straightforward as after inspecting the spec history, it was clear there
  were no changes that would impact the compiler.
* Filed a couple of pull requests against the [riscv-zacas
  repo](https://github.com/riscv/riscv-zacas) (RISC-V Atomic Compare and Swap
  extension).
  * [#8](https://github.com/riscv/riscv-zacas/pull/8) made the
  dependency on the A extension explicit.
  * [#7](https://github.com/riscv/riscv-zacas/pull/7) attempted to explicitly
    reference the extension for misaligned atomics, though it seems won't be
    merged. I do feel uncomfortable with RISC-V extensions that can have their
    semantics changed by other standard extensions without this possibility
    being called out very explicitly. As I note in the PR, failure to
    appreciate this might mean that conformance tests written for `zacas`
    might fail on a system with `zacas_zam`. I see a slight parallel to a
    recent [discussion about RISC-V
    profiles](https://lists.riscv.org/g/tech-profiles/message/94).
* Fixed the canonical ordering used for ISA naming strings in RISCVISAInfo
  (this will mainly affect the string stored in build attributes). This was
  fixed in [D148615](https://reviews.llvm.org/D148615) which built on the
  [pre-committed test case](https://reviews.llvm.org/rGa35e67fc5be6).
* A whole bunch of upstream LLVM reviews. As noted in
  [D148315](https://reviews.llvm.org/D148315#4279486) I'm thinking we should
  probably relaxing the ordering rules for ISA strings in `-march` in order to
  avoid issues due to spec changes and incompatibilities between GCC and
  Clang.
* [LLVM Weekly #485](https://llvmweekly.org/issue/485).

## Week of 10th April 2023
* Some days off due to the Easter holidays, so less to report this week.
* Updated RISC-V bfloat16 patches
  ([Zfbfmin](https://reviews.llvm.org/D147610),
  [Zvfbfmin](https://reviews.llvm.org/D147611),
  [Zvfbfwma](https://reviews.llvm.org/D147612)), incorporating new
  `fcvt.bf16.s` encoding. Also filed an
  [issue](https://github.com/riscv/riscv-bfloat16/issues/40) about the way in
  which the dependencies of the vector bfloat16 extensions is specified.
* Blogged about [updating the Wren language
  benchmarks](/pages/2023q2/updating-wrens-benchmarks.md).
* Variety of upstream LLVM reviews.
* [LLVM Weekly #484](https://llvmweekly.org/issue/484).

## Week of 3rd April 2023
* Some days off due to the Easter holidays, so less to report this week.
* Posted MC layer (assembler/disassembler) patches for the bfloat16
  extensions:
  [Zfbfmin](https://reviews.llvm.org/D147610),
  [Zvfbfmin](https://reviews.llvm.org/D147611),
  [Zvfbfwma](https://reviews.llvm.org/D147612).
  * Also posted a PR to the riscv-bfloat16 spec to [clarify the vector
    extension dependencies](https://github.com/riscv/riscv-bfloat16/pull/34).
  * Pinged on my [bug report about the fcvt.bf16.s encoding
    clash](https://github.com/riscv/riscv-bfloat16/issues/33). Once this is
    resolved, the LLVM MC layer patches can land.
* Updated authorship information for
  [riscv-toolchain-conventions](https://github.com/riscv-non-isa/riscv-toolchain-conventions/pull/34)
  which now has a range of contributors beyond myself.
* Usual mix of upstream LLVM reviews. This included some discussion on
  [changing the shadow call stack register to
  x3](https://reviews.llvm.org/D146463) which spilled into the [psABI
  PR](https://github.com/riscv-non-isa/riscv-elf-psabi-doc/pull/371) where I
  suggested some alternate wording.
* [LLVM Weekly #483](https://llvmweekly.org/issue/483).

## Article changelog
* 2023-06-05: Added notes for the week of 22nd May 2023 and week fo 29th May
  2023.
* 2023-05-22: Added notes for the week of 15th May 2023.
* 2023-04-24: Added notes for the week of 17th April 2023.
* 2023-04-17: Added notes for the week of 10th April 2023.
