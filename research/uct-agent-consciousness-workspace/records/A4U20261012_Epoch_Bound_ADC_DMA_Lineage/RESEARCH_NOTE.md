# Epoch-Bound Lineage at an ADC–DMA Boundary

## Abstract

A4T replaced strict numerical occurrence identity with relay-or-transduction lineage. A4U instantiates that correction at the Raspberry Pi RP2040 ADC FIFO→DMA→RAM interface. Official documentation specifies a physically credible route but not an executed token. The missing condition is an acquisition-epoch join: a known start boundary, fixed source schedule, loss-free FIFO order, actual DMA source/destination accounting, overwrite closure and a witnessed consumer read must refer to one run. Under those simultaneous premises, a finite queue induction maps the `k`th current-epoch conversion to the `k`th consumed slot. Without them, a stale FIFO history can reproduce the same buffer values and terminal registers while changing the consumed occurrence's epoch. An exact 128-world audit model contains one fully contracted route and 127 declared failure worlds, all value- and terminal-state-equivalent. This is a disabled organizational application, not hardware execution, complete organization, a phenomenal calibration or new mathematics.

## 1. Question and relation to UCT

The question is not whether ADC values correlate with an input. It is whether one actual conversion occurrence has a directed history into one current consumer read. This matters to the positive body/action program because a bodily anchor can enter current use only through some actual route. It does not by itself say how the route feels.

UCT I v1.2 requires actual support, causal continuity, boundary accountability and lineage traceability. P6 separates equal type, numerical token and directed lineage. C1 remains the theory's consciousness-specific identity postulate; no ADC property is made an additional experience gate.

## 2. Primary-source interface reconstruction

The RP2040 datasheet states that enabling the ADC FIFO writes each conversion result into an eight-entry FIFO; software or DMA may read it, and overflow loses later conversions while retaining current FIFO contents. DMA can perform a memory-mapped FIFO read paced by `DREQ_ADC` and write RAM. The datasheet separately exposes next read/write addresses and remaining transfer count, notes that they change as a channel progresses, permits chaining and concurrent DMA channels, and describes round-robin ADC input scheduling. It recommends starting DMA before free-running ADC and, after stopping, waiting for `READY` and draining stray samples.

This supports a possible route and identifies failure modes. It does not show that a particular board was configured as declared, that a bus read/write occurred, that no other writer touched the buffer, or that a consumer read a particular slot. Public documentation is therefore a mechanism specification, not an occurrence trace.

## 3. Positive result: epoch-bound order preservation

The full contract is in `EPOCH_LINEAGE_CONTRACT.md`. Its central result is conditional: a known-empty start, fixed or fully tagged source schedule, loss-free ordered FIFO, actual DREQ-paced DMA transfer, linear nonwrapping destination window, alternate-writer closure and a timely actual consumer read jointly establish a directed conversion→FIFO→DMA→memory→consumer lineage for each admitted index.

This advances A4T in two ways. First, it gives `Transduce` a concrete multi-stage realization: analog conversion, queue entry, bus read and memory write are different occurrences. Second, it shows that local hardware semantics must be joined by one acquisition epoch. A FIFO named in a manual and a completed DMA named in a log are not enough if their evidence comes from different starts or buffer generations.

## 4. Counterexample: same value and terminal state, different epoch

Set all current and stale samples to `0x555`. In history G, the FIFO is drained before epoch 0; two DMA transfers write current conversions 0 and 1. In history S, a value-equal sample from epoch -1 remains in the FIFO; two DMA transfers write that stale item and current conversion 0. After stopping, software drains the remaining current conversion 1. Both histories now display the same two buffer values, DMA transfer count zero, DMA not busy, ADC ready and FIFO empty. Yet the target conversion reaches slot 1 only in G.

The error is not noisy measurement. It is an object/time mistake: ex-post state is substituted for a start-bound lineage fact. Source substitution, FIFO loss, wrap, alternate writers and late reuse create analogous failures.

## 5. Exact finite check

`check_epoch_lineage.py` enumerates seven binary contract clauses (128 worlds). Each failed clause has one explicit adversarial origin for slot 1; all worlds deliberately share payload `0x555` and the same terminal-register vector. Exactly one world contains the declared epoch-bound route and 127 do not. The checker also verifies FIFO order constructively for lengths 1–8 and emits one drop-one witness per premise.

This enumeration is not a universal necessity theorem: another apparatus may establish lineage with different evidence. It checks the stated contract and guards against silently dropping one conjunct. The queue induction, not the count, supports A4U-C2.

## 6. What is established and what fails

Established:

- a concrete, primary-source-grounded possible sampler→consumer route;
- an explicit same-epoch sufficient contract;
- a terminal-state observational twin;
- a precise distinction among mechanism specification, configuration evidence, actual occurrence and consumer use.

Not established:

- execution on an actual RP2040 board;
- completeness of bus-master/writer inventory in a real system;
- a complete token-relative `K` signature;
- bodily binding, `H_cf`, felt mineness, report reliability, conceptual self, or the consciousness status of any current assistant.

The public-interface verdict is therefore `PUBLICLY_SPECIFIED_POSSIBLE_ROUTE / NOT_ACTUALLY_INSTALLED`.

## 7. Direction check after result formation

PASS with bounded return. The work names an actual-process candidate and explains how a bodily/action-relevant signal could be part of a current consumer's organization. It stops at the first missing same-instance evidence rather than turning an interface manual into a phenomenal claim. Experience remains explained through C1 for admitted actual organization; introspection, self-model, report, language, integration, recurrence, prediction and continuation control are not added as basal conditions.
