+++
published = 2026-01-07
description = "Can we reasonably use the InferenceMAX benchmark dataset to get a Wh per query figure?"
+++

# Per-query energy consumption of LLMs

How much energy is consumed when querying an LLM? We're largely in the dark
when it comes to proprietary models, but for open weight models that anyone
can host on readily available, albeit eye-wateringly expensive, hardware this
is something that can be measured and reported, right? In fact, given other
people are [doing the hard work](https://inferencemax.semianalysis.com/) of
setting up and running benchmarks across all kinds of different hardware and
software configurations for common open weight models, can we just re-use that
to get a reasonable figure in terms of Watt-hours (Wh) per query?

For the kind of model you can run locally on a consumer GPU then of course
there's some value in seeing how low the per-query energy usage might be on a
large scale commercial setup. But my main interest is in larger and more
capable models, the kind that you wouldn't realistically run locally and end
up using in a pay-per-token manner either directly with your host of choice or
through an intermediary like [OpenRouter](https://openrouter.ai/). In these
cases where models are efficiently served with a minimum of 4-8 GPUs or even
[multi-node
clusters](https://www.perplexity.ai/hub/blog/lower-latency-and-higher-throughput-with-multi-node-deepseek-deployment)
it's not easy to get a feel for the resources you're using. I'm pretty happy
that simple back of the envelope maths shows that whether providers are
properly amortising the cost of their GPUs or not, it's implausible that
they're selling per-token API access for open models at below the cost of
electricity. That gives a kind of upper bound on energy usage, and looking at
the pennies I spend on such services it's clearly a drop in the ocean compared
to my overall energy footprint. But it's not a very tight bound, which means
it's hard to assess the impact of increasing my usage.

We can look at things like [Google's published figures on energy usage for
Gemini](https://arxiv.org/pdf/2508.15734) but this doesn't help much. They
don't disclose the length of the median prompt and its response, or details of
the model used to serve that median query meaning it's not helpful for
either estimating how it might apply to other models or how it might apply to
your own usage (which may be far away from this mysterious median query).
Mistral [released
data](https://mistral.ai/news/our-contribution-to-a-global-environmental-standard-for-ai)
on the per query environmental impact (assuming for a 400 token query), but
the size of the Mistral Large 2 model is not disclosed and they don't calculate
a Wh per query figure. CO2 and water per query are very helpful to evaluate a
particular deployment, but the actual energy used is a better starting point
that can be applied to other providers assuming different levels of carbon
intensity. If one of the API providers were to share statistics based on a
real world deployment of one of the open models with a much higher degree of
transparency (i.e. sharing stats on the number of queries served during the
period, statistics on their length, and measured system power draw) that would
be a useful source of data. But today we're looking at what we can conclude
from the [InferenceMAX benchmark
suite](https://inferencemax.semianalysis.com/) published results.

I'd started looking at options for getting good figures thinking I might
have to invest in the hassle and expense of renting a multi-GPU cloud
instance to run my own benchmarks, then felt InferenceMAX may make that
unnecessary. After writing this up along with all my provisos I'm perhaps
tempted again to try to generate figures myself. Anyway, read on for a more
detailed look at that benchmark suite. You can scroll past all the provisos
and <a href="#results">jump ahead to the figures</a> giving the Wh/query
figures implied by the benchmark results across different GPUs, different
average input/output sequence lengths, and for gpt-oss 120B and
DeepSeek-R1-0528. But I hope you'll feel a bit guilty about it.

If you see any errors, please let me know.

## High-level notes on InferenceMAX

[InferenceMAX benchmark suite](https://inferencemax.semianalysis.com/) has the
[stated
goal](https://newsletter.semianalysis.com/p/inferencemax-open-source-inference)
to "provide benchmarks that both emulate real world applications as much as
possible and reflect the continuous pace of software innovation." They
differentiate themselves from other benchmarking efforts noting "Existing
performance benchmarks quickly become obsolete because they are static, and
participants often game the benchmarks with unrealistic, highly specific
configurations."

The question I'm trying to answer is "what is the most 'useful AI' I can
expect for a modern GPU cluster in a realistic deployment and how much energy
does it consume". Any benchmark is going to show peak throughput higher than
you'd expect to achieve in real workload and there's naturally a desire to
keep it pinned on a specific model for as long as it isn't _totally_
irrelevant in order to enable comparisons as hardware and software evolves
with a common point of reference. But although I might make slightly
different choices about what gets benchmarked and how, the InferenceMAX setup
at first look seems broadly aligned with what I want to achieve.

They benchmark
[DeepSeek-R1-0528](https://huggingface.co/deepseek-ai/DeepSeek-R1-0528) (both
at the native fp8 quantisation and at fp4) which is a 671B parameter model
with 37B active weights released ~7 months ago and seems a fair representative
of a large MoE open weight model.
[gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b) is also
benchmarked, providing a point of comparison for a much smaller and efficient
to run model. Different input sequence length and output sequence length (ISL
and OSL - the number of input and output tokens) are tested: 1k/1k, 1k/8k,
8k/1k, which provides coverage of different query types. Plus tests against a
wide range of GPUs (including the 72-GPU GB200 NVL72 cluster) and sweeps
different settings.

At the time of writing you might reasonably consider to be 'InferenceMAX' is
split into around three pieces:
* The frontend website you can [see at
  inferencemax.semianalysis.com](https://inferencemax.semianalysis.com/) (not
  currently open source but [planned to
  be](https://github.com/SemiAnalysisAI/InferenceX/issues/315))
* The [script for executing queries against the LLM serving infrastructure and
  collecting stats](https://github.com/kimbochen/bench_serving) (currently in
  a seperate repo but [planned to be incorporated into the main InferenceMAX
  repository](https://github.com/SemiAnalysisAI/InferenceX/issues/338)),
* The wrapper/runner scripts and GitHub actions workflows that live in the
  [main InferenceMAX
  repository](https://github.com/SemiAnalysisAI/InferenceX).
  * This is actively contributed to by at least Nvidia and AMD engineers.

GitHub Actions is used to orchestrate the runs, ultimately producing a zip
file containing JSON with the statistics of each configuration (e.g.
[here](https://github.com/SemiAnalysisAI/InferenceX/actions/runs/20216709902/job/58149531774)).
The `benchmark_serving.py` script is invoked via the [`run_benchmark_serving` wrapper
in
`benchmark_lib.sh`](https://github.com/SemiAnalysisAI/InferenceX/blob/84320a0aadacae1114265b553830f48b56231817/benchmarks/benchmark_lib.sh#L107)
which hardcodes some options and passes through some others from the workflow
YAML. The results logged by `benchmark_serving.py` are [processed in
InferenceMAX's `process_result.py`
helper](https://github.com/SemiAnalysisAI/InferenceX/blob/84320a0aadacae1114265b553830f48b56231817/utils/process_result.py)
which will produce JSON in the desired output format. Together, these scripts
provide statistics like throughput (input and output token), end to end
latency, interactivity (output tokens per second) etc.

## Further studying the benchmark setup

So, let's look at the benchmarking logic in more detail to look for any
surprises or things that might affect the accuracy of the Wh-per-query figure
I want to generate. I'll note that InferenceMAX is an ongoing project that is
actively being developed. These observations are based on a recent repo
checkout, but of course things may have changed since then if you're reading
this post some time after it was first published.

Looking through I made the following observations. Some represent potential
issues (see the next subheading for a list of the upstream issues I filed),
while others are just notes based on aspects of the benchmark I wanted to
better understand.

* One of the required arguments to the benchmark serving script is
  `--random-range-ratio`. This is set by default [to 0.8 in
  `benchmark-tmpl.yml`](https://github.com/SemiAnalysisAI/InferenceX/blob/84320a0aadacae1114265b553830f48b56231817/.github/workflows/benchmark-tmpl.yml#L56)
  and [in
  `benchmark-multinode-tmpl.yml`](https://github.com/SemiAnalysisAI/InferenceX/blob/84320a0aadacae1114265b553830f48b56231817/.github/workflows/benchmark-multinode-tmpl.yml#L49)
  and is not overridden elsewhere.
  * This argument is ultimately used in
    [`sample_random_requests`](https://github.com/kimbochen/bench_serving/blob/499c0b171b499b02a1fd546fb2326d2175a5d66e/benchmark_serving.py#L366).
    It uses `np.random.randint` to sample input/output lengths between the
    `range_ratio * {input,output}_len` and `{input,output}_len`.
  * Taken together, this logic means for for a workload advertised as having
    8k input or output tokens (8192), the benchmark will actually run with an
    average ~7373 (`0.9*num_tokens`, due to the length being a random number
    between `0.8*num_tokens` and `num_tokens`) tokens.
  * Because the throughput figures are [calculated using the actual input and
    output token
    lengths](https://github.com/kimbochen/bench_serving/blob/499c0b171b499b02a1fd546fb2326d2175a5d66e/benchmark_serving.py#L498),
    the figure _does_ represent what was observed, it's just the workload
    doesn't quite match the description. The reported end to end latency for
    instance will be misleadingly lower than you would get for a workload that
    actually did have the expected input / output sequence lengths.
* The various request functions in
  [backend_request.func.py](https://github.com/kimbochen/bench_serving/blob/499c0b171b499b02a1fd546fb2326d2175a5d66e/backend_request_func.py)
  will set `output.success = False` if they don't get a HTTP 200 status code
  back for a request. There is no logic to retry a refused request and
  [metrics will be calculated skipping any failed
  requests](https://github.com/kimbochen/bench_serving/blob/499c0b171b499b02a1fd546fb2326d2175a5d66e/benchmark_serving.py#L485).
  This means an overloaded server will perform better on this benchmark for
  metrics like E2E latency and TTFT if it refuses requests rather than accept
  them and serve them slowly. As the number of failed requests isn't included
  in the results json it's not easy to tell if this is a factor for any
  benchmarks.
* Many of the various scripts in the benchmarks/ subdirectory [set a
  max-model-len
  parameter](https://github.com/SemiAnalysisAI/InferenceX/blob/84320a0aadacae1114265b553830f48b56231817/benchmarks/gptoss_fp4_b200_docker.sh#L22)
  or the similar `--max_seq_len` parameter for trt-llm (e.g. [the b200
  config](https://github.com/SemiAnalysisAI/InferenceX/blob/84320a0aadacae1114265b553830f48b56231817/benchmarks/gptoss_fp4_b200_trt_docker.sh#L65)
  which if I'm not mistaken will ultimately be set from the max_model_len
  [defined in
  generate_sweep_configs.py](https://github.com/SemiAnalysisAI/InferenceX/blob/84320a0aadacae1114265b553830f48b56231817/utils/matrix_logic/generate_sweep_configs.py).
  This parameter is [documented in
  vllm](https://docs.vllm.ai/en/latest/cli/serve/#-max-model-len) and [in
  TensortRT-LLM](https://nvidia.github.io/TensorRT-LLM/1.0.0rc2/commands/trtllm-serve.html#cmdoption-trtllm-serve-serve-max_seq_len)
  and controls the maximum supported length of a request, including both the
  prompt and any generated output. Setting it 20 or 200 tokens above the sum
  of the benchmarked ISL+OSL to minimise memory use does not seem like a
  realistic real-world deployment, which seems the wrong choice given the
  InferenceMAX complaint that in other suites "participants often
  game the benchmarks with unrealistic, highly specific configurations".
  Benchmarks naturally show a 'best case', but if you're generating figures
  like $ per M tokens it's a figure that makes little sense if it reflects a
  configuration you wouldn't feasibly use/sell.
* Throughput is [calculated in
  `benchmark_serving.py`](https://github.com/kimbochen/bench_serving/blob/499c0b171b499b02a1fd546fb2326d2175a5d66e/benchmark_serving.py#L546)
  based on the total number of tokens divided by the duration of the
  benchmark. This is then normalised on a per-GPU basis [in
  process_result.py](https://github.com/SemiAnalysisAI/InferenceX/blob/84320a0aadacae1114265b553830f48b56231817/utils/process_result.py#L90).
  No problems here, I just wanted to clarify the source of the figure.
* In terms of the source of the input tokens themselves, we can see that
  [`--dataset-name random` is always passed to
  `benchmark_serving.py`](https://github.com/SemiAnalysisAI/InferenceX/blob/84320a0aadacae1114265b553830f48b56231817/benchmarks/benchmark_lib.sh#L222).
  This leads to
  [`sample_random_requests`](https://github.com/kimbochen/bench_serving/blob/499c0b171b499b02a1fd546fb2326d2175a5d66e/benchmark_serving.py#L366)
  being called, which will pick random token ids and create a list of tokens
  of the desired length (mapping these randomly picked IDs to tokens).
  * The `--ignore-eos` flag is passed to the `benchmark_serving.py` script
    which will in turn set this option in the JSON when making the LLM request.
    [`backend_request_func.py`](https://github.com/kimbochen/bench_serving/blob/499c0b171b499b02a1fd546fb2326d2175a5d66e/backend_request_func.py)
    sets this and also sets `max_tokens` to the desired `output_len` which
    _should_ ensure that the response has that exact desired number of output
    tokens. `ignore_eos` means that the LLM server will keep generating tokens
    even after seeing the end of sequence token.
  * It's interesting that some of the benchmark configurations enable
    multi-token prediction, and presumably find it beneficial even given the
    totally random token inputs. Is it possible that such configurations
    benefit from undesirable looped outputs (due to a combination of random
    inputs and continuing to sample tokens past the EOS marker) that
    potentially are very predictable and give an extra boost?
* The --num-prompts parameter controls the total number of requests that are
  issued. The benchmark script is written so it will wait for all of these to
  complete (either successfully or unsuccessfully). This is
  [typically](https://github.com/SemiAnalysisAI/InferenceX/blob/84320a0aadacae1114265b553830f48b56231817/benchmarks/gptoss_fp4_h100_slurm.sh#L51)
  set to the concurrency times 10, but some benchmark setups set it higher
  (presumably as the default figure finishes too quickly for good results).
* In terms of how requests are submitted with a certain level of concurrency:
  * See above for a discussion of the total number of requests
  * `--request-rate inf` is always passed, so there's no limit on submitting
    requests up to the concurency limit.
  * It [precomputes a list of requests to
    submit](https://github.com/kimbochen/bench_serving/blob/499c0b171b499b02a1fd546fb2326d2175a5d66e/benchmark_serving.py#L962)
    and then [uses a semaphore to limit
    concurrency](https://github.com/kimbochen/bench_serving/blob/499c0b171b499b02a1fd546fb2326d2175a5d66e/benchmark_serving.py#L664)
    but otherwise continuously submits requests up to the concurrency limit,
    and then waits until they call complete.
* There are no tests that the configuration is serving the model with the
  expected quality currently, but there's an [issue tracking at least adding a
  simple quality
  benchmark](https://github.com/SemiAnalysisAI/InferenceX/issues/123).
  Although none of the explored settings _should_ impact the quality of output,
  it's always possible they trigger a bug and in this case it's not
  interesting to benchmark.
* It would be helpful for reproducibility if more complete system information
  for the benchmark runners was released. This is [being worked
  on](https://github.com/SemiAnalysisAI/InferenceX/issues/393).
* You should of course consider whether the tested input and output sequence
  lengths correspond to a workload you are interested in (thank you to Aaron
  Zhao for [reminding me to mention
  this](https://www.linkedin.com/feed/update/urn:li:activity:7414767337058242562?commentUrn=urn%3Ali%3Acomment%3A%28activity%3A7414767337058242562%2C7415321431900905472%29&dashCommentUrn=urn%3Ali%3Afsd_comment%3A%287415321431900905472%2Curn%3Ali%3Aactivity%3A7414767337058242562%29).
  This benchmarking approach also doesn't consider caching. Both factors could
  be highly relevant if trying to estimate energy cost for a long context chat
  or 'agentic' flow. But I'm happy enough with the tested workloads as a
  starting point, and my main focus here is trying to get a degree of comfort
  with the reported numbers for the ISL/OSL combinations they've chosen to
  test.

## Filed issues

I ended up filing the following issues upstream:

* FIXED [Token throughput per MW is described as reflecting the generated tokens but
  is actually processed+generated
  tokens](https://github.com/SemiAnalysisAI/InferenceX/issues/293)
  * The companion [article introducing
    InferenceMAX](https://newsletter.semianalysis.com/p/inferencemax-open-source-inference)
    has previously defined throughput as the rate at which the GPU
    __generates__ tokens yet the figure displayed in the UI was the total
    number of output _and_ input tokens per second. The definition in the
    article has now been fixed, and changes to the UI make it more obvious
    based on context that throughput refers to input+output tokens (as y-axis
    metric options now exist to show "input token throughput per GPU" and
    "output token throughput per GPU").
  * [This talking head video from
    Nvidia](https://www.youtube.com/watch?v=yYha_OtxA14) seems to make the
    same error, talking about the number of tokens 'generated' per second per
    GPU when looking at the relevant results these sem to be the total throughput
    (i.e. output __plus__ the much faster to process input tokens).
* [Presented input/output token throughput per GPU for disaggregated setups
  not usefully comparable to standard multi-gpu
  setups](https://github.com/SemiAnalysisAI/InferenceX/issues/299)
  * In disaggregated setups you have some number of GPUs dedicated to prefill
    (processing input tokens) and some number dedicated to decode (generating
    output tokens). In this case, the reported input/output throughput figures
    refer to the input or output throughput per prefill GPU or per decode GPU.
    It doesn't make sense (IMHO) to plot this figure against the input/output
    throughput figures for a non-disaggregated setup. To make it comparable,
    the input/output throughput per GPU should be calculated by averaging
    across the whole cluster rather than just the GPUs dedicated to prefill or
    decode respectively.
* [Standard deviatation of interactivity (std_intvty) in result json is
  incorrectly
  calculated](https://github.com/SemiAnalysisAI/InferenceX/issues/300)
  * Not a big issue as the figure isn't used anywhere. Interactivity
    (tokens/second) metrics are calculated from the recorded time per output
    token. `1000/$tpot_metric` is correct for the mean, median, and p99 figures
    but mathematically incorrect for the standard deviation. e.g. a small
    standard deviation for time per output token will result in a huge
    standard deviation being computed for interactivity.
* FIXED [Reference kW figures no longer shown in frontend for each
  GPU](https://github.com/SemiAnalysisAI/InferenceX/issues/349)
  * At some point updates to the frontend logic meant that the per-GPU kW
    figures used in calculating the token throughput per utility MW were no
    longer displayed. This has now been fixed.
* [How will full workflow run output be retained beyond 90
  days](https://github.com/SemiAnalysisAI/InferenceX/issues/350)
  * The benchmark frontend helpfully links to the GitHub Actions run that
    generated the displayed results and has a datepicker to view previous
    results. Clicking through to GitHub means you can download the original
    .zip of the JSON format benchmark results which is something I take
    advantage of in the analysis later in this article. According to GitHub
    docs, [the maximum retention period for Actions artifacts and logs is 90
    days for a public
    repo](https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization).
    It would be good to have a mechanism so that this information is backed up
    rather than lost.
* [Contents of CONFIG_DIR path as used in launch_gb200-nv.sh is
  undisclosed](https://github.com/SemiAnalysisAI/InferenceX/issues/365)
  * Most benchmark configuration lives in the main repository, but
    unfortunately one of the Nvidia DeepSeek R1 configurations [relies on
    a config dir that's not publicly
    available](https://github.com/SemiAnalysisAI/InferenceX/blob/ff7dfc7365034aa84245f41c517c38618860d484/runners/launch_gb200-nv.sh#L26)
    meaning it can't be audited or reproduced. This is a case where tightening
    up benchmark rules and review process can hopefully avoid it happening in
    the future.
* [Reconsider allowing setting max_model_len / max_seq_len to
  isl+osl+tiny_margin](https://github.com/SemiAnalysisAI/InferenceX/issues/359)
  * As explained above, a number of benchmarks set `max_model_len` (or for
    Nvidia's TensorRT, `--max_seq_len`) to some figure that is just above
    ISL+OSL. Although some degree of tuning is expected, to me this goes
    against the idea that "[We want server configs to reflect real world
    deployments as much as
    possible](https://newsletter.semianalysis.com/p/inferencemax-open-source-inference)"
    and the stated goal "to provide benchmarks that both emulate real world
    applications as much as possible and reflect the continuous pace of
    software innovation". It's hard to imagine a realistic deployment that
    would configure their serving engine in a way such that it errors if
    input+output tokens passes ~2k tokens for instance. Looking at the
    [DeepSeek R1 0528 providers on
    OpenRouter](https://openrouter.ai/deepseek/deepseek-r1-0528), the vast
    majority offer greater than 128k context.
  * By my understanding, with PagedAttention the KV cache is dynamically
    allocated anyway so this setting would largely impact other data
    structures. Plus vllm at least contains a startup check that there is
    sufficient VRAM to serve at least one request at the maximum configured
    context. I would really like to see what impact this setting has on
    benchmarks.
  * The repository maintainers renamed my issue to a title that doesn't
    reflect my report. I'm hopeful they will review my recent comment and
    title it back.
* [Some reported metrics will be inflated if a serving engine sheds
  load](https://github.com/SemiAnalysisAI/InferenceX/issues/357)
  * This covers the observation made above that failed requests are simply
    skipped. As the number of failed requests isn't tracked, it's not easy to
    see if a particular configuration may appear better (better E2E latency,
    lower time to first token) as a reset of shedding load rather than
    queueing.
  * The repository maintainers renamed this issue to "[feature suggestion for
    vllm/vllm benchmark_serving]" and closed it. I'm hopeful they will read my
    [response](https://github.com/SemiAnalysisAI/InferenceX/issues/357#issuecomment-3680821210)
    and reconsider on the grounds that:
    * The benchmark_serving script isn't doing anything "wrong" necessarily.
      It is simply making an implementation choice with potential impact on
      results that the InferenceMAX harness isn't tracking.
    * The script is planned to be added to the repo soon anyway.
* [Benchmarked ISL and OSL averages 0.9*target_length meaning results are
  over-optimistic](https://github.com/SemiAnalysisAI/InferenceX/issues/356).
  * This is the problem mentioned above where the introduced variance in
    input/output sequence length has an average lower than the headline rate.
    As noted, this means specifically the end to end latency figure is
    misleading, but also impacts tokens/second and throughput to the extent
    that the cost of serving a query doesn't scale with O(n).
  * This will be fixed by [PR
    339](https://github.com/SemiAnalysisAI/InferenceX/pull/339) which
    upstreams the `benchmark_serving.py` script and in that modified branch
    changes `sample_random_requests` to sample a range with multiplier between
    `1 - RANGE_RATIO` and `1 + RANGE_RATIO`.

In the best case, you'd hope to look at the benchmark results, accept they're
probably represent a higher degree of efficiency than you'd likely get on a
real workload, that an API provider might achieve 50% of that and double the
effective cost per query to give a very rough upper estimate on per-query cost
But that only really works if the reported benchmark results roughly match the
achievable throughput in a setup configured for commercial serving.  Given the
tuning to specific isl/osl values, I'm not at all confident thats the case and
I don't know how wide the gap is.

## Generating results

Firstly I wrote a [quick
script](https://gist.github.com/asb/44fe17f4f5b7abed7836481be45c5a38#file-check-py)
to check some assumptions about the data and look for anything that seems
anomalous. Specifically:
* Check that total throughput per GPU matches what you'd expect based on the
  input token and output token throughput per GPU, even in the disaggregated
  case. i.e. the total thoughput per GPU averaged over the whole cluster
  should equal the sum of the input and output throughput per GPU provided
  those figures are averaged over the whole cluster.
* The ratio of input token throughput to output token throughput should be
  almost equal to the to the ratio of input to output tokens in the
  benchmark's workload. If not, there is something surprising that needs
  investigating.

Based on the information available in the generated result JSON and the
reported all-in power per GPU (based on SemiAnalysis' model), we can calculate
the Watt hours per query. First calculate the joules per token (watts per GPU
divided by the total throughput per GPU). This gives a weighted average of the
joules per token for the measured workload (i.e. reflecting the ratio of
isl:osl). Multiplying joules per token by the tokens per query (isl+osl) gives
the joules per query, and we can just divide by 3600 to get Wh.

There is some imprecision because we're constructing the figure for e.g.
8192/1024 ISL based on measurements with an average `0.9*8192` input and
`0.9*1024` output length. The whole calculation would be much simpler if the
benchmark harness recorded the number of queries executed and in what time,
meaning we can directly calculate the Wh/query from the Wh for the system over
the benchmark duration divided by the number of queries served (and
remembering that in the current setup each query is on average 90% of the
advertised sequence length).
 
This logic is wrapped up in a [simple
script](https://gist.github.com/asb/44fe17f4f5b7abed7836481be45c5a38#file-process_results-py).

There's been a recent change to [remove the 'full sweep'
workflows](https://github.com/SemiAnalysisAI/InferenceX/pull/381) in favour of
only triggering a subset of runs when there is a relevant change. But I
grabbed my results from before this happened, from a December 15th 2025 run.
However when finalising this article I spotted Nvidia managed to land some new
NVL72 DeepSeek R1 0528 configurations just before Christmas, so I've merged in
those results as well, using a run from December 19th. All data and scripts are
collected together [in this
Gist](https://gist.github.com/asb/44fe17f4f5b7abed7836481be45c5a38).

## Results

As well as giving the calculated Wh per query, the script also gives a
comparison point of minutes of PS5 gameplay ([according to
Sony](https://www.playstation.com/en-gb/legal/ecodesign/), "Active Power
Consumption" ranges from ~217W to ~197W depending on model - we'll just use
200W). The idea here is to provide some kind of reference point for what a
given Wh figure means in real-world times, rather than focusing solely on the
relative differences between different deployments. Comparisons to "minutes of
internet streaming" seem popular at the moment, presumably as it's because an
activity basically everyone does. I'm steering away from that because I'd
be comparing one value that's hard to estimate accurately and has many
provisos to another figure that's hard to estimate accurately and has many
provisos, which just injects more error and uncertainty into this effort to
better measure/understand/contextualise energy used for LLM inference.

I'm now going to cherry-pick some results for discussion. Firstly for DeepSeek
R1 0528 with 8k/1k ISL/OSL, we see that the reported configurations that give
a usable level of interactivity at fp8 report between 0.96-3.74 Wh/query
(equivalent to 0.29-1.12 minutes of PS5 gaming). The top row which is
substantially
more efficient is the newer [GB200 NVL72 configuration added at the end of
last
year](https://github.com/SemiAnalysisAI/InferenceX/commit/c040b5cf23ced2c7e23d1da03e1abae89e6426aa).
It's not totally easy to trace the configuration changes given they're
accompanied by a reworking of the associated scripts, but as far as I can see
the configuration ultimately used is [this file from the dynamo
repository](https://github.com/ai-dynamo/dynamo/blob/b7107d008/examples/backends/sglang/slurm_jobs/scripts/gb200-fp8/disagg/8k1k-max-tpt.sh).
Looking at the JSON the big gain comes from significantly higher prefill
throughput (with output throughput per GPU remaining roughly the same). This
indicates the older results (the second row) were bottlenecked waiting for
waiting for prefill to complete.

Workload               | Intvty (tok/s) | E2EL (s) | Details                                          | Wh/Q     | PS5 min
---------------------- | -------------- | -------- | ------------------------------------------------ | -------- | -------
fp8 DS R1 0528 8k/1k   | 39.5           | 36.5     | gb200 dynamo-sglang (72 GPUs disagg, conc: 2048, pfill_dp_attn, dec_dp_attn) | 0.96     | 0.29
fp8 DS R1 0528 8k/1k   | 31.3           | 55.2     | gb200 dynamo-sglang (72 GPUs disagg, conc: 1024, pfill_dp_attn, dec_dp_attn) | 3.13     | 0.94
fp8 DS R1 0528 8k/1k   | 20.9           | 48.8     | h200 trt (8 GPUs, conc: 64, dp_attn)             | 3.32     | 1.00
fp8 DS R1 0528 8k/1k   | 19.5           | 49.6     | h200 sglang (8 GPUs, conc: 64)                   | 3.39     | 1.02
fp8 DS R1 0528 8k/1k   | 23.9           | 39.9     | b200-trt trt (8 GPUs, conc: 64)                  | 3.39     | 1.02
fp8 DS R1 0528 8k/1k   | 22.3           | 44.5     | b200 sglang (8 GPUs, conc: 64)                   | 3.74     | 1.12

Now taking a look at the results for an fp4 quantisation of the same workload,
the result is significantly cheaper to serve with similer or better
interactivity and the NVL72 setup Nvidia submitted does have a significant
advantage over the 4/8 GPU clusters. This time we see 0.63-1.67 Wh/query
(equivalent to 0.19-0.50 minutes of PS5 power draw while gaming). Serving at a
lower quantisation impacts the quality of results of course, but the improved
efficiency, including on smaler 4 GPU setups helps demonstrate why models like
[Kimi K2 thinking](https://huggingface.co/moonshotai/Kimi-K2-Thinking) are
distributed as "native int4", with benchmark results reported at this
quantisation and quantisation aware training used to maintain quality of
result.

Workload               | Intvty (tok/s) | E2EL (s) | Details                                          | Wh/Q     | PS5 min
---------------------- | -------------- | -------- | ------------------------------------------------ | -------- | -------
fp4 DS R1 0528 8k/1k   | 41.6           | 24.6     | gb200 dynamo-trt (40 GPUs disagg, conc: 1075, pfill_dp_attn, dec_dp_attn) | 0.63     | 0.19
fp4 DS R1 0528 8k/1k   | 22.8           | 43.2     | b200-trt trt (4 GPUs, conc: 128, dp_attn)        | 0.93     | 0.28
fp4 DS R1 0528 8k/1k   | 18.7           | 59.3     | b200 sglang (4 GPUs, conc: 128)                  | 1.25     | 0.38
fp4 DS R1 0528 8k/1k   | 30.3           | 39.4     | b200 sglang (4 GPUs, conc: 64)                   | 1.67     | 0.50

Looking now at the 1k/8k workload (i.e. generating significant output) and the
cost is 15.0-16.3 Wh/query (equivalent to 4.49-4.89 minutes of PS5 power draw
while gaming). As expected this is significantly higher than the 8k/1k
workload as prefill (processing input tokens) is much cheaper per token than
decode (generating output tokens)

Workload               | Intvty (tok/s) | E2EL (s) | Details                                          | Wh/Q     | PS5 min
---------------------- | -------------- | -------- | ------------------------------------------------ | -------- | -------
fp8 DS R1 0528 1k/8k   | 42.5           | 176.3    | b200 sglang (8 GPUs, conc: 64)                   | 15.0     | 4.49
fp8 DS R1 0528 1k/8k   | 31.9           | 232.2    | h200 sglang (8 GPUs, conc: 64)                   | 15.9     | 4.76
fp8 DS R1 0528 1k/8k   | 31.2           | 237.9    | h200 trt (8 GPUs, conc: 64)                      | 16.3     | 4.88
fp8 DS R1 0528 1k/8k   | 39.1           | 189.5    | b200-trt trt (8 GPUs, conc: 64)                  | 16.3     | 4.89

Again, fp4 has a significant improvement in efficiency:

Workload               | Intvty (tok/s) | E2EL (s) | Details                                          | Wh/Q     | PS5 min
---------------------- | -------------- | -------- | ------------------------------------------------ | -------- | -------
fp4 DS R1 0528 1k/8k   | 29.7           | 251.5    | b200-trt trt (4 GPUs, conc: 256, dp_attn)        | 2.73     | 0.82
fp4 DS R1 0528 1k/8k   | 37.7           | 197.5    | b200-trt trt (8 GPUs, conc: 256, dp_attn)        | 4.31     | 1.29
fp4 DS R1 0528 1k/8k   | 34.2           | 221.2    | b200 sglang (4 GPUs, conc: 128)                  | 4.75     | 1.43
fp4 DS R1 0528 1k/8k   | 33.1           | 223.1    | b200-trt trt (4 GPUs, conc: 128)                 | 4.79     | 1.44

As you'd expect for a much smaller model at native fp4 quantisation,
GPT-OSS-120B is much cheaper to serve. e.g. for 8k/1k:

Workload               | Intvty (tok/s) | E2EL (s) | Details                                          | Wh/Q     | PS5 min
---------------------- | -------------- | -------- | ------------------------------------------------ | -------- | -------
fp4 GPT-OSS 120B 8k/1k | 45.8           | 20.8     | b200-trt trt (1 GPUs, conc: 128)                 | 0.11     | 0.03
fp4 GPT-OSS 120B 8k/1k | 93.1           | 10.5     | b200-trt trt (2 GPUs, conc: 128, dp_attn)        | 0.11     | 0.03
fp4 GPT-OSS 120B 8k/1k | 44.3           | 21.4     | b200 vllm (1 GPUs, conc: 128)                    | 0.11     | 0.03
fp4 GPT-OSS 120B 8k/1k | 145.7          | 6.7      | b200-trt trt (2 GPUs, conc: 64, dp_attn)         | 0.14     | 0.04
fp4 GPT-OSS 120B 8k/1k | 103.8          | 9.2      | b200 vllm (2 GPUs, conc: 64)                     | 0.20     | 0.06

Or for 1k/8k:

Workload               | Intvty (tok/s) | E2EL (s) | Details                                          | Wh/Q     | PS5 min
---------------------- | -------------- | -------- | ------------------------------------------------ | -------- | -------
fp4 GPT-OSS 120B 1k/8k | 80.5           | 91.6     | b200-trt trt (1 GPUs, conc: 128)                 | 0.49     | 0.15
fp4 GPT-OSS 120B 1k/8k | 72.3           | 102.0    | b200 vllm (1 GPUs, conc: 128)                    | 0.55     | 0.16
fp4 GPT-OSS 120B 1k/8k | 144.9          | 51.1     | b200-trt trt (2 GPUs, conc: 128, dp_attn)        | 0.55     | 0.17
fp4 GPT-OSS 120B 1k/8k | 129.4          | 57.0     | b200-trt trt (2 GPUs, conc: 128)                 | 0.61     | 0.18

## Conclusion

Well, this took rather a lot more work than I thought it would and I'm
not yet fully satisfied with the result. Partly we have to accept a degree of
fuzziness about marginal energy usage of an individual query - it's going to
depend on the overall workload of the system so there's going to be some
approximation when you try to cost a single query.

I'm glad that InferenceMAX exists and am especially glad that it's open and
publicly developed, which is what has allowed me to dive into its
implementation to the extent I have and flag concerns/issues. I feel it's not
yet fully living up to its aim of providing results that reflect real world
application, but I hope that will improve with further maturation and better
rules for benchmark participants. Of course, it may still make most sense to
collect benchmark figures myself and even if doing so, being able to refer to
the benchmarked configurations and get an indication of what hardware can
achieve what performance is helpful in doing so. Renting a 72-GPU cluster is
expensive and as far as I can see not typically available for a short time, so
any benchmarking run by myself would be limited to 4-8 GPU configurations. If
the gap in efficiency is huge for such setups vs the NVL72 then these smaller
setups are maybe less interesting.

If I found the time to run benchmarks myself, what would I be testing? I'd
move to [DeepSeek V3.2](https://huggingface.co/deepseek-ai/DeepSeek-V3.2). One
of the big features of this release was the movement to a new attention
mechanism which [scales _much_ closer to linearly with sequence
length](https://huggingface.co/deepseek-ai/DeepSeek-V3.2/resolve/main/assets/paper.pdf#section.3).
With e.g. [Kimi Linear](https://github.com/MoonshotAI/Kimi-Linear) and
[Qwen3-Next](https://qwen.ai/blog?id=4074cca80393150c248e508aa62983f9cb7d27cd),
other labs are moving in a similar direction experimentally at least. I'd
try to set up 8 GPU configuration with sglang/vllm configured in a way that it
would be capable of serving a commercial workload with varied input/output
sequence lengths and test this is the case (Chutes [provide their deployed
configs](https://chutes.ai/app/chute/398651e1-5f85-5e50-a513-7c5324e8e839?tab=source)
which may be another reference point). I'd want to see how much the effective
Wh per million input/output tokens varies depending on the different isl/osl
workloads. These _should_ be relatively similar given the linear attention
mechanism, and if so it's a lot easier to estimate the rough energy cost of a
series of your own queries of varied length. I would stick with the random
input tokens for the time being.

So where does that leave us? All of this and we've got figures for two
particular models, with one benchmark harness, a limited set of input/output
sequence lengths, and a range of
potential issues that might impact the conclusion. I think this is a useful
yardstick / datapoint, though I'd like to get towards something that's even
more useful and that I have more faith in.

## Article changelog
* 2026-02-17: (minor)
  * Changed GitHub links to point to SemiAnalysisAI/InferenceX rather than
    InferenceMAX/InferenceMAX, as they were broken by the upstream rename.
* 2026-01-09: (minor)
  * Fix broken link.
  * Add note that more complete system info would be helpful for
    reproducibility.
  * Add note about variety of input/output sequence lengths tested.
