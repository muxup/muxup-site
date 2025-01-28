+++
published = 2023-11-26
description = "Some notes on storing data in pointers and the impact of >48-bit virtual addresses"
+++

# Storing data in pointers

## Introduction
On mainstream 64-bit systems, the maximum bit-width
of a virtual address is somewhat lower than 64 bits (commonly 48 bits). This
gives an opportunity to repurpose those unused bits for data storage, if
you're willing to mask them out before using your pointer (or have a hardware
feature that does that for you - more on this later). I wondered what happens
to userspace programs relying on such tricks as processors gain support for
wider virtual addresses, hence this little blog post. TL;DR is that there's no
real change unless certain hint values to enable use of wider addresses are
passed to `mmap`, but read on for more details as well as other notes about
the general topic of storing data in pointers.

## Storage in upper bits assuming 48-bit virtual addresses

Assuming your platform has 48-bit wide virtual addresses, this is pretty
straightforward. You can stash whatever you want in those 16 bits, but you'll
need to ensure you masking them out for every load and store (which is cheap,
but has at least some cost) and would want to be confident that there's no
other attempted users for these bits. The masking would be slightly different
in kernel space due to rules on how the upper bits are set:
* x86-64 defines a [canonical form of
  addresses](https://cdrdv2.intel.com/v1/dl/getContent/671200) (see 3.3.7.1).
  This describes how on an implementation with 48-bit virtual addresses, bits
  63:48 must be set to the value of bit 47 (i.e. sign extended). The [memory
  map used by the Linux
  kernel](https://docs.kernel.org/arch/x86/x86_64/mm.html) uses bit 47 to
  split the address space between kernel and user addresses, so that bit will
  always be 0 for user-space addresses meaning bits 63:48 must also be 0 to be
  in canonical form.
* RISC-V has essentially the same restriction (see [4.5.1 in the RISC-V
  privileged
  specification](https://github.com/riscv/riscv-isa-manual/releases/download/Priv-v1.12/riscv-privileged-20211203.pdf))
  "instruction fetch addresses and load and store effective addresses, which
  are 64 bits, must have bits 63-48 all equal to bit 47, or else a page-fault
  exception will occur." The virtual memory layout used by the Linux kernel
  [uses the same approach as for
  x86-64](https://docs.kernel.org/arch/riscv/vm-layout.html).
* AArch64 has a slight variant on the above which essentially provides a
  49-bit address space (meaning user-space virtual memory can cover 256TiB
  rather than 128TiB). As [described in the Armv8-A address translation
  documentation](https://documentation-service.arm.com/static/5efa1d23dbdee951c1ccdec5?token=)
  (section 3), for a 48-bit address space bits 63:48 must be all 0s or all 1s.
  However, they don't need to be a copy of bit 47, and a different address
  translation table is used depending on whether bits 63:48 are 1 or 0. This
  [allows splitting kernel/user addresses without giving up bit
  47](https://docs.kernel.org/arch/arm64/memory.html).

## What if virtual addresses are wider than 48 bits?

So we've covered the easy case, where you can freely (ab)use the upper 16 bits
for your own purposes. But what if you're running on a system that has wider
than 48 bit virtual addresses? How do you know that's the case? And is it
possible to limit virtual addresses to the 48-bit range if you're sure you
don't need the extra bits?

You can query the virtual address width from the command-line by `cat`ting
`/proc/cpuinfo`, which might include a line like `address sizes	: 39 bits
physical, 48 bits virtual`. I'd hope there's a way to get the same information
without parsing `/proc/cpuinfo`, but I haven't been able to find it.

As for how to keep using those upper bits on a system with wider virtual
addresses, helpfully the behaviour of `mmap` is defined with this
compatibility in mind. It's explicitly documented [for
x86-64](https://docs.kernel.org/arch/x86/x86_64/5level-paging.html#user-space-and-large-virtual-address-space),
[for
AArch64](https://docs.kernel.org/arch/arm64/memory.html#bit-userspace-vas) and
[for RISC-V](https://docs.kernel.org/arch/riscv/vm-layout.html#userspace-vas)
that addresses beyond 48-bits won't be returned unless a hint parameter beyond
a certain width is used (the details are slightly different for each target).
This means if you're confident that nothing within your process is going to be
passing such hints to `mmap` (including e.g. your `malloc` implementation), or
at least that you'll never need to try to reuse upper bits of addresses
produced in this way, then you're free to presume the system uses no more than
48 bits of virtual address.

## Top byte ignore and similar features

Up to this point I've completely skipped over the various architectural
features that allow some of the upper bits to be ignored upon dereference,
essentially providing hardware support for this type of storage of additional
data within pointeres by making additional masking unnecessary.

* x86-64 keeps things interesting by having slightly different variants of
  this for Intel and AMD.
  * Intel introduced Linear Address Masking (LAM), documented in chapter 6 of
    [their document on instruction set extensions and future
    features](https://cdrdv2.intel.com/v1/dl/getContent/671368). If enabled
    this modifies the canonicality check so that, for instance, on a system
    with 48-bit virtual addresses bit 47 must be equal to bit 63. This would
    allow bits 62:48 (15 bits) can be freely used with no masking needed.
    "LAM57" allows 62:57 to be used (6 bits). It seems as if Linux is
    currently opting to [only support LAM57 and not
    LAM48](https://lwn.net/Articles/902094/). Support for LAM can be
    configured separately for user and supervisor mode, but I'll refer you to
    the Intel docs for details.
  * AMD instead [describes Upper Address
    Ignore](https://www.amd.com/content/dam/amd/en/documents/processor-tech-docs/programmer-references/24593.pdf)
    (see section 5.10) which allows bits 63:57 (7 bits) to be used, and unlike
    LAM doesn't require bit 63 to match the upper bit of the virtual address.
    As documented in LWN, this [caused some concern from the Linux kernel
    community](https://lwn.net/Articles/888914/). Unless I'm missing it, there
    doesn't seem to be any level of support merged in the Linux kernel at the
    time of writing.
* RISC-V has the proposed [pointer masking
  extension](https://github.com/riscv/riscv-j-extension/blob/1c7cf98295e678e015750ff0b7fdc54ed213b95e/zjpm-spec.pdf)
  which defines new supervisor-level extensions Ssnpm, Smnpm, and Smmpm to
  control it. These allow `PMLEN` to potentially be set to 7 (masking the
  upper 7 bits) or 16 (masking the upper 16 bits). In usual RISC-V style, it's
  not mandated which of these are supported, but the [draft RVA23 profile
  mandates that PMLEN=7 must be supported at a
  minimum](https://github.com/riscv/riscv-profiles/blob/ff79c48f975f93c25f6359d47d0f578b3ecb8555/rva23-profile.adoc).
  Eagle-eyed readers will note that the proposed approach has the same issue
  that caused concern with AMD's Upper Address Ignore, namely that the most
  significant bit is no longer required to be the same as the top bit of the
  virtual address. This is
  [noted](https://github.com/riscv/riscv-j-extension/blob/1c7cf98295e678e015750ff0b7fdc54ed213b95e/zjpm/background.adoc#pointer-masking-and-privilege-modes)
  in the spec, with the suggestion that this is solvable at the ABI level and
  some operating systems may choose to mandate that the MSB not be used for
  tagging.
* AArch64 has the [Top Byte
  Ignore](https://developer.arm.com/documentation/den0024/a/ch12s05s01) (TBI)
  feature, which as the name suggests just means that the top 8 bits of a
  virtual address are ignored when used for memory accesses and can be used to
  store data. Any other bits between the virtual address width and top byte
  must be set to all 0s or all 1s, as before. TBI is also used by Arm's
  [Memory Tagging
  Extension](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/Arm_Memory_Tagging_Extension_Whitepaper.pdf)
  (MTE), which uses 4 of those bits as the "key" to be compared against the
  "lock" tag bits associated with a memory location being accessed. Armv8.3
  defines another potential consumer of otherwise unused address bits,
  [pointer
  authentication](https://www.qualcomm.com/content/dam/qcomm-martech/dm-assets/documents/pointer-auth-v7.pdf)
  which uses 11 to 31 bits depending on the virtual address width if TBI isn't
  being used, or 3 to 23 bits if it is.

A relevant historical note that multiple people pointed out: the original
Motorola 68000 had a 24-bit address bus and so the top byte was simply
ignored which caused [well documented porting issues when trying to expand the
address space](https://macgui.com/news/article.php?t=527).

## Storing data in least significant bits

Another commonly used trick I'd be remiss not to mention is repurposing a
small number of the least significant bits in a pointer. If you know a certain
set of pointers will only ever be used to point to memory with a given minimal
alignment, you can exploit the fact that the lower bits corresponding to that
alignment will always be zero and store your own data there. As before,
you'll need to account for the bits you repurpose when accessing the pointer -
in this case either by masking, or by adjusting the offset used to access the
address (if those least significant bits are known).

As [suggested by Per
Vognsen](https://fosstodon.org/@pervognsen@mastodon.social/111478311705167492),
after this article was first published, you can exploit x86's [scaled index
addressing mode](https://en.wikipedia.org/wiki/ModR/M#SIB_byte) to use up
to 3 bits that are unused due to alignment, but storing your data in the upper bits.
The scaled index addressing mode meaning there's no need for separate pointer
manipulation upon access. e.g. for an 8-byte aligned address, store it
right-shifted by 3 and use the top 3 bits for metadata, then scaling by 8
using SIB when accessing (which effectively ignores the top 3 bits).  This has
some trade-offs, but is such a neat trick I felt I have to include it!

## Some real-world examples

To state what I hope is obvious, this is far from an exhaustive list. The
point of this quick blog post was really to discuss cases where additional
data is stored alongside a pointer, but of course unused bits can also be
exploited to allow a more efficient tagged union representation (and this is
arguably more common), so I've included some examples of that below:

* The [fixie trie](https://www.cipht.net/2017/10/29/fixie-tries.html), is a
  variant of the trie that uses 16 bits in each pointer to store a bitmap used
  as part of the lookup logic. It also exploits the minimum alignment of
  pointers to repurpose the least significant bit to indicate if a value is a
  branch or a leaf.
* On the topic of storing data in the least significant bits, we have a handy
  [PointerIntPair](https://github.com/llvm/llvm-project/blob/dc8b055c71d2ff2f43c0f4cac66e15a210b91e3b/llvm/include/llvm/ADT/PointerIntPair.h#L64)
  class in LLVM to allow the easy implementation of this optimisation. There's
  also an ['alignment niches'
  proposal](https://github.com/rust-lang/rfcs/pull/3204) for Rust which would
  allow this kind of optimisation to be done automatically for `enum`s (tagged
  unions). Another example of repurposing the LSB found in the wild would be
  the Linux kernel [using it for a spin
  lock](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/include/linux/list_bl.h)
  (thanks Vegard Nossum for the
  [tip](https://fosstodon.org/@vegard@mastodon.social/111478755690419785), who
  notes this is used in the kernel's directory entry cache hashtable). There
  are surely many many more examples.
* Go repurposes both upper and lower bits in its
  [taggedPointer](https://github.com/golang/go/blob/master/src/runtime/tagptr_64bit.go),
  used internally in its runtime implementation.
* If you have complete control over your heap then there's more you can do to
  make use of embedded metadata, including using additional bits by avoiding
  allocation outside of a certain range and using redundant mappings to avoid
  or reduce the need for masking. OpenJDK's ZGC [is a good example of
  this](https://dinfuehr.github.io/blog/a-first-look-into-zgc/), utilising a
  42-bit address space for objects and upon allocation mapping pages to
  different aliases to allow pointers using their metadata bits to be
  dereferenced without masking.
* A fairly common trick in language runtimes is to exploit the fact that
  values can be stored inside the payload of double floating point NaN (not a
  number) values and overlap it with pointers (knowing that the full 64 bits
  aren't needed) and even small integers. There's a nice description of this
  [in
  JavaScriptCore](https://github.com/WebKit/WebKit/blob/0a64dd54421137c48a57e6e0aab15a99139a8776/Source/JavaScriptCore/runtime/JSCJSValue.h#L403),
  but it was famously used in
  [LuaJIT](http://lua-users.org/lists/lua-l/2009-11/msg00089.html). Andy Wingo
  also has a [helpful
  write-up](https://wingolog.org/archives/2011/05/18/value-representation-in-javascript-implementations).
  Along similar lines, OCaml steals just the least significant bit in order to
  [efficiently support unboxed
  integers](https://blog.janestreet.com/what-is-gained-and-lost-with-63-bit-integers/)
  (meaning integers are 63-bit on 64-bit platforms and 31-bit on 32-bit
  platforms).
* Apple's Objective-C implementation makes heavy use of unused pointer bits,
  with some examples
  [documented](https://www.mikeash.com/pyblog/friday-qa-2012-07-27-lets-build-tagged-pointers.html)
  [in](https://www.mikeash.com/pyblog/friday-qa-2013-09-27-arm64-and-you.html)
  [detail](https://www.mikeash.com/pyblog/friday-qa-2015-07-31-tagged-pointer-strings.html)
  on Mike Ash's excellent blog (with a more recent scheme [described on Brian
  T. Kelley's blog](https://alwaysprocessing.blog/2023/03/19/objc-tagged-ptr).
  Inlining the reference count (falling back to a hash lookup upon overflow)
  is a fun one. Another example of using the LSB
  to store small strings in-line is [squoze](https://squoze.org/).
* V8 opts to limit the heap used for V8 objects to 4GiB using [pointer
  compression](https://v8.dev/blog/pointer-compression), where an offset is
  used alongside the 32-bit value (which itself might be a pointer or a 31-bit
  integer, depending on the least significant bit) to refer to the memory
  location.
* As this list is becoming more of a collection of things slightly outside the
  scope of this article I might as well round it off with [the XOR linked
  list](https://en.wikipedia.org/wiki/XOR_linked_list), which reduces the
  storage requirements for doubly linked lists by exploiting the reversibility
  of the XOR operation.
* I've focused on storing data in conventional pointers on current commodity
  architectures but there is of course a huge wealth of work involving tagged
  memory (also an area where [I've
  dabbled](https://github.com/lowRISC/lowrisc-site/blob/master/static/downloads/lowRISC-memo-2014-001.pdf) -
  something for a future blog post perhaps) and/or alternative pointer
  representations. I've touched on this with MTE (mentioned due to its
  interaction with TBI), but another prominent example is of course
  [CHERI](https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-941.pdf) which moves
  to using 128-bit capabilities in order to fit in additional inline metadata.
  David Chisnall provided some [observations based on porting code to CHERI
  that relies on the kind of tricks described in this
  post](https://lobste.rs/s/5417dx/storing_data_pointers#c_j12qr0).
* Sometime after this article was published, Troy Hinckley put together a
  really interesting blog post [benchmarking different pointer tagging
  schemes](https://coredumped.dev/2024/09/09/what-is-the-best-pointer-tagging-method/).

## Fin

What did I miss? What did I get wrong? Let me know [on
Mastodon](https://fosstodon.org/@asb) or email (asb@asbradbury.org).

You might be interested in the discussion of this article [on
lobste.rs](https://lobste.rs/s/5417dx/storing_data_pointers), [on
HN](https://news.ycombinator.com/item?id=38424090), [on various
subreddits](https://old.reddit.com/r/cpp/duplicates/184n4bd/storing_data_in_pointers/),
or [on Mastodon](https://fosstodon.org/@asb/111478289261238134).

## Article changelog
* 2025-01-28: (minor) Add link to Troy Hinkcley's blog post benchmarking
  pointer tagging schemes.
* 2023-12-02: (minor)
  * Reference Brian T. Kelley's blog providing a more up-to-date description
    of "pointer tagging" in Objective-C. [Spotted on
    Mastodon](https://fosstodon.org/@uliwitness@chaos.social/111510381669628525).
* 2023-11-27: (minor)
  * Mention Squoze (thanks to [Job van der
    Zwan](https://fosstodon.org/@vanderZwan@vis.social/111482795620805222)).
  * Reworded the intro so as not to claim "it's quite well known" that the
    maximum virtual address width is typically less than 64 bits. This might
    be interpreted as shaming readers for not being aware of that, which
    wasn't my intent.  Thanks to HN reader jonasmerlin for [pointing this
    out](https://news.ycombinator.com/item?id=38430812).
  * Mention CHERI is the list of "real world examples" which is becoming
    dominated by instances of things somewhat different to what I was
    describing! Thanks to Paul Butcher [for the
    suggestion](https://www.linkedin.com/feed/update/urn:li:activity:7134613236737302528).
  * Link to relevant posts on Mike Ash's blog
    ([suggested](https://lobste.rs/s/5417dx/storing_data_pointers#c_la63sf) by
    Jens Alfke).
  * Link to the various places this article is being discussed.
  * Add link to M68k article
    [suggested](https://fosstodon.org/@christer@mastodon.gamedev.place/111480158347208956)
    by Christer Ericson (with multiple others suggesting something similar -
    thanks!).
* 2023-11-26: (minor)
  * Minor typo fixes and rewordings.
  * Note the Linux kernel repurposing the LSB as a spin lock (thanks to Vegard
    Nossum for the
    [suggestion](https://fosstodon.org/@vegard@mastodon.social/111478755690419785)).
  * Add SIB addressing idea [shared by Per
    Vognsen](https://fosstodon.org/@pervognsen@mastodon.social/111478311705167492).
  * Integrate note
    [suggested](https://fosstodon.org/@wingo@mastodon.social/111478367520587737)
    by Andy Wingo that explicit masking often isn't needed when the least
    significant pointer bits are repurposed.
  * Add a reference to Arm Pointer Authentication (thanks to the
    [suggestion](https://twitter.com/tmikov/status/1728849257439150425) from
    Tzvetan Mikov).

