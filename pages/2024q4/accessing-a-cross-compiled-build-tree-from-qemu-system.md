+++
published = 2024-10-15
description = "A quick benchmark of several approaches for accessing a large build tree"
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

# Accessing a cross-compiled build tree from qemu-system

I'm cross-compiling a large codebase (LLVM and sub-projects such as Clang) and
want to access the full tree - the source and the build artifacts from under
qemu. This post documents the results of my experiments in various ways to do
this. Note that I'm explicitly choosing to run timings using something that
approximates the work I want to do rather than any microbenchmark targeting
just file access time.

Requirements:
* The whole source tree and the build directories are accessible from the
  qemu-system VM.
* Writes must be possible, but don't need to be reflected in the original
  directory (so importantly, although files are written as part of the test
  being run, I don't need to get them back out of the virtual machine).

## Results

The test simply involves taking a cross-compiled LLVM tree (with RISC-V as the
only enabled target) and running the equivalent of `ninja check-llvm` on it
after exposing / transferring it to the VM using the listed method. Results in
chart form for overall time taken in the "empty cache" case:

<table class="chart">
  <tr>
    <th>9pfs</th><td><div class="chart-bar" style="width: 94%;">13m05s&nbsp;</div></td>
  </tr>
  <tr>
    <th>virtiofsd</th><td><div class="chart-bar" style="width: 100%;">13m56s&nbsp;</div></td>
  </tr>
  <tr>
    <th>squashfs</th><td><div class="chart-bar" style="width: 83%;">11m33s&nbsp;</div></td>
  </tr>
  <tr>
    <th>ext4</th><td><div class="chart-bar" style="width: 84%;">11m42s&nbsp;</div></td>
  </tr>
</table>

* 9pfs: 13m05s with empty cache, 12m45s with warm cache
* virtiofsd: 13m56s with empty cache, 13m49s with warm cache
* squashfs: 11m33s (~17s image build, 11m16s check-llvm) with empty cache,
  11m16s (~3s image build, 11m13s check-llvm) with warm cache
* new ext4 filesystem: 11m42s, (~38s image build, 11m4s check-llvm) with empty
  cache, 11m34s (~30s image build, 11m4s check-llvm) with warm cache.

By way of comparison, it takes ~10m40s to naively transfer the data by piping
it over ssh (tarring on one end, untarring on the other).

For this use case, building and mounting a filesystem seems the most
compelling option with the ext4 being overall simplest (no need to use
overlayfs) assuming you have an e2fsprogs new enough to support tar input to
`mkfs.ext4`. I'm not sure why I'm not seeing the purported performance
improvements when using virtiofsd.

## Notes on test setup

* The effects of caching are accounted for by taking measurements in two
  scenarios below. Although neither is a precise match for the situation in a
  typical build system, it at least gives some insight into the impact of the
  page cache in a controlled manner.
  * "Empty cache". Caches are dropped (`sync && echo 3 | sudo tee /proc/sys/vm/drop_caches`)
    before building the filesystem (if necessary) and launching QEMU.
  * "Warm cache". Caches are dropped as above but immediately after that (i.e.
    before building any needed filesystem) we load all files that will
    be accessed so they will be cached. For simplicity, just do this by doing
    using a variant of the `tar` command described below.
* Running on AMD Ryzen 9 7950X3D with 128GiB RAM.
* QEMU 9.1.0, running qemu-system-riscv64, with 32 virtual cores matching the
  number 16 cores / 32 hyper-threads in the host.
* LLVM HEAD as of 2024-10-13 (48deb3568eb2452ff).
* Release+Asserts build of LLVM with all non-experimental targets enabled.
  Built in a two-stage cross targeting rv64gc_zba_zbb_zbs.
* Running riscv64 Debian unstable within QEMU.
* Results gathered via `time ../bin/llvm-lit -sv .` running from 
  `test/` within the build directory, and combining this with the timing for
  whatever command(s) are needed to transfer and extract the source+build
  tree.
* Only the time taken to build the filesystem (if relevant) and to run the
  tests is measured. There may be very minor difference in the time taken to
  mount the different filesystems, but we assume this is too small to be worth
  measuring.
* If I were to rerun this, I would invoke `lit` with `--order=lexical` to
  ensure runtimes aren't affected by the order of tests (e.g. long-running
  tests being scheduled last).
* Total size of the files being exposed is ~8GiB or so.
* Although not strictly necessary, I've tried to map to the uid:gid pair used
  in the guest where possible.

## Details: 9pfs (QEMU -virtfs)

* Add `-virtfs
  local,path=$HOME/llvm-project/,mount_tag=llvm,security_model=none,id=llvm`
  to the QEMU command line.
