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
* 2023-04-17: Added notes for the week of 10th April 2023.
