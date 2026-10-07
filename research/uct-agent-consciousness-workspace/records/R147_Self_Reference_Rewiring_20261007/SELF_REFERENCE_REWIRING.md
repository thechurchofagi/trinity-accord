# Self-Reference Under Sensor, Action and Memory Exchange

R147 research extension to *Experience, Intelligence, and Self* v0.1. 7 October 2026. Unpublished; not a new paper release.

## 1. The thought experiment and its question

Two identically constructed systems, A and B, each contain a controller, a body with a changing state, sensory connections, action connections, and records describing their histories. Start with ordinary local connections. Consider five distinct operations:

1. Exchange only the external names A and B.
2. Exchange only the sensory connections.
3. Exchange only the action connections.
4. Exchange both sensory and action connections.
5. Exchange or copy the historical records while keeping current connections fixed.

The first operation changes a description if every affected label is transported consistently. The next three change actual relations in the stipulated mechanism. The last changes particular physical memory states and their provenance without automatically changing present sensor/action attachment. We must not call all five operations a transfer of the self.

The question is: what exactly does successful prediction of action consequences identify? Does it identify an internal predictive relation, a controlled body, the process that physically contains the predictor, or an experienced sense of ownership? The experiment matters because these targets normally coincide in familiar cases and can therefore be confused without an explicit logical test.

This is a finite counterexample inquiry, not a proposed human intervention or a new empirical experiment. Its physical and phenomenal interpretations remain conditional. Source basis: A §§2-3, 7, 8.11-8.14; B's port-aware translation distinction; C's fixed-capability and identification results; D §2 and §11; R146's self-model contract.

## 2. Three physically different reference relations

Let controller labels and body labels each range over \(\{1,\ldots,n\}\), with \(n\ge2\). They name two different sorts. Define three bijections from controllers to bodies:

