+++
published = 2025-12-01
description = "GPU hours and energy used in training the recent Olmo 3 models"
+++

# Olmo 3 training cost

Recently I jotted down some notes on [LLM inference vs training costs for
DeepSeek](/pages/2025q4/minipost-llm-inference-vs-training-cost-for-deepseek.md)
and I wanted to add on an additional datapoint for training cost based on the
recently released [Olmo3 models](https://allenai.org/blog/olmo3) from the
Allen Institute for AI ("Ai2"). The model family has 7B and 32B parameter
models, with 'Think' variants available for 7B and 32B but so far only a 7B
'Instruct' non-reasoning version (but [watch this
space](https://xcancel.com/allen_ai/status/1991545790263857609)). What's
particularly interesting about the Olmo models to me is that beyond providing
open weights, the training scripts and datasets are openly available as well.

Going by the reported benchmarks at least it's competitive with less open
models at a similar size, and importantly they've increased the supported
context length from the rather limiting 4k tokens supported by the Olmo 2
series to a much more usable 64k tokens. Given the relatively small size these
models are less capable than relatively chunky models like DeepSeek R1/V3.x or
Kimi K2, but I've been impressed by the capability of 32B dense models for
basic queries, and from my non-scientific testing both the 32B and 7B Olmo3
variants seem to do a reasonable job of summarising things like discussion
threads. You can experiment yourself at
[playground.allenai.org](https://playground.allenai.org/).

## Energy required for training Olmo 3

One of the neat things about this level of openness is that it _should_ act as
a floor in terms of performance for future models of this size class assuming
they're appropriately funded and don't take too many risks chasing novelty.
Rerunning the training process with an updated dataset and some minor tweaks
is something you could imagine doing on some regular cadence, ideally as a
shared endeavour. Imagining this effort in the future, how much energy is
required? The initial version of the [detailed Olmo 3 technical
report](http://allenai.org/papers/olmo3) unfortunately has little to say on
this. We can get a back of the envelope figure in terms of GPU hours for
pre-training based on the reported 7700 tokens per second per GPU for the 7B
base model and 1900 tokens per second for the 32B base model and the ~6T token
dataset. But even better than that, we can just __ask__ the Ai2 folks
(sometimes the internet really does work wonderfully!). After asking on their
[public Discord](https://discord.gg/ai2) I was rapidly furnished with this
helpful answer:

<blockquote>
For some detailed numbers, we measured power consumption throughout training,
along with total GPU hours. We used ~234k H100 hours to pretrain the 7B, and
~1.05m H100 hours to pretrain the 32B. 1900 TPS is generally what our trainer
is capable of, but with restarts, evaluations, checkpointing, and occasional
network issues, the 32B took 1.05m hours. We measured an average power
consumption of ~621W while pretraining the 7B and ~649W while pretraining the
32B, and this means that our GPUs consumed ~146MWh for the 7B and ~681MWh for
the 32B. We'll include more detailed GPU hour information in a future version
of the paper, including for post-training!

_Ai2 Olmo 3 team [on their
Discord](https://discord.com/channels/1241138968448340109/1441462011618922647/1441471645046014038)._
</blockquote>


So that's 0.681 GWh in GPU power draw for pretraining the 32B model and
0.146 GWh in GPU power draw for pretraining the 7B model. As noted in the
quote, this is inclusive of restarts, checkpointing etc. But perhaps won't
include previous early stage experimentation. I look forward to an updated
technical report with full details, but pretraining should cover the bulk of
the compute requirements (as a reference point, today's [DeepSeek V3.2
paper](https://huggingface.co/deepseek-ai/DeepSeek-V3.2/blob/main/assets/paper.pdf)
found it notable that the post-training compute budget exceeded 10% of the
pretraining cost).

The 0.681 GWh figure doesn't account for full system power and cooling
cost. I'd love to be corrected, but I believe a 1.5x-2x multiplier would be an
assumption towards the upper end. But for the sake of this yardstick
comparison let's look at a few comparisons based on the reported number:

* 0.681 GWh of electricity would cost about £180k at UK residential rates
  (capped at 26.35p per kWh currently). Substantially less in the USA.
* [A larger leisure centre with a pool consumes ~2.5 GWh of energy per
  year](https://www.gov.wales/sites/default/files/publications/2023-11/leisure-centre-decarbonisation-guidance-note.pdf).
  I don't know if the idea of a "leisure centre" translates outside of the UK,
  but basically it's a swimming pool plus gym, squash/tennis courts etc.
  * The linked page claims ~2 GWh of energy in gas and 0.5 GWh in electricity.
    For the gas, to compare like with like you'd need to consider the source
    of energy for the electricity used for Olmo training.
* 0.681 GWh is ~0.11% of [LHC's annual 600 GWh energy
  consumption](https://www.home.cern/resources/faqs/facts-and-figures-about-lhc)
  or ~0.05% of CERN's annual consumption.
* We can estimate a Boeing 787-9 flying from London Heathrow to SFO
  consumes jet fuel containing ~0.58 GWh of energy.
  * Calculated with 8638km distance, 5.62kg fuel/km (taking the most economic
    787-9 long haul figure from [this table on
    Wikipedia](https://en.wikipedia.org/wiki/Fuel_economy_in_aircraft) and
    [11.95kWh/kg specific energy of jet
    fuel](https://en.wikipedia.org/wiki/Jet_fuel#Typical_physical_properties_for_Jet_A_and_Jet_A-1)).
  * This is a yardstick rather than a direct comparison. A direct comparison
    to the GWh of electricity used for the GPU compute of the LLM would depend
    on the source of the electricity. If it was e.g. gas rather than
    solar/hydro/wind then you'd want to compare the number of GWh consumed to
    create that electricity which would of course be higher.
  * As a further point of reference, FlightAware indicates 5 separate
    direct LHR to SFO flights scheduled per day.

## More efficient LLM training

We can hope for new breakthroughs, more efficient hardware, better datasets
and so on. But here is some work I noticed in the area. Fair warning: this
isn't my field, and we have to recognise applying a research result to a
production training run is sure to have challenges even if the research
suggests the trade-offs are worthwhile. So consider this vague gesticulating
about seemingly interesting work that is going on and find someone who knows
what they're talking about to confirm the degree to which it is
interesting/viable.

* Mixture of Experts (MoE) models are substantially cheaper to train which is
  one reason the industry has moved in that direction. The next Ai2 Olmo
  model is [expected to be
  MoE](https://old.reddit.com/r/LocalLLaMA/comments/1p24aet/ai2_just_announced_olmo_3_a_leading_fully_open_lm/npzqw4h/?context=3).
  The [Qwen
  blog](https://qwen.ai/blog?id=4074cca80393150c248e508aa62983f9cb7d27cd) has
  a
  [graph](https://img.alicdn.com/imgextra/i1/O1CN01FUbdQa1i6J7tAfCCn_!!6000000004363-2-tps-2860-1114.png)
  comparing the relative training cost in GPU hours of the dense Qwen3-32B vs
  Qwen3-30B-A3b vs Qwen3-Next-80B-A3B, where the latter
  makes further architectural changes, reporting a 10.7x reduction. ~2.5x of
  that is going to come from the reduced corpus size (15T tokens down from
  36T), but that still leaves plenty of improvement from other factors.
* Maybe it will be shown viable to train in lower precision such as MXFP8 or
  even NVFP4, which would allow much more throughput for a similar energy
  budget. Nvidia have worked to demonstrate this can be effective for
  [both](https://arxiv.org/pdf/2506.08027)
  [formats](https://arxiv.org/pdf/2509.25149) (see also [this work from
  MIT](https://arxiv.org/pdf/2512.02010)).
* Also from Nvidia, [Nemotron Elastic](https://arxiv.org/pdf/2511.16664)
  showed a model architecture that allows deriving smaller models without
  doing a separate pre-training runs.

Finally, the cheapest way to train an LLM from scratch is...to find a way to
avoid the need to. For models like Olmo 3 that release the base model and
checkpoints, people can apply their own post-training or perform additional
pre-training.

## Bonus comparison point: Apertus

[Apertus](https://www.swiss-ai.org/apertus) is a Swiss project to produce an
open LLM, with 70B and 8B models released so far. Their [full tech
report](https://arxiv.org/pdf/2509.14233) notes the following "Once a
production environment has been set up, we estimate that the model can be
realistically trained in approximately 90 days on 4096 GPUs, accounting for
overheads. If we assume 560 W power usage per Grace-Hopper module in this
period, below the set power limit of 660 W, we can estimate 5 GWh power usage
for the compute of the pretraining run."

## Article changelog
* 2025-12-04: (minor) Add link to "Four Over Six" NVFP4 training paper.
* 2025-12-02: (minor) Added clarifying note about energy via gas in the
  leisure centre comparison.
