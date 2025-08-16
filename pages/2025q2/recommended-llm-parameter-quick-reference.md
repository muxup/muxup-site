+++
published = 2025-06-23
description = "temperature, top_p, top_k, and more - which models have a vendors recommendation and which leave you on your own"
+++

# Vendor-recommended LLM parameter quick reference

I've been kicking the tires on various LLMs lately, and like many have been
quite taken by the pace of new releases especially of models with weights
distributed under open licenses, always with impressive benchmark results. I
don't have local GPUs so trialling different models necessarily requires using
an external host. There are various configuration parameters you can set when
sending a query that affect generation and many vendors document
recommended settings on the model card or associated documentation. For my own
purposes I wanted to collect these together in one place, and also confirm in
which cases common serving software like
[vLLM](https://github.com/vllm-project/vllm) will use defaults provided
alongside the model.

## Main conclusions

* If accessing a model via a hosted API you typically don't have much insight
  into their serving setup, so **explicitly setting parameters client-side is
  probably your best bet** if you want to try out a model and ensure any
  recommended parameters are applied to generation.
* Although recent versions of vLLM will take preferred parameters from
  `generation_config.json`, not all models provide that file or if they do,
  they may not include their documented recommendations in it.
* Some model providers have very strong and clear recommendations about which
  parameters to set to which values, for others it's impossible to find any
  guidance one way or another (or even what sampling setup was used for their
  benchmark results).
* Sadly there doesn't seem to be a good alternative to trawling through the
  model descriptions and associated documentation right now (though hopefully
  this page helps!).
* Even if every model starts consistently setting preferred parameters in
  `generation_config.json` (and inference API providers respect this), and/or
  a standard like [model.yaml](https://modelyaml.org/) is adopted containing
  these parameters, some attention may still be required if a model has
  different recommendations for different use cases / modes (as Qwen3 does).
* And of course there's a non-conclusion on how much this really matters. I
  don't know. Clearly for some models it's deemed very important, for the
  other's it's not always clear whether it just doesn't matter much, or if the
  model producer has done a poor job of documenting it.

## Overview of parameters

The parameters supported by vLLM are [documented
here](https://docs.vllm.ai/en/stable/api/vllm/index.html#vllm.SamplingParams),
though not all are supported in the HTTP API provided by different vendors.
For instance, the subset of parameters supported by models on
[Parasail](https://www.parasail.io/) (an inference API provider I've been
kicking the tires on recently) is [documented
here](https://docs.parasail.io/parasail-docs/serverless/available-parameters)
I cover just that subset below:

* `temperature`: controls the randomness of sampling of tokens. Lower values are
  more deterministic, higher values are more random. This is one the
  parameters you'll see spoken about the most.
* `top_p`: limits the tokens that are considered. If set to e.g. 0.5 then only
  consider the top most probable tokens whose summed probability doesn't
  exceed 50%.
* `top_k`: also limits the tokens that are considered, such that only the top
  `k` tokens are considered.
* `frequency_penalty`: penalises new tokens based on their frequency in the
  generated text. It's possible to set a negative value to encourage
  repetition.
* `presence_penalty`: penalises new tokens if they appear in the generated text
  so far. It's possible to set a negative value to encourage repetition.
* `repetition_penalty`: This is documented as being a parameter that penalises
  new tokens based on whether they've appeared so far in the generated text or
  prompt.
  * Based on that description it's not totally obvious how it differs from the
    frequency or presence penalties, but given the description talks about
    values less than 1 penalising repeated tokens and less than 1 encouraging
    repeated tokens we can infer this is applied as a multiplication on
    rather than an addition.
  * We can confirm this implementation by tracing through [where penalties are
    applied in vllm's
    sampler.py](https://github.com/vllm-project/vllm/blob/ea10dd9d9e00a88705a6203ad3318a367f6c372e/vllm/model_executor/layers/sampler.py#L272),
    which in turn calls the [apply_penalties helper
    function](https://github.com/vllm-project/vllm/blob/ea10dd9d9e00a88705a6203ad3318a367f6c372e/vllm/model_executor/layers/utils.py#L30).
    This confirms how the frequency and presence penalties are applied based
    only on the output, unlike the repetition penalty is applied taking the
    prompt into account as well. Following the call-stack down to an
    [implementation of the repetition
    penalty](https://github.com/vllm-project/vllm/blob/c3bf9bad11193ee684ed6083b6692d0b5bf2bac7/vllm/_custom_ops.py#L284)
    shows that if the
    [logit](https://stackoverflow.com/questions/41455101/what-is-the-meaning-of-the-word-logits-in-tensorflow/52111173#52111173)
    is positive, it divides by the penalty and otherwise multiplies by it.
  * This was a pointless sidequest as this is a vllm-specific parameter that
    none of the models I've seen has a specific recommendation for.

## Default vLLM behaviour

The above settings are typically exposed via the API, but what if you don't
explicitly set them? vllm
[documents](https://docs.vllm.ai/en/stable/getting_started/quickstart.html#openai-compatible-server)
that it will by default apply settings from `generation_config.json`
distributed with the model on HuggingFace if it exists (overriding its own
defaults), but you can ignore `generation_config.json` to just use vllm's own
defaults by setting `--generation-config vllm` when launching the server. This
behaviour was introduced [in a PR that landed in early March this
year](https://github.com/vllm-project/vllm/pull/12622).  We'll explore below
which models actually have a `generation_config.json` with their recommended
settings, but what about parameters not set in that file, or if that file
isn't present? As far as I can see, that's where
[`_DEFAULT_SAMPLING_PARAMS`](https://github.com/vllm-project/vllm/blob/c76a506bd60f56d364da0de415c48798870e1312/vllm/entrypoints/openai/protocol.py#L427)
comes in and we get `temperature=1.0` and repetition_penalty, top_p, top_k and
min_p set to values that have no effect on the sampler.

Although Parasail use vllm for serving most (all?) of their hosted models,
it's not clear if they're running with a configuration that allows defaults to
be taken from `generation_config.json`. I'll update this post if that is
clarified.

## Recommended parameters from model vendors

As all of these models are distributed with benchmark results front and
center, it should be easy to at least find what settings were used for these
results, even if it's not an explicit recommendation on which parameters to
use - right? Let's find out. I've decided to step through models groups by
their level of openness.


**Open weight and open dataset models**

* [allenai/OLMo-2-0325-32B-Instruct](https://huggingface.co/allenai/OLMo-2-0325-32B-Instruct)
  * **Recommendation**: None
  * **`generation_config.json` with recommended parameters**: No.
  * **Notes**: No recommendation in the model card, nothing specified in
    [generation_config.json](https://huggingface.co/allenai/OLMo-2-0325-32B-Instruct/blob/main/generation_config.json),
    in [the paper](https://arxiv.org/pdf/2501.00656), and a [request for
    recommendations for hte eqrlier 13B OLMo 2
    model](https://huggingface.co/allenai/OLMo-2-1124-13B/discussions/3) sadly
    didn't get a response.

**Open weight models**

* [deepseek-ai/DeepSeek-V3-0324](https://huggingface.co/deepseek-ai/DeepSeek-V3-0324)
  * **Recommendation**: `temperature=0.3` (specified on model card)
  * **`generation_config.json` with recommended parameters**: No.
  * **Notes**:
    * This model card is what made me pay more attention to these parameters -
      DeepSeek went as far as to [map a temperature of 1.0 via the API to
      their recommended
      0.3](https://huggingface.co/deepseek-ai/DeepSeek-V3-0324#temperature)
      (temperatures between 0 and 1 are multiplied by 0.7, and they subtract
      0.7 for temperatures between 1 and 2). So clearly they're keen to
      override clients that default to setting temperture=1.0.
    * There's no `generation_config.json` and the [V3 technical
      report](https://arxiv.org/pdf/2412.19437) indicates they used
      temperature=0.7 for for some benchmarks. They also state "Benchmarks
      containing fewer than 1000 samples are tested multiple times using varying
      temperature settings to derive robust final results" (not totally clear if
      results are averaged, or the best result is taken). There's no
      recommendation I can see for other generation parameters, and to add some
      extra confusion the DeepSeek API docs have a [page on the temperature
      parameter](https://api-docs.deepseek.com/quick_start/parameter_settings)
      with specific recommendations for different use cases and it's not totally
      clear if these apply equally to V3 (after its temperature scaling) and R1.
* [deepseek-ai/DeepSeek-R1-0528](https://huggingface.co/deepseek-ai/DeepSeek-R1-0528)
  * **Recommendation**: `temperature=0.6`, `top_p=0.95` (specified on model
    card)
  * **`generation_config.json` with recommended parameters**: Yes.
  * **Notes**: They report using temperature=0.6 and top_p=0.95 for their
    benchmarks (this is stated both on the model card and the
    [paper](https://arxiv.org/pdf/2501.12948)) and state that temperature=0.6
    is the value used for the web chatbot interface. They do have a
    [generation_config.json that includes that
    setting](https://huggingface.co/deepseek-ai/DeepSeek-R1-0528/blob/main/generation_config.json).
* [ibm-granite/granite-3.3-8b-instruct](https://huggingface.co/ibm-granite/granite-3.3-8b-instruct)
  * **Recommendation**: None.
  * **`generation_config.json` with recommended parameters**: File
    [exists](https://huggingface.co/ibm-granite/granite-3.3-8b-instruct/blob/main/generation_config.json),
    sets no parameters.
* [microsoft/phi-4](https://huggingface.co/microsoft/phi-4)
  * **Recommendation**: None.
  * **`generation_config.json` with recommended parameters**: No.
  * **Notes**: No explicit recommendation in the model card and [nothing set
    in
    generation_config.json](https://huggingface.co/microsoft/phi-4/blob/main/generation_config.json),
    although most evaluations in the [Phi-4 technical
    report](https://arxiv.org/pdf/2412.08905) seem to use `temperature=0.5`.
* [microsoft/Phi-4-reasoning](https://huggingface.co/microsoft/Phi-4-reasoning)
  * **Recommendation**: `temperature=0.8`, `top_k=50`, `top_p=0.95` (specified
    on model card)
  * **`generation_config.json` with recommended parameters**:
    [Yes](https://huggingface.co/microsoft/Phi-4-reasoning/blob/main/generation_config.json).
* [mistralai/Mistral-Small-3.2-24B-Instruct-2506](https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506)
  * **Recommendation**: `temperature=0.15`. (specified on model card)
  * **`generation_config.json` with recommended parameters**:
    [Yes](https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506/blob/main/generation_config.json)
  * Recommends `temperature=0.15` and [includes this in
    generation_config.json](https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506/blob/main/generation_config.json).
  * **Notes**: I saw that [one of Mistral's API
    methods](https://docs.mistral.ai/api/#tag/models/operation/list_models_v1_models_get)
    for their hosted models returns the `default_model_temperature`. Executing
    `curl --location "https://api.mistral.ai/v1/models" --header
    "Authorization: Bearer $MISTRAL_API_KEY" | jq -r '.data[] | "\(.name):
    \(.default_model_temperature)"' | sort` gives some confusing results. The
    `mistral-small-2506` version isn't yet available on the API. But the older
    `mistral-small-2501` is, with a default temperature of `0.3` (differing
    from the recommendation on [the model
    card](https://huggingface.co/mistralai/Mistral-Small-24B-Instruct-2501).
    `mistral-small-2503` has `null` for its default temperature. Go figure.
* [mistralai/Devstral-Small-2505](https://huggingface.co/mistralai/Devstral-Small-2505)
  * **Recommendation**: Unclear.
  * **`generation_config.json` with recommended parameters**: No.
  * **Notes**: This is a fine-tune of Mistral-Small-3.1. There is no explicit
    recommendation for temperature on the model card, but the example code
    does use `temperature=0.15`. However, this [isn't set in
    generation_config.json](https://huggingface.co/mistralai/Devstral-Small-2505/blob/main/generation_config.json)
    (which doesn't set any default parameters) and Mistral's API indicates a
    default temperature of `0.0`.
* [mistralai/Magistral-Small-2506](https://huggingface.co/mistralai/Magistral-Small-2506)
  * **Recommendation**: `temperature=0.7`, `top_p=0.95` (specified on model
    card)
  * **`generation_config.json` with recommended parameters**:
    [No](https://huggingface.co/mistralai/Magistral-Small-2506/blob/main/generation_config.json) (file exists, but parameters missing).
  * **Notes**: The model card has a very clear recommendation to use
    `temperature=0.7` and `top_p=0.95` and this default temperature is also reflected
    in Mistral's API mentioned above.
* [qwen3
  family](https://huggingface.co/collections/Qwen/qwen3-67dd247413f0e2e4f653967f)
  including Qwen/Qwen3-235B-A22B, Qwen/Qwen3-30B-A3B, Qwen/Qwen3-32B, and
  more.
  * **Recommendation**: `temperature=0.6`, `top_p=0.95`, `top_k=20`, `min_p=0` for thinking mode
    and for non-thinking mode `temperature=0.7`, `top_p=0.8`, `top_k=20`
    `min_p=0` (specified on model card)
  * **`generation_config.json` with recommended parameters**: Yes, e.g. [for
    Qwen3-32B](https://huggingface.co/Qwen/Qwen3-32B/blob/main/generation_config.json)
    (uses the "thinking mode" recommendations). (All the ones I've checked
    have this at least).
  * **Notes**: Unlike many others, there is a very clear recommendation under
    the [best practices section of each model
    card](https://huggingface.co/Qwen/Qwen3-32B#best-practices), which for all
    models in the family that I've checked makes the same recommendation. They
    also suggest setting the `presence_penalty` between 0 and 2 to reduce
    endless repetitions. The [Qwen 3 technical
    report](https://arxiv.org/pdf/2505.09388) notes the same parameters but
    also states that for the non-thinking mode they set `presence_penalty=1.5`
    and applied the same setting for thinking mode for the Creative Writing v3
    and WritingBench benchmarks.
* [THUDM/GLM-4-32B-0414](https://huggingface.co/THUDM/GLM-4-32B-0414)
  * **Recommendation**: None.
  * **`generation_config.json` with recommended parameters**:
    [No](https://huggingface.co/THUDM/GLM-4-32B-0414/blob/main/generation_config.json)
    (file exists, but parameters missing).
  * **Notes**: There's a [request for recommended sampling
    parameters](https://huggingface.co/THUDM/GLM-4-32B-0414/discussions/10) on
    the HuggingFace page but it's not had a response.
* [THUDM/GLM-Z1-32B-0414](https://huggingface.co/THUDM/GLM-Z1-32B-0414)
  * **Recommendation**: `temperature=0.6`, `top_p=0.95`, `top_k=40` and
    `max_new_tokens=30000` (specified on model card).
  * **`generation_config.json` with recommended parameters**:
    [No](https://huggingface.co/THUDM/GLM-Z1-32B-0414/blob/main/generation_config.json).

**Weight available (non-open) models**

* [google/gemma-3-27b-it](https://huggingface.co/google/gemma-3-27b-it)
  * **Recommendation**: Allegedly `temperature=1.0`, `top_k=64`, `top_p=0.96`
    ([source](https://old.reddit.com/r/LocalLLaMA/comments/1j9hsfc/gemma_3_ggufs_recommended_settings/)).
  * **`generation_config.json` with recommended parameters**:
    [Yes](https://huggingface.co/google/gemma-3-27b-it/blob/main/generation_config.json)
    (`temperature=1.0` should be the vllm default anyway, so it shouldn't
    matter it isn't specified).
  * **Notes**: It was surprising to not see more clarity on this in the model
    card or [technical
    report](https://storage.googleapis.com/deepmind-media/gemma/Gemma3Report.pdf),
    neither of which have an explicit recommendation. As noted above, the
    `generation_config.json` does set `top_k` and `top_p` and the Unsloth
    folks apparently had confirmation from the Gemma team on recommended
    temperature though I couldn't find a public comment directly from
    the Gemma team.
* [meta-llama/Llama-4-Scout-17B-16E-Instruct](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct)
  * **Recommendation**: `temperature=0.6`, `top_p=0.9` (source:
    `generation_config.json`).
  * **`generation_config.json` with recommended parameters**:
    [Yes](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct/blob/main/generation_config.json).
  * **Notes**: There was no discussion of recommended parameters in the model
    card itself. I accessed `generation_config.json` via a third-party mirror
    as providing name and DoB to view it on HuggingFace (as required by
    Llama's restrictive access policy) seems ridiculous.

## model.yaml

As it happens, while writing this blog post I saw [Simon Willison blogged
about model.yaml](https://simonwillison.net/2025/Jun/21/model-yaml/).
[Model.yaml](https://modelyaml.org/) is an initiative from the LM Studio folks
to provide a definition of a model and its sources that can be used with
multiple local inference tools. This includes the ability to specify preset
options for the model. It doesn't appear to be used by anyone else though, and
looking at the [LM Studio model catalog](https://lmstudio.ai/models), taking
[qwen/qwen3-32b](https://lmstudio.ai/models/qwen/qwen3-32b) as an example:
although the Qwen3 series have very strongly recommended default settings, the
model.yaml only sets `top_k` and `min_p`, leaving `temperature` and `top_p`
unset.
