+++
published = 2025-05-12
description = "A helper script for working with llvm-test-suite build configurations."
+++

# suite-helper

In my work on RISC-V LLVM, I end up working with the llvm-test-suite a lot,
especially as I put more effort into performance analysis, testing, and
regression hunting.
[suite-helper](https://github.com/muxup/medley/blob/main/suite-helper) is a
Python script that helps with some of the repetitive tasks when setting up,
building, and analysing [LLVM test
suite](https://github.com/llvm/llvm-test-suite) builds. (Worth nothing for
those who aren't LLVM regulars: llvm-test-suite is a separate repository to
LLVM and includes execution tests and benchmarks, which is different to the
targeted unit tests including in the LLVM monorepo).

[Get it from GitHub](https://github.com/muxup/medley/blob/main/suite-helper).

## Motivation

As always, it scratches an itch for me. The design target is to provide a
starting point that is hopefully good enough for many use cases, but it's easy
to modify (e.g. by editing the generated scripts or emitted command lines) if
doing something that isn't directly supported.

The main motivation for putting this script together came from my habit of
writing fairly detailed "lab notes" for most of my work. This typically
includes a listing of commands run, but I've found such listings rather
verbose and annoying to work with. This presented a good opportunity for
factoring out common tasks into a script, resulting in `suite-helper`.

## Functionality overview

`suite-helper` has the following subtools:

* create
  * Checkout llvm-test-suite to the given directory. Use the `--reference`
    argument to reference git objects from an existing local checkout.
* add-config
  * Add a build configuration using either the "cross" or "native" template.
    See `suite-helper add-config --help` for a listing of available options.
    For a build configuration 'foo', a `_rebuild-foo.sh` file will be created
    that can be used to build it within the `build.foo` subdirectory.
* status
  * Gives a listing of suite-helper managed build configurations that were
    detected, attempting to indicate if they are up to date or not (e.g.
    spotting if the hash of the compiler has changed).
* run
  * Run the given build configuration using `llvm-lit`, with any additional
    options passed on to lit.
* match-tool
  * A helper that is used by `suite-helper reduce-ll` but may be useful in
    your own reduction scripts. When looking at generated assembly or
    disassembly of an object file/binary and an area of interest, your natural
    inclination may well be to try to carefully craft logic to match something
    that has equivalent/similar properties. Credit to Philip Reames for
    underlining to me just how unresonably effective it is to completely
    ignore that inclination and just write something that naively matches a
    precise or near-precise assembly sequence. The resulting IR might include
    some extraneous stuff, but it's a lot easier to cut down after this
    initial minimisation stage, and a lot of the time it's good enough. The
    `match-tool` helper takes a multiline sequence of glob patterns as its
    argument, and will attempt to find a match for them (a sequential set of
    lines) on stdin. It also normalises whitespace.
* get-ll
  * Query ninja nad process its output to try to produce and execute a
    compiler command that will emit a .ll for the given input file (e.g. a .c
    file). This is a common first step for llvm-reduce, or for starting to
    inspect the compilation of a file with debug options enabled.
* reduce-ll
  * For me, it's fairly common to want to produce a minimised .ll file that
    produces a certain assembly pattern, based on compiling a given source
    input. This subtool automates that process, using `get-ll` to retrieve the
    ll, then `llvm-reduce` and `match-tool` to match the assembly.


## Usage example

`suite-helper` isn't intended to avoid the need to understand how to build the
LLVM test suite using CMake and run it using `lit`, rather it aims to
streamline the flow. As such, a good starting point might be to work through
some llvm-test-suite builds yourself and then look here to see if anything
makes your use case easier or not.

All of the notes above may seem rather abstract, so here is an example of
using the helper to while investigating some poorly canonicalised
instructions and testing my work-in-progress patch to address them.

```sh
suite-helper create llvmts-redundancies --reference ~/llvm-test-suite

for CONFIG in baseline trial; do
  suite-helper add-config cross $CONFIG \
    --cc=~/llvm-project/build/$CONFIG/bin/clang \
    --target=riscv64-linux-gnu \
    --sysroot=~/rvsysroot \
    --cflags="-march=rva22u64 -save-temps=obj" \
    --spec2017-dir=~/cpu2017 \
    --extra-cmake-args="-DTEST_SUITE_COLLECT_CODE_SIZE=OFF -DTEST_SUITE_COLLECT_COMPILE_TIME=OFF"
  ./_rebuild-$CONFIG.sh
done

# Test suite builds are now available in build.baseline and build.trial, and
# can be compared with e.g. ./utils/tdiff.py.

# A separate script had found a suspect instruction sequence in sqlite3.c, so
# let's get a minimal reproducer.
suite-helper reduce build.baseline ./MultiSource/Applications/sqlite3/sqlite3.c \
  'add.uw  a0, zero, a2
   subw    a4, a4, zero' \
  --reduce-bin=~/llvm-project/build/baseline/bin/llvm-reduce \
  --llc-bin=~/llvm-project/build/baseline/bin/llc \
  --llc-args=-O3
```

The above produces the following reduced.ll:

```ll
target datalayout = "e-m:e-p:64:64-i64:64-i128:128-n32:64-S128"
target triple = "riscv64-unknown-linux-gnu"

define fastcc ptr @sqlite3BtreeDataFetch(ptr %pCur, ptr %pAmt, ptr %0, i16 %1, i32 %conv20.i, i1 %tobool.not.i) #0 {
entry:
  br i1 %tobool.not.i, label %if.else9.i, label %fetchPayload.exit

if.else9.i:                                       ; preds = %entry
  br label %fetchPayload.exit

fetchPayload.exit:                                ; preds = %if.else9.i, %entry
  %nKey.0.i = phi i32 [ %conv20.i, %if.else9.i ], [ 0, %entry ]
  %idx.ext16.i = zext i32 %nKey.0.i to i64
  %add.ptr17.i = getelementptr i8, ptr %0, i64 %idx.ext16.i
  %sub.i = sub i32 %conv20.i, %nKey.0.i
  store i32 %sub.i, ptr null, align 4
  ret ptr %add.ptr17.i
}

attributes #0 = { "target-features"="+b" }
```
