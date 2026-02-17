+++
published = 2026-02-17
description = "Per-query energy consumption figures based on recent Lambda benchmarks"
+++

# Additional figures for per-query energy consumption of LLMs

Last month I wrote up a fairly long piece on [per-query energy consumption of
LLMs using the data from
InferenceMAX](/pages/2026q1/per-query-energy-consumption-of-llms.md) (note:
InferenceMAX has since been renamed to InferenceX). Much of the write-up was
dedicated to exploring what you can actually conclude from these figures and
how that interacts with some of the implementation decisions in the benchmark,
but I feel the results still give a useful yardstick. Beyond concerns about
overly-specialised serving engine configurations and whether the workload is
representative of real-world model serving in a paid API host, the other
obvious limitation is that InferenceMAX is only testing GPT-OSS 120b and
DeepSeek R1 0528 when there is a world of other models out there. I dutifully
added "run my own tests using other models" to the todo list and here we are.
By "here we are" I of course mean I made no progress towards that goal but
[Zach Mueller](https://muellerzr.github.io/) at [Lambda](https://lambda.ai/)
started publishing [model cards with the needed
data](https://lambda.ai/inference-models) - thanks Zach!

The setup for Lambda is simple - each model card lists the observed token
generation throughput and total throughput (along with other stats) for an
input sequence length / output sequence length (ISL/OSL) of 8192/1024, as
benchmarked using `vllm bench serve`. The command used to serve the LLM (using
sglang or vllm depending on the model) is also given. As a starting point this
is no worse than the InferenceMAX data, and potentially somewhat better due to
figures being taken from a configuration that's not [overly specialised to a
particular query
length](https://github.com/SemiAnalysisAI/InferenceX/issues/359#issue-3750796719).

The figures each Lambda model card gives us that are relevant for calculating
the energy per query are: the hardware used, token generation throughput and
total token throughput (input+output tokens). Other statistics such as the
time to first token, inter-token latency, and parallel requests tested help
confirm whether this is a configuration someone would realistically use. Using
an equivalent methodology to before, we get the Watt hours per query by:
* Determining the total Watts for the GPU cluster. We take the figures used by
  SemiAnalysis (2.17kW for a single B200) and multiply by the number of GPUs.
* Calculate the joules per token by dividing this total Watts figure by the
  total token throughput. This gives a weighted average of the joules per
  token for the measured workload, reflecting the ratio of isl:osl.
* Multiply this weighted average of joules per token by the tokens per query
  (isl+osl) to get the joules per query. Then divide by 3600 to get Wh.

Collecting the data from the individual model cards we can generate the
following (as before, using minutes of PlayStation 5 gameplay as a point of
comparison):

```python
data = {
    "Qwen/Qwen3.5-397B-A17B": {
        "num_b200": 8,
        "total_throughput": 11092,
    },
    "MiniMaxAI/MiniMax-M2.5": {
        "num_b200": 2,
        "total_throughput": 8062,
    },
    "zai-org/GLM-5-FP8": {
        "num_b200": 8,
        "total_throughput": 6300,
    },
    "zai-org/GLM-4.7-Flash": {
        "num_b200": 1,
        "total_throughput": 8125,
    },
    "arcee-ai/Trinity-Large-Preview": {
        "num_b200": 8,
        "total_throughput": 15611,
    },
}

# 8192 + 1024
TOKENS_PER_QUERY = 9216

# Taken from <https://inferencex.semianalysis.com/>
B200_KW = 2.17

# Reference power draw for PS5 playing a game. Taken from
# <https://www.playstation.com/en-gb/legal/ecodesign/> ("Active Power
# Consumption"). Ranges from ~217W to ~197W depending on model.
PS5_KW = 0.2


def wh_per_query(num_b200, total_throughput, tokens_per_query):
    total_cluster_kw = num_b200 * B200_KW
    total_cluster_watts = total_cluster_kw * 1000
    # joules_per_token is a weighted average for the measured mix of input
    # and output tokens.
    joules_per_token = total_cluster_watts / total_throughput
    joules_per_query = joules_per_token * tokens_per_query
    # Convert joules to watt-hours
    return joules_per_query / 3600.0

def ps5_minutes(wh):
    ps5_watts = PS5_KW * 1000
    return (wh / ps5_watts) * 60.0

MODEL_WIDTH = 31
WH_WIDTH = 8
PS5_WIDTH = 8

header = f"{'Model':<{MODEL_WIDTH}} | {'Wh/q':<{WH_WIDTH}} | {'PS5 min':<{PS5_WIDTH}}"
separator = f"{'-' * MODEL_WIDTH} | {'-' * WH_WIDTH} | {'-' * PS5_WIDTH}"

print(header)
print(separator)

for model, vals in data.items():
    wh = wh_per_query(vals["num_b200"], vals["total_throughput"], TOKENS_PER_QUERY)
    ps5_min = ps5_minutes(wh)

    wh_str = f"{wh:.2f}" if wh < 10 else f"{wh:.1f}"
    print(f"{model.strip():<{MODEL_WIDTH}} | {wh_str:<{WH_WIDTH}} | {ps5_min:.2f}")
```

This gives the following figures (reordered to show Wh per query in ascending
order, and added a column for interactivity (1/TPOT)):

Model                                 | Intvty (tok/s) | Wh/q     | PS5 min.
------------------------------------- | -------------- | -------- | --------
zai-org/GLM-4.7-Flash (bf16)          | 34.0           | 0.68     | 0.21
MiniMaxAI/MiniMax-M2.5 (fp8)          | 30.3           | 1.38     | 0.41
arcee-ai/Trinity-Large-Preview (bf16) | 58.8           | 2.85     | 0.85
Qwen/Qwen3.5-397B-A17B (bf16)         | 41.7           | 4.01     | 1.20
zai-org/GLM-5-FP8 (fp8)               | 23.3           | 7.05     | 2.12

As a point of comparison, the most efficient 8 GPU deployment of fp8 DeepSeek
R1 0528 from my figures in the [previous
article](/pages/2026q1/per-query-energy-consumption-of-llms.md) was 3.32 Wh
per query.

And that's all I really have for today. Some interesting datapoints with
hopefully more to come as Lambda puts up more model cards in this format.
There's a range of interesting potential further experiments to do, but for
now, I just wanted to share this initial look.