* Within the guest `sudo mount -t 9p -o trans=virtio,version=9p2000.L,msize=512000 llvm /mnt`.
  I haven't swept different parameters for
  [msize](https://wiki.qemu.org/Documentation/9psetup#Performance_Considerations_(msize))
  and mount reports 512000 is the maximum for the virtio transport.
* Sadly 9pfs doesn't support [ID-mapped
  mounts](https://lpc.events/event/11/contributions/1086/attachments/926/1826/christian_brauner_idmapped_mounts.pdf)
  at the moment, which would allow us to easily remap the uid and gid used
  within the file tree on the host to one of an arbitrary user account in the
  guest without `chown`ing everything (which would also require
  `security_model=mapped-xattr` or `security_model=mapped-file` to be passed
  to qemu. In the future you should be able to do `sudo mount --bind
  --map-users 1000:1001:1 --map-groups 984:1001:1 /mnt mapped`
* We now need to set up an overlayfs that we can freely write to.
  * `mkdir -p upper work llvm-project`
  * `sudo mount -t overlay overlay -o lowerdir=/mnt,upperdir=$HOME/upper,workdir=$HOME/work $HOME/llvm-project`
* You could create a user account with appropriate uid/gid to match those in
  the exposed directory, but for simplicity I've just run the tests as root
  within the VM.

## Details: virtiofsd

* Installed the virtiofsd package on Arch Linux (version 1.11.1). Refer to the
  [documentation](https://gitlab.com/virtio-fs/virtiofsd#examples) for
  examples of how to run.
* Run `/usr/lib/virtiofsd --socket-path=/tmp/vhostqemu --shared-dir=$HOME/llvm-project --cache=always`
* Add the following commands to your qemu launch command (where the memory size
  parameter to `-object` seems to need to match the `-m` argument you used):
```sh
  -chardev socket,id=char0,path=/tmp/vhostqemu \
  -device vhost-user-fs-pci,queue-size=1024,chardev=char0,tag=llvm \
  -object memory-backend-memfd,id=mem,size=64G,share=on -numa node,memdev=mem
```
* `sudo mount -t virtiofs llvm /mnt`
* Unfortunately id-mapped mounts also aren't quite supported for virtiofs at
  the time of writing.  The changes were recently merged into the upstream
  kernel and a merge request to virtiofsd [is
  pending](https://gitlab.com/virtio-fs/virtiofsd/-/merge_requests/245).
* `mkdir -p upper work llvm-project`
* `sudo mount -t overlay overlay -o lowerdir=/mnt,upperdir=$HOME/upper,workdir=$HOME/work $HOME/llvm-project`
* As with the 9p tests, just ran the tests using sudo.

## Details: squashfs

* I couldn't get a regex that squashfs would accept to exclude all build/*
  directories except build/stage2cross, so use `find` to generate the
  individual directory exclusions.
* As you can see in the commandline below, I disabled compression altogether.
* `mksquashfs ~/llvm-project llvm-project.squashfs -no-compression -force-uid 1001 -force-gid 1001 -e \
  .git $(find $HOME/llvm-project/build -maxdepth 1 -mindepth 1 -type d -not -name 'stage2cross' -printf '-e build/%P ')`
* Add this to the qemu command line: `-drive
  file=$HOME/llvm-project.squashfs,if=none,id=llvm,format=raw -device
  virtio-net-device,netdev=net`
* `sudo mount -t squashfs /dev/vdb /mnt`
* Use the same instructions for setting up overlayfs as for 9pfs above.
  There's no need to run the tests using sudo as we've set the appropriate
  uid.

## Details: new ext4 filesystem

* Make use of the `-d` parameter of `mkfs.ext4` which allows you to create a
  filesystem, using the given directory or tarball to initialise it. As
  `mkfs.ext4` lacks features for filtering the input or forcing the uid/gid of
  files, we rely on tarball input (only just added in e2fsprogs 1.47.1).
* Create a filesystem image that's big enough with `fallocate -l 15GiB
  llvm-project.img`
* Execute:
```sh
tar --create \
  --file=- \
  --owner=1001 \
  --group=1001 \
  --exclude=.git \
  $(find $HOME/llvm-project/build -maxdepth 1 -mindepth 1 -type d -not -name 'stage2cross' -printf '--exclude=build/%P ') \
  -C $HOME/llvm-project . \
  | mkfs.ext4 -d - llvm-project.img
```
* Attach the drive by adding this to the qemu command line `-device
  virtio-blk-device,drive=hdb -drive
  file=$HOME/llvm-project.img,format=raw,if=none,id=hdb`
* Mount in qemu with `sudo mount -t ext4 /dev/vdb $HOME/llvm-project`

## Details: tar piped over ssh

* Essentially, use the tar command above and pipe it to tar running under
  qemu-system over ssh to extract it to root filesystem (XFS in my VM setup).
* This could be optimised. e.g. by selecting a less expensive ssh encryption
  algorithm (or just `netcat`), a better networking backend to QEMU, and so
  on. But the intent is to show the cost of the naive "obvious" solution.
* Execute:
```sh
tar --create \
  --file=- \
  --owner=1001 \
  --group=1001 \
  --exclude=.git \
  $(find $HOME/llvm-project/build -maxdepth 1 -mindepth 1 -type d -not -name 'stage2cross' -printf '--exclude=build/%P ') \
  -C $HOME/llvm-project . \
  | ssh -p10222 asb@localhost "mkdir -p llvm-project && tar xf - -C \
  llvm-project"
```
