# Attempting, observing, and imagining: the actuality of a process and the actuality of its referent

R179 v0.1, 8 October 2026. Unpublished conceptual analysis with a finite illustrative model. Baseline: R178 and SB20261008 at be720aa4d5aed5978f677d945ea6fecae3765fdf. C1 is assumed, not empirically established here.

## 1. The positive question and the correction

R178 proposes an enacted action-source/consequence relation as a candidate contributor to felt agency. Its next problem is substantive: why should an action attempt differ from observing or imagining the same movement? Merely naming one register SELF, or classifying an output as an action, would put the desired answer into the model.

This round supplies a bounded organizational answer and identifies its remaining explanatory debt. **A represented movement feature can be the same while the actual uses of that representation differ.** A feature can currently contribute to an effector-directed command, an internal rehearsal update, a sensory registration, or several of these together. Thus matching a movement feature does not match its mode-qualified organization. Conversely, a process that imagines a movement can be physically actual even when that movement does not occur. Under C1, the organization of that actual process is the relevant starting point; the nonactuality of its represented event does not remove the representing process.

Neither distinction is claimed as a new philosophical discovery or a proof of a named feeling. The project-level increment is a correction to the intended R178 comparison: specify **agency concerning which activity and at which organizational level**. Deliberately imagining a hand movement may itself be an activity one experiences as doing, without experiencing the hand as actually moving. Therefore the categories 'attempt', 'observation', and 'imagery' cannot be globally exclusive states of the whole person.

## 2. Target and scope before mechanism

Distinguish the following intended descriptive targets: F_try(c,I), the feeling of trying to bring about movement c; F_do(c,I), the feeling of doing/bringing about that movement; F_imagine(c,I), imagining that movement; and F_do(imagining(c),I), feeling oneself actively imagining it. These are descriptions fixing questions, not binary variables computed by our program or an exhaustive taxonomy. A wish to move, a proximal issued command, a successful movement, and a feeling of trying are not synonyms.

For the formal illustration fix P_R, one stipulated finite assembly, over I=[0,2]. It contains a plan-feature register q, a prospective register E, three installed gated routes, a proximal motor port U, an internal scratch register H, a display input D and sensory register S, a downstream plant B, a downstream blocker b, and an imposed-displacement input x. These components and the route settings are in the toy signature K_R. The display input and imposed input are boundary inputs; their prior production is outside I. Register initialization and route settings are fixed before t=1. No human, hidden interpreter, conscious controller, or actual phenomenal bearer is inferred from this roster.

P_H, a future human application, requires a separate actual membership and realization argument. A motor command concerning a body part is not by definition a command concerning the whole bearer. The reference binding from a token c to a body, tool, display, or imagined event must be independently justified. In particular D is a display of a movement feature, not guaranteed veridical afferent feedback from B. This declared separation allows fixed represented features even when the plant is blocked; it must not be silently advertised as matched natural proprioception.

## 3. A finite route construction, not a simulated subject

Let q be either -1 or +1. All destination registers start empty. At t=1, the enabled dispatch route d writes U=q; the enabled rehearsal route r writes H=q; the enabled sensory route s writes S=q from D. Disabled routes leave their destination empty. In every case E=q. At t=2, the plant displacement is q if either (d and not b) or x holds, and zero otherwise. Here x is a specified externally imposed displacement. Cases with both sources are explicitly permitted by the OR mechanism; we infer no exclusive causal author from the output.

Route roles are specified by endpoints and executed effects. U is proximal to the declared plant, H updates only internal scratch state in the restricted base architecture, and S registers a display input. An auditor need not run a perturbation during the actual episode to make these relations part of that episode. Testing an implementation would provide evidence about them; it would not create their actuality. The construction proves model properties by its equations and program execution, not actual human installation.

The three route bits are not experience labels. The full 64-row enumeration is two features times five independent Boolean settings (d,r,s,b,x). All eight route profiles are realizable assignments in this stipulated program; this does not revive the earlier withdrawn claim of eight independent semantic/phenomenal states. Eleven checks verify the equations and counterexamples. The complete results and runnable program are retained.

