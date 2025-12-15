+++
published = 2025-12-02
description = "Using QEMU to capture execution count for each translation block"
+++

# QEMU-based instruction execution counting

Although analysing performance by way of instruction counting has obvious
limitations, it can be helpful (especially when combined with appropriate
analysis scripts) to get rapid feedback on the impact of code generation
changes or to explore hypotheses about why code from one compiler might be
performing differently from another - for instance, by looking at instruction
mix in the most executed translation blocks. In this post we'll look at how to
capture the necessary data to perform such an analysis using a QEMU plugin.
Future posts will give details of the analysis scripts I've used, and walk
through an example or two of putting them to use.

## Modifying QEMU

Over the past few years, QEMU's plugin API has developed a fair bit. QEMU
includes several plugins, and `hotblocks` provides _almost_ what we want but
doesn't allow configurability of the number of blocks it will print
information on. I submitted a [small patch
series](https://lore.kernel.org/qemu-devel/cf5a00136738b981a12270b76572e8d502daf208.1753857212.git.asb@igalia.com/T/)
(and [submitted it a second
time](https://lore.kernel.org/qemu-devel/cover.1764716538.git.asb@igalia.com/)
addressing this and other minor issues found along the way. The series has now
been [accepted by the
maintainer](https://lore.kernel.org/qemu-devel/87o6o3ucy6.fsf@draig.linaro.org/).

To build QEMU with this patch:

```sh
git clone https://github.com/qemu/qemu && cd qemu
git checkout v10.1.2
cat - <<'EOF' > hotblocks.patch
index 98404b6885..8ecf033997 100644
--- a/contrib/plugins/hotblocks.c
+++ b/contrib/plugins/hotblocks.c
@@ -73,28 +73,29 @@ static void exec_count_free(gpointer key, gpointer value, gpointer user_data)
 static void plugin_exit(qemu_plugin_id_t id, void *p)
 {
     g_autoptr(GString) report = g_string_new("collected ");
-    GList *counts, *it;
+    GList *counts, *sorted_counts, *it;
     int i;

     g_string_append_printf(report, "%d entries in the hash table\n",
                            g_hash_table_size(hotblocks));
     counts = g_hash_table_get_values(hotblocks);
-    it = g_list_sort_with_data(counts, cmp_exec_count, NULL);
+    sorted_counts = g_list_sort_with_data(counts, cmp_exec_count, NULL);

-    if (it) {
+    if (sorted_counts) {
         g_string_append_printf(report, "pc, tcount, icount, ecount\n");

-        for (i = 0; i < limit && it->next; i++, it = it->next) {
+        for (i = 0, it = sorted_counts; (limit == 0 || i < limit) && it;
+             i++, it = it->next) {
             ExecCount *rec = (ExecCount *) it->data;
             g_string_append_printf(
-                report, "0x%016"PRIx64", %d, %ld, %"PRId64"\n",
+                report, "0x%016"PRIx64", %d, %ld, %"PRIu64"\n",
                 rec->start_addr, rec->trans_count,
                 rec->insns,
                 qemu_plugin_u64_sum(
                     qemu_plugin_scoreboard_u64(rec->exec_count)));
         }

-        g_list_free(it);
+        g_list_free(sorted_counts);
     }

     qemu_plugin_outs(report->str);
@@ -170,6 +171,13 @@ int qemu_plugin_install(qemu_plugin_id_t id, const qemu_info_t *info,
                 fprintf(stderr, "boolean argument parsing failed: %s\n", opt);
                 return -1;
             }
+        } else if (g_strcmp0(tokens[0], "limit") == 0) {
+            char *endptr = NULL;
+            limit = g_ascii_strtoull(tokens[1], &endptr, 10);
+            if (endptr == tokens[1] || *endptr != '\0') {
+                fprintf(stderr, "unsigned integer parsing failed: %s\n", opt);
+                return -1;
+            }
         } else {
             fprintf(stderr, "option parsing failed: %s\n", opt);
             return -1;
diff --git a/docs/about/emulation.rst b/docs/about/emulation.rst
index 4a7d1f4178..e8793b0f9c 100644
--- a/docs/about/emulation.rst
+++ b/docs/about/emulation.rst
@@ -463,6 +463,18 @@ Example::
   0x000000004002b0, 1, 4, 66087
   ...

+Behaviour can be tweaked with the following arguments:
+
+.. list-table:: Hot Blocks plugin arguments
+  :widths: 20 80
+  :header-rows: 1
+
+  * - Option
+    - Description
+  * - inline=true|false
+    - Use faster inline addition of a single counter.
+  * - limit=N
+    - The number of blocks to be printed. (Default: N = 20, use 0 for no limit).

 Hot Pages
 .........
EOF
patch -p1 < hotblocks.patch
./configure --prefix=$(pwd)/inst --target-list="riscv32-linux-user riscv64-linux-user"
make -j$(nproc)
cd ..
```

## Using this plugin to capture statistics from running a binary under qemu-user

Assuming you have an [appropriate
sysroot](/pages/2024q4/rootless-cross-architecture-debootstrap.md), you can
run a binary and have the execution information emitted to stderr by doing
something like:

```sh
QEMUDIR=$HOME/qemu/build
SYSROOT=$HOME/rvsysroot
$QEMUDIR/qemu-riscv64 \
  -L $SYSROOT \
  -plugin $QEMUDIR/contrib/plugins/libhotblocks.so,limit=0,inline=on \
  -d plugin,nochain \
  my_rv64_binary
```

This produces output like:

```
collected 2229 entries in the hash table
pc, tcount, icount, ecount
0x00007fffee7012ba, 1, 1, 3737
0x00007fffee7012be, 1, 3, 3737
0x00007ffff741e738, 1, 23, 1074
0x00007fffee71bb38, 1, 5, 884
0x00007ffff741bb2e, 1, 11, 662
...
```

This listing indicates the address of the translation block, the number of
times it's been translated, the number of instructions it contains, and the
number of times it was executed. Note that a translation block is not the same
as a basic block in the compiler. A translation block can span multiple basic
blocks in the case of fallthrough, and this can also mean an instruction may
show up in multiple translation blocks.

At least for my use cases, I need something a bit more involved than this. In
order to add collection of these statistics to an existing benchmark harness I
need a wrapper script that transparently collects these statistics to a file.
It's also helpful to capture the runtime address of executable mappings for
loaded libraries, allowing translation blocks to be attributed easily to
either the binary itself or `libc`, `libm` etc. We have `gdb` connect to
QEMU's gdbserver in order to dump those mappings. Do ensure you're using a
recent version of QEMU (the version suggested in the patch application
instructions is definitely good) for this as I wasted quite some time running
into a [bug with file descriptor
numbers](https://github.com/qemu/qemu/commit/8b647bd352505234cab2acd2422aba183a1aa1fd)
that caused odd breakage.

This `qemu-forwarder.sh` script will capture the plugin's output in a
`.qemu_out` file and the mappings in a `.map` file, both of which can be later
consumed by a detailed analysis script.

```sh
#!/bin/sh
QEMUDIR=$HOME/qemu/build
SYSROOT=$HOME/rvsysroot
QEMU="$QEMUDIR/qemu-riscv64 \
  -L $SYSROOT \
  -plugin $QEMUDIR/contrib/plugins/libhotblocks.so,limit=0,inline=on \
  -d plugin,nochain"

SUFFIX=""
if [ -e "$1.qemu_out" ]; then
  NUM=1
  while [ -e "$1.qemu_out.$NUM" ]; do
    NUM=$((NUM + 1))
  done
  SUFFIX=".$NUM"
fi

GDB_SOCK=$(mktemp -u)
setarch $(uname -m) -R $QEMU -g $GDB_SOCK -D $1.qemu_out$SUFFIX "$@" &
QEMU_PID=$!

RETRY_COUNT=0
while ! [ -e "$GDB_SOCK" ]; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -eq 10 ]; then
    echo "Timed out waiting for gdb socket to be created"
    exit 1
  fi
  sleep 0.1
  if ! kill -0 $QEMU_PID 2>/dev/null; then
    echo "QEMU process died before gdb socket was created"
    wait $QEMU_PID
    exit $?
  fi
done

gdb -batch \
  -ex "set pagination off" \
  -ex "target remote $GDB_SOCK" \
  -ex "break main" \
  -ex "continue" \
  -ex "set logging file $1.map$SUFFIX" \
  -ex "set logging enabled on" \
  -ex "info proc mappings" \
  -ex "detach" > /dev/null 2>&1
wait $QEMU_PID
```

The above will work under LLVM's `lit`, though you will need to use a recent
enough version that doesn't strip `HOME` from the environment (or else edit
the script accordingly). It also produces output in sequentially numbered
files, again motivated by the desire to run under this script from `lit` as
used by `llvm-test-suite`'s SPEC configuration which can involve multiple
invocations of the same binary for a given benchmark (e.g. 500.perlbench_r).

## Analysing the output

A follow-up post will introduce the scripting I've built around this.

## Recording and analysing results from running SPEC

Assuming you have `qemu-forwarder.sh`, in your llvm-test-suite directory:

```sh
CONF=clang-head-test
CLANG_BIN_DIR=$HOME/llvm-project/build/release/bin
CFLAGS="-march=rv64gc_zba_zbb_zbs"
cat - <<EOF > $CONF.cmake
set(CMAKE_SYSTEM_NAME Linux)

set(CMAKE_SYSROOT $HOME/rvsysroot)

set(CMAKE_C_COMPILER $CLANG_BIN_DIR/clang)
set(CMAKE_CXX_COMPILER $CLANG_BIN_DIR/clang++)

set(CMAKE_C_COMPILER_TARGET riscv64-linux-gnu)
set(CMAKE_CXX_COMPILER_TARGET riscv64-linux-gnu)
set(CMAKE_C_FLAGS_INIT "$CFLAGS")
set(CMAKE_CXX_FLAGS_INIT "$CFLAGS")

set(CMAKE_LINKER_TYPE LLD)

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
EOF
cmake -G Ninja \
  -B build.$CONF \
  --toolchain=$CONF.cmake \
  -DTEST_SUITE_SPEC2017_ROOT=~/cpu2017 \
  -DTEST_SUITE_SUBDIRS=External/SPEC \
  -DTEST_SUITE_COLLECT_CODE_SIZE=OFF \
  -DTEST_SUITE_COLLECT_COMPILE_TIME=OFF \
  -DTEST_SUITE_USER_MODE_EMULATION=ON \
  -DTEST_SUITE_RUN_UNDER=$(pwd)/qemu-forwarder.sh
cmake --build build.$CONF
$CLANG_BIN_DIR/llvm-lit -v --filter-out='.+_s|specrand' build.$CONF
```

The `526.blender_r` test takes twice as long as the others, so you may wish to
skip it by instead executing something like:

```sh
$CLANG_BIN_DIR/llvm-lit -v --filter-out='.+_s|specrand|blender' build.$CONF
```

If you want to re-run tests you must delete the previous `.qemu_out` and
`.map` files, which can be done with:

```sh
[ -n "build.$CONF" ] && find "build.$CONF" -type f -name "*.qemu_out*" -exec sh -c '
    for q_file do
        base_path="${q_file%.qemu_out*}"
        rm -f "$q_file" "${base_path}.map"*
    done
' sh {} +
```

In order to compare two SPEC builds, you can use something like the following
hacky script. Using the captured translation block execution data to generate
a plain executed instruction count is overkill as the example
[tests/tcg/plugin/insn.c](https://www.qemu.org/docs/master/about/emulation.html#instruction)
can easily dump for this for you directly. But by collecting the data upfront,
you can easily dive right into a more detailed analysis when you see a
surprising difference in executed instruction counts without rerunning the
binary.

```py
#!/usr/bin/env python3

from pathlib import Path
from collections import defaultdict
import sys

def collect_totals(root_dir):
    totals = defaultdict(int)
    root_path = Path(root_dir)/"External"

    for file_path in root_path.rglob("*.qemu_out*"):
        benchmark_name = file_path.parts[4]

        try:
            with file_path.open("r") as f:
                file_total = 0
                for line in f:
                    parts = line.strip().split(',')
                    # Only sum lines that match the expected format.
                    if len(parts) == 4 and parts[2].strip().isdigit():
                        # icount * ecount.
                        file_total += int(parts[2]) * int(parts[3])
                totals[benchmark_name] += file_total
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return totals

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: spec-compare-helper <dir_a> <dir_b>")
        sys.exit(1)

    dir_a, dir_b = sys.argv[1], sys.argv[2]
    totals_a = collect_totals(dir_a)
    totals_b = collect_totals(dir_b)

    benchmarks = sorted(set(totals_a.keys()) | set(totals_b.keys()))

    print(f"{'Benchmark':<20} {'DirA':>15} {'DirB':>15} {'Diff (%)':>10}")
    print("=" * 60)

    for benchmark in benchmarks:
        val_a = totals_a.get(benchmark, 0)
        val_b = totals_b.get(benchmark, 0)
        diff_pct = ((val_b - val_a) / val_a * 100) if val_a else float("inf")

        print(f"{benchmark:<20} {val_a:>15} {val_b:>15} {diff_pct:>9.2f}%")
```

Which produces output looking something like this:

```
Benchmark                       DirA            DirB   Diff (%)
============================================================
500.perlbench_r         180245097594    182078714777      1.02%
502.gcc_r               220874510659    219647717585     -0.56%
505.mcf_r               131589945456    134271153130      2.04%
508.namd_r              220648061019    216682202888     -1.80%
510.parest_r            291341820355    291844973715      0.17%
511.povray_r             31911866906     31103201809     -2.53%
519.lbm_r                94166321698     86910581403     -7.71%
520.omnetpp_r           138002605692    137676301622     -0.24%
523.xalancbmk_r         283566182007    284735075518      0.41%
525.x264_r              380165035845    379862173371     -0.08%
526.blender_r           660528270138    659361380750     -0.18%
531.deepsjeng_r         355058534962    349621355155     -1.53%
538.imagick_r           238573643488    238560676372     -0.01%
541.leela_r             421886351310    405423320484     -3.90%
544.nab_r               415595728542    391443973852     -5.81%
557.xz_r                132548718317    130229753780     -1.75%
```

It's worth highlighting that as we're running this under user-mode emulation,
the dynamic instruction count naturally never counts any instructions on the
kernel side that you would see if profiling a real system.

## Article changelog
* 2025-12-15: (minor) Note that the qemu patches have now been accepted in the
  maintainer's tree.
