+++
published = 2024-02-20
description = "Helper script to dump P-Code for a hex-encoded instruction"
+++

# Clarifying instruction semantics with P-Code

I've recently had a need to step through quite a bit of disassembly for
different architectures, and although some architectures have well-written ISA
manuals it can be a bit jarring switching between very different assembly
syntaxes (like "source, destination" for AT&T vs "destination, source" for
just about everything else) or tedious looking up different ISA manuals to
clarify the precise semantics. I've been using a very simple script to help
convert an encoded instruction to a target-independent description of its
semantics, and thought I may as well share it as well as some thoughts on
its limitations.

## [instruction_to_pcode](https://github.com/muxup/medley)

[The script](https://github.com/muxup/medley) is simplicity itself, thanks to
the [pypcode](https://github.com/angr/pypcode) bindings to
[Ghidra](https://en.wikipedia.org/wiki/Ghidra)'s SLEIGH library which provides
an interface to convert an input to the P-Code representation. Articles like
[this one](https://riverloopsecurity.com/blog/2019/05/pcode/) provide an
introduction and there's the [reference manual in the Ghidra
repo](https://htmlpreview.github.io/?https://github.com/NationalSecurityAgency/ghidra/blob/master/GhidraDocs/languages/html/pcoderef.html)
but it's probably easiest to just look at a few examples. P-Code is used as
the basis of Ghidra's decompiler and provides a consistent human-readable
description of the semantics of instructions for supported targets.

Here's an example aarch64 instruction:

```
$ ./instruction_to_pcode aarch64 b874c925
-- 0x0: ldr w5, [x9, w20, SXTW #0x0]
0) unique[0x5f80:8] = sext(w20)
1) unique[0x7200:8] = unique[0x5f80:8]
2) unique[0x7200:8] = unique[0x7200:8] << 0x0
3) unique[0x7580:8] = x9 + unique[0x7200:8]
4) unique[0x28b80:4] = *[ram]unique[0x7580:8]
5) x5 = zext(unique[0x28b80:4])
```

In the above you can see that the disassembly for the instruction is dumped,
and then 5 P-Code instructions are printed showing the semantics. These P-Code
instructions directly use the register names for architectural registers (as a
reminder, [AArch64 has 64-bit GPRs X0-X30 with the bottom halves acessible
through
W-W30](https://developer.arm.com/documentation/dui0801/l/Overview-of-AArch64-state/Registers-in-AArch64-state?lang=en)).
Intermediate state is stored in `unique[addr:width]` locations. So the above
instruction sign-extends `w20`, adds to `x9`, and reads a 32-bit value from
the resulting address, then zero-extends to 64-bits when storing into `x5`.

The output is somewhat more verbose for architectures with flag registers,
e.g. `cmpb $0x2f,-0x1(%r11)` produces:
```
./instruction_to_pcode x86-64 --no-reverse-input "41 80 7b ff 2f"
-- 0x0: CMP byte ptr [R11 + -0x1],0x2f
0) unique[0x3100:8] = R11 + 0xffffffffffffffff
1) unique[0xbd80:1] = *[ram]unique[0x3100:8]
2) CF = unique[0xbd80:1] < 0x2f
3) unique[0xbd80:1] = *[ram]unique[0x3100:8]
4) OF = sborrow(unique[0xbd80:1], 0x2f)
5) unique[0xbd80:1] = *[ram]unique[0x3100:8]
6) unique[0x28e00:1] = unique[0xbd80:1] - 0x2f
7) SF = unique[0x28e00:1] s< 0x0
8) ZF = unique[0x28e00:1] == 0x0
9) unique[0x13180:1] = unique[0x28e00:1] & 0xff
10) unique[0x13200:1] = popcount(unique[0x13180:1])
11) unique[0x13280:1] = unique[0x13200:1] & 0x1
12) PF = unique[0x13280:1] == 0x0
```

But simple instructions that don't set flags do produce concise P-Code:

```
$ ./instruction_to_pcode riscv64 "9d2d"
-- 0x0: c.addw a0,a1
0) unique[0x15880:4] = a0 + a1
1) a0 = sext(unique[0x15880:4])
```

## Other approaches

P-Code was an intermediate language I'd encountered before and of course
benefits from having an easy to use Python wrapper and fairly good support for
a range of ISAs in Ghidra. But there are lots of other options -
[angr](https://angr.io/) (which
uses Vex, taken from Valgrind) [compares some
options](https://docs.angr.io/en/latest/faq.html#why-did-you-choose-vex-instead-of-another-ir-such-as-llvm-reil-bap-etc)
and there's [more in this
paper](https://softsec.kaist.ac.kr/~soomink/paper/ase17main-mainp491-p.pdf).
Radare2 has [ESIL](https://book.rada.re/disassembling/esil.html), but while
I'm sure you'd get used to it, it doesn't pass the readability test for me.
The [rev.ng](https://rev.ng/) project uses QEMU's
[TCG](https://www.qemu.org/docs/master/devel/tcg-ops.html). This is an
attractive approach because you benefit from more testing and ISA extension
support for some targets vs P-Code (Ghidra support [is
lacking](https://github.com/NationalSecurityAgency/ghidra/pull/5778) for RVV,
bitmanip, and crypto extensions).

Another route would be to pull out the semantic definitions from a formal spec
(like [Sail](https://www.cl.cam.ac.uk/~pes20/sail/)) or even an easy to read
simulator (e.g. [Spike](https://github.com/riscv-software-src/riscv-isa-sim)
for RISC-V). But in both cases, definitions are written to minimise repetition
to some degree, while when expanding the semantics we prefer explicitness, so
would want to expand to a form that differs a bit from the Sail/Spike code as
written.
