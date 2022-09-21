+++
published = 2022-09-21
description = "Details on newly added features in Clang, LLVM, and LLD 15 for RISC-V"
+++
# What's new for RISC-V in LLVM 15

LLVM 15.0.0 was
[released](https://discourse.llvm.org/t/llvm-15-0-0-release/65099) around
about two weeks ago now, and I wanted to highlight some of RISC-V specific
changes or improvements that were introduced while going into a little more
detail than I was able to in the [release
notes](https://releases.llvm.org/15.0.0/docs/ReleaseNotes.html#changes-to-the-risc-v-backend).

In case you're not familiar with LLVM's release schedule, it's worth noting
that there are two major LLVM releases a year (i.e. one roughly every 6
months) and these are timed releases as opposed to being cut when a pre-agreed
set of feature targets have been met. We're very fortunate to benefit from an
active and growing set of contributors working on RISC-V support in LLVM
projects, who are responsible for the work I describe below - thank you!
I coordinate biweekly sync-up calls for RISC-V LLVM contributors, so if you're
working in this area please [consider dropping
in](https://discourse.llvm.org/c/code-generation/riscv/57).

## Linker relaxation

Linker relaxation is a mechanism for allowing the linker to optimise code
sequences at link time. A code sequence to jump to a symbol might
conservatively take two instructions, but once the target address is known at
link-time it might be small enough to fit in the immediate of a single
instruction, meaning the other can be deleted. Because a linker performing
relaxation may delete bytes (rather than just patching them), offsets
including those for jumps within a function may be changed. To allow this to
happen without breaking program semantics, even local branches that might
typically be resolved by the assembler must be emitted as a relocation when
linker relaxation is enabled. See the [description in the RISC-V
psABI](https://github.com/riscv-non-isa/riscv-elf-psabi-doc/blob/master/riscv-elf.adoc#linker-relaxation)
or [Palmer Dabbelt's blog post on linker
relaxation](https://www.sifive.com/blog/all-aboard-part-3-linker-relaxation-in-riscv-toolchain)
for more background.

Although LLVM has supported codegen for linker relaxation for a long time, LLD
(the LLVM linker) has until now lacked support for processing these
relaxations. Relaxation is primarily an optimisation, but processing of
`R_RISCV_ALIGN` (the alignment relocation) is necessary for correctness when
linker relaxation is enabled, meaning it's not possible to link such object
files correctly without at least some minimal support. Fangrui Song
implemented support for
`R_RISCV_ALIGN/R_RISCV_CALL/R_RISCV_CALL_PLT/R_RISCV_TPREL_*` relocations in
LLVM 15 and wrote up a [blog post with more implementation
details](https://maskray.me/blog/2022-07-10-riscv-linker-relaxation-in-lld),
which is a major step in bringing us to parity with the GCC/binutils
toolchain.

## Optimisations

As with any release, there's been a large number of codegen improvements, both
target-independent and target-dependent. One addition to highlight in the
RISC-V backend is the new [RISCVCodeGenPrepare
pass](https://github.com/llvm/llvm-project/blob/release/15.x/llvm/lib/Target/RISCV/RISCVCodeGenPrepare.cpp).
This is the latest piece of a long-running campaign (largely led by Craig
Topper) to improve code generation related to sign/zero extensions on RV64.
[CodeGenPrepare](https://llvm.org/docs/Passes.html#codegenprepare-optimize-for-code-generation)
is a target-independent pass that performs some late-stage transformations to
the input ahead of lowering to SelectionDAG. The RISC-V specific version looks
for opportunities to convert zero-extension to i64 with a sign-extension
(which is cheaper).

Another new pass that may be of interest is
[RISCVMakeCompressible](https://github.com/llvm/llvm-project/blob/release/15.x/llvm/lib/Target/RISCV/RISCVMakeCompressible.cpp)
(contributed by Lewis Revill and Craig Blackmore).  Rather than trying to
improve generated code performance, this is solely focused on reducing code
size, and may increase the static instruction count in order to do so (which
is why it's currently only enabled at the `-Oz` optimisation level). It looks
for cases where an instruction has been selected which can't be represented by
one of the compressed (16-bit as opposed to 32-bit wide) instruction forms.
For instance due to the register not being one of the registers addressable
from the compressed instruction, or the offset being out of range). It will
then look for opportunities to transform the input to make the instructions
compressible. Grabbing two examples from the header comment of the pass:

```asm
; 'zero' register not addressable in compressed store.
                 =>   li a1, 0
sw zero, 0(a0)   =>   c.sw a1, 0(a0)
sw zero, 8(a0)   =>   c.sw a1, 8(a0)
sw zero, 4(a0)   =>   c.sw a1, 4(a0)
sw zero, 24(a0)  =>   c.sw a1, 24(a0) 
```

and
```asm
; compressed stores support limited offsets
lui a2, 983065     =>   lui a2, 983065 
                   =>   addi  a3, a2, -256
sw  a1, -236(a2)   =>   c.sw  a1, 20(a3)
sw  a1, -240(a2)   =>   c.sw  a1, 16(a3)
sw  a1, -244(a2)   =>   c.sw  a1, 12(a3)
sw  a1, -248(a2)   =>   c.sw  a1, 8(a3)
sw  a1, -252(a2)   =>   c.sw  a1, 4(a3)
sw  a0, -256(a2)   =>   c.sw  a0, 0(a3)
```

There's a whole range of other backend codegen improvements, including
additions to existing RISC-V specific passes but unfortunately it's not
feasible to enumerate them all.

One improvement to note from the Clang frontend is that [the C intrinsics for
the RISC-V Vector extension are now lazily
generated](https://reviews.llvm.org/rG7a5cb15ea6fa), avoiding the need to
parse a huge pre-generated header file and improving compile times.

## Support for new instruction set extensions

A batch of new instruction set extensions [were ratified at the end of last
year](https://riscv.org/announcements/2021/12/riscv-ratifies-15-new-specifications/)
(see also the [recently ratified extension
list](https://wiki.riscv.org/display/HOME/Recently+Ratified+Extensions).  LLVM
14 already [featured a number of
these](https://releases.llvm.org/14.0.0/docs/ReleaseNotes.html#changes-to-the-risc-v-target)
(with the vector and ratified bit manipulation extensions no longer being
marked as experimental). In LLVM 15 we were able to fill in some of the gaps,
adding support for additional ratified extensions as well as some new
experimental extensions.

In particular:
* Assembler and disassembler support for the [Zdinx, Zfinx, Zhinx, and Zhinxmin
  extensions](https://github.com/riscv/riscv-zfinx/blob/main/zfinx-1.0.0.pdf).
  Cores that implement these extensions store double/single/half precision
  floating point values in the integer register file (GPRs) as opposed to having a
  separate floating-point register file (FPRs).
  * The instructions defined in the conventional floating point extensions are
    defined to instead operate on the general purpose registers, and
    instructions that become redundant (namely those that involve moving
    values from FPRs to GPRs) are removed.
  * Cores might implement these extensions rather than the conventional
    floating-point in order to reduce the amount of architectural state that
    is needed, reducing area and context-switch cost. The downside is of
    course that register pressure for the GPRs will be increased.
  * Codegen for these extensions is not yet supported (i.e. the extensions are
    only supported for assembly input or inline assembly). A patch to provide
    this support [is under review](https://reviews.llvm.org/D122918) though.
* Assembler and disassembler support for the [Zicbom, Zicbop, and Zicboz
  extensions](https://github.com/riscv/riscv-CMOs/blob/master/specifications/cmobase-v1.0.pdf).
  These cache management operation (CMO) extensions add new instructions for
  invalidating, cleaning, and flushing cache blocks (Zicbom), zeroing cache
  blocks (Zicboz), and prefetching cache blocks (Zicbop).
  * These operations aren't currently exposed via C intrinsics, but these will
    be added once the appropriate naming has been agreed.
  * One of the questions raised during implementation was about the [preferred
    textual format for the
    operands](https://github.com/riscv/riscv-CMOs/issues/47). Specifically,
    whether it should be e.g. `cbo.clean (a0)`/`cbo.clean 0(a0)` to match the
    format used for other memory operations, or `cbo.clean a0` as was used in
    an early binutils patch. We were able to agree between the CMO working
    group, LLVM, and GCC developers on the former approach.
* Assembler, disassembler, and codegen support for the [Zmmul
  extension](https://github.com/riscv/riscv-isa-manual/commit/f518c259c008f926eba4aba67804f62531b6e94b).
  This extension is just a subset of the 'M' extension providing just the
  multiplication instructions without the division instructions.
* Assembler and disassembler support for the additional CSRs (control and
  status registers) and instructions introduced by the [hypervisor and
  Svinval additions to the privileged architecture
  specification](https://github.com/riscv/riscv-isa-manual/commit/f518c259c008f926eba4aba67804f62531b6e94b).
  Svinval provides fine-grained address-translation cache invalidation and
  fencing, while the hypervisor extension provides support for efficiently
  virtualising the supervisor-level architecture (used to implement KVM for
  RISC-V).
* Assembler and disassembler support for the
  [Zihintpause
  extension](https://github.com/riscv/riscv-isa-manual/blob/266f3759c9c88b0ae18cfca70f875662d89b52db/src/zihintpause.tex).
  This adds the `pause` instruction intended for use as a hint within
  spin-wait loops.
  * Zihintpause was actually the first extension to [go
    through](https://riscv.org/announcements/2021/02/risc-v-international-unveils-fast-track-architecture-extension-process-and-ratifies-zihintpause-extension/)
    RISC-V International's fast-track architecture extension process back in
    early 2021. We were clearly slow to add it to LLVM, but are trying to keep
    a closer eye on ratified extensions going forwards.
* Support was added for the not yet ratified [Zvfh
  extension](https://github.com/riscv/riscv-v-spec/pull/780), providing
  support for half precision floating point values in RISC-V vectors.
  * Unlike the extensions listed above, support for Zvfh is experimental. This
    is a status we use within the RISC-V backend for extensions that are not
    yet ratified and may change from release to release with no guarantees on
    backwards compatibility. Enabling support for such extensions requires
    passing `-menable-experimental-extensions` to Clang and specifying the
    extension's version when listing it in the `-march` string.

It's not present in LLVM 15, but LLVM 16 onwards will feature a
[user guide for the RISC-V
target](https://github.com/llvm/llvm-project/blob/main/llvm/docs/RISCVUsage.rst)
summarising the level of support for each extension (huge thanks to Philip
Reames for kicking off this effort).

## Other changes

In case I haven't said it enough times, there's far more interesting changes
than I could reasonably cover. Apologies if I've missed your favourite new
feature or improvement. In particular, I've said relatively little about
RISC-V Vector support. There's been a long series of improvements and
correctness fixes in the LLVM 15 development window, after RVV was made
non-experimental in LLVM 14 and there's much more to come in LLVM 16 (e.g.
scalable vectorisation becoming enabled by default).
