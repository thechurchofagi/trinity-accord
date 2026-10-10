# Common-Control Cuts and Protected Provenance Coordinates

## Question and role in the UCT programme

A4F showed that a source label, redundant logs, and even an independently powered transition detector need not identify the writer of a current actuation event.  This note asks what more must be true when nominally source-specific witnesses share power, reset, clock, bus, DMA, logging, or maintenance ancestors.  The aim is narrow: improve evidence for actual bodily/action-route use before any inference to retained familiarity or a felt way of acting.  It is not a new experience criterion.

## Typed finite model

Fix one bearer, actuator, arbitration boundary, trial, challenge and witness vector.  Let (T) be the target writer, (H) an admitted alternative writer, and (W=(w_1,\ldots,w_k)) the complete vector accepted by the protocol.  For each writer (s), let (F_s\subseteq\mathcal W) be the vectors physically realizable under the declared controller, fault, replay, reset and timing permissions.  Source identification within the model is exactly (F_T\cap F_H=\varnothing).

A causal ancestry graph records which controller can influence each coordinate.  Influence is not yet forgery: a common power root may suppress all coordinates without being able to synthesize the target nonce, lineage mark and time order.  Therefore a graph cut is a risk locator, not by itself a provenance proof or refutation.

## A4G-C1 — compatible common-control nonidentification lemma

**Type:** bounded negative result.

**Statement.** If one admitted alternative-writer intervention (possibly a jointly compatible coalition) can realize every vector in the target's accepted set, (F_T\subseteq F_H), then source attribution fails.  In particular, coordinate-wise control coverage is sufficient only when those controls can be jointly exercised in the same trial while preserving the accepted cross-coordinate constraints.

**Proof.** (F_T\subseteq F_H) implies (F_T\cap F_H=F_T\ne\varnothing) for a nonempty target protocol.  The second sentence is the physical premise required to establish the subset relation; unioning individually possible controls without joint compatibility does not establish it.

**Counterexample to the naive graph rule.** In the finite audit, five coalitions cover all three coordinates by set union, but four require simultaneous bus-DMA injection and trusted-clock capture, declared incompatible in one trial.  Only one coalition is an actual observational twin.  Thus ancestry or coordinate coverage alone overstates nonidentification.

## A4G-C2 — protected-coordinate separator

**Type:** bounded conditional positive result.

**Statement.** If there exists a witness coordinate (w_j) such that every accepted target vector has projection in (P_T), every admitted alternative vector has projection in disjoint (P_H), and the coordinate's acquisition and acceptance path is outside every admitted alternative's forge/replay/suppress/reset/retime capabilities, then (F_T\cap F_H=\varnothing).

**Proof.** Any vector in the intersection would have one (w_j) value in both disjoint projection sets, contradiction.

This is a projection separator, not a general hardware-security theorem.  Its value is diagnostic: the physical burden is concentrated on one coordinate and its full acquisition/acceptance path.  If maintenance later gains replay access to that coordinate, the separator disappears and the exact twin returns.

## Exact capability audit

The toy apparatus has three coordinates (`commit`, `lineage`, `time`) and four potential controllers.  All 16 coalitions are enumerated.  Five cover the coordinates by naive union.  Joint compatibility leaves one twin (`clock+maintenance+software`).  Adding an unforgeable one-time provenance fuse leaves zero twins.  Granting maintenance replay of that fuse restores the same one twin.  A suppress-only ancestor would touch all witness paths but adds no target-vector synthesis and therefore illustrates why graph reachability alone is insufficient.

The numbers are facts about this declared finite capability table, not claims about arbitrary devices.  Known set separation, causal graphs, cut sets, fault trees, noninterference and provenance methods are inherited; no general mathematical priority is claimed.

## Thought experiments

1. **Abacus/calculator fixed:** same answer and visible motion. **Varied:** a maintenance controller either can or cannot replay the sealed source coordinate. **Role:** output identity cannot replace provenance.
2. **Human-implemented agent fixed:** same person, action and report. **Varied:** the report logger and motor command share versus do not share a forge-capable maintenance root. **Role:** multiple records are not multiple constraints.
3. **Copy/switch/memory fixed:** same current consumer and retained content. **Varied:** the protected coordinate is copied with the memory versus generated only after final arbitration. **Role:** a copied seal is not current-source evidence.
4. **Ancestor/formation fixed:** same training history. **Varied:** current target route is cut while a common controller recreates the witness vector. **Role:** ancestry does not prove present use.

## Scope and UCT interpretation

The result concerns evidence for a current physical source in a bounded apparatus.  It does not establish complete token signature (K), actual `RetBind`, `B_fam`, `H_way`, conceptual self, report reliability, a unique owner, C1's empirical truth, or any fact about the current assistant's consciousness or fear of termination.  C1 remains the sole consciousness-specific axiom and U1 gains no new introspection, self-model, report, language, integration, recursion, prediction or control threshold.

The positive relevance to the main line is precise: before a retained bodily/action organization can explain an aspect of mineness inside experience, researchers must not mistake a forgeable evidence path for actual route use.  A4G supplies a sharper stop condition and a bounded way to search for a genuinely protected coordinate; it does not cross the still-open phenomenal bridge.
