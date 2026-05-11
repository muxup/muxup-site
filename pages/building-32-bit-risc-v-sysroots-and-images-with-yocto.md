+++
published = 2026-05-11
description = "How to produce 32-bit RISC-V artifacts with Yocto"
+++

# Building 32-bit RISC-V sysroots and images with Yocto

Thanks to the Debian 64-bit RISC-V port it's really easy to build a sysroot
appropriate for cross-compiling Clang/LLVM and its separate [test
suite](https://llvm.org/docs/TestSuiteGuide.html). Either [use my
rootless-deboostrap-wrapper
script](/pages/2024q4/rootless-cross-architecture-debootstrap.md) or the
[command I documented in LLVM's cross-compilation
instructions](https://llvm.org/docs/HowToCrossCompileLLVM.html#setting-up-a-sysroot),
being sure to [see the note on working around a Ninja dependency
issue](https://llvm.org/docs/HowToCrossCompileLLVM.html#working-around-a-ninja-dependency-issue).
For a bootable QEMU image, Debian-based recipes are [similarly
straightforward](/pages/2026q2/bootable-qemu-image-menagerie-with-rootless-debootstrap.md).
But we don't have the luxury of a precompiled distribution for 32-bit RISC-V
and so we'll lean on [Yocto](https://www.yoctoproject.org/) to produce the
needed sysroot by building from source. I cover three cases: 1) building a
sysroot for cross-compiling projects like LLVM, 2) doing the same but in a way
that requires fewer build steps, 3) building an image approximating my
debootstrap image recipes.

