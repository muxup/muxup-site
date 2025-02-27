+++
published = 2025-02-27
description = "TL;DR: ccache base_dir saves the day"
+++

# ccache for LLVM builds across multiple directories

## Problem description

If you're regularly rebuilding a large project like LLVM, you almost certainly
want to be using [ccache](https://ccache.dev/). Incremental builds are
helpful, but it's quite common to be swapping between different commit IDs and
it's very handy to have the build complete relatively quickly without needing
any explicit thought on your side. Enabling `ccache` with LLVM's CMake build
system is trivial, but out of the box you will suffer from cache misses if
building `llvm-project` in different build directories, even for an identical
commit and identical build settings (and even for identical source directories,
i.e. without even considering separate checkouts or separate git work trees):

```sh
mkdir -p exp && cd exp
ccache -zC # Clear old ccache
git clone --reference-if-able ~/llvm-project https://github.com/llvm/llvm-project/
cd llvm-project
cmake -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=clang \
  -DCMAKE_CXX_COMPILER=clang++ \
  -DLLVM_ENABLE_LLD=ON \
  -DLLVM_TARGETS_TO_BUILD="X86" \
  -DCMAKE_{C,CXX}_COMPILER_LAUNCHER=ccache \
  -B build/a \
  -S llvm
cmake --build build/a
echo "@@@@@@@@@@ Stats after building build/a @@@@@@@@@@"
ccache -s
cmake -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=clang \
  -DCMAKE_CXX_COMPILER=clang++ \
  -DLLVM_ENABLE_LLD=ON \
  -DLLVM_TARGETS_TO_BUILD="X86" \
  -DCMAKE_{C,CXX}_COMPILER_LAUNCHER=ccache \
  -B build/b \
  -S llvm
cmake --build build/b
echo "@@@@@@@@@@ Stats after building build/b @@@@@@@@@@"
ccache -s
```

We see no cache hits:
```
@@@@@@@@@@ Stats after building build/a @@@@@@@@@@
Cacheable calls:    2252 /   2253 (99.96%)
  Hits:                0 /   2252 ( 0.00%)
    Direct:            0
    Preprocessed:      0
  Misses:           2252 /   2252 (100.0%)
Uncacheable calls:     1 /   2253 ( 0.04%)
Local storage:
  Cache size (GiB):  0.2 / 1024.0 ( 0.02%)
  Cleanups:          256
  Hits:                0 /   2252 ( 0.00%)
  Misses:           2252 /   2252 (100.0%)

@@@@@@@@@@ Stats after building build/b @@@@@@@@@@
Cacheable calls:    4504 /   4506 (99.96%)
  Hits:               71 /   4504 ( 1.58%)
    Direct:            0 /     71 ( 0.00%)
    Preprocessed:     71 /     71 (100.0%)
  Misses:           4433 /   4504 (98.42%)
Uncacheable calls:     2 /   4506 ( 0.04%)
Local storage:
  Cache size (GiB):  0.5 / 1024.0 ( 0.04%)
  Cleanups:          256
  Hits:               71 /   4504 ( 1.58%)
  Misses:           4433 /   4504 (98.42%)
```

Let's take a look at a build command to check what's going on:

```sh
$ ninja -C build/b -t commands lib/Support/CMakeFiles/LLVMSupport.dir/APInt.cpp.o
ccache /usr/bin/clang++ -DGTEST_HAS_RTTI=0 -D_GNU_SOURCE -D__STDC_CONSTANT_MACROS -D__STDC_FORMAT_MACROS -D__STDC_LIMIT_MACROS -I/home/asb/exp/llvm-project/build/b/lib/Support -I/home/asb/exp/llvm-project/llvm/lib/Support -I/home/asb/exp/llvm-project/build/b/include -I/home/asb/exp/llvm-project/llvm/include -fPIC -fno-semantic-interposition -fvisibility-inlines-hidden -Werror=date-time -Werror=unguarded-availability-new -Wall -Wextra -Wno-unused-parameter -Wwrite-strings -Wcast-qual -Wmissing-field-initializers -pedantic -Wno-long-long -Wc++98-compat-extra-semi -Wimplicit-fallthrough -Wcovered-switch-default -Wno-noexcept-type -Wnon-virtual-dtor -Wdelete-non-virtual-dtor -Wsuggest-override -Wstring-conversion -Wmisleading-indentation -Wctad-maybe-unsupported -fdiagnostics-color -ffunction-sections -fdata-sections -Werror=global-constructors -O3 -DNDEBUG -std=c++17  -fno-exceptions -funwind-tables -fno-rtti -MD -MT lib/Support/CMakeFiles/LLVMSupport.dir/APInt.cpp.o -MF lib/Support/CMakeFiles/LLVMSupport.dir/APInt.cpp.o.d -o lib/Support/CMakeFiles/LLVMSupport.dir/APInt.cpp.o -c /home/asb/exp/llvm-project/llvm/lib/Support/APInt.cpp
```

We can see that as LLVM generates header files, it has absolute directories
specified in `-I` within the build directory, which of course differs for
build `a` and build `b` above, causing a cache miss. Even if there was a
workaround for the generated headers, we'd still fail to get cache hits if
building from different llvm-project checkouts or worktrees.

## Solution

Unsurprisingly, this is a common problem with `ccache` and it has [good
documentation](https://ccache.dev/manual/latest.html#_compiling_in_different_directories)
on the solution. It advises:
* Setting the `base_dir` ccache option to enable ccache's rewriting of
  absolute to relative paths for any path with that prefix.
* Setting the `absolute_paths_in_stderr` ccache option in order to rewrite
  relative paths in stderr output to absolute (thus avoiding confusing error
  messages).
  * I have to admit that trialling this alongside forcing an error in a header
    with `# error "forced error"` I'm not sure I see a difference for Clang's
    output when attempting to build LLVM.
* If compiling with `-g`, use the `-fdebug-prefix-map` option.

The ccache changes can be actioned by:
```sh
ccache --set-config base_dir=/home
ccache --set-config absolute_paths_in_stderr=true
```

The `-fdebug-prefix-map` option can be enabled by setting
`-DLLVM_USE_RELATIVE_PATHS_IN_DEBUG_INFO=ON` in your CMake invocation.

## Testing the solution

Repeating the cmake and ccache invocations from earlier, we see that `build/b`
had almost a 100% hit rate:

```
@@@@@@@@@@ Stats after building build/a @@@@@@@@@@
Cacheable calls:    2252 /   2253 (99.96%)
  Hits:                0 /   2252 ( 0.00%)
    Direct:            0
    Preprocessed:      0
  Misses:           2252 /   2252 (100.0%)
Uncacheable calls:     1 /   2253 ( 0.04%)
Local storage:
  Cache size (GiB):  0.2 / 1024.0 ( 0.02%)
  Cleanups:          256
  Hits:                0 /   2252 ( 0.00%)
  Misses:           2252 /   2252 (100.0%)

@@@@@@@@@@ Stats after building build/b @@@@@@@@@@
Cacheable calls:    4504 /   4506 (99.96%)
  Hits:             2251 /   4504 (49.98%)
    Direct:         2251 /   2251 (100.0%)
    Preprocessed:      0 /   2251 ( 0.00%)
  Misses:           2253 /   4504 (50.02%)
Uncacheable calls:     2 /   4506 ( 0.04%)
Local storage:
  Cache size (GiB):  0.2 / 1024.0 ( 0.02%)
  Cleanups:          256
  Hits:             2251 /   4504 (49.98%)
  Misses:           2253 /   4504 (50.02%)
```

And additionally building llvm from a new worktree (i.e. a different absolute
path to the source directory):

```sh
git worktree add -b main-wt1 wt1 && cd wt1
cmake -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=clang \
  -DCMAKE_CXX_COMPILER=clang++ \
  -DLLVM_ENABLE_LLD=ON \
  -DLLVM_TARGETS_TO_BUILD="X86" \
  -DCMAKE_{C,CXX}_COMPILER_LAUNCHER=ccache \
  -B build/c \
  -S llvm
cmake --build build/c
echo "@@@@@@@@@@ Stats after building build/c @@@@@@@@@@"
ccache -s
```

Which results in the following stats (i.e., another close to 100% hit rate):

```
@@@@@@@@@@ Stats after building build/c @@@@@@@@@@
Cacheable calls:    6756 /   6759 (99.96%)
  Hits:             4502 /   6756 (66.64%)
    Direct:         4502 /   4502 (100.0%)
    Preprocessed:      0 /   4502 ( 0.00%)
  Misses:           2254 /   6756 (33.36%)
Uncacheable calls:     3 /   6759 ( 0.04%)
Local storage:
  Cache size (GiB):  0.2 / 1024.0 ( 0.02%)
  Cleanups:          256
  Hits:             4502 /   6756 (66.64%)
  Misses:           2254 /   6756 (33.36%)
```

And building with `-DLLVM_USE_RELATIVE_PATHS_IN_DEBUG_INFO=ON` and
`-DCMAKE_BUILD_TYPE=Debug`:

```sh
cmake -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_C_COMPILER=clang \
  -DCMAKE_CXX_COMPILER=clang++ \
  -DLLVM_ENABLE_LLD=ON \
  -DLLVM_TARGETS_TO_BUILD="X86" \
  -DCMAKE_{C,CXX}_COMPILER_LAUNCHER=ccache \
  -DLLVM_USE_RELATIVE_PATHS_IN_DEBUG_INFO=ON \
  -B build/debug_a \
  -S llvm
cmake --build build/debug_a
echo "@@@@@@@@@@ Stats after building build/debug_a @@@@@@@@@@"
ccache -s
cmake -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_C_COMPILER=clang \
  -DCMAKE_CXX_COMPILER=clang++ \
  -DLLVM_ENABLE_LLD=ON \
  -DLLVM_TARGETS_TO_BUILD="X86" \
  -DCMAKE_{C,CXX}_COMPILER_LAUNCHER=ccache \
  -DLLVM_USE_RELATIVE_PATHS_IN_DEBUG_INFO=ON \
  -B build/debug_b \
  -S llvm
cmake --build build/debug_b
echo "@@@@@@@@@@ Stats after building build/debug_b @@@@@@@@@@"
ccache -s
```

This results in no hits for `debug_a` and close to 100% hits for `debug_b`
as expected:

```
@@@@@@@@@@ Stats after building build/debug_a @@@@@@@@@@
Cacheable calls:    9008 /   9012 (99.96%)
  Hits:             4502 /   9008 (49.98%)
    Direct:         4502 /   4502 (100.0%)
    Preprocessed:      0 /   4502 ( 0.00%)
  Misses:           4506 /   9008 (50.02%)
Uncacheable calls:     4 /   9012 ( 0.04%)
Local storage:
  Cache size (GiB):  3.1 / 1024.0 ( 0.31%)
  Cleanups:          256
  Hits:             4502 /   9008 (49.98%)
  Misses:           4506 /   9008 (50.02%)

@@@@@@@@@@ Stats after building build/debug_b @@@@@@@@@@
Cacheable calls:    11260 /  11265 (99.96%)
  Hits:              6753 /  11260 (59.97%)
    Direct:          6753 /   6753 (100.0%)
    Preprocessed:       0 /   6753 ( 0.00%)
  Misses:            4507 /  11260 (40.03%)
Uncacheable calls:      5 /  11265 ( 0.04%)
Local storage:
  Cache size (GiB):   3.2 / 1024.0 ( 0.31%)
  Cleanups:           256
  Hits:              6753 /  11260 (59.97%)
  Misses:            4507 /  11260 (40.03%)
```

## Limitations

Rewriting paths to relative works in most cases, but you'll still experience
cache misses if the location of your build directory relative to the source
directory differs. This might happen if you compile directly in
`build/` in one checkout, but in `build/foo` in another, or if compiling
outside of the `llvm-project` source tree altogether in one case, but within
it (e.g. in `build/`) in another.

This is normally pretty easy to avoid, but is worth being aware of. For
instance I find it helpful on LLVM buildbots I administer to be able to rapidly
reproduce a previous build using `ccache`, but the default source vs build
directory layout used during CI is different to what I normally use in day to
day development.

## Other helpful options

I was going to advertise `inode_cache = true`, but I see this is enabled by
default since I last looked. Otherwise, `file_clone = true`
([docs](https://ccache.dev/manual/latest.html#config_file_clone) makes sense
for my case where I'm in a filesystem with reflink support (XFS) and have
plenty of space.