| Selected episode | Proximal dispatch | Rehearsal | Display registration | Plant displacement | What the episode demonstrates |
|---|---|---|---|---|---|
| Issued and moving | yes | no | yes | yes | One ordinary output route |
| Issued but blocked | yes | no | yes | no | Issued token need not yield movement |
| Scratch only | no | yes | no | no | Actual internal rehearsal without represented displacement |
| Display only | no | no | yes | no | Same movement feature used perceptually |
| Mixed consumers | yes | yes | yes | yes | Simultaneous use defeats a one-hot mode partition |
| Imposed motion | no | no | yes | yes | Movement does not imply the plan-to-port dispatch |

The feature q and prospective E are held fixed in this table. Full register trajectories, route organization, afferent body states, and phenomenology are not held fixed. Consequently this is not another hidden-source matched-downstream lemma. It deliberately changes the organizational use whose relevance R178 left open.

Three local consequences follow. C1: under the stipulated route equations, neither prospective-feature presence nor plant motion is a sufficient classifier of proximal dispatch; the blocked and imposed cases also separate dispatch from motion in both directions. C2: at each fixed q the program admits multiple executed-use profiles including simultaneous dispatch/rehearsal/registration, so no exclusive three-way whole-system classification follows. C3: a nonempty H update can coexist with no corresponding plant displacement. These elementary construction facts are not new general mathematical theorems.

## 4. What this adds to the agency interpretation

Replace a bare feature-level comparison by an indexed relation Psi_A(c,P,I,mu), where c fixes the represented activity and mu records the independently grounded actual source and consumer roles relevant to that activity. This is a proposed refinement, not a new primitive that solves experience by definition. The material question is which actual relations mu should contain for a particular target.

For a restricted overt-action application, current command issuance toward the selected effector is a possible contributor to F_try(c). A successful change in that effector is a further relation; it is not built into the definition of an issued attempt. This allows a principled difference between failed attempted action and merely displaying a movement feature. It also avoids requiring successful control for every self-related experience.

For imagery, the actual rehearsal relation concerns a representation of c. The process doing the rehearsal may itself have an actual task-commitment relation. F_do(imagining(c)) therefore need not equal F_do(c). A single token-level assertion 'there is agency' erases which target is meant. Likewise, a person may actively attend while passively observing another movement. Reference and activity level must be held fixed before comparing feelings.

Under A:C1 and a separately admitted actual instance with a common P/I/K binding, selected grounded source/use relations have corresponding experiential structural relations. The relevant relation is a relation in experience, not an extra owner reading an internal picture. However, calling that transported relation F_try, F_do or F_imagine still requires a substantive interpretation. C1 does not choose these names or make our three route bits universally necessary or sufficient. This preserves R158's relation-not-arbitrary-substructure amendment and R159's internal-reference distinction.

The resulting positive proposal is modest: **the same represented event may be embedded in different actual activities, and self-related experiential contrasts should be sought in those target-relative activities rather than in whether the represented event simply exists.** Intelligence may improve the represented model or the success of dispatch without being identical to either the occurrence of experience or the mode of self-related experience. The present construction does not measure an intelligence scale or settle its causal relation to experience.

## 5. Failures that limit the candidate

First, dispatch does not establish intention or ownership. A externally injected token at a motor port, a reflex, or an automatic learned response may yield the same proximal equation. Additional source/reference organization is needed for any proposed self-related interpretation; no extra organization is required merely to allow basal experience under U1. We explicitly reject 'nonempty motor port iff felt trying'.

Second, the scratch-only restriction is architectural, not the essence of all imagery. Connecting a rehearsal output to a BCI/effector makes rehearsal and outward efficacy coexist. Holding the local scratch feature fixed does not hold the larger causal organization fixed. The base model does not include this added route; it is a scope-changing boundary case, not a row secretly satisfying the original scratch-only assumption.

Third, even within the base architecture a plan can be dispatched and rehearsed simultaneously. Therefore physical route modes form a profile. They are not three exhaustive, exclusive categories of human experience. Nor does removing a route prove absence of its corresponding named feeling in a person. The map must preserve this inferential direction.

Fourth, a matched movement feature q is weaker than matched content in every sense. The purported comparison 'same content but different mode' must say it matches the movement feature, while leaving mode/target relations open. If mode is part of full phenomenal content, declaring full content equality and demanding a content difference would be contradictory. R179 corrects this prospective wording before making a stronger claim.

