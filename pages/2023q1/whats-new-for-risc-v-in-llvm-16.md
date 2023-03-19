+++
published = 2023-03-18
description = "Details on newly added RISC-V features and improvements to Clang, LLVM, and other subprojects for LLVM 16.x."
+++
# What's new for RISC-V in LLVM 16

LLVM 16.0.0 was [just
released today](https://discourse.llvm.org/t/llvm-16-0-0-release/69326), and
as [I did for LLVM 15](/pages/2022q3/whats-new-for-risc-v-in-llvm-15.md), I
wanted to highlight some of the RISC-V specific changes and improvements. This
is very much a tour of a chosen subset of additions rather than an attempt to
be exhaustive. If you're interested in RISC-V, you may also want to check out
my recent attempt to enumerate the [commercially available RISC-V
SoCs](/pages/2023q1/commercially-available-risc-v-silicon.md) and if you want
to find out what's going on in LLVM as a whole on a week-by-week basis, then
I've got [the perfect newsletter for you](https://llvmweekly.org/).

In case you're not familiar with LLVM's release schedule, it's worth noting
that there are two major LLVM releases a year (i.e. one roughly every 6
months) and these are timed releases as opposed to being cut when a pre-agreed
set of feature targets have been met. We're very fortunate to benefit from an
active and growing set of contributors working on RISC-V support in LLVM
projects, who are responsible for the work I describe below - thank you!
I coordinate biweekly sync-up calls for RISC-V LLVM contributors, so if you're
working in this area please [consider dropping
in](https://discourse.llvm.org/c/code-generation/riscv/57).

## Documentation

LLVM 16 is the first release featuring a user guide for the RISC-V target
([16.0.0 version](https://releases.llvm.org/16.0.0/docs/RISCVUsage.html),
[current HEAD](https://llvm.org/docs/RISCVUsage.html). This fills a
long-standing gap in our documentation, whereby it was difficult to tell at a
glance the expected level of support for the various RISC-V instruction set
extensions (standard, vendor-specific, and experimental extensions of either
type) in a given LLVM release. We've tried to keep it concise but informative,
and add a brief note to describe any known limitations that end users should
know about. Thanks again to Philip Reames for kicking this off, and the
reviewers and contributors for ensuring it's kept up to date.

## Vectorization

LLVM 16 was a big release for vectorisation. As well as a long-running strand
of work making incremental improvements (e.g. better cost modelling) and
fixes, scalable vectorization was [enabled by
default](https://reviews.llvm.org/rG15c645f7ee67). This allows LLVM's [loop
vectorizer](https://llvm.org/docs/Vectorizers.html#loop-vectorizer) to use
scalable vectors when profitable. Follow-on work
[enabled](https://reviews.llvm.org/rGb45a262679ab) support for loop
vectorization using fixed length vectors and [disabled vectorization of
epilogue loops](https://reviews.llvm.org/rG269bc684e7a0). See the talk
[optimizing code for scalable vector
architectures](https://www.youtube.com/watch?v=daWLCyhwrZ8)
([slides](https://llvm.org/devmtg/2021-11/slides/2021-OptimizingCodeForScalableVectorArchitectures.pdf))
by Sander de Smalen for more information about scalable vectorization in LLVM
and [introduction to the RISC-V vector
extension](https://eupilot.eu/wp-content/uploads/2022/11/RISC-V-VectorExtension-1-1.pdf)
by Roger Ferrer Ibáñez for an overview of the vector extension and some of its
codegen challenges.

The RISC-V vector intrinsics supported by Clang have changed (to match e.g.
[this](https://github.com/riscv-non-isa/rvv-intrinsic-doc/pull/186) and
[this](https://github.com/riscv-non-isa/rvv-intrinsic-doc/pull/185)) during
the 16.x development process in a backwards incompatible way, as the [RISC-V
Vector Extension Intrinsics
specification](https://github.com/riscv-non-isa/rvv-intrinsic-doc) evolves
towards a v1.0. In retrospect, it would have been better to keep the
intrinsics behind an experimental flag when the vector codegen and MC layer
(assembler/disassembler) support became stable, and this is something we'll be
more careful of for future extensions. The good news is that thanks to
Yueh-Ting Chen, headers [are
available](https://github.com/riscv-non-isa/rvv-intrinsic-doc/tree/master/auto-generated/rvv-v0p10-compatible-headers)
that provide the old-style intrinsics mapped to the new version.

## Support for new instruction set extensions

I refer to 'experimental' support many times below. See the [documentation on
experimental extensions within RISC-V
LLVM](https://releases.llvm.org/16.0.0/docs/RISCVUsage.html#experimental-extensions)
for guidance on what that means. One point to highlight is that the extensions
remain experimental until they are ratified, which is why some extensions on
the list below are 'experimental' despite the fact the LLVM support needed is
trivial. On to the list of newly added instruction set extensions:

* Experimental support for the
  [Zca, Zcf, and
  Zcd](https://github.com/riscv/riscv-code-size-reduction/releases/tag/V0.70.1-TOOLCHAIN-DEV)
  instruction set extensions. These are all 16-bit instructions and are being
  defined as part of the output of the RISC-V code size reduction working
  group.
  * Zca is just a subset of the standard 'C' compressed instruction set
    extension but without floating point loads/stores.
  * Zcf is also a subset of the standard 'C' compressed instruction set
    extension, including just the single precision floating point loads and
    stores (`c.flw`, `c.flwsp`, `c.fsw`, `c.fswsp`).
  * Zcd, as you might have guessed, just includes the double precision
    floating point loads and stores from the standard 'C' compressed
    instruction set extension (`c.fld`, `c.fldsp`, `c.fsd`, `c.fsdsp`).
* Experimental support for the
  [Zihintntl](https://github.com/riscv/riscv-isa-manual/releases/tag/draft-20220831-bf5a151)
  instruction set extension. This provides a small set of instructions that
  can be used to hint that the memory accesses of the following instruction
  exhibits poor temporal locality.
* Experimental support for the
  [Zawrs](https://github.com/riscv/riscv-zawrs/releases/download/V1.0-rc3/Zawrs.pdf)
  instruction set extension, providing a pair of instructions meant for use in
  a polling loop allowing a core to enter a low-power state and wait on a
  store to a memory location.
* Experimental support for the
  [Ztso](https://github.com/riscv/riscv-isa-manual/releases/download/draft-20220723-10eea63/riscv-spec.pdf)
  extension, which for now just means setting the appropriate ELF header flag.
  If a core implements Ztso, it implements the Total Store Ordering memory
  consistency model. Future releases will provide alternate lowerings of
  atomics operations that take advantage of this.
* Code generation support for the [Zfhmin
  extension](https://drive.google.com/file/d/1z3tQQLm5ALsAD77PM0l0CHnapxWCeVzP/view)
  (load/store, conversion, and GPR/FPR move support for 16-bit floating point
  values).
* Codegen and assembler/disassembler support for the
  [XVentanaCondOps](https://github.com/ventanamicro/ventana-custom-extensions/releases/download/v1.0.0/ventana-custom-extensions-v1.0.0.pdf)
  vendor extension, which provides conditional arithmetic and move/select
  operations.
* Codegen and assembler/disassembler support for the
  [XTHeadVdot](https://github.com/T-head-Semi/thead-extension-spec/blob/master/xtheadvdot.adoc)
  vendor extension, which implements vector integer four 8-bit multiple and
  32-bit add.

## LLDB

LLDB has started to become usable for RISC-V in this period due to
work by contributor 'Emmer'. As they [summarise
here](https://discourse.llvm.org/t/is-lldb-for-riscv-ready-to-use/68326/2),
LLDB should be usable for debugging RV64 programs locally but support is
lacking for remote debug (e.g. via the gdb server protocol). During the LLVM
16 development window, LLDB gained [support for software single stepping on
RISC-V](https://reviews.llvm.org/rG4fc7e9cba24b), support in
`EmulateInstructionRISCV` for
[RV{32,64}I](https://reviews.llvm.org/rGff7b876aa75d), as well as extensions
[A and M](https://reviews.llvm.org/rG49f9af1864d9),
[C](https://reviews.llvm.org/rG05ae747a5353),
[RV32F](https://reviews.llvm.org/rG6d4ab6d92179) and
[RV64F](https://reviews.llvm.org/rG2d7f43f9eaf3), and
[D](https://reviews.llvm.org/rG6493fc4bccd2).

## Short forward branch optimisation

Another improvement that's fun to look more closely at is support for "short
forward branch optimisation" for the [SiFive 7
series](https://www.sifive.com/press/sifive-core-ip-7-series-creates-new-class-of-embedded)
cores. What does this mean? Well, let's start by looking at the problem it's
trying to solve. The base RISC-V ISA doesn't include conditional moves or
predicated instructions, which can be a downside if your code features
unpredictable short forward branches (with the ensuing cost in terms of
branch mispredictions and bloating branch predictor state). The [ISA
spec](https://github.com/riscv/riscv-isa-manual/releases/download/Ratified-IMAFDQC/riscv-spec-20191213.pdf)
includes commentary on this decision (page 23), noting some disadvantages of
adding such instructions to the specification and noting microarchitectural
techniques exist to convert short forward branches into predicated code
internally. In the case of the SiFive 7 series, this is achieved using
[macro-op fusion](https://en.wikichip.org/wiki/macro-operation_fusion) where a
branch over a single ALU instruction is fused and executed as a single
conditional instruction.

In the LLVM 16 cycle, compiler optimisations targeting this microarchitectural
feature were enabled for [conditional move style
sequences](https://reviews.llvm.org/rG2b32e4f98b4f) (i.e. branch over a
register move) as well as for [other ALU
operations](https://reviews.llvm.org/rGda7415acdafb). The job of the
compiler here is of course to emit a sequence compatible with the
micro-architectural optimisation when possible and profitable. I'm not aware
of other RISC-V designs implementing a similar optimisation - although there
are developments in terms of instructions to support such operations directly
in the ISA which would avoid the need for such microarchitectural tricks. See
[XVentanaCondOps](https://github.com/ventanamicro/ventana-custom-extensions/releases/download/v1.0.0/ventana-custom-extensions-v1.0.0.pdf),
[XTheadCondMov](https://github.com/T-head-Semi/thead-extension-spec/blob/master/xtheadcondmov.adoc),
the previously proposed but now abandoned [Zbt
extension](https://github.com/riscv/riscv-bitmanip/releases/download/v0.93/bitmanip-0.93.pdf)
(part of the earlier bitmanip spec) and more recently the proposed
[Zicond](https://github.com/riscv/riscv-zicond) (integer conditional
operations) standard extension.

## Atomics

It's perhaps not surprising that code generation for atomics can be tricky to
understand, and the [LLVM documentation on atomics codegen and
libcalls](https://llvm.org/docs/Atomics.html#atomics-and-codegen) is actually
one of the best references on the topic I've found. A particularly important
note in that document is that if a backend supports any inline lock-free
atomic operations at a given size, all operations of that size must be
supported in a lock-free manner. If targeting a RISC-V CPU without the atomics
extension, all atomics operations would usually be lowered to `__atomic_*`
libcalls. But if we know a bit more about the target, it's possible to do
better - for instance, a single-core microcontroller could implement an atomic
operation in a lock-free manner by disabling interrupts (and conventionally,
lock-free implementations of atomics are provided through `__sync_*`
libcalls).  This kind of setup is exactly what the [`+forced-atomics`
feature](https://reviews.llvm.org/rGf5ed0cb217a9988f97b55f2ccb053bca7b41cc0c)
enables, where atomic load/store can be lowered to a load/store with
appropriate fences (as is supported in the base ISA) while other atomic
operations generate a `__sync_*` libcall.

There's also been a very minor improvement for targets with native atomics
support (the 'A' instruction set extension) that I may as well mention while
on the topic. As you might know, atomic operations such as compare and swap
that are lowered to an instruction sequence involving `lr.{w,d}` (load reserved) and
`sc.{w,d}` (store conditional). There are very specific rules about these
instruction sequences that must be met to align with the [architectural
forward progress
guarantee](https://github.com/riscv/riscv-isa-manual/releases/download/Ratified-IMAFDQC/riscv-spec-20191213.pdf) (section 8.3, page 51),
which is why we expand to a fixed instruction sequence at a very late stage in
compilation (see [original
RFC](https://lists.llvm.org/pipermail/llvm-dev/2018-June/123993.html)). This
means the sequence of instructions implementing the atomic operation are
opaque to LLVM's optimisation passes and are treated as a single unit. The
obvious disadvantage of avoiding LLVM's optimisations is that sometimes there
are optimisations that would be helpful and wouldn't break that
forward-progress guarantee. One that came up in real-world code was the lack
of branch folding, which would have simplified a branch in the expanded
`cmpxchg` sequence that just targets another branch with the same condition
(by just folding in the eventual target). With some [relatively simple
logic](https://reviews.llvm.org/rGce381281940f), this suboptimal codegen is
resolved.

```asm
; Before                 => After
.loop:                   => .loop
  lr.w.aqrl a3, (a0)     => lr.w.aqrl a3, (a0)
  bne a3, a1, .afterloop => bne a3, a1, .loop
  sc.w.aqrl a4, a2, (a0) => sc.w.aqrl a4, a2, (a0)
  bnez a4, .loop         => bnez a4, .loop
.aferloop:               =>
  bne a3, a1, .loop      =>
  ret                    => ret
```

## Assorted optimisations

As you can imagine, there's been a lot of incremental minor improvements over
the past ~6 months. I unfortunately only have space (and patience) to highight
a few of them.

A new pre-regalloc pseudo instruction expansion pass was
[added](https://reviews.llvm.org/rG260a64106854986a981e49ed87ee740460a23eb5)
in order to allow [optimising](https://reviews.llvm.org/rG0bc177b6f54b) the
global address access instruction sequences such as those found in the [medany
code
model](https://github.com/riscv-non-isa/riscv-toolchain-conventions/blob/master/README.mkd#specifying-the-target-code-model-with--mcmodel)
(and was later [broadened further](https://reviews.llvm.org/rGda5b1bf5bb0f)).
This results in improvements such as the following (note: this transformation
was already supported for the medlow code model):

```asm
; Before                            => After
.Lpcrel_hi1:                        => .Lpcrel_hi1
auipc a0, %pcrel_hi1(ga)            => auipc a0, %pcrel_hi1(ga+4)
addi a0, a0, %pcrel_lo(.Lpcrel_hi1) =>
lw a0, 4(a0)                        => lw a0, %pcrel_lo(.Lpcrel_hi1)(a0)
```

A missing target hook (`isUsedByReturnOnly`) had been preventing tail calling
libcalls in some cases. This was
[fixed](https://reviews.llvm.org/rG47b1f8362aa4), and later support was added
for [generating an inlined sequence of
instructions](https://reviews.llvm.org/rGe94dc58dff1d) for some of the
floating point libcalls.

The RISC-V compressed instruction set extension defines a number of 16-bit
encodings that map to a 32-bit longer form (with restrictions on addressable
registers in the compressed form of course). The conversion 32-bit
instructions 16-bit forms when possible happens at a very late stage, after
instruction selection. But of course over time, we've introduced more tuning
to influence codegen decisions in cases where a choice can be made to produce
an instruction that can be compressed, rather than one that can't. A recent
addition to this was the [RISCVStripWSuffix
pass](https://reviews.llvm.org/rGd64d3c5a8f81), which for RV64 targets will
convert `addw` and `slliw` to `add` or `slli` respectively when it can be
determined that all the users of its result only use the lower 32 bits. This
is a minor code size saving, as `slliw` has no matching compressed instruction
and `c.addw` can address a more restricted set of registers than `c.add`.

## Other

At the risk of repeating myself, this has been a selective tour of some
additions I thought it would be fun to write about. Apologies if I've missed
your favourite new feature or improvement - the [LLVM release
notes](https://releases.llvm.org/16.0.0/docs/ReleaseNotes.html#changes-to-the-risc-v-backend)
will include some things I haven't had space for here. Thanks again for
everyone who has been contributing to make the RISC-V in LLVM even better.

If you have a RISC-V project you think me and my colleagues and at Igalia may
be able to help with, then do [get in touch](https://www.igalia.com/contact/)
regarding our services.
