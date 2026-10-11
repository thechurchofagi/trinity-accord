# Epoch-Bound ADC–DMA Lineage Contract

## 1. Binding

Fix one actual RP2040 token `P`, ADC instance `A`, DMA channel `D`, RAM buffer `B=[b_0,...,b_{N-1}]`, consumer `C`, acquisition epoch `e=[t_0,t_1]`, source schedule `sigma_e`, and declared finite signature `K_view`. These are not inferred from matching numbers.

For the `k`th conversion occurrence `a_{e,k}`, FIFO occurrence `q_{e,k}`, DMA read/write occurrence `d_{e,k}`, memory occurrence `m_{e,k}` and consumer-read occurrence `c_{e,k}`, define:

`EpochRoute_e(k,C) := BIND ∧ START ∧ SOURCE ∧ FIFO ∧ DMA ∧ WINDOW ∧ READ`.

Every conjunct must hold on the same binding.

- `BIND`: the named hardware instances, channel, buffer, consumer, epoch and event grain are fixed.
- `START`: conversions are stopped, completion is awaited, and the ADC FIFO is witnessed empty before the epoch; DMA start and ADC start are ordered.
- `SOURCE`: one fixed ADC channel is used, or a complete round-robin schedule identifies the source channel of every occurrence.
- `FIFO`: each admitted conversion produces its FIFO successor, FIFO order is preserved, and no overflow, underflow or conversion error affects the admitted range.
- `DMA`: the actual enabled channel reads the ADC FIFO register, is paced by `DREQ_ADC`, writes the declared start address with declared transfer size/increment, and completes exactly `N` writes.
- `WINDOW`: the admitted destination region does not wrap or get reused before consumption; all other writers/chain triggers capable of changing it are inventoried and excluded or separately traced.
- `READ`: `C` actually reads the declared slot after its DMA write and before any overwrite/reuse.

`START`, `SOURCE`, `FIFO`, `DMA`, `WINDOW`, and `READ` are occurrence claims. Configuration values and logs are evidence for them, not identical to them.

## 2. Conditional order theorem

**A4U-C2.** Fix `N>0`. If all seven contract clauses hold for epoch `e`, and the FIFO's admitted read semantics are first-in/first-out, then for every `0<=k<N`, the occurrence read by `C` from `b_k` is a directed transductive descendant of `a_{e,k}` (or of the `k`th occurrence in the declared round-robin schedule). The relation is lineage, not numerical identity; byte shifting may change the represented value.

**Proof.** `START` supplies an empty queue at `t_0`. By `SOURCE` and `FIFO`, the admitted enqueue sequence is exactly `q_{e,0},...,q_{e,N-1}` with no loss or alien predecessor. FIFO semantics make the `k`th admitted DMA dequeue consume `q_{e,k}`. `DMA` writes that dequeue to `b_k`; `WINDOW` preserves that occurrence; `READ` makes the consumer read it. Composition of the conversion, FIFO, DMA and read edges yields the stated lineage. This is ordinary finite queue induction, not new mathematics.

## 3. Observational non-identifiability

**A4U-C3.** Buffer values, `TRANS_COUNT=0`, `BUSY=0`, `READY=1` and an empty FIFO *after cleanup* do not identify the epoch of the consumed occurrence.

Witness: let every payload equal `0x555`. A drained start writes `[a_{e,0},a_{e,1}]`. A stale start writes `[s_{e-1},a_{e,0}]`; a later cleanup removes the remaining `a_{e,1}`. Both histories have the same displayed buffer and terminal registers, but only the first delivers `a_{e,1}` to slot 1. Therefore an attested start boundary cannot be replaced by an ex-post empty state.

## 4. Challenge matrix and stop conditions

| Challenge | Failure exposed | Required interpretation |
|---|---|---|
| Pre-start drain/empty witness omitted | stale FIFO shifts the epoch | `START` remains open |
| Round-robin enabled without per-entry provenance | channel fan-in changes source | fixed-channel inference fails |
| Overflow/underflow/error admitted | conversions can be lost or undefined | no total index map |
| Wrong DREQ/source or untraced chain | DMA may read another source | `DMA` remains open |
| Ring wrap or buffer reuse | later conversion can replace `m_{e,k}` | `WINDOW` remains open |
| Another writer shares the RAM region | matching value may have alien origin | writer closure remains open |
| Consumer read not witnessed | RAM arrival is only availability | `READ` remains open |

Stop at `PUBLICLY_SPECIFIED_POSSIBLE_ROUTE / NOT_ACTUALLY_INSTALLED` if any occurrence-level clause lacks same-instance evidence. Do not enter `H_cf`, C1 transport, mineness, conceptual self or report inference.

## 5. Thought-experiment roles

- **Copy/rewiring/memory:** the stale-FIFO twin fixes values and terminal registers while changing epoch lineage; it is the principal counterexample.
- **Abacus/calculator:** the same numeral on a bead, display and paper does not identify the calculation occurrence; an actual read/write history is required.
- **Human-realized agent:** two people can relay identical cards across shifts; without a shift/slot epoch, locally genuine handoffs can be composed across different runs.
- **Ancestor/formation:** a conversion may branch to multiple consumers and multiple ADC channels may merge into one FIFO schedule. Lineage need not be unique or exclusive, and the contract does not count subjects.