\[
\beta:\text{controller}\to\text{containing assembly's body},\qquad
\sigma:\text{controller}\to\text{sensed body},\qquad
\tau:\text{controller}\to\text{acted-on body}.
\]

The assembly relation \(\beta\) is fixed independently of prediction success. For a physical application, it must be justified by the declared actual assembly's support, physical attachment and continuation; it is not supplied by drawing a box or naming a self. Such an assembly need not be autonomous: A allows boundary-crossing interactions. The theorem below is first a result about a model containing these relations, not a proof that every chosen assembly is an actual bearer.

Each body has a bit \(x_j\). Controller \(i\) receives \(m_i=x_{\sigma(i)}\) and issues a bit command \(u_i\). The body dynamics are

\[
x_j^+=x_j\oplus u_{\tau^{-1}(j)}.
\]

All command vectors \(u\in\{0,1\}^n\) are legal and independently variable; there are no unmodeled couplings or delays. The controller's installed elementary predictor is

\[
\widehat m_i^+=m_i\oplus u_i.
\]

Two predicates answer different questions:

\[
\mathsf{Loop}(i)\iff\sigma(i)=\tau(i),
\]

\[
\mathsf{Own}_{\beta}(i)
\iff\sigma(i)=\tau(i)=\beta(i).
\]

The first says that the controller senses the same body on which its command acts. The second additionally says that this is the body of the independently specified containing assembly. The second is a restricted sensorimotor relation, not a universal definition of selfhood, agency, experience or phenomenological ownership. A person can use a remote tool without the remote object becoming part of that person's constitutive body, while a different justified extended-process comparison may ask another question.

This definition retains the R146 distinction between a target law and its bearer. It does not prohibit partial, erroneous or non-sensorimotor self-models.

## 3. Proposition: loop prediction identifies relative binding

Define the controller permutation

\[
L=\tau^{-1}\circ\sigma.
\]

**Proposition (relative-binding identification and bearer ambiguity).** Under §2's model:

1. The complete sensor-response update is \(m_i^+=m_i\oplus u_{L(i)}\).
2. Controller \(i\)'s installed predictor is correct for every state and every command vector if and only if \(L(i)=i\), equivalently \(\sigma(i)=\tau(i)\).
3. Two connection pairs \((\sigma,\tau)\) and \((\sigma',\tau')\) have the same complete labeled sensor-response law if and only if \(\tau^{-1}\sigma=(\tau')^{-1}\sigma'\). Equivalently, there exists one body permutation \(g\) such that \(\sigma'=g\sigma\) and \(\tau'=g\tau\).
4. Consequently the sensor-response law alone does not identify \(\mathsf{Own}_{\beta}\) when the domain permits joint rewiring of sensors and actuators while \(\beta\) is fixed. It can identify relative loop binding without identifying attachment to the containing assembly.

**Proof.** Substitute \(j=\sigma(i)\) into the body update. This gives clause 1. If \(L(i)=i\), the installed predictor equals that update. If \(L(i)\ne i\), choose a legal vector with \(u_i\ne u_{L(i)}\); the predictor fails, proving clause 2. For clause 3, equal permutations give the same update. If the permutations differ at \(i\), an independently chosen command vector separating those two command coordinates distinguishes the updates at \(i\). For the equivalent form, a common postcomposition cancels in \((g\tau)^{-1}(g\sigma)\). Conversely, equal \(L\) and \(g=\tau'\tau^{-1}\) give \(g\tau=\tau'\) and \(g\sigma=\sigma'\).

For clause 4, take \(\beta=\mathrm{id}\). The ordinary pairing \(\sigma=\tau=\mathrm{id}\) has every \(\mathsf{Own}_{\beta}(i)\) true. Choose a fixed-point-free permutation \(g\), for example a cyclic shift, and set \(\sigma'=\tau'=g\). Every \(\mathsf{Own}_{\beta}(i)\) is now false, but both models have \(L=\mathrm{id}\), identical sensor-response laws and perfect installed predictions. \(\square\)

There are exactly \(n!\) pairs \((\sigma,\tau)\) for each fixed \(L\): choose \(\tau\) arbitrarily and set \(\sigma=\tau L\). This is an elementary permutation calculation, not a new general theorem of system identification. The substantive use is to expose an insufficient proposed definition of functional self: accurate closed-loop prediction does not by itself establish bearer-relative reference.

The indistinguishability statement concerns the specified sensor-response interface. If initial sensor vectors are matched, identical update maps preserve all histories under the same controller policy, including coupled private randomness independent of hidden connection choice. Body-indexed readouts, known spatial attachments, asymmetric bodily signatures, timing differences or changes of initial preparation can provide additional evidence. Those are outside the stipulated interface, not impossible in principle.

## 4. The two-system experiment, fully resolved

Let \(S\) exchange the two bodies and keep \(\beta=\mathrm{id}\).

| Physical operation | \(\sigma\) | \(\tau\) | \(L\) | Prediction from own command | Assembly-relative local loop |
|---|---|---|---|---|---|
| Ordinary connections | id | id | id | Exact for every command | Yes |
| Sensors exchanged | S | id | S | Fails for unequal commands | No |
| Actuators exchanged | id | S | S | Fails for unequal commands | No |
| Both exchanged | S | S | id | Exact for every command | No |

Two further controls are essential.

**Synchronized-action control.** If one tests only \(u_1=u_2\), even the singly exchanged cases predict perfectly. Restricted behavior can conceal a relational mismatch. The general iff in the proposition therefore needs the independent-command premise.

**Renaming control.** Under a simultaneous coordinate rename of controllers by \(h\) and bodies by \(g\), all three maps become \(g\beta h^{-1}\), \(g\sigma h^{-1}\), and \(g\tau h^{-1}\). The truth of both predicates is preserved. In contrast, postcomposing only \(\sigma,\tau\) while holding the actual \(\beta\) relation fixed is physical rewiring in this model. It is not erased by saying that the two bodies merely changed names.

The ordinary and doubly exchanged structures are therefore distinguishable when the \(\beta\) relation is retained in the comparison signature: the structural sentence \(\forall i,\sigma(i)=\beta(i)\) holds in one and fails in the other. This remains so under admissible renaming of both sorts. If this represented relation is actually constitutive of the compared actual tokens, complete organizational equivalence cannot erase the distinction. Only with that additional physical premise does the existing A:C1-OI route give a conditional complete experiential-type distinction. No particular feeling, relocation of experience, or exclusive subject is thereby identified.

## 5. What memory exchange does and does not decide

For a simple extension, attach a record register \(r_i\) to each controller, and let a report channel read a supplied autobiographical string from it. In this extension only, the register has no causal input into \(\sigma,\tau\) or the body-update/predictor equations. Exchanging or copying those records changes the record provenance and possibly the reports but leaves \(L\) and the two attachment predicates unchanged. If the content was initially identical, copying can even leave the immediate report unchanged.

This conditional construction is enough to reject the universal inference that copied autobiography alone determines copied sensorimotor reference or numerical identity. It is not a theory that autobiographical memory never affects self-modeling. In a richer system, memory can guide recalibration, future policy or the interpretation of a sensor. Those extra pathways change the model and must be included.

D's distinction among current process, successor, memory, type and task continuation is retained. Two descendants can inherit the same record without becoming one numerical occurrence. Nor does a matching present report establish the same complete physical organization: provenance may remain physically represented, and the earlier history matters exactly insofar as it belongs to the declared current organization or chosen lineage question. A's no-ghost-history qualification must not be discarded.

## 6. A correction to the research question, not another gate

R146 ended by asking whether self-reference could be grounded without simply stipulating its referent. That is a useful request for physical justification, but an overstrong version would be mistaken: it is not necessary to derive one uniquely privileged, uncentered self from the entire world before studying any local self relation.

An appropriate local question supplies or investigates an actual process token and asks which installed relations concern its own state, constituents or continuation. A model occurrence can belong to more than one justified nested or overlapping process. A target may count as a constituent property relative to one bearer and an external property relative to another. This need not be an inconsistency; the bearer argument must remain explicit. A unique exclusive subject partition is an additional thesis, not a prerequisite for precise analysis.

Within the finite class above, \(\beta\) provides a physically interpretable assembly relation and \(\sigma,\tau\) provide actual routing relations. Their equality can be evaluated without reading the words “I” or “self.” Thus a restricted organizational self-relation can be precise and invariant to names. The proposition also shows exactly why deleting the bearer relation loses relevant information. It does not derive physical tokenhood from an arbitrary model or solve all semantic aboutness.

The remaining task is consequently narrower than finding a metaphysical owner behind the computation: justify the token and the relevant constituent/attachment relations in a declared application, then distinguish actual relational organization, the system's model of it, and any selected phenomenal interpretation. C1 already concerns the actual organization. An inaccurate self-model is itself part of that organization; its represented claim need not become a true claim about the surrounding world.

## 7. Return to the main line and earlier thought experiments

**Experience.** No new prerequisite has been added to experience existence. Under C1/U1, valid actual tokens do not acquire their first experience merely by attaining perfect prediction or local sensorimotor closure. A change of actual complete organization can have the established conditional type interpretation; a coarse performance match cannot establish complete type equality.

**Intelligence.** Predicting the stipulated sensor consequences is one capability coordinate. The ordinary and doubly rewired cases match it while differing in assembly-relative attachment. Other tasks can distinguish them. Neither the accuracy score nor a failure on a restricted task supplies a scalar amount of experience.

**Self.** Actual bearer relation, operational target, internal representation, autobiographical content, and felt ownership remain separate. The thought experiment demonstrates why the definition requires these arguments rather than one circular slogan such as “a self is whatever models itself.”

**All ancestors remain available.** The original experiment still motivates the existential question; proposed self-related organizations themselves have formation histories. In the current example, introducing, strengthening or recalibrating a relation concerns a particular organization and capacity. This must not be promoted to an experience-onset proof. Gradual physical formation alone does not exclude a discontinuous predicate; A's explicit countermodel and separate conditional E1/E3 routes remain.

**Abacus and calculator.** A mechanism that helps solve a task does not thereby have a model of its bearer. A calculator monitoring a battery has a particular target; the same accurate channel monitoring another machine's battery has a different relation. Task success alone does not establish that distinction.

**Human computer.** Participants can have their own local reference relations while the implemented agent models a coordinated computational process. The target of its “I” must be fixed at the intended level. A modeled tool, a participant and the entire coordinated process cannot be exchanged merely because a program variable has the same name. Valid nested processes may coexist.

Thus the thought experiment changes the formal specification and rules out an inadequate inference. It does not serve merely as an illustration after the mathematics is finished.

## 8. Prior art and contribution boundary

Bongard, Zykov and Lipson (2006) already demonstrate machine self-modeling based on actuation-sensation relations and use of the learned model for locomotion. Their physical robot has a grounded experimental configuration. The present counterexample concerns what follows if sensor/action attachment can be jointly reassigned while the evidence interface omits the independent bearer relation; it does not refute their result or claim that robotic self-modeling is new.

Petkova and Ehrsson (2008) manipulate visual perspective and correlated multisensory information to study reported bodily-ownership illusions. This is a relevant empirical antecedent for separating bodily ownership experience from ordinary physical-body attribution. It is not an experiment establishing transfer of numerical identity, and it does not validate the binary rewiring model as a model of human phenomenology.

Perry's indexicality arguments, Metzinger's functional/phenomenal self-model distinctions, A's symmetry analysis and C's fiber criterion remain explicit antecedents from R146. The permutation algebra and nonidentification logic are established tools. The project's increment is a sharp bearer/routing distinction, a complete swap table with controls, and a correction of an unnecessarily absolute formulation of the grounding question.

This is substantive progress in the definitions-first manuscript, not evidence of a historically unprecedented theorem. It strengthens a conceptual/methodological paper. Original-results publication suitability remains unestablished, and no publication or biological experiment is initiated.

### Reading scope and references

- A / UCT I v1.2; B / UCT II v1.1; C / UCT III v1.0; D / TA-TR-2026-24 v1.0: pinned sources in the common map. This round reread A §§8.11-8.14, D §2 and the current map/R146 contract; earlier source audits remain in force.
- Bongard, J., Zykov, V., and Lipson, H. (2006). *Resilient Machines Through Continuous Self-Modeling*. Science 314, 1118-1121. DOI: 10.1126/science.1133687. [Primary four-page article](https://gwern.net/doc/reinforcement-learning/robot/2006-bongard.pdf). Abstract and mechanism discussion inspected; no replication or exhaustive novelty audit.
- Petkova, V. I., and Ehrsson, H. H. (2008). *If I Were You: Perceptual Illusion of Body Swapping*. PLOS ONE 3(12), e3832. [Primary article](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0003832). Abstract, introduction and selected results inspected; no reanalysis of participant data.

General proof review is manual and by the same assistant. The accompanying finite enumeration checks the rewiring formula, identification classes, independent-action control and coordinate invariance; it does not establish actual constitution, semantics or consciousness.
