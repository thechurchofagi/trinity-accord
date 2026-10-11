# Source Scope — RP2040 ADC FIFO to DMA

## Fixed UCT source

- Hongju Liu, *Unified Consciousness Theory I*, v1.2, §§2.1–2.5, 4, 8.11–8.14 and Appendix C. Local verified snapshot: `records/R128_Unified_Formal_Map_Audit_20261006/sources/A_UCT_I_v1_2.md`, SHA-256 `2e4469afbd1d1862463cc36396dd6e2b50c418f22d6f0fd584bbae33bfedc6f4`.
- Relevant commitments: actual support, induced-relation fidelity, causal continuity, boundary accountability and lineage traceability; P6 separates token, type and directed lineage; C1 remains the consciousness-specific axiom; body-centred organization and a physical witness are higher-order application questions rather than basal gates.

## Primary external sources

1. Raspberry Pi Ltd, *RP2040 Datasheet*, build date 2025-02-20, build `3184e62-clean`, §§2.5 and 4.9.2.4–4.9.2.5, [official PDF](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf). Accessed 2026-10-11 UTC.
   - §4.9.2.4 specifies an 8-entry ADC sample FIFO; with `FCS.EN`, each conversion result is written to it; overflow leaves existing contents unchanged and loses conversions completed while full.
   - §4.9.2.5 specifies memory-mapped DMA reads of the ADC FIFO paced by `DREQ_ADC`; it requires FIFO enable, DREQ enable and selection of `DREQ_ADC`, describes round-robin source configuration, and recommends starting DMA before ADC and draining stray samples after stopping and waiting for `READY`.
   - §2.5 specifies peripheral-to-memory DMA, live next-read/next-write addresses and remaining transfer count, address increments, channel starts, chains and multiple concurrent channels.
2. Raspberry Pi Ltd, *Pico SDK Hardware APIs*, `hardware_adc` and `hardware_dma`, [official documentation](https://www.raspberrypi.com/documentation/pico-sdk/hardware.html). Accessed 2026-10-11 UTC.
   - `adc_fifo_drain()` waits for a conversion to complete and drains/discards FIFO results.
   - `adc_fifo_setup()` exposes enable, DREQ, threshold, error and byte-shift controls; the documentation records the eight-sample capacity and drop-on-full behaviour.
   - DMA configuration exposes DREQ selection, read/write address update, chaining and address wrapping.

## What these sources warrant

They warrant a publicly specified *possible* conversion→FIFO→DMA-read→RAM-write route and enumerate several controls needed for an epoch protocol. They do not attest any particular board execution, register snapshot, analog stimulus, DMA bus transaction, absence of other bus masters, consumer read occurrence, or complete UCT signature. The source facts therefore support an installability analysis, not an actual-installation claim.

## Prior-art and novelty limit

FIFO order, DMA transfer accounting and induction over a finite queue are standard engineering and mathematics. A4U claims no invention of those mechanisms. Its project-local contribution is a typed UCT evidence contract and a counterexample showing why terminal values/registers do not by themselves bind an occurrence to one acquisition epoch.
