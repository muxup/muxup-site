+++
published = 2023-03-03
description = "An attempt to enumerate all the RISC-V silicon available to buy today"
+++
# Commercially available RISC-V silicon

The RISC-V instruction set architecture has seen huge excitement and growth in
recent years ([10B cores estimated to have shipped as of Dec
2022](https://venturebeat.com/ai/how-risc-v-has-become-a-viable-third-processor-architecture-calista-redmond/))
and I've been keeping very busy with RISC-V related work [at
Igalia](https://www.igalia.com/contact/). I thought it would be fun to look
beyond the cores I've been working with and to enumerate the SoCs that are
available for direct purchase or in development boards that feature RISC-V
cores programmable by the end user. I'm certain to be missing some
SoCs or have some mistakes or missing information - any corrections very
gratefully received at asb@muxup.com or
[@asbradbury](https://twitter.com/asbradbury). I'm focusing almost
exclusively on the RISC-V aspects of each SoC - i.e. don't expect a detailed
listing of other on-chip peripherals or accelerators.

## A few thoughts
* It was absolutely astonishing how difficult it was to get basic information
  about the RISC-V specification implemented by many of these SoCs. In a
  number of cases, just a description of a "RV32 core at xxMHz" with further
  detective work being needed to find any information at all about even the
  standard instruction set extensions supported.
* The way I've focused on the details of individual cores does a bit of a
  disservice to those SoCs with compute clusters or interesting cache
  hierarchies. If I were to do this again (or if I revisit this in the
  future), I'd look to rectify that. There a whole bunch of other
  micro-architectural details it would be interesting to detail too.
  * I've picked up CoreMark numbers where available, but of course that's a
    very limited metric to compare cores. It's also not always clear which
    compiler was used, which extensions were targeted and so on. Plus when the
    figure is taken from an IP core product page, the numbers may refer to a
    newer version of the IP. Where there are multiple numbers floating about
    I've listed them all.
* There's a lot of chips here - but although I've likely missed some, not so
  many that it's impossible to enumerate. RISC-V is growing rapidly, so
  perhaps this will change in the next year or two.
* A large proportion of the SoC designs listed are based on proprietary core
  designs (with one of the most notable exceptions being those based on the
  Apache-licensed T-Head IP). As a long-term proponent of open source silicon
  I'd hope to see this change over time. Once a company has moved from a
  proprietary ISA to an open standard (RISC-V), there's a much easier
  transition path to switch from a proprietary IP core to one that's open
  source.


## 64-bit Linux-capable application processors

* [StarFive
  JH7110](https://doc-en.rvspace.org/JH7110/TRM/JH7110_DS/highlighted_features.html)
  * **Core design**:
    * 4 x RV64GC_Zba_Zbb [SiFive U74](https://www.sifive.com/cores/u74)
      application cores, 1 x RV64IMAC SiFive S7
      ([this?](https://www.sifive.com/cores/s76)) monitor core, and 1 x
      RV32IMFC [SiFive E24](https://www.sifive.com/cores/e24)
      ([ref](https://doc-en.rvspace.org/JH7110/PDF/JH7110_Datasheet.pdf),
      [ref](https://lore.kernel.org/lkml/dda144a8397a175f3ce092485f08896c9a66d232.camel@icenowy.me/)).
    * The U74 is a dual-issue in-order pipeline with 8 stages.
  * **Key stats**:
    * 1.5 GHz, fabbed on TSMC 28nm
      ([ref](https://riscv.or.jp/wp-content/uploads/day3_StarFive_risc-v_tokyo_day2022Autumn.pdf)).
    * StarFive
      [report](https://riscv.or.jp/wp-content/uploads/day3_StarFive_risc-v_tokyo_day2022Autumn.pdf)
      a CoreMark/MHz of 5.09.
  * **Development board**:
    * Available in the [VisionFive
      2](https://www.kickstarter.com/projects/starfive/visionfive-2)
      and [Pine64 Star64](https://wiki.pine64.org/wiki/STAR64) development
      boards.
* [T-Head C910 ICE](https://github.com/T-head-Semi/riscv-aosp)
  * **Core design**:
    * 2 x RV64GC [T-Head C910](https://www.t-head.cn/product/c910) application
      cores and an additional T-Head C910 RV64GCV core (i.e., with the vector
      extension).
    * The C910 is a 3-issue out-of-order pipeline with 12 stages.
  * **Key stats**:
    * 1.2 GHz, fabbed on a 28nm process
      ([ref](https://github.com/T-head-Semi/riscv-aosp)).
  * **Development board**:
    * Available in the
      [RVB-ICE](https://www.aliexpress.com/item/1005003395978459.html).
* [Allwinner D1-H](https://d1.docs.aw-ol.com/en/)
  ([datasheet](https://github.com/DongshanPI/Awesome_RISCV-AllwinnerD1/blob/master/Tina-SDK/Hardware%E7%A1%AC%E4%BB%B6%E7%B1%BB%E6%96%87%E6%A1%A3/%E8%8A%AF%E7%89%87%E6%89%8B%E5%86%8C/D1-H_Datasheet_V1.0.pdf),
  [user
  manual](https://github.com/DongshanPI/Awesome_RISCV-AllwinnerD1/blob/master/Tina-SDK/Hardware%E7%A1%AC%E4%BB%B6%E7%B1%BB%E6%96%87%E6%A1%A3/%E8%8A%AF%E7%89%87%E6%89%8B%E5%86%8C/D1-H_User%20Manual_V1.0.pdf))
  * **Core design**:
    * 1 x RV64GC [T-Head C906](https://www.t-head.cn/product/c906?lang=en)
      application core. Additionally supports the unratified, v0.7.1 RISC-V
      vector specification
      ([ref](https://old.reddit.com/r/RISCV/comments/v1dvww/allwinner_d1_extensions/ialzm2q/)).
    * Single-issue in-order pipeline with 5 stages.
    * Verilog for the core is [on
      GitHub](https://github.com/T-head-Semi/openc906) under the Apache
      License (see [discussion](https://news.ycombinator.com/item?id=30691980)
      on what is included).
    * At least early versions of the chip [incorrectly trapped on
      `fence.tso`](https://bugs.llvm.org/show_bug.cgi?id=50746). It's unclear if
      this has been fixed in later revisions.
  * **Key stats**:
    * 1GHz, taped out on a 22nm process node.
    * [Reportedly](https://linuxgizmos.com/99-sbc-runs-linux-on-risc-v-based-allwinner-d1/) 3.8 CoreMark/MHz.
  * **Development board**:
    * Available in a number of development boards (e.g.  [Allwinner
      Nezha](https://d1.docs.aw-ol.com/en/d1_dev/), [SiPeed Lichee
      RV](https://wiki.sipeed.com/hardware/en/lichee/RV/RV.html), and
      [more](https://linux-sunxi.org/Category:D1_Boards)).
* [StarFive JH7100](https://starfivetech.com/uploads/JH7100%20Datasheet.pdf)
  * **Core design**:
    * 2 x RV64GC [SiFive U74](https://www.sifive.com/cores/u74) application
      cores and 1 x RV32IMAFC [SiFive E24](https://www.sifive.com/cores/e24).
    * The U74 is a dual-issue in-order pipeline with 8 stages. 
  * **Key stats**:
    * 1.2GHz (as listed on [StarFive's
    page](https://www.starfivetech.com/en/site/soc) but articles about the V1
    board claimed 1.5GHz), presumably fabbed on TSMC 28nm (the [JH7110
    is](https://riscv.or.jp/wp-content/uploads/day3_StarFive_risc-v_tokyo_day2022Autumn.pdf)).
    * The current U74 product page claims 5.75 CoreMark/MHz ([previous
      reports](https://linuxgizmos.com/hifive-unmatched-sbc-showcases-new-fu740-risc-v-soc/)
      suggested 4.9 CoreMark/MHz).
  * **Development board**:
    * Available on the [VisionFive V1 development
      board](https://www.cnx-software.com/2021/11/27/visionfive-v1-risc-v-linux-sbc-resurrects-beaglev-single-board-computer/).
* [Kendryte K210](https://www.canaan.io/product/kendryteai)
  ([datasheet](https://cdn.hackaday.io/files/1654127076987008/kendryte_datasheet_20181011163248_en.pdf))
  * **Core design**:
    * 2 x RV64GC application cores
      ([reportedly](https://lore.kernel.org/all/48e10b3d-12f3-a65c-8017-99c780c63040@gmail.com/)
      implementations of the open-source
      [Rocket](https://github.com/chipsalliance/rocket-chip) core design).
    * If it's correct the K210 uses Rocket, it's a single-issue in-order
      pipeline with 5 stages.
    * Has a non-standard (older version of the privileged spec?) MMU
      ([ref](https://github.com/riscv-software-src/opensbi/pull/206#issuecomment-821726609),
      so the [nommu Linux
      port](https://lore.kernel.org/all/20200212103432.660256-5-damien.lemoal@wdc.com/t/)
      is typically used.
  * **Key stats**:
    * 400MHz, fabbed on TSMC 28nm.
  * **Development board**:
    * Available in [development boards from
      SiPeed](https://wiki.sipeed.com/hardware/maixface/en/core_modules/k210_core_modules.html).
* [MicroChip PolarFire SoC
  MPFSxxxT](https://www.microchip.com/en-us/products/fpgas-and-plds/system-on-chip-fpgas/polarfire-soc-fpgas)
  * **Core design**:
    * 4 x RV64GC [SiFive U54](https://www.sifive.com/cores/u54) application
      cores, 1 x RV64IMAC SiFive E51 (now renamed to
      [S51](https://www.sifive.com/cores/s51)) monitor core.
    * The U54 is a single-issue, in-order pipeline with 5 stages.
  * **Key stats**:
    * 667 MHz ([ref](https://www.microsemi.com/document-portal/doc_download/1244584-polarfire-soc-product-overview)),
    fabbed on a 28nm node
    ([ref](https://riscv.org/wp-content/uploads/2019/04/RISC-V-Linux-Foundation.pdf)).
    * Microchip report 3.125 CoreMark/MHz.
  * **Development board**:
    * Available in the
      ['Icicle'](https://www.microsemi.com/existing-parts/parts/152514)
    development board.
* [SiFive
  FU740](https://sifive.cdn.prismic.io/sifive/1a82e600-1f93-4f41-b2d8-86ed8b16acba_fu740-c000-manual-v1p6.pdf)
  * **Core design**:
    * 4 x RV64GC [SFive U74](https://www.sifive.com/cores/u74) application
    cores, 1 x RV64IMAC SiFive S71 monitor core.
    * It's hard to find details for the S71 core, the FU740 manual refers to
      it as an S7 while the HiFive Unmatched refers to it as the S71 - but
      neither have a page on SiFive's site (there is an
      [S76](https://www.sifive.com/cores/s76) though).
    * The U74 is a dual-issue in-order pipeline with 8 stages.
  * **Key stats**:
    * 1.2 GHz, fabbed on TSMC 28nm ([ref](https://www.theregister.com/2020/10/29/sifive_riscv_pc/)).
    * The current U74 product page claims 5.75 CoreMark/MHz ([previous
      reports](https://linuxgizmos.com/hifive-unmatched-sbc-showcases-new-fu740-risc-v-soc/)
      suggested 4.9 CoreMark/MHz).
  * **Development board**:
    * Was available on the now-discontinued [HiFive Unmatched development
      board](https://www.sifive.com/boards/hifive-unmatched).
* [SiFive FU540](https://static.dev.sifive.com/FU540-C000-v1.0.pdf)
  * **Core design**:
    * 4 x RV64GC [SiFive U54](https://www.sifive.com/cores/u54) application
      cores, 1 x RV64IMAC SiFive E51 (now renamed to
      [S51](https://www.sifive.com/cores/s51)) monitor core.
    * The U54 is a single-issue, in-order pipeline with 5 stages.
  * **Key stats**:
    * 1.5GHz, fabbed on TSMC 28nm
    ([ref](https://riscv.org/wp-content/uploads/2018/05/14.15-14.30-RISC-V-Barcelona-workshop.pdf)).
    * The current U54 product page claims 3.16 CoreMark/MHz but it was [2.75
      in 2017](https://twitter.com/wikichip/status/917585069509959680).
  * **Development board**:
    * Was available on the now-discontinued [HiFive Unleashed development
      board](https://www.sifive.com/boards/hifive-unleashed).
* [Bouffalo Lab
  BL808](https://github.com/bouffalolab/bl_docs/blob/main/BL808_DS/en/BL808_DS_1.2_en.pdf)
  * **Core design**:
    * 1 x RV64IMAFCV [T-Head C906](https://www.t-head.cn/product/c906?lang=en)
      application core, 1 x RV32IMAFCP [T-Head
      E907](https://www.t-head.cn/product/e907?lang=en), 1 x RV32E?? [T-Head
      E902](https://www.t-head.cn/product/e902?lang=en)
      ([ref](https://wiki.pine64.org/wiki/Ox64)).
    * See notes elsewhere for more info on these T-Head core designs.
  * **Key stats**:
    * The C906 runs at 480 MHz, the E907 at 320 MHz and the E902 at 150 MHz.
  * **Development board**:
    * Available in the [Ox64](https://wiki.pine64.org/wiki/Ox64) from Pine64.
* [Renesas
  RZ/Five](https://www.renesas.com/in/en/products/microcontrollers-microprocessors/rz-mpus/rzfive-general-purpose-microprocessors-risc-v-cpu-core-andes-ax45mp-single-10-ghz-2ch-gigabit-ethernet)
  * **Core design**:
    * 1 x RV64GC [Andes
      AX45MP](http://www.andestech.com/en/products-solutions/andescore-processors/riscv-ax45mp/)
      application core with additional Andes extensions (draft of the 'P'
      packed SIMD spec, Andes 'V5' extensions).
    * Dual issue, in-order pipeline with 8 stages.
  * **Key stats**:
    * 1.0 GHz, 5.63 CoreMark/MHz
      ([ref](http://www.andestech.com/en/products-solutions/andescore-processors/riscv-ax45mp/)).
  * **Development board**:
    * [Evaluation
      kit](https://www.renesas.com/us/en/products/microcontrollers-microprocessors/rz-mpus/rzfive-evaluation-board-kit-rzfive-evaluation-board-kit)
      available.
* [Kendryte K510](https://www.canaan.io/product/kendryte-k510)
  * **Core design**:
    * 2 x RV64GC application cores and 1 x RV64GC core with DSP extensions.
    [Apparently](https://www.robertlipe.com/elusive-k510-specs-start-to-show-developer-board-now-available/)
    based on the [AndeStar
    V5](http://www.andestech.com/en/products-solutions/andestar-architecture/)
    but I can't find the original source for this.
  * **Key stats**:
    * 800 MHz.
  * **Development board**:
    * [K510
      CRB-KIT](https://www.canaan.io/product/kendryte-k510-crb-kit-developer-kit)
      developer kit is available.
* (Upcoming) [Intel-SiFive Horse Creek SoC](https://www.sifive.com/boards/hifive-pro-p550)
  * **Core design**:
    * 4 x RV64GBC SiFive P550 application cores (docs not yet available, but
      [an overview is
      here](https://www.cnx-software.com/2021/06/23/sifive-performance-p550-fastest-64-bit-risc-v-processor/)).
    * 13 stage, 3 issue, out-of-order pipeline.
    * As the bit manipulation extension was split into a range of
      sub-extensions it's unclear exactly which of the 'B' family extensions
      will be supported.
  * **Key stats**:
    * 2.2 GHz, fabbed on Intel's '4' process node
      ([ref](https://fuse.wikichip.org/news/7277/intel-sifive-demo-high-performance-risc-v-horse-creek-dev-platform-on-intel-4-process/)).
  * **Development board**:
    * Will be available in the [HiFive Pro P550 development
      board](https://www.sifive.com/boards/hifive-pro-p550).
* (Upcoming) T-Head TH1520
  ([announcement](https://riscv.org/blog/2022/10/deepcomputing-and-xcalibyte-announce-the-roma-laptop-will-be-powered-by-th1520-the-first-soc-from-wujian-600s-platform-by-alibaba-t-head-xcalibyte/))
  * **Core design**:
    * 4 x RV64GC [T-Head C910](https://www.t-head.cn/product/c910) application
      cores, 1 x RV64GC [T-Head
      C906](https://www.t-head.cn/product/c906?lang=en), 1 x RV32IMC [T-Head
      E902](https://www.t-head.cn/product/e902).
    * The C910 is a 3-issue out-of-order pipeline with 12 stages, the C906 is
      single-issue in-order with 5 stages, and the E902 is single-issue in-order
      with 2 stages.
    * Verilog for the cores is up on GitHub under the Apache license:
      [C910](https://github.com/T-head-Semi/openc910),
      [C906](https://github.com/T-head-Semi/openc906),
      [E902](https://github.com/T-head-Semi/opene902).
      See [discussion](https://news.ycombinator.com/item?id=30691980)
      on what is included).
  * **Key stats**:
    * 2.4 GHz, fabbed on a 12nm process
      ([ref](https://sipeed.com/licheepi4a/)).
  * **Development board**:
    * Will be available on the [SiPeed Lichee Pi
      4A](https://sipeed.com/licheepi4a/).

## Embedded / specialised SoCs (mostly 32-bit)

* [SiFive
  FE310](https://static.dev.sifive.com/SiFive-E310-G000-manual-v1.0.1.pdf)
  * **Core design**:
    * 1 x RV32IMAC [SiFive E31](https://www.sifive.com/cores/e31) core.
    * Single-issue, in-order pipeline with 5-6 stages ('variable pipeline').
  * **Key stats**:
    * 320 MHz
      ([ref](https://sifive.cdn.prismic.io/sifive/4999db8a-432f-45e4-bab2-57007eed0a43_fe310-g002-datasheet-v1p2.pdf)),
      fabbed on TSMC 180nm
      ([ref](https://static.dev.sifive.com/SiFive-E310-G000-manual-v1.0.1.pdf)),
    * 2.73 CoreMark/MHz [in the FE310-G002
      datasheet](https://sifive.cdn.prismic.io/sifive/4999db8a-432f-45e4-bab2-57007eed0a43_fe310-g002-datasheet-v1p2.pdf),
      3.17 CoreMark/MHz on the [E31 product
      page](https://www.sifive.com/cores/e31).
  * **Development board**:
    * Available in development boards such as the [HiFive 1 Rev
      B](https://www.sifive.com/boards/hifive1-rev-b).
* [GigaDevice GD32VF103
  series](https://www.gigadevice.com/products/microcontrollers/gd32/risc-v/mainstream-line/gd32vf103-series/)
  * **Core design**:
    * 1 x RV32IMAC Nuclei [Bumblebee
      N200](https://github.com/nucleisys/Bumblebee_Core_Doc) ("jointly
      developed by Nuclei System Technology and Andes Technology.")
    * No support for PMP (Physical Memory Protection), includes the 'ECLIC'
      interrupt controller derived from the CLIC design.
    * Single-issue, in-order pipeline with 2 stages.
  * **Key stats**:
    * 108 MHz. 360 CoreMark
      ([ref](https://www.eenewseurope.com/en/open-source-risc-v-mcu-with-bumblebee-core/)),
      implying 3.33 CoreMark/MHz.
  * **Development board**:
    * Available in development boards such as the [Sipeed Longan
      Nano](https://www.seeedstudio.com/Sipeed-Longan-Nano-V1-1-p-5118.html).
* [GreenWaves GAP8](https://greenwaves-technologies.com/gap8_mcu_ai/)
  * **Core design**:
    * Fabric Controller (FC) core and compute cluster of 8 cores based on
      [PULP](https://pulp-platform.org/). Implements RV32IMC with alongside
      [additional custom
      extensions](https://greenwaves-technologies.com/manuals/BUILD/HOME/html/index.html).
  * **Key stats**:
    * 175 MHz Fabric Controller, 250 MHz cluster. Fabbed on TSMC's 55nm
      process ([ref](https://en.wikichip.org/wiki/greenwaves/gap8)).
    * 22.65 GOPS at 4.24mW/GOP
      ([ref](https://greenwaves-technologies.com/low-power-processor/)).
    * Shipped 150,000 units, composed of roughly 80% open source and 20%
      proprietary IP
      ([ref](https://www.eetimes.eu/greenwaves-channels-funding-into-new-risc-v-processors/)).
  * **Development board**:
    * Available in the
      [GAPuino](https://greenwaves-technologies.com/product/gapuino/).
* [GreenWaves GAP9](https://greenwaves-technologies.com/gap9_processor/)
    * **Core design**:
      * Fabric Controller (FC) and compute cluster of 9 cores. Extends the
        RV32IMC (plus extensions) GAP8 core design with additional custom
        extensions
        ([ref](https://riscv.org/wp-content/uploads/2019/12/12.10-17.10a-The-Next-Generation-of-GAP8-An-IoT-Application-Processor-for-Inference-at-the-Very-Edge.pdf)).
    * **Key stats**:
      * 400 MHz Fabric Controller and computer cluster. Fabbed on Global
        Foundries 22nm FDX process
        ([ref](https://greenwaves-technologies.com/gap9_iot_application_processor/)).
      * 150.8 GOPS at 0.33mW/GOP
        ([ref](https://greenwaves-technologies.com/low-power-processor/)).
    * **Development board**:
      * GAP9 evaluation kit listed on [Greenwaves
        store](https://greenwaves-technologies.com/store/) but you must email
        to receive access to order it.
* [Renesas
  RH850/U2B](https://www.renesas.com/eu/en/products/microcontrollers-microprocessors/rh850-automotive-mcus/rh850u2b-zonedomain-and-vehicle-motion-microcontroller)
  * **Core design**:
    * Features an [NSITEXE
      DR1000C](https://www.nsitexe.com/en/ip-solutions/data-flow-processor/DR1000C/)
      RISC-V parallel coprocessor, comprised of RV32I scalar processor units,
      a control core unit, and a vector processing unit based on the RISC-V
      vector extension.
  * **Key stats**:
    * 400 MHz. Fabbed on a 28nm process.
  * **Development board**:
    * None I can find.
* [Renesas
  R9A02G020](https://www.renesas.com/eu/en/products/microcontrollers-microprocessors/risc-v/r9a02g020-assp-easy-mcu-motor-control-based-risc-v)
  * **Core design**:
    * 1 x RV32IMC [AndesCore
      N22](http://www.andestech.com/en/products-solutions/andescore-processors/riscv-n22/)
      (additionally supporting the Andes 'Performance' and 'CoDense'
      instruction set extensions).
    * Single-issue in-order with a 2-stage pipeline.
  * **Key stats**:
    * 32 MHz.
  * **Development board**:
    * The
      [R9A02G020-EVK](https://www.renesas.com/eu/en/products/microcontrollers-microprocessors/risc-v/r9a02g020-evk-r9a02g020-assp-easy-motor-control-kit)
      motor control kit is available.
* [Analog Devices
  MAX78000](https://www.analog.com/en/products/max78000.html#product-overview)
  * **Core design**:
    * Features an RV32 RISC-V coprocessor of unknown (to me!) design and
      unknown ISA naming string.
  * **Key stats**:
    * 60 MHz (for the RISC-V co-processor), fabbed on a TSMC 40nm process
      ([ref](https://forums.tinyml.org/t/two-tinyml-talks-on-october-27-2020-by-kristopher-ardis-and-robert-muchsel-from-maxim-integrated-and-manuele-rusci-from-greenwaves-technologies/385)).
  * **Development board**:
    * [MAX78000EVKIT](https://www.analog.com/en/design-center/evaluation-hardware-and-software/evaluation-boards-kits/max78000evkit.html)
      and
      [MAX78000FTHR](https://www.analog.com/en/design-center/evaluation-hardware-and-software/evaluation-boards-kits/max78000fthr.html).
* [Espressif ESP32-C3](https://www.espressif.com/en/products/socs/esp32-c3) / ESP8685
  * **Core design**:
    * 1 x RV32IMC core of unknown design, single issue in-order 4-stage
      pipeline
      ([ref](https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf)).
  * **Key stats**:
    * 160 MHz, fabbed on a TSMC 40nm process
      ([ref](https://www.espressif.com.cn/sites/default/files/ESP32-C3%20%26%20ESP32-S3%20BQB%20Certification_0.pdf)).
    * 2.55 CoreMark/MHz.
  * **Development board**:
    * Available in a number of formats including the
      [ESP32-C3-DevKitM-1](https://www.mouser.co.uk/ProductDetail/Espressif-Systems/ESP32-C3-DevKitM-1?qs=pUKx8fyJudB1sOWbbEnGFw%3D%3D)
      and the [M5Stack M5Stamp
      C3](https://www.mouser.co.uk/new/m5stack/m5stack-m5stamp-c3-set/).
* [Espressif ESP32-C2](https://www.espressif.com/en/products/socs/esp32-c2) / ESP8684
  * **Core design**:
    * 1 x RV32IMC core of unknown design, single issue in-order 4-stage
      pipeline
      ([ref](https://www.espressif.com/sites/default/files/documentation/esp8684_datasheet_en.pdf)).
  * **Key stats**:
    * 160 MHz, fabbed on a TSMC 40nm process.
    * 2.55 CoreMark/MHz.
    * Die photo available [in this article](https://blog.espressif.com/esp32-c2-and-why-it-matter-s-bcf4d7d0b2c6).
  * **Development board**:
    * Available in the
      [ESP8684-DevKitM-1-H4](https://eu.mouser.com/ProductDetail/Espressif-Systems/ESP8684-DevKitM-1-H4?qs=tlsG%2FOw5FFjDvS55rvTa7Q%3D%3D).
* [Espressif ESP32-C6](https://www.espressif.com/en/products/socs/esp32-c6)
  * **Core design**:
    * 1 x RV32IMAC core of unknown design (four stage pipeline) and 1 x RV32IMAC
      core of unknown design (two stage pipeline) for low power operation ([ref](https://www.espressif.com/sites/default/files/documentation/esp32-c6_datasheet_en.pdf)).
  * **Key stats**:
    * 160 MHz high performance (HP) core with 2.76 CoreMark/MHz, 20 MHz low power (LP) core.
  * **Development board**:
    * Available in the
      [ESP32-C6-DevKitC-1-N8](https://www.mouser.co.uk/ProductDetail/Espressif-Systems/ESP32-C6-DevKitC-1-N8?qs=8Wlm6%252BaMh8TjnOR8RwmaBw%3D%3D).
* [HiSilicon
  Hi3861](https://www.hisilicon.com/en/products/smart-iot/ShortRangeWirelessIOT/Hi3861V100)
  * **Core design**:
    * 1 x RV32IM core of unknown design, supporting additional non-standard
      compressed instruction set extensions
      ([ref](https://github.com/koendv/hi3861_notes)).
  * **Key stats**:
    * 160 MHz.
  * **Development board**:
    * A low-cost board [is
      available](https://www.aliexpress.com/item/1005003342192909.html)
      advertising support for Harmony OS.
* [Bouffalo Lab BL602/BL604](https://en.bouffalolab.com/product/?type=detail&id=1)
  * **Core design**:
    * 1 x RV32IMAFC [SiFive E24](https://www.sifive.com/cores/e24) core
      ([ref](https://maero.dk/bl602-firmware-image-format/)).
    * 3-stage pipeline.
  * **Key stats**:
    * 192 MHz, 3.1 CoreMark/MHz
      ([ref](http://download.bl602.fun/BL602_%E5%AE%98%E6%96%B9%E8%8A%AF%E7%89%87%E8%B5%84%E6%96%99.pdf)).
  * **Development board**:
    * Available in the very low cost
      [Pinecone](https://pine64.com/product/pinecone-bl602-evaluation-board/)
      evaluation board.
  * **Other**:
    * The [BL702](https://en.bouffalolab.com/product/?type=detail&id=4)
      appears to have the same core, so I haven't listed it separately.
* [Bluetrum AB5301A](http://www.bluetrum.com/product/ab5301a.html)
  * **Core design**:
    * 1 x RV32 core of uknown design and unknown ISA naming string ([CNX
      Software tried and failed to get
      clarification](https://www.cnx-software.com/2021/03/09/bluetrum-ab32vg1-board-features-ab5301a-bluetooth-risc-v-mcu-runs-rt-thread-rtos/).
  * **Key stats**:
    * 125 MHz.
  * **Development board**:
    * Available in the
      [AB32VG1](https://www.aliexpress.com/item/1005002953148585.html)
      development board.
* [WCH CH583](http://www.wch-ic.com/products/CH583.html)/CH582/CH581
  * **Core design**:
    * 1 x RV32IMAC [Qingke V4a](http://www.wch-ic.com/downloads/file/367.html)
      core, which also supports a "hardware prologue/epilogue" extension.
    * Single issue in-order pipeline with 2 stages.
  * **Key stats**:
    * 20MHz.
  * **Development board**:
    * An evaluation board [is
      available](https://www.aliexpress.com/i/1005003926698348.html).
* [WCH CH32V307](http://www.wch-ic.com/products/CH32V307.html)
  * **Core design**:
    * 1 x RV32IMAFC [Qingke
      V4f](http://www.wch-ic.com/downloads/file/367.html) core.
  * **Key stats**:
    * 144 MHz.
  * **Development board**:
    * An evaluation board [is
      available](https://www.aliexpress.com/item/1005004511264952.html).
* [WCH CH32V003](http://www.wch-ic.com/products/CH32V003.html)
  * **Core design**:
    * 1 x RV32EC [Qinkge V2A](http://www.wch-ic.com/downloads/file/369.html)
      with custom instruction set extensions ('XW' for sign-extended byte and
      half word operations).
  * **Key stats**:
    * 48 MHz.
    * Notably announced as [costing less than 10
      cents](https://twitter.com/patrick_riscv/status/1580384430996484101).
  * **Development board**:
    * Various boards
      [available](https://www.aliexpress.com/item/1005004988121617.html).
* [PicoCom PC802](https://picocom.com/products/socs/pc802/)
  * **Core design**:
    * Two clusters of 16 RV32IMAC [Andes
      N25F](http://www.andestech.com/en/products-solutions/andescore-processors/riscv-n25f/)
      cores
      ([ref](https://www.electronicsweekly.com/news/business/picocom-adopts-andes-risc-v-cores-o-ran-soc-2020-08/)).
    * Single issue, in order pipeline with 5 stages.
    * Also see the [2021 RISC-V summit
      talk](https://www.youtube.com/watch?v=EmG0fWFwIqI) for more insight on
      the architecture.
  * **Key stats**:
    * Fabbed on TSMC 12nm process
      ([ref](https://www.eenewseurope.com/en/picocom-tapes-out-multicore-risc-v-openran-chip-for-oranic-board/)).
  * **Development board**:
    * Several boards [are available](https://picocom.com/products/boards/).

## Bonus: Other SoCs that don't match the above criteria or where there's insufficient info

* The [Espressif ESP32-P4](https://www.espressif.com/en/news/ESP32-P4) was
  announced, featuring a dual-core 400MHz RISC-V CPU with "an AI instructions
  extension". I look forward to incorporating it into the list above when more
  information is available.
* I won't try to enumerate every use of RISC-V in chips that aren't
  programmable by end users or where development boards aren't available, but
  it's worth noting the [use of RISC-V Google's Titan
  M2](https://www.androidauthority.com/titan-m2-google-3261547/)
* In January 2022 Intel Mobileye
  [announced](https://www.anandtech.com/show/17165/mobileye-announces-eyeq-ultra-l4-auto-soc)
  the EyeQ Ultra featuring 12 RISC-V cores (of unknown design), but there
  hasn't been any news since.

## Article changelog
* 2023-03-04: (minor)
  * Further Espressif information and new ESP32-C2 entry
    [contributed](https://github.com/muxup/muxup-site/pull/1) by Ivan
    Grokhotkov.
  * Clarified cores in the JH7110 and JH7100 (thanks to Conor Dooley for the
    tip).
  * Added T-Head C910-ICE (thanks to a tip via email).
* 2023-03-03: (minor)
  * Added note about CoreMark scores.
  * Added the Renesas R9A02G020 (thanks to Giancarlo Parodi for the tip!).
  * Various typo fixes.
  * Add link to PicoCom RISC-V Summit talk and clarify the ISA extensions
    supported by the PC802 Andes N25F clusters.
