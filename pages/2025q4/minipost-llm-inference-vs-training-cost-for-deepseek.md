+++
published = 2025-11-29
description = "Looking at data from DeepSeek for GPU hours serving their API vs final run training."
+++

# LLM inference vs training costs for DeepSeek

Tl;dr: Based on published data from DeepSeek, we can estimate it takes
something like ~70 days of inference traffic (served by DeepSeek themselves,
ignoring any other providers) to match the GPU hours used for the final
training run for V3 and R1.

Simon Willison recently [reshared some figures on inference costs for
LLMs](https://bsky.app/profile/simonwillison.net/post/3m6qdf5rffs2l). I
couldn't agree more with the comment further down that thread "The big AI labs
continue to be infuriatingly opaque about the actual figures for their total
electricity and water consumption".

A number of responses wonder about the cost of training. If you accept the
reported figures for serving a query, what impact does it have if you amortise
the energy spent training the model over the served queries? Mistral did this
for their [lifecycle
analysis](https://mistral.ai/news/our-contribution-to-a-global-environmental-standard-for-ai)
but they grouped together "training and inference" and kept confidential the
ratio of energy for training vs inference by reporting a figure that combined
the training cost with 18 months of usage. The thread reminded me of another
datapoint available for DeepSeek that seemed worth writing up. I think this
gives some helpful intuition for the amortised cost of training for a widely
used model of that size, but to state the obvious any attempt to apply that
intuition to other models is totally reliant on how widely used it is.

DeepSeek have published figures both on training and on inference for
DeepSeek's website and API users. I will attempt to consistently refer to the
figure for training as "final run training cost" to reflect the fact the
number of GPU hours used in experimentation and failed attempts isn't
reported. For final run training for DeepSeek-R1:
* 2.788M H800 GPU hours for V3 which serves as the R1 base (see Table 1
  in the [V3 technical report](https://arxiv.org/pdf/2412.19437)).
* 0.147M H800 GPU hours for building R1 on top of V3 (see Supplementary Table
  4 in the [supplementary
  information](https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-025-09422-z/MediaObjects/41586_2025_9422_MOESM1_ESM.pdf)
  for the [R1 Nature
  article](https://www.nature.com/articles/s41586-025-09422-z)).
* **Total**: 2.935M H800 GPU hours

Now for inference, back in February DeepSeek wrote up [details of their
inference
system](https://github.com/deepseek-ai/open-infra-index/blob/main/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md)
giving details of cost of serving, profit margin, and load over a 24h period.
So yes, we're extrapolating from this datapoint and assuming it's
representative. Given the worldwide inference of DeepSeek R1/V3 is surely much
larger (being openly licensed there are many vendors who are serving it), I'm
not overly worried about this aspect. Their reported average inference serving
infrastructure occupancy is 226.75 nodes (each node containing 8 H800 GPUs),
meaning **43536 H800 GPU hours per day**. At that rate, it will take **~67.5
days** of traffic for the same number of H800 GPU hours to be used for
inference as for the final training run.

All this to say, for a widely used model of DeepSeek R1 scale when looking at
the cost of inference, accounting for the amortised final run training cost is
more likely to be a multiplier of 2x or less rather than something much
larger. In terms of energy, this does assume that the power draw of the H800
GPUs while running inference is similar to the draw during training. And to
underline again, the reported training cost surely doesn't include
experimentation, aborted runs etc.