In this article I use release 5.3 ('Whinlatter'), which [introduced the
`bitbake-setup` helper
tool](https://docs.yoctoproject.org/dev/migration-guides/release-notes-5.3.html).
For documentation, I found the [Yocto quick build
guide](https://docs.yoctoproject.org/dev/brief-yoctoprojectqs/index.html), and
[bitbake-setup
docs](https://docs.yoctoproject.org/dev/brief-yoctoprojectqs/index.html), and
[image customisation
guide](https://docs.yoctoproject.org/dev-manual/customizing-images.html#customizing-images)
helpful.

I'm not a Yocto developer, so if you reading this and think there are other
approaches to consider or alternative ways of solving the problem that are
better, please do drop me a note!

## Common setup

I'm running on Arch Linux which isn't one of the tested Yocto host
distributions, but seemed to work just fine.

I found I needed to enable the `en_US` locale:
```sh
sudo sed /etc/locale.gen -i -e "s/^\#en_US.UTF-8 UTF-8.*/en_US.UTF-8 UTF-8/"
sudo locale-gen
```

And install the following additional packages:
```sh
sudo pacman -S inetutils chrpath cpio diffstat rpcsvc-proto flex bison zstd
```

Now we will check out bitbake into a work directory and set a directory to be
used to hold downloaded files:

```sh
mkdir yocto-work && cd yocto-work
git clone https://git.openembedded.org/bitbake
./bitbake/bin/bitbake-setup settings set default dl-dir $HOME/.cache/yocto/dl
```

## Producing a sysroot based on core-image-minimal

As is often the case, the workload I'm interested in here is LLVM. If you're
looking to build a sysroot to cross-compile something else, you may need a
slightly different package list.

In this first stanza, we use `bitbake-setup` to initialise our development
environment. Because there isn't a predefined machine target for riscv32 in
`bitbake/default-registry/configurations/poky-whinlatter.conf.json`, we
avoid selecting `machine` and will address it later. Importantly, we set a
`SSTATE_DIR` which will be used for the shared state cache, avoiding
rebuilding packages when not necessary (I'm not totaly sure when this isn't
exposed in `bitbake-setup settings` like `dl-dir` is).

```sh
./bitbake/bin/bitbake-setup init --non-interactive \
  --skip-selection machine \
  ./bitbake/default-registry/configurations/poky-whinlatter.conf.json \
  poky \
  distro/poky

printf 'SSTATE_DIR = "%s"\n' "$HOME/.cache/yocto/sstate" >> bitbake-builds/site.conf
```

With that done, we can source the generated definitions to enter the build
environment (note we're using the default setup directory, you can override it
to something other than `poky-whinlatter` by using `--setup-dir-name`) and
use `enable-fragment` to set the qemuriscv32 machine:

```sh
. bitbake-builds/poky-whinlatter/build/init-build-env
bitbake-config-build enable-fragment machine/qemuriscv32
```

Now configure the build, indicating the additional libraries that need to be
present and run `bitbake` to actually produce it:

```sh
cat >> conf/local.conf <<'EOF'
IMAGE_INSTALL:append = " \
  glibc-dev \
  libgcc \
  libgcc-dev \
  libatomic \
  libatomic-dev \
  libstdc++ \
  libstdc++-dev \
"
EOF

bitbake core-image-minimal
```

This results in 4482 build tasks and takes quite some time to complete if you
haven't run it before (i.e. aren't hitting in the sstate cache). The next
section of this article explores how to produce the needed output while
building much less, but let's finish the job and extract a rootfs from what
was built. I would like to now [follow advice in the
documentation](https://docs.yoctoproject.org/sdk-manual/appendix-obtain.html#extracting-the-root-filesystem)
and do `runqemu-extract-sdk
tmp/deploy/images/qemuriscv32/core-image-minimal-qemuriscv32.rootfs.tar.zst
~/rv32sysroot`, except that fails because the `runqemu-extract-sdk` script
doesn't recognise .tar.zst (I've [submitted a
patch](https://lists.openembedded.org/g/openembedded-core/message/229316)). So
instead we manually extract the .tar from the .tar.zst and then run the
runqemu-extract-sdk script:

```
zstd -d -k -f tmp/deploy/images/qemuriscv32/core-image-minimal-qemuriscv32.rootfs.tar.zst
runqemu-extract-sdk tmp/deploy/images/qemuriscv32/core-image-minimal-qemuriscv32.rootfs.tar ~/rv32sysroot
```

At this point, you have a sysroot that's _almost_ directly usable for
cross-compiling Clang/LLVM (with `--target=riscv32-poky-linux`) but there are
three finalisation steps we will perform:

* Add an additional symlink to the tree so that upstream Clang's search
  procedure for the GCC install finds the correct directory. The combination
  of
  [these](https://git.openembedded.org/openembedded-core/tree/meta/recipes-devtools/clang/clang/0010-clang-Define-releative-gcc-installation-dir.patch?h=whinlatter)
  [two](https://git.openembedded.org/openembedded-core/tree/meta/recipes-devtools/clang/clang/0018-llvm-clang-Insert-anchor-for-adding-OE-distro-vendor.patch?h=whinlatter)
  downstream patches which Yocto applies to its own Clang builds would make
  this unnecessary. I'm not sure if upstreaming has ever been pursued.
* Convert all absolute symlinks to relative ones. Yocto provides a Python
  script for this, which is in our `$PATH` after sourcing
  `build/init-build-env`.
* (Optional) Apply workaround [for a ninja
  issue](https://llvm.org/docs/HowToCrossCompileLLVM.html#working-around-a-ninja-dependency-issue)
  that would otherwise mean incremental builds don't work.

```sh
mkdir -p "$HOME/rv32sysroot/usr/lib/gcc" && ln -s ../riscv32-poky-linux "$HOME/rv32sysroot/usr/lib/gcc/riscv32-poky-linux"
sysroot-relativelinks.py $HOME/rv32sysroot
ln -s usr/include $HOME/rv32sysroot/include
```

## Producing a sysroot with fewer build steps

The `core-image-minimal` recipe above is straightforward, but does a lot more
work than strictly necessary. We can reduce this by instead adding a
dependency-only recipe that explicitly lists the needed build-time
dependencies and contains logic to produce the sysroot.

First, create a layer:

```sh
. bitbake-builds/poky-whinlatter/build/init-build-env
bitbake-layers create-layer --add-layer ../layers/meta-rv32-llvm-sysroot
```

Then add the recipe:

```sh
recipe_dir="../layers/meta-rv32-llvm-sysroot/recipes-devtools/rv32-llvm-deps-sysroot"
mkdir -p "$recipe_dir"

cat > "$recipe_dir/rv32-llvm-deps-sysroot.bb" <<'EOF'
SUMMARY = "Dependency-only recipe to export an RV32 sysroot"
LICENSE = "MIT-0"

INHIBIT_DEFAULT_DEPS = "1"
EXCLUDE_FROM_WORLD = "1"
PACKAGE_ARCH = "${MACHINE_ARCH}"

DEPENDS = "virtual/libc libgcc virtual/${MLPREFIX}compilerlibs zlib"

inherit deploy nopackages

do_configure[noexec] = "1"
do_compile[noexec] = "1"
do_install[noexec] = "1"
do_populate_sysroot[noexec] = "1"

do_deploy() {
  export_dir="${DEPLOYDIR}/${PN}-${MACHINE}"
  rm -rf "$export_dir"
  mkdir -p "$export_dir"
  cp -a "${RECIPE_SYSROOT}/." "$export_dir/"

  sysroot-relativelinks.py "$export_dir"

  mkdir -p "$export_dir/usr/lib/gcc"
  ln -s ../riscv32-poky-linux "$export_dir/usr/lib/gcc/riscv32-poky-linux"
  ln -s usr/include "$export_dir/include"
}
addtask deploy after do_prepare_recipe_sysroot before do_build
EOF
```

The `do_deploy` function implements the sysroot preparation logic that largely
mirrors the previous section. Otherwise, `DEPENDS` specifies the needed
dependencies (of these, `virtual/${MLPREFIX}compilerlibs` is a bit magic -
this resolves to the compiler runtime provider which pulls in things like
`libstdc++`).

Build the sysroot with:

```sh
bitbake rv32-llvm-deps-sysroot
```

This performs ~850 build tasks and will produce the sysroot at
`tmp/deploy/images/qemuriscv32/rv32-llvm-deps-sysroot-qemuriscv32/`.

The sysroot is slightly larger than the one in the section above because it
contains large unstripped static archives like `usr/lib/libstdc++.a`.

## Producing a featureful image bootable in QEMU

Watch this space!