Fifth, this finite architecture is too coarse to distinguish a voluntary attempt from externally evoked dispatch, or actively imagining from spontaneously arising imagery. That is a real remaining failure, not something to fix by relabeling d as INTENTION. The next positive task is one grounded source/commitment relation with an automatic/reflex countercase, on a fixed activity target and bearer. A new Boolean label or generic control score is insufficient.

## 6. Primary constraints and retrieval limits

Kilteni, Andersson, Houborg and Ehrsson (2018), Nature Communications 9:1617, DOI 10.1038/s41467-018-03989-0, report attenuation of real touch during imagined self-touch and discuss prediction of sensory consequences. The previously retrieved publisher PDF abstract, introduction and initial results constrain an equation of prediction with overt execution. They do not show complete neural equivalence, identical agency, or that all imagery lacks motor output. No new claims about EMG controls are made: a later targeted retrieval failed. PubMed re-access returned 429 and publisher re-access an identity redirect error. Earlier source reading remains limited to the recorded scope.

Desmurget et al. (2009), Science 324:811–813, DOI 10.1126/science.1169896, report stimulation observations in seven awake neurosurgical patients, including reported intention/movement and detected movement dissociations. The full primary article was read from the York-hosted article PDF; supplements and raw data were not inspected. These observations constrain simple output-based interpretations. Reported desire is not automatically attempted action, and no detected target EMG is not proof of no internal motor process.

Karnath, Borchers and Himmelbach (2010), Science 327:1200, DOI 10.1126/science.1183758, question whether stimulation effects uniquely support the activation-based interpretation. Only its PubMed abstract was read. This cautions against deriving a unique neural mechanism from the preceding observations. None of these sources tests C1 or supplies our complete bearer/target admission. The finite construction is our illustration; these papers did not run it.

## 7. The four retained thought-experiment families

Formation/ancestors: vary acquired route/reference organization along an actual developmental or evolutionary story, without treating the first command or self-description as the beginning of experience. Continuity of physical development alone does not establish a particular metric of phenomenal similarity.

Abacus/calculator: fix a numerical output or SELF inscription and vary which physical consumers actually use it. This blocks analyst-imputed mode. An abacus is not declared nonexperiential, and a motor port is not declared conscious agency.

Human-implemented agent: fix the abstract instructions and distinguish the interpreter's own act of imagining/executing from the implemented process and coupled ensemble. F_do(implementation) cannot simply be substituted for F_do(the represented hand movement). Nested actual processes remain allowed.

Copy/reconnection/memory: fix copied scratch content or autobiographical description and reconnect an outgoing route. The larger executed-use profile can change while the copied feature stays fixed. That supports the scope contract, not a proof about numerical personal identity or death fear.

The live/replay family from R178 and this mode comparison form the two focused applications in the proposed paper. The older four families motivate and constrain them; they are not six independent confirmations of the same hypothesis.

## 8. Result, map direction, and next question

We have a concrete positive organizational distinction, three finite-model consequences and explicit failures of its stronger interpretations. We do not have a sufficient account of felt trying or familiar mineness. QC08/09 scoped resolution is retained; QC10, IA-QC11 and the actual application of QC12 remain open. No new canonical theorem or rule is added. Graph objects remain unchanged; this note and the audit supply a scoped interpretation update.

Next question: on one fixed effector-directed episode, can a physically specified task commitment/source relation distinguish attempted movement from automatic or externally imposed command issuance, while predicting a selected contrast with imagined trying? State the difference before looking at reports, and preserve spontaneous imagery and reflex countercases. This stays on the experience–intelligence–self problem rather than expanding certificates.

The author has authorized preparation of a synthesis paper including six thought-experiment families. A separate outline records that authorization and the argument structure. A complete paper, novelty audit, phenomenal bridge, submission or DOI is not claimed here.

## 9. Mandatory overlap correction after the author request

PRIOR_PAPER_OVERLAP_AUDIT.md governs contribution claims. TA25 §§4,6 already state that mistaken attribution is actual organization, and §§2,6 contain the four inherited experiment families. The representing/referent discussion here applies that foundation; it is not a new discovery. The broad dialogue paper outline has been narrowed. The present distinct project application is the mode/target-qualified attempt–observation–imagery comparison and its explicit failed sufficiency shortcuts, with no claim of historical priority or completed phenomenal explanation.
