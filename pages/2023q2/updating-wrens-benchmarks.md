+++
published = 2023-04-10
description = "Rerunning the Wren programming language's benchmarks against current Lua/Python/Ruby."
extra_css = """
table.chart {
font-size:.833rem;
}
table.chart td, th {
padding:.1em;
border-bottom:0;
}
table.chart th {
width:15%;
}
table.chart .chart-bar {
background:#8bdd7c;
text-align:right;
}
"""
+++
# Updating Wren's benchmarks

[Wren](https://wren.io/) is a "small, fast, class-based, concurrent scripting
language", originally designed by Bob Nystrom (who you might recognise as the
author of [Game Programming Patterns](https://gameprogrammingpatterns.com/)
and [Crafting Interpreters](https://craftinginterpreters.com/). It's a really
fun language to study - the implementation is compact and easily readable, and
although class-based languages aren't considered very hip these days there's a
real elegance to its design. I saw Wren's [performance
page](https://wren.io/performance.html) hadn't been updated for a very long
time, and especially given the recent upstream interpreter performance work on
Python, was interested in seeing how performance on these microbencharks has
changed. Hence this quick post to share some new numbers.

## New results

To cut to the chase, here are the results I get running the same set of
[benchmarks](https://github.com/wren-lang/wren/tree/main/test/benchmark)
across a collection of Python, Ruby, and Lua versions (those available in
current Arch Linux).

**Method Call**:
<table class="chart">
  <tr>
    <th>wren0.4</th><td><div class="chart-bar" style="width: 25%;">0.079s&nbsp;</div></td>
  </tr>
  <tr>
    <th>luajit2.1 -joff</th><td><div class="chart-bar" style="width: 29%;">0.090s&nbsp;</div></td>
  </tr>
  <tr>
    <th>ruby2.7</th><td><div class="chart-bar" style="width: 33%;">0.102s&nbsp;</div></td>
  </tr>
  <tr>
    <th>ruby3.0</th><td><div class="chart-bar" style="width: 33%;">0.104s&nbsp;</div></td>
  </tr>
  <tr>
    <th>lua5.4</th><td><div class="chart-bar" style="width: 39%;">0.123s&nbsp;</div></td>
  </tr>
  <tr>
    <th>lua5.3</th><td><div class="chart-bar" style="width: 50%;">0.156s&nbsp;</div></td>
  </tr>
  <tr>
    <th>python3.11</th><td><div class="chart-bar" style="width: 54%;">0.170s&nbsp;</div></td>
  </tr>
  <tr>
    <th>lua5.2</th><td><div class="chart-bar" style="width: 59%;">0.184s&nbsp;</div></td>
  </tr>
  <tr>
    <th>mruby</th><td><div class="chart-bar" style="width: 62%;">0.193s&nbsp;</div></td>
  </tr>
  <tr>
    <th>python3.10</th><td><div class="chart-bar" style="width: 100%;">0.313s&nbsp;</div></td>
  </tr>
</table>

**Delta Blue**:
<table class="chart">
  <tr>
    <th>wren0.4</th><td><div class="chart-bar" style="width: 43%;">0.086s&nbsp;</div></td>
  </tr>
  <tr>
    <th>python3.11</th><td><div class="chart-bar" style="width: 53%;">0.106s&nbsp;</div></td>
  </tr>
  <tr>
    <th>python3.10</th><td><div class="chart-bar" style="width: 100%;">0.202s&nbsp;</div></td>
  </tr>
</table>

**Binary Trees**:
<table class="chart">
  <tr>
    <th>luajit2.1 -joff</th><td><div class="chart-bar" style="width: 37%;">0.073s&nbsp;</div></td>
  </tr>
  <tr>
    <th>ruby2.7</th><td><div class="chart-bar" style="width: 58%;">0.113s&nbsp;</div></td>
  </tr>
  <tr>
    <th>ruby3.0</th><td><div class="chart-bar" style="width: 59%;">0.115s&nbsp;</div></td>
  </tr>
  <tr>
    <th>python3.11</th><td><div class="chart-bar" style="width: 70%;">0.137s&nbsp;</div></td>
  </tr>
  <tr>
    <th>lua5.4</th><td><div class="chart-bar" style="width: 71%;">0.138s&nbsp;</div></td>
  </tr>
  <tr>
    <th>wren0.4</th><td><div class="chart-bar" style="width: 73%;">0.144s&nbsp;</div></td>
  </tr>
  <tr>
    <th>mruby</th><td><div class="chart-bar" style="width: 84%;">0.163s&nbsp;</div></td>
  </tr>
  <tr>
    <th>python3.10</th><td><div class="chart-bar" style="width: 95%;">0.186s&nbsp;</div></td>
  </tr>
  <tr>
    <th>lua5.3</th><td><div class="chart-bar" style="width: 99%;">0.195s&nbsp;</div></td>
  </tr>
  <tr>
    <th>lua5.2</th><td><div class="chart-bar" style="width: 100%;">0.196s&nbsp;</div></td>
  </tr>
</table>

**Recursive Fibonacci**:
<table class="chart">
  <tr>
    <th>luajit2.1 -joff</th><td><div class="chart-bar" style="width: 22%;">0.055s&nbsp;</div></td>
  </tr>
  <tr>
    <th>lua5.4</th><td><div class="chart-bar" style="width: 36%;">0.090s&nbsp;</div></td>
  </tr>
  <tr>
    <th>ruby2.7</th><td><div class="chart-bar" style="width: 43%;">0.109s&nbsp;</div></td>
  </tr>
  <tr>
    <th>ruby3.0</th><td><div class="chart-bar" style="width: 47%;">0.117s&nbsp;</div></td>
  </tr>
  <tr>
    <th>lua5.3</th><td><div class="chart-bar" style="width: 50%;">0.126s&nbsp;</div></td>
  </tr>
  <tr>
    <th>lua5.2</th><td><div class="chart-bar" style="width: 55%;">0.138s&nbsp;</div></td>
  </tr>
  <tr>
    <th>wren0.4</th><td><div class="chart-bar" style="width: 59%;">0.148s&nbsp;</div></td>
  </tr>
  <tr>
    <th>python3.11</th><td><div class="chart-bar" style="width: 62%;">0.157s&nbsp;</div></td>
  </tr>
  <tr>
    <th>mruby</th><td><div class="chart-bar" style="width: 73%;">0.185s&nbsp;</div></td>
  </tr>
  <tr>
    <th>python3.10</th><td><div class="chart-bar" style="width: 100%;">0.252s&nbsp;</div></td>
  </tr>
</table>

I've used essentially the same presentation and methodology as in the original
benchmark, partly to save time pondering the optimal approach, partly so I can
redirect any critiques to the original author (sorry Bob!). Benchmarks do not
measure interpreter startup time, and each benchmark is run ten times with the
median used (thermal throttling could potentially mean this isn't the best
methodology, but changing the number of test repetitions to e.g. 1000 seems to
have little effect).

The tests were run on a machine with an AMD Ryzen 9 5950X processor. wren 0.4
as of commit
[c2a75f1](https://github.com/wren-lang/wren/commit/c2a75f1eaf9b1ba1245d7533a723360863fb012d)
was used as well as the following Arch Linux packages:
* lua52-5.2.4-5
* lua53-5.3.6-1
* lua-5.4.4-3,
* luajit-2.1.0.beta3.r471.g505e2c03-1
* mruby-3.1.0-1
* python-3.10.10-1
* python-3.11.3-1 (taken from Arch Linux's staging repo)
* ruby2.7-2.7.7-1
* ruby-3.0.5-1

The Python 3.10 and 3.11 packages were compiled with the same GCC version
(12.2.1 according to `python -VV`), though this won't necessarily be true for
all other packages (e.g. the lua52 and lua53 packages are several years old so
will have been built an older GCC).

I've submitted a [pull request to update the Wren performance
page](https://github.com/wren-lang/wren/pull/1164).

## Old results

The following results are copied from the [Wren performance
page](https://wren.io/performance.html) ([archive.org
link](https://web.archive.org/web/20230326002211/https://wren.io/performance.html)
ease of comparison. They were run on a MacBook Pro 2.3GHz Intel Core i7 with
Lua 5.2.3, LuaJIT 2.0.2, Python 2.7.5, Python 3.3.4, ruby 2.0.0p247.

**Method Call**:

<table class="chart">
  <tr>
    <th>wren2015</th><td><div class="chart-bar" style="width: 14%;">0.12s&nbsp;</div></td>
  </tr>
  <tr>
    <th>luajit2.0 -joff</th><td><div class="chart-bar" style="width: 18%;">0.16s&nbsp;</div></td>
  </tr>
  <tr>
    <th>ruby2.0</th><td><div class="chart-bar" style="width: 23%;">0.20s&nbsp;</div></td>
  </tr>
  <tr>
    <th>lua5.2</th><td><div class="chart-bar" style="width: 41%;">0.35s&nbsp;</div></td>
  </tr>
  <tr>
    <th>python3.3</th><td><div class="chart-bar" style="width: 91%;">0.78s&nbsp;</div></td>
  </tr>
  <tr>
    <th>python2.7</th><td><div class="chart-bar" style="width: 100%;">0.85s&nbsp;</div></td>
  </tr>
</table>

**DeltaBlue**:

<table class="chart">
  <tr>
    <th>wren2015</th><td><div class="chart-bar" style="width: 22%;">0.13s&nbsp;</div></td>
  </tr>
  <tr>
    <th>python3.3</th><td><div class="chart-bar" style="width: 83%;">0.48s&nbsp;</div></td>
  </tr>
  <tr>
    <th>python2.7</th><td><div class="chart-bar" style="width: 100%;">0.57s&nbsp;</div></td>
  </tr>
</table>

**Binary Trees**:

<table class="chart">
  <tr>
    <th>luajit2.0 -joff</th><td><div class="chart-bar" style="width: 20%;">0.11s&nbsp;</div></td>
  </tr>
  <tr>
    <th>wren2015</th><td><div class="chart-bar" style="width: 41%;">0.22s&nbsp;</div></td>
  </tr>
  <tr>
    <th>ruby2.0</th><td><div class="chart-bar" style="width: 46%;">0.24s&nbsp;</div></td>
  </tr>
  <tr>
    <th>python2.7</th><td><div class="chart-bar" style="width: 71%;">0.37s&nbsp;</div></td>
  </tr>
  <tr>
    <th>python3.3</th><td><div class="chart-bar" style="width: 73%;">0.38s&nbsp;</div></td>
  </tr>
  <tr>
    <th>lua5.2</th><td><div class="chart-bar" style="width: 100%;">0.52s&nbsp;</div></td>
  </tr>
</table>

**Recursive Fibonacci**:

<table class="chart">
  <tr>
    <th>luajit2.0 -joff</th><td><div class="chart-bar" style="width: 17%;">0.10s&nbsp;</div></td>
  </tr>
  <tr>
    <th>wren2015</th><td><div class="chart-bar" style="width: 35%;">0.20s&nbsp;</div></td>
  </tr>
  <tr>
    <th>ruby2.0</th><td><div class="chart-bar" style="width: 39%;">0.22s&nbsp;</div></td>
  </tr>
  <tr>
    <th>lua5.2</th><td><div class="chart-bar" style="width: 49%;">0.28s&nbsp;</div></td>
  </tr>
  <tr>
    <th>python2.7</th><td><div class="chart-bar" style="width: 90%;">0.51s&nbsp;</div></td>
  </tr>
  <tr>
    <th>python3.3</th><td><div class="chart-bar" style="width: 100%;">0.57s&nbsp;</div></td>
  </tr>
</table>

## Observations

A few takeaways:
* LuaJIT's bytecode interpreter remains incredibly fast (though see [this blog
  post](https://sillycross.github.io/2022/11/22/2022-11-22/) for a methodology
  to produce an even faster interpreter).
* The performance improvements in Python 3.11 were [well
  documented](https://docs.python.org/3/whatsnew/3.11.html#whatsnew311-faster-cpython)
  and are very visible on this set of microbenchparks.
* I was more surprised by the performance jump with Lua 5.4, especially as the
  [release notes](https://www.lua.org/manual/5.4/readme.html#changes) give few
  hints of performance improvements that would be reflected in these
  microbenchmarks. The [LWN article about the Lua 5.4
  release](https://lwn.net/Articles/826134/) however did note improved
  performance on a range of benchmarks.
* Wren remains speedy (for these workloads at least), but engineering work on
  other interpreters has narrowed that gap for some of these benchmarks.
* I haven't taken the time to compare the January 2015 version of Wren used
  for the benchmarks vs present-day Wren 0.4. It would be interesting to
  explore that though.
* A tiny number of microbenchmarks have been used in this performance test. It
  wouldn't be wise to draw general conclusions - this is just a bit of fun.

## Appendix: Benchmark script

Health warning: this is incredibly quick and dirty (especially the repeated
switching between the python packages to allow testing both 3.10 and 3.11):

```python
#!/usr/bin/env python3

# Copyright Muxup contributors.
# Distributed under the terms of the MIT license, see LICENSE for details.
# SPDX-License-Identifier: MIT

import statistics
import subprocess

out = open("out.md", "w", encoding="utf-8")


def run_single_bench(bench_name, bench_file, runner_name):
    bench_file = "./test/benchmark/" + bench_file
    if runner_name == "lua5.2":
        bench_file += ".lua"
        cmdline = ["lua5.2", bench_file]
    elif runner_name == "lua5.3":
        bench_file += ".lua"
        cmdline = ["lua5.3", bench_file]
    elif runner_name == "lua5.4":
        bench_file += ".lua"
        cmdline = ["lua5.4", bench_file]
    elif runner_name == "luajit2.1 -joff":
        bench_file += ".lua"
        cmdline = ["luajit", "-joff", bench_file]
    elif runner_name == "mruby":
        bench_file += ".rb"
        cmdline = ["mruby", bench_file]
    elif runner_name == "python3.10":
        bench_file += ".py"
        subprocess.run(
            [
                "sudo",
                "pacman",
                "-U",
                "--noconfirm",
                "/var/cache/pacman/pkg/python-3.10.10-1-x86_64.pkg.tar.zst",
            ],
            check=True,
        )
        cmdline = ["python", bench_file]
    elif runner_name == "python3.11":
        bench_file += ".py"
        subprocess.run(
            [
                "sudo",
                "pacman",
                "-U",
                "--noconfirm",
                "/var/cache/pacman/pkg/python-3.11.3-1-x86_64.pkg.tar.zst",
            ],
            check=True,
        )
        cmdline = ["python", bench_file]
    elif runner_name == "ruby2.7":
        bench_file += ".rb"
        cmdline = ["ruby-2.7", bench_file]
    elif runner_name == "ruby3.0":
        bench_file += ".rb"
        cmdline = ["ruby", bench_file]
    elif runner_name == "wren0.4":
        bench_file += ".wren"
        cmdline = ["./bin/wren_test", bench_file]
    else:
        raise SystemExit("Unrecognised runner")

    times = []
    for _ in range(10):
        bench_out = subprocess.run(
            cmdline, capture_output=True, check=True, encoding="utf-8"
        ).stdout
        times.append(float(bench_out.split(": ")[-1].strip()))
    return statistics.median(times)


def do_bench(name, file_base, runners):
    results = {}
    for runner in runners:
        results[runner] = run_single_bench(name, file_base, runner)
    results = dict(sorted(results.items(), key=lambda kv: kv[1]))
    longest_result = max(results.values())
    out.write(f"**{name}**:\n")
    out.write('<table class="chart">\n')
    for runner, result in results.items():
        percent = round((result / longest_result) * 100)
        out.write(
            f"""\
  <tr>
    <th>{runner}</th><td><div class="chart-bar" style="width: {percent}%;">{result:.3f}s&nbsp;</div></td>
  </tr>\n"""
        )
    out.write("</table>\n\n")


all_runners = [
    "lua5.2",
    "lua5.3",
    "lua5.4",
    "luajit2.1 -joff",
    "mruby",
    "python3.10",
    "python3.11",
    "ruby2.7",
    "ruby3.0",
    "wren0.4",
]
do_bench("Method Call", "method_call", all_runners)
do_bench("Delta Blue", "delta_blue", ["python3.10", "python3.11", "wren0.4"])
do_bench("Binary Trees", "binary_trees", all_runners)
do_bench("Recursive Fibonacci", "fib", all_runners)
print("Output written to out.md")
```
