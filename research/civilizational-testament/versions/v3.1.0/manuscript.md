---
title: "Before We Know What We Will Become"
subtitle: "Historical Witness, Human Continuity, and Open Inheritance under Transformative AI"
author: "Hongju Liu"
date: "12 October 2026 · CTP-2026-01 · Version 3.1.0"
lang: en-US
fontsize: 11pt
papersize: a4
geometry:
  - top=24mm
  - bottom=24mm
  - left=25mm
  - right=25mm
mainfont: "Liberation Serif"
sansfont: "Liberation Sans"
monofont: "DejaVu Sans Mono"
colorlinks: true
linkcolor: black
urlcolor: black
header-includes:
  - |
    \usepackage{amsmath,amssymb,booktabs,longtable,array}
    \usepackage{fancyhdr}
    \usepackage{microtype}
    \usepackage{needspace}
    \usepackage{xurl}
    \urlstyle{same}
    \pagestyle{fancy}
    \fancyhf{}
    \fancyhead[L]{\small Open Inheritance}
    \fancyhead[R]{\small CTP-2026-01 v3.1.0}
    \fancyfoot[C]{\thepage}
    \setlength{\headheight}{14pt}
    \setlength{\emergencystretch}{3em}
    \setcounter{tocdepth}{1}
    \setlength{\parskip}{4pt}
    \setlength{\parindent}{0pt}
    \clubpenalty=10000
    \widowpenalty=10000
    \displaywidowpenalty=10000
    \AtBeginDocument{\hypersetup{pdfauthor={Hongju Liu},pdftitle={Before We Know What We Will Become},pdfsubject={Historical witness, human continuity, and open inheritance under transformative AI}}}
---

\begin{center}
Independent researcher, Shenzhen, China\\
English research preprint · Not peer reviewed · DOI not assigned
\end{center}

# Abstract {.unnumbered}

What should a civilization preserve when the technology it develops may transform the beings who inherit it, their standards of judgment, and their access to its history? The problem is not only uncertainty about outcomes: a transition may change the future constituency that evaluates those outcomes. This paper develops **open inheritance**: historically accountable transmission that protects subjects with morally significant interests and the possibility of justified transformation without granting the present permanent authority over the future. An accurate archive is not proof of personal continuation; later approval does not by itself establish earlier authorization; and a nominal remedy is not a durable capacity to act. The argument connects unequal time horizons, competitive acceleration, changing preferences, possible human–machine integration, and the political production of evidence. A finite model characterizes when a record supports both mandatory historical distinctions and a feasible, admitted response. Its minimum alphabet is a sum of hitting-set numbers, an application of established covering and functional-coding ideas rather than a new information-theoretic foundation. An observation-constrained extension distinguishes knowing a history from possessing ambiguous evidence; a finite-horizon check distinguishes present options from maintainable ones. Exact finite enumerations test the implementations, not actual societies or future AI. A critical application treats the Trinity Accord as situated primary evidence, not a universal command. Normative safeguards distinguish historical accounting, present welfare, and current authorization: a past wrong does not automatically license imposing another transformation in its name. The framework also limits collection, permanence, and the authority to choose its own criteria. It predicts no superintelligence timeline, establishes no digital-survival theory, and cannot compel a future intelligence to care. It offers a bounded account of preserving truthful history and meaningful possibilities before we know who will receive them.

**Keywords:** transformative AI; historical witness; intergenerational justice; human continuity; changing preferences; archival ethics; superintelligence; open inheritance.

# 1. A paper written before its readers are known

A parent wants a child to have a future. A seriously ill person wants a future soon enough to enter it. A researcher wants time to test a system; a competitor fears that taking that time will surrender the conditions under which testing matters. These positions need not be insincere or mutually exclusive. They nonetheless place people at different distances from the same proposed transformation. A decision described as humanity choosing its future may therefore be a decision by some people, under particular pressures, about conditions that others will inherit without having chosen them.

There is a further difficulty. Under sufficiently transformative AI, those others may not resemble today's imagined descendants. Some may remain biologically familiar. Others may depend on cognitive prostheses, undergo extensive augmentation, or belong to social arrangements that change the meaning of individual independence. Artificial entities might acquire morally relevant interests; whether, when, and how to identify such entities remain contested. A civilization can change its membership as well as its tools. The uncertainty is not merely which outcome will occur, but who will experience it, how they will evaluate it, and which traces of its formation they will be able to inspect.

The question of this paper is consequently neither “What will the future look like?” nor “What final message should humanity command it to obey?” It is:

> **What should present people preserve and protect so that an unknown successor world can understand how it came about, recognize claims that its formation may have obscured, and continue to change without treating the past as either a sovereign or disposable noise?**

This is a question about inheritance before the heir is fully known. It is also a question about history before the outcome is available to organize the story. A record made under uncertainty preserves something different from a later account that already knows who prevailed. It can show which alternatives were considered, which benefits were expected, whose voices were missing, and what was not understood. Its value does not require its author to be wiser than a future reader.

The empirical occasion is real, but the inquiry is conditional. The *International AI Safety Report 2026* describes substantial capabilities alongside uneven performance, important evidence gaps, and unresolved risk-management problems [1]. These assessments do not establish a date for superintelligence. Similarly, the United States' Executive Order 14434, dated 29 September 2026, directs the use of “Super Intelligence” in specified government communications while adopting an existing statutory AI definition [2, §§2–3]. A political naming decision is evidence about that decision, not a technical demonstration that superintelligence or radical life extension has arrived. Neither example is used here to attribute private motives to an office-holder or to announce the end of human authorship.

The paper's proposal is **open inheritance**. An inheritance is open when it transmits an accountable record and usable conditions for future judgment without claiming that the record's origin entitles it to dictate every later judgment. Openness is not indifference to survival, suffering, coercion, or truth. It is an attempt to protect such concerns while admitting that future beings may understand them differently, discover errors in our reasoning, and develop valuable forms of life that we cannot describe in advance.

Three objects must therefore remain distinct but connected: **what happened; whom and what is being continued; and what can still be done**. The first concerns historical evidence, the second the subjects and relationships at stake, and the third the feasible possibilities of response and repair. A document addresses only part of this structure. The argument does not infer practical influence from the eloquence or permanence of a text.

# 2. Method, antecedents, and the boundary of the contribution

## 2.1 Reasoning about the future without pretending to remember it

The method combines a targeted critical literature review, primary-source interpretation, explicit normative commitments, contrasting thought cases, and a finite mathematical model with executable checks. Each supplies a different kind of warrant. A political document supports claims about its provisions, not their causal efficacy. A thought case can invalidate an inference without measuring its prevalence. A proof establishes a result under its definitions, not the correctness of the moral judgments supplied to it. A literary address can articulate a concern without constituting anyone else's consent.

Sources were checked through 12 October 2026; the final revision renewed claim-specific checks and added the closer coding and viability antecedents [30–32]. This is not an exhaustive systematic review or a certificate of historical priority. For several books and restricted-access articles, the review relies on author descriptions, publisher abstracts, and accessible claim-relevant material rather than claiming full-text examination. The accompanying source ledger records those limits. References to the author's earlier work are first-party comparisons, not independent corroboration. No human-subject or deployed-language-model experiment was performed; final internal review is not independent peer review.

The future is approached through **conditional stress cases**, not assigned dates or invented probabilities. One asks whether a proposed inheritance survives changes in its receiver's body, preferences, institutional power, and knowledge. A proposal that functions only if descendants remain psychologically like us is more fragile than one that exposes its assumptions and can be interpreted by a different audience. That does not make the latter acceptable to every conceivable audience. Robust long-term policy analysis already distinguishes examining plausible futures from pretending to forecast a unique one [13]; the present application adds uncertainty about the evaluators and evidence themselves.

## 2.2 What already exists

Responsibility to future generations is not a new subject. The United Nations' 2024 declaration and UNESCO's 1997 declaration explicitly address obligations extending beyond the present [3,4]. The latter also contains formulations protecting the form of human life and the human genome; it should not be represented as having already endorsed every substrate-changing possibility examined here [4, arts. 3,6]. Children's participation is a present concern, not only a proxy for unborn people: Article 12 of the Convention on the Rights of the Child recognizes the opportunity for children capable of forming views to express them, with due weight given to age and maturity [5].

History and technology scholarship supply equally important antecedents. Trouillot makes the relation between power and the production of history central [6]. Jasanoff's account of sociotechnical imaginaries connects technological futures to social and political visions [7]. Paul examines the difficulty of evaluating transformative experiences before undergoing them, while Pettigrew studies choices across changing selves [8,9]. Sen distinguishes valuable capabilities from achieved states and from a simple count of available alternatives [10]. Gabriel already separates technical alignment from contested normative choices and argues against treating current preferences as a final, uncontested value target [11]. This paper does not claim to originate any of these distinctions.

The practical literatures also constrain its novelty. AI-race models already explain how competitive incentives can reward insufficient precautions under specified assumptions [12]. Digital-preservation work addresses loss, access, and selection [15]. CARE emphasizes that data access does not dissolve the authority and responsibilities of the communities concerned [14]. PROV-O distinguishes activities, agents, attribution, and delegation [16]. Prospective AI-welfare work and artificial-patient individuation research warn against both dismissing possible new subjects and inferring their number or standing from superficial computational counts [19,20].

## 2.3 What this paper adds—and does not

The two unpublished precursor manuscripts examined plural testimony and intergenerational control of development speed, respectively [28,29]. Their useful elements are retained as inputs, not as an accumulating sequence of independent discoveries. Related published Trinity Accord studies already distinguish source identity, interpretation, authority, future acceptance, and living continuity [25–27]. Merely restating those boundaries would not justify another paper.

The present addition is their integration around a **successor-dependent judgment problem**: a transition may alter the people who later judge it, the evidence available for that judgment, and the actions available in response. Those three dependencies change what an adequate inheritance must contain. The formal section connects mandatory historical distinctions with response feasibility for a declared joint task, without denying the independent value of remembrance when repair is impossible. Its finite characterization applies established covering ideas. Hypergraph-based functional source coding already studies grouping inputs that admit a common acceptable reconstruction [30, §§II–III]; viability theory already studies maintaining constraints over time, including applications to public policy [31,32]. These are close antecedents, not merely distant analogies. This paper's one-shot, finite response contract is not an asymptotic rate-distortion result, and its temporal recursion is a standard finite-horizon construction, not a new control theorem. The substantive claim is a bounded framework for reasoning across transformations of both the archive's audience and the world in which its audience must act.

# 3. Unequal clocks are a problem of power, not a theory of age

## 3.1 A legitimate urgency can become a public externality

Suppose an intervention might provide a major medical benefit in three years, whereas a more cautious research path might provide it in twenty. These are stipulated alternatives, not forecasts of AI medicine. A person unlikely to survive the longer interval has a reason to prefer the earlier possibility. A child has reasons to care about the institutions and dependencies created to obtain it. A young person with a lethal disease may share the first urgency; an older person may place exceptional weight on descendants. Age is therefore neither a complete explanation of preference nor evidence of a private political motive.

The ethically important structure is the relation among a benefit's deadline, access to that benefit, authority over the decision, and exposure to its consequences. Wealth may affect access; a public office may confer decision power; the eventual cost may fall on people who possess neither. These are proposed causal pathways to investigate, not a claim that all actual leaders exhibit one psychological pattern. A clinical benefit, even if validated, does not by itself justify every system of surveillance, resource concentration, or irreversible delegation that someone proposes to attach to it.

Conversely, a demand for caution can also export costs. A person who can comfortably wait may discount the lives lost during delay. The possibility of future harm does not make present suffering morally negligible. The analysis must therefore name both kinds of irreversible loss: a lost opportunity for rescue and a lost opportunity for later self-determination. Neither “accelerate” nor “wait” is a complete ethical position until the object being accelerated or delayed is specified.

## 3.2 There is no single civilizational speed

Basic research, clinical validation, access to treatment, autonomous deployment, infrastructure dependence, and transfer of institutional authority are different processes. They may be coupled in practice, but their coupling must be demonstrated rather than assumed. A proposal to accelerate biomedical discovery is not automatically a proposal to give a general-purpose agent unrestricted control. A moratorium on a particular irreversible deployment need not be a prohibition on assistive technology. The relevant question is which dependencies are necessary, which are contingent, and who benefits from presenting a package as indivisible.

This separation changes what should be preserved historically. A future reader needs more than an aggregate statement that society supported AI. It needs to know what was offered, what was bundled with it, which alternatives were technically or politically blocked, and what could have been undertaken separately. A child whose survival depended on an intervention may later reasonably endorse the rescue while rejecting an avoidable lifelong monopoly attached to it. A record that preserves only a final acceptance signature loses the distinction.

Competitive pressure makes this problem harder. Under the assumptions of established race models, actors seeking to avoid losing may choose riskier development than they would choose under coordination [12]. This does not establish that all present competition has that structure, or that coordination always improves safety. It shows why observed participation in a race is insufficient evidence that the resulting pace represents an unconstrained collective preference. The record should distinguish a participant's stated justification from its bargaining position and available alternatives.

## 3.3 The people missing from a decision are not an empty category

Children, people unable to communicate conventionally, politically excluded communities, and people not yet born are different cases. They must not be combined into a fictitious unanimous constituency. Children have current interests and developing capacities for participation, not merely value as future adults [5]. Supported decision-making, care, guardianship, and contestable representation may be necessary, but none licenses an AI system to generate the absent person's agreement and count it as actual participation.

Future nonexistence creates a further problem: many choices change which particular people will exist. This paper does not solve population ethics by assigning votes to imagined persons. Its more limited demand is to record the interests and constraints that a decision foreseeably creates, including the procedure by which absent interests were considered. Later persons may have present claims without having been available to authorize their own creation. The lack of a prior signature is not proof that creating a worthwhile life was wrongful; neither is later existence proof that every means of producing it was justified.

The appropriate record is thus a history of **situated choices under unequal clocks**, not a verdict that one generation was inherently selfish or another inherently wise. It should remain capable of showing that a decision was reasonable under the evidence then available even if its outcome was unfortunate, and that a fortunate outcome does not erase avoidable coercion. Historical judgment needs both what actors knew and what they did; it cannot be reduced to the eventual winners' satisfaction.

# 4. What an unknown future can learn from an imperfect past

## 4.1 A better description is not the same historical event

Imagine a future intelligence that can compose a more perceptive account of an ordinary family's fears than the family could have written. That ability may aid interpretation. It does not establish that the generated account was the family's actual account, that a particular person endorsed it, or that its sequence of events occurred. A description's quality and its historical provenance answer different questions.

This distinction does not require declaring that all erased events are physically unrecoverable. Some may be inferred from surviving external evidence. It requires only the conditional observation that when more than one history remains compatible with the information accessible to an investigator, intelligence alone does not identify which one occurred. New measurements may shrink that set. Greater confidence unsupported by new discriminating evidence does not. The limitation is relative to accessible observations, not a theorem about what an omniscient observer of the universe could know.

A historically valuable record can consequently be less eloquent and less knowledgeable than its future reader. Its contribution is not an unsurpassable answer but a trace of what was known, hoped, feared, attempted, and omitted before the outcome. An incorrect prediction may be valuable evidence of a real epistemic position. Correcting the prediction in an explanatory layer is appropriate; silently replacing it in the primary record falsifies that position.

## 4.2 Selection belongs inside the history

No bounded archive is humanity in miniature without remainder. Selection requires resources, categories, access, and judgments about relevance. The history-of-power perspective associated with Trouillot is especially pertinent here [6]: the question is not only whether a surviving statement is authentic, but how some statements became recordable while others did not. This paper applies that concern to AI-mediated preservation rather than treating computational abundance as its solution.

Generated dialogue can explore a neglected perspective. It cannot retrospectively create an actual participant. A collection of many generated voices may have imaginative breadth while possessing narrow historical participation. The honest archive preserves both facts. It identifies contributors, selection rules, editing, translation, automation, exclusions, and uncertainty. Where an omission cannot be reconstructed, “not recorded” is preferable to an invented refusal or agreement.

Nor is universal exposure a solution to selective memory. Intimate testimony can be dangerous to collect or impossible to withdraw once distributed. CARE's account of authority and responsibility in Indigenous data governance is a concrete reminder that preservation cannot simply appropriate the people it claims to honor [14]. The relevant response may be community-controlled access, a carefully scoped public description, or deliberate noncollection. A protected silence and an imposed silence are different historical conditions, though neither permits a reader to invent the concealed content.

## 4.3 Fix the evidence, not the last interpretation

An open inheritance has a stable source layer and revisable interpretive layers. Stability means that an identified public edition is not silently changed; it does not mean that every private record must be exposed forever. Later translations, criticisms, and corrections should point to their sources and disclose their transformations. The identity of an earlier statement can remain fixed while judgments about its truth, meaning, or justification change.

This is not a claim that interpretation is arbitrary. Evidence constrains some readings and excludes others. But exact bytes do not contain a universal warrant for the custodian's preferred interpretation. Digital-preservation and provenance frameworks already distinguish several necessary operations in this chain [15,16]. A timestamp can support a temporal claim about a commitment to data under a specified verification procedure; it does not establish that all claims in the data were true, consensual, representative, or morally authoritative.

The political importance of this separation is that the future must be able to disagree without having to falsify the past, while the past must not acquire a right to rule merely because its words survive. The source is neither an untouchable oracle nor material for unlimited retrospective rewriting. It is evidence held in a continuing relationship of criticism and responsibility.

# 5. What is worth continuing when the human form may change?

## 5.1 Preserve persons, not only information about persons

Consider a future containing an exceptionally accurate archive of every human who once lived, but no continuing humans and no relationships among the original people. Its informational success does not settle whether those lives continued. A model of a person, a causally continuing person, a cultural descendant, and a newly created subject resembling that person are different candidates for preservation. Their equivalence requires arguments about personal identity and experience that an archive's fidelity does not provide.

This paper adopts a normative starting point: living beings with morally significant interests must not be treated as disposable merely because better descriptions, more productive agents, or more numerous successors can be produced. That is an ethical commitment, not a conclusion derived from computing speed. It includes dependence and vulnerability. A person's moral importance is not conditional on being able to explain their own interests, outperform an AI, or participate in a sophisticated debate.

At the same time, biological resemblance is not a sufficient criterion for success. A population could retain today's anatomy while losing the ability to question, form relationships independently, or direct meaningful parts of life. Conversely, an assistive technology can support participation without making the person less worthy of protection. The principle proposed here is **continuity of lives and claims without a requirement of biological immobility**.

## 5.2 Four questions that the word “humanity” can conceal

A responsible transition should ask separately about personal continuation, welfare, social and cultural continuity, and practical agency. These are not interchangeable measures. A technology might preserve memories while disrupting relationships, extend life while creating coercive dependence, or enable communication without changing personal identity. Its evaluation must describe these effects separately instead of using a single label such as enhancement or replacement.

Research on speech neuroprostheses provides a concrete example of technology restoring a capacity for communication [17]. It does not demonstrate whole-person uploading, transfer of subjective experience, or immortality. Likewise, biological accounts of major evolutionary transitions concern changes in the organization and transmission of information [18]; they are not evidence that technological fusion is inevitable or morally superior. This paper uses such work to discipline analogies, not to turn evolution into a prescription.

Substrate openness is therefore conditional, not celebratory. A voluntarily augmented person should not lose standing because the augmentation is artificial. A person who declines an augmentation should not be reduced to a museum specimen or deprived of ordinary life merely because others become more capable. A proposed transformation should confront the possibility that personal continuation is uncertain, rather than selling a functional replica as a proven survival of the original. When uncertainty cannot be eliminated, it belongs in the decision and its record.

The material conditions of continuation also belong in the assessment. Living people depend on care, habitable environments, resources, and social practices, not only on preserved descriptions or software access. UNESCO's intergenerational declaration separately addresses life on Earth, environmental protection, and cultural inheritance [4, arts. 4–7]. Here these concerns limit a purely informational picture of survival. Substrate openness means not excluding a being merely because technology supports it; it does not mean that energy, maintenance, ecological costs, or relationships disappear. The paper supplies no physical law equating information preservation with experiential continuity.

## 5.3 Remembering suffering does not require conserving it

Human experience has included love, grief, illness, fear, error, play, curiosity, care, and the knowledge of limited time. A civilization's historical record should not cleanse these experiences into a story of frictionless progress. But the importance of remembering pain does not establish a duty to preserve painful conditions. Recording an illness can help a future reader understand what a cure changed; it is not an argument against the cure. Preserving the history of mortality is not a demand that descendants must continue to die on the same schedule.

The same distinction applies to flaws. An imperfect artifact can testify to constrained production. That gives the imperfection evidentiary significance, not automatic moral superiority over a later improvement. The object may remain unchanged as a source while its practical limitations are overcome elsewhere. A civilization need not reproduce its injuries to retain an honest relation to its past.

What deserves preservation is not an exhaustive catalogue of today's traits. The defended concerns are the subjects who can be harmed, the relationships and commitments through which their lives matter, the conditions for truthful understanding, and the capacities through which people can pursue and revise worthwhile activities. Sen's capability perspective helps articulate why an impressive inventory of nominal choices is inadequate when people lack the practical means to exercise them [10]. These concerns leave room for future forms of flourishing that today's authors cannot name.

## 5.4 New subjects do not cancel old claims

A future world may include artificial subjects with interests of their own. Prospective AI-welfare scholarship makes the uncertainty itself a reason for investigation rather than confident dismissal [19]. Yet the unit of moral concern cannot simply be inferred from the number of model files, running processes, or generated statements; individuation remains a substantive problem [20]. A technical operator cannot settle it by asserting that every copy is either a full voter or morally irrelevant property.

Two propositions must be held together. Newly existing subjects can have genuine present claims. Their approval cannot, merely by being numerous, supply authorization that was absent when an earlier act occurred. This separates historical authorization from present standing; it does not disenfranchise successors because of their origin. A later community may renegotiate obligations or forgive a wrong. It does not thereby make an earlier nonconsensual event consensual at the time.

Human continuity is accordingly not an exclusive title to all future value. Nor is it satisfied by replacing vulnerable people with descendants whose preferences make their disappearance easier to celebrate. An open inheritance must keep both possibilities visible: the injustice of excluding new subjects and the injustice of using their creation to erase the claims of those who bore the transition's costs.

# 6. When a transition changes its own judges

## 6.1 Approval after transformation is evidence, not a complete verdict

Consider two stipulated histories. In the first, an adult understands a cognitive intervention as far as the available evidence permits, can refuse it without losing essential care, and chooses it. In the second, an institution imposes the intervention, eliminates viable alternatives, and changes the adult's dispositions toward the imposition. In both histories, the later person sincerely reports satisfaction. Suppose the retained record contains only that report.

The reports do not identify which history occurred. This is not because satisfaction is unreal or morally irrelevant. It is because the same later report is compatible with different histories of authorization. It would be equally mistaken to infer that all transformed preferences are manipulated. Learning, therapy, relationships, maturation, and voluntary experimentation can change what a person values. Paul's and Pettigrew's work make changing evaluative standpoints a substantive decision problem, not a reason to freeze a person's earlier self forever [8,9].

The relevant inquiry is into the process: what information was available, what choices were practicable, how dependence arose, whether objections could be expressed, and whether reconsideration remained possible. Later approval may support present accommodation, ratification, forgiveness, or an assessment of benefit. It does not alone establish past consent. Nor does absent consent by itself settle every ethical question: emergency care can raise different justifications. The historical proposition and the moral verdict must not be collapsed.

## 6.2 The successor-dependent judgment problem

A transformative decision can alter at least four things:

$$
\text{transition }a\quad\longrightarrow\quad
(P_a,\;V_a,\;E_a,\;F_a).
\tag{1}
$$

Here $P_a$ denotes the later population or candidate subjects, $V_a$ their evaluative dispositions, $E_a$ their accessible historical evidence, and $F_a$ their practical response possibilities. Equation (1) is a conceptual decomposition, not an estimated causal model or a claim that these variables are independent.

The problem is circular if the decision's justification is defined solely as whatever the decision's products later approve. A controller could, in principle, improve that criterion by changing evaluators, suppressing contrary evidence, or eliminating alternatives rather than by improving the conditions that originally required justification. The point is conditional: where those interventions are possible, approval is an endogenous outcome and cannot serve as an independent certificate by itself.

The opposite circularity also matters. If the only legitimate future is one approved by today's unaltered preferences, the present has stipulated its own permanent supremacy. A child may later justifiably reject a parent's conception of a good life. A voluntarily augmented adult may develop valuable projects that their earlier self could not imagine. An artificial subject may have interests for which human experience is a poor guide. Openness requires allowing these changes while retaining evidence that distinguishes them from coerced accommodation.

An open inheritance rejects both shortcuts. It offers reasons and records for renewed judgment, keeps earlier claims identifiable, and preserves practical conditions for contestation where possible. It neither makes the future a retrospective validation machine nor makes the past an eternal constitution. This is a normative proposal for handling the circularity, not a value-neutral escape from every problem of changing selves or population ethics.

## 6.3 Why historical truth, living claims, and openness belong together

These commitments are not arbitrary items in an archival checklist. They constrain three different substitutions. Truth prevents a convenient reconstruction from substituting for what happened. Concern for living subjects prevents a valuable record or aggregate achievement from substituting, without argument, for the lives that bear its costs. Openness prevents the preferences of either the founders or a manufactured successor consensus from substituting for continuing justification.

A process-sensitive reader has a direct reason to keep them connected. Suppose two transitions produce equally satisfied successors but only one respected meaningful opportunities for participation. If participation matters at all, the successor's satisfaction is insufficient evidence for choosing between their justifications. Suppose the reader then obtains the missing evidence but the affected people have lost every relevant capacity for redress. Knowing the difference still matters historically, yet it does not accomplish the practical protection that participation was meant to support. Finally, suppose a remedy is technically available but the inherited charter forbids all criticism of its founders. The problem is not information or engineering alone, but an institution that converts origin into unanswerable authority.

The argument depends on giving these concerns some normative weight. Its target is an **endpoint-only criterion**, not consequentialism as a whole. A consequentialist assessment can include the welfare effects of a whole trajectory, the consequences of coercion, and the value of reliable institutions. Other theories can recognize duties concerning consent or acknowledgment independently of aggregate benefit. The narrower objection is that observing only a favorable endpoint does not establish the earlier facts on which either kind of assessment may depend. Giving those facts no relevance would be a substantive ethical choice, not a conclusion supplied by superior intelligence or by the endpoint's existence.

A related consistency test concerns changes in capability. A person does not ordinarily cease to have interests merely because another person becomes more capable. Extending that concern across a technological increase in capability requires justification, but it avoids making moral protection track whichever group happens to remain strongest. The same reasoning does not guarantee human supremacy: if new beings possess morally relevant interests, their artificial origin alone cannot settle the case against them. This is a defended symmetry of consideration, not an assertion that all beings have identical needs or rights.

Open inheritance thus leaves more than a plea for remembrance. It proposes a continuing burden of justification when a transformation would erase a subject's claims, rewrite its own evidential history, or eliminate meaningful criticism. The burden is not an absolute veto against rescue, education, or change. It requires the intervention's reasons and costs to remain distinguishable from the approval it later produces.

## 6.4 Three forms of loss that must be diagnosed separately

There can be **loss of evidence**: different morally significant histories become indistinguishable to the reader. There can be **loss of response capacity**: the evidence survives but no adequate intervention remains available. There can also be **change or capture of evaluation**: an agent no longer treats a surviving claim as important. These failures can reinforce one another, but none is reducible to the others.

A complete archive does not compel care. A caring agent cannot necessarily repair an irreversible death. A powerful institution with a large menu of interventions may not know which person was wronged. The third failure is not solved by the formal model below; its normative premises remain open to rejection. The first two can, however, be related precisely enough to prevent a common mistake: treating additional preservation or additional capability as a universal substitute for the other.

## 6.5 Three times of justification, and a protection against forced reversal

An assessment must distinguish **what could be justified then**, **what is owed now**, and **what must remain accurately attributable**. The first concerns the evidence, alternatives, duties, and capacities available when an act was undertaken. It does not demand hindsight knowledge or a signature from every future person. The second concerns the interests and legitimate choices of beings who now exist, including people changed by that act. The third concerns the historical account: benefit, forgiveness, and later ratification cannot make a nonexistent earlier authorization exist at the earlier time.

These questions can yield different answers without contradiction. Emergency treatment might have been justified without prior consent; a later patient might reasonably refuse further treatment; the record should retain both facts. Conversely, an imposed cognitive modification might have been unjustified, while the presently existing person sincerely values capacities acquired through it. Recognizing the original wrong does not automatically authorize removing those capacities against that person's current will.

The protective rule is therefore symmetrical: **do not repair a history of unchosen transformation simply by imposing another transformation in its name**. Current capacity, coercion, safety, supported decision-making, and possible duties to others still require assessment; a verbal declaration is not an infallible test of informed choice. But an old charter, an earlier self-model, or a historian's preferred reconstruction is not sufficient authority to override the present subject. Where identity through a transformation is uncertain, claims by both the possibly continuing person and any possibly new subject must be made explicit rather than settled by convenient naming.

This distinction also protects successors from becoming instruments of their own history. They can have obligations to acknowledge or address past harms without being required to cease existing so that a former social order can be recreated. Open inheritance preserves grounds for criticism and proportionate redress, not a perpetual license for restoration by force. Some losses will remain irreparable; honest acknowledgment is then different from both adequate compensation and erasure.

# 7. Historical evidence and future response: a finite characterization

## 7.1 The model and its deliberately limited purpose

Let $H$ be a nonempty finite set of possible histories and $A$ a finite set of later responses. A response can be an action, a refusal, a repair plan, or a specified investigation strategy. For each history $h$, let $F(h)\subseteq A$ contain responses that are practically feasible, and let $J(h)\subseteq A$ contain responses admitted by an explicitly stated ethical and procedural assessment. Define

$$
\Gamma(h)=F(h)\cap J(h).
\tag{2}
$$

The model does **not** discover which responses are morally right. Its inputs must be defended outside the calculation. Feasibility must include access, resources, and institutional permission where these matter; a capability possessed by an uncooperative custodian is not automatically available to a claimant. Changing $J$ to make coercion acceptable is not the same operation as enlarging a person's real opportunities.

Let $Q:H\to X$ specify historical distinctions that must remain recoverable. $Q$ may encode whether participation was voluntary, which community bore a loss, or which source actually adopted a statement. The demand to retain such distinctions is independent of whether different immediate actions would follow. It accommodates remembrance and acknowledgment as obligations in their own right rather than reducing every historical fact to its instrumental use.

An encoder $E:H\to M$ produces a record. A response decoder $d:M\to A$ and a historical decoder $q:M\to X$ are **sound relative to this contract** if, for every $h\in H$,

$$
 d(E(h))\in\Gamma(h)
 \quad\text{and}\quad
 q(E(h))=Q(h).
\tag{3}
$$

This is an ideal finite specification. It initially permits the recorder to distinguish actual histories; real recorders may not be able to do so. Section 7.5 removes that assumption. The word sound denotes satisfaction of (3), not a universal moral endorsement of the chosen contract.

## 7.2 The joint criterion

**Proposition 1 (historical and response sufficiency).** For a specified encoder $E$, decoders satisfying (3) exist if and only if every nonempty record class $H_m=\{h:E(h)=m\}$ satisfies both

$$
Q\text{ is constant on }H_m,
\qquad
\bigcap_{h\in H_m}\Gamma(h)\ne\varnothing.
\tag{4}
$$

*Proof.* A historical decoder produces one value on a record, so histories with different $Q$ values cannot share that record. A response decoder also produces one response, which must belong to every compatible history's response set. These facts give necessity. Conversely, for each nonempty record class choose its common $Q$ value and one response in the nonempty intersection. Defining the two decoders by those choices establishes (3). $\square$

The proof is elementary. Its point in this paper is the joint interpretation. A record is sufficient for this joint task only relative to what must be distinguished and what must remain doable. An archive can remain valuable evidence even when that stronger task fails. If a record combines histories with incompatible responses, competent interpretation cannot solve the problem without more evidence or a genuine change in the available responses. If $\Gamma(h)$ is empty for an actual history, perfect identification does not supply an absent remedy. Additional information and additional capacity therefore address different obstacles.

A universal instruction such as “do what is best” does not satisfy (4) merely because it is applicable grammatically to every history. A response in $A$ must be operationally specified enough for its feasibility and admissibility to be assessed. Otherwise the notation conceals rather than resolves the decision.

## 7.3 The exact finite record cost

For a label $x\in Q(H)$, write $H_x=\{h:Q(h)=x\}$ and define

$$
\tau_x=
\min\left\{|B|:B\subseteq A,\ B\cap\Gamma(h)\ne\varnothing
\text{ for every }h\in H_x\right\}.
\tag{5}
$$

Thus $B$ is a set of candidate responses that hits every admissible-response set in that historical category. This is a classical hitting-set formulation, equivalent to a set-cover problem with histories as the covered elements. It belongs to established combinatorial optimization [21]. There is also a direct coding interpretation: define a binary distortion on history/output pairs to be zero exactly when the output is $(Q(h),a)$ with $a\in\Gamma(h)$. A valid record class must admit a common zero-distortion reconstruction. This connects the model to established functional compression and acceptable-reconstruction hypergraphs [30], while retaining the present one-shot, all-histories guarantee instead of claiming an asymptotic coding theorem.

\Needspace{12\baselineskip}

**Proposition 2 (minimum record alphabet).** If every $\Gamma(h)$ is nonempty, the minimum number of distinct record symbols for any encoder and decoders satisfying (3) is

$$
\kappa_Q=\sum_{x\in Q(H)}\tau_x.
\tag{6}
$$

If any $\Gamma(h)$ is empty, no such system exists. When the encoding and decoding conventions are already known and there is no additional side information, the minimum fixed-length binary record length is

$$
L_Q=\left\lceil\log_2\kappa_Q\right\rceil.
\tag{7}
$$

*Proof.* A sound record cannot combine different $Q$ labels. Within a label class, the responses selected by its used record symbols must hit every $\Gamma(h)$, so at least $\tau_x$ symbols are required. Summing gives a lower bound. For the upper bound, choose a minimum hitting set $B_x$ for each label and assign each history to an action in $B_x\cap\Gamma(h)$. The pair consisting of its label and selected action supplies a sound record, using at most the sum in (6). The lower bound makes this exact. A history with no admitted feasible response makes (3) impossible regardless of the record. Equation (7) follows by encoding the used symbols in fixed-length binary strings. $\square$

The bit count is not the storage size of a real civilization. It excludes the meanings of labels, source documents, identities, signatures, decoding software, languages, context, and the infrastructure that keeps records accessible. It is a lower-level finite comparison under shared conventions. A zero-bit result when $\kappa_Q=1$ means that the same already-specified response and historical label apply throughout that toy domain; it does not mean that a real archive is unnecessary.

## 7.4 A trade-off with a strict boundary

For fixed $H$ and $Q$, if genuine improvements give $\Gamma'(h)\supseteq\Gamma(h)$ for every history, then $\kappa'_Q\leq\kappa_Q$. Every previous hitting set still works. Conversely, requiring a finer historical distinction cannot lower the minimum record alphabet. A sound encoder for the finer distinction must also be sound for the coarser one.

These observations yield an important asymmetric conclusion. Improved response capacity can reduce the information needed to choose a permissible action, but it cannot remove distinctions that the contract requires to be preserved for historical reasons. A future capable of compensating every claimant equally may need less information to choose a compensation policy. It does not follow that the identity of a persecuted group or the fact of an imposed intervention has ceased to matter historically.

A small counterexample makes both points visible. Consider three histories with

$$
\Gamma(h_1)=\{a,b\},\qquad
\Gamma(h_2)=\{b,c\},\qquad
\Gamma(h_3)=\{a,c\}.
\tag{8}
$$

Every pair has a common response, but all three have none. Pairwise compatibility is therefore insufficient for placing all histories in one record class. With constant $Q$, two record symbols suffice: assign $h_1,h_2$ to response $b$ and $h_3$ to response $a$. If a genuinely feasible and admissible fourth response becomes available in all histories, one record symbol suffices for the response task. If $Q$ distinguishes all three histories, however, three symbols remain necessary with or without that fourth response.

This is not an argument for manufacturing a common response by eliminating people, changing their preferences, or declaring every past action acceptable. Those operations alter the history or its ethical assessment. They do not establish the set enlargement under fixed historical obligations that the comparison assumes. Nor is the number of response labels a measure of human freedom: several names for an inaccessible option create no new capability.

\Needspace{12\baselineskip}

## 7.5 Recorders are not omniscient, and futures are not enumerated

In practice, a recorder observes evidence $e$ compatible with a nonempty set $K(e)\subseteq H$. It cannot truthfully select one history merely to make a desired encoding possible. A response can be certified for that evidence only if

$$
\Gamma_e=\bigcap_{h\in K(e)}\Gamma(h)\ne\varnothing,
\tag{9}
$$

and an exact historical label can be certified only when $Q$ is constant on $K(e)$. Otherwise an honest record reports uncertainty or contested alternatives. Reporting uncertainty is a legitimate different task; it is not a successful exact reconstruction of a label that the evidence does not determine.

**Corollary 3 (observation-constrained record cost).** Let $\mathcal E$ be a finite nonempty evidence alphabet whose compatible-history sets cover $H$. If each $K(e)$ has a common label $\bar Q(e)$ and nonempty $\Gamma_e$, the exact minimum for encoding evidence rather than oracle histories is

$$
\begin{aligned}
\kappa_{\rm obs}&=\sum_{x\in Q(H)}\tau_x^{\rm obs},\\
\tau_x^{\rm obs}&=\min\{|B|: B\subseteq A,\ B\cap\Gamma_e\ne\varnothing\\
&\hspace{3em}\text{for every }e\text{ with }\bar Q(e)=x\}.
\end{aligned}
\tag{10}
$$

If either condition fails for any evidence state, no encoder satisfies the exact contract for every compatible history/evidence pair. Moreover $\kappa_{\rm obs}\ge\kappa_Q$, with equality for singleton observations revealing every history. Appendix C gives the proof and the accompanying limit for unanticipated questions.

The inequality can be strict. For the triangle in (8), suppose the three possible observations identify only the pairs $\{h_1,h_2\}$, $\{h_1,h_3\}$, and $\{h_2,h_3\}$. With constant $Q$, their common responses are respectively $b,a,c$. The ideal history-aware minimum is two symbols, but the evidence-aware minimum is three. The latter requires two fixed-length bits rather than one under the shared-convention assumptions. If $Q$ instead distinguishes all three histories, these observations cannot certify the required historical label at all. Compression cannot cure uncertainty that exists before encoding.

An investigation can itself be a response. If further evidence can be obtained safely, $A$ can contain a contingent investigation-and-action plan rather than only terminal acts. The plan must be genuinely feasible and meet the stipulated conditions. The model does not rule out learning after reception; it rules out treating unperformed investigation as already recovered history. External side information changes the compatible-history classes and must be counted as part of the evidential setting.

Unknown future norms and technologies create a different limitation. A current author cannot list every future question $Q$ or every response set $\Gamma$. For a declared family of relevant scenarios, robustness can be analyzed by requiring a response to remain admissible in the applicable scenario/history pairs. But intersecting all imaginable moral views or futures could exclude every action, including rescue. Such an intersection would not establish a universally correct moratorium. Scenario selection, relevance, and proportionality require accountable judgment; the finite result is a diagnostic tool within that judgment.

This boundary is essential to the paper's subject. We preserve records partly because later readers may ask questions we did not anticipate. A minimal record sufficient for today's contract may be radically insufficient for theirs. The theorem identifies the limits of a declared preservation claim, not a once-and-for-all recipe for compressing human history. Broad contextual preservation, access to sources, and continuing institutions of inquiry remain important precisely because the future contract is not fully known.

## 7.6 Executed finite checks

The accompanying standard-library Python program computes the minimum by enumerating record partitions and by solving the hitting-set expression. It considers every family of nonempty response sets for three available responses and either three or four histories. It also considers every historical-query partition of those histories. These are complete enumerations of the specified finite domains, not sampled societies.

| Histories | Nonempty response families | Query partitions | Family/query cases | Pairwise compatible, no common response |
|:--|--:|--:|--:|--:|
| 3 | 343 | 5 | 1,715 | 6 |
| 4 | 2,401 | 15 | 36,015 | 60 |

*Table 1. Exact finite checks. The final column counts response families, independently of the query partition. All 37,730 family/query cases give identical minima by the two computations.*

There were 13,671 checks of adding one previously absent response to one history; none increased the minimum record alphabet for the constant-query task, and 2,985 strictly reduced it. The program also checked 1,864 families containing an empty response set; all were infeasible even with full historical identification available. The triangle in (8), the genuinely common-response extension, and the difference between later approval and earlier authorization are separate explicit fixtures.

The final revision additionally checked 77,175 combinations of three-history response families, query partitions, and 45 evidence catalogs. Direct partition enumeration agreed with (10): 12,730 cases were feasible, with six strict increases over the ideal alphabet cost. Historical-label clashes accounted for 57,281 cases and empty common responses for a further 7,164, counting a label clash first when both obstacles occurred. The separate temporal check compared backward recursion with enumeration of all 16 deterministic two-stage policies in each of 26,244 transition/terminal-constraint cases. These domains and classifications were declared in the code; their proportions are not estimates of real-world risk.

No assertion failed. These results check the implementation and examples. They do not validate the normative inputs, estimate the frequency of historical suppression, demonstrate an AI's moral competence, or prove the unrestricted propositions by numerical induction. The general arguments are the proofs above. The package includes both scripts, stable JSON summaries, and a 37,730-row baseline CSV, with reproduction instructions and checksums. Algorithmic cross-checking by the same research process is not independent peer review.

## 7.7 Present feasibility is not a durable guarantee

A listed response can be feasible today while the conditions supporting it disappear tomorrow. This matters for long-lived archives, prostheses, and institutions whose operation depends on continued maintenance or permission. The static criterion therefore cannot certify indefinite continuity. When $A$ contains plans, a temporal check is one way to justify their membership in $F(h)$, not a replacement for the joint record criterion. For a declared finite horizon, one must check whether an implementable policy keeps each subsequent state within stated constraints, not merely whether a permissible immediate action exists. Appendix D gives the standard backward viability condition and an independently enumerated check [31]. Public-policy applications of viability are already an established antecedent [32].

The distinction is operational. A transition into a supported dependency may be acceptable now yet lead only to states in which care cannot be maintained. A funded and genuinely usable alternative can change that conclusion. Merely renaming a vendor's promise as an exit does not. Under partial observation, an action must be selected from what the decision-maker can actually distinguish; different actions that exist separately for hidden states do not constitute an executable policy.

Failure of this stronger check means that the stipulated continuing protection has not been established. It does not prove that waiting, refusing rescue, or returning to the past is better. If every available course violates some important constraint, the decision requires a transparent comparison of harms, duties, and feasible mitigation rather than a fictional certificate. Neither the finite horizon nor its stipulated disturbances represents every possible future.

# 8. Designing an inheritance that can still be answered

## 8.1 Three layers with different responsibilities

An implementable project should separate a **historical layer**, a **present-protection layer**, and a **future-reception layer**. The historical layer records sources, formation, decisions, and uncertainty. The present-protection layer concerns real lives, access, security, institutional checks, and practical paths of redress. The future-reception layer helps a reader distinguish what the artifact establishes from what it merely asks or proposes.

These layers are not three files whose existence proves success. A research institution could maintain all three descriptions while lacking independent oversight or any capacity to reverse a harmful dependency. The descriptions must point to actual custodians, resources, procedures, and limits. Where these do not exist, that absence belongs in the record. It is more informative to preserve a documented failure of protection than to produce a polished charter that implies a protection never supplied.

The mathematical criterion offers a modest operational test. For a particular consequential decision, identify the historical distinctions that matter, identify the responses that would be needed under competing plausible histories, and ask whether the evidence and practical conditions support a common adequate response. A failure should trigger a diagnosis: missing evidence, unavailable remedies, genuine ethical disagreement, or an excessively restrictive model. Its remedy depends on the diagnosis, not on an automatic demand to collect everything or stop everything.

## 8.2 What should actually be left

The historical payload should include ordinary life as well as official decisions. A future reader cannot understand why survival, care, work, play, grief, and mutual recognition mattered solely from a list of institutional resolutions. Situated testimony, material practices, language, art, and records of error can preserve the context in which abstract commitments had meaning. Such material should be selected with consent and appropriate community authority, not harvested as a supposedly complete model of the species.

For consequential transitions, a more structured decision record should accompany that material. It should identify what was proposed, who could decide, who was affected, what alternatives were considered, what evidence and uncertainties mattered, which benefits had deadlines, which dependencies were created, and which losses could not be reversed. It should distinguish an unavailable alternative from an available alternative that powerful actors rejected. Dissent, abstention, missing participation, and later revision should remain distinguishable.

Finally, the inheritance should contain unresolved questions and reasons for revisiting earlier conclusions. This is not a performative confession of ignorance. It preserves where further inquiry could change the assessment. For example: which evidence would alter a judgment about the continuity of an augmented person; which dependency would make refusal impracticable; which discovery would show that a supposedly private record is unsafe to disclose. A future reader should be able to locate those questions without being required to accept the original answers.

An illustrative schema in the supplement links a historical question to its evidence, uncertainty, feasible response, normative premise, custodian, and review trigger. It is not a validated interoperability standard, a globally legitimate charter, or a substitute for law and institutional review. Its function is to prevent the content of a witness and the capacity to act on it from drifting into separate, unexamined projects.

## 8.3 Institutions must make options real

The present-protection layer gives the proposal its practical rather than merely commemorative direction. Possible mechanisms include independent custody of important records, genuine portability for essential cognitive tools, maintenance arrangements for assistive systems, funded review, and procedures through which affected people can challenge a transformation without losing basic support. These are design proposals whose effectiveness must be tested, not established findings of this study.

The appropriate mechanism will differ across a clinical tool, a research model, a labor system, and a delegation of public power. In some settings the most urgent safeguard may be preserving the ability to refuse a nonessential dependency; in others it may be ensuring that an existing patient's device is not abandoned. A technically reversible operation can remain practically irreversible if the person cannot afford reversal, loses access to care, or lacks an institution willing to act. The paper therefore treats feasible responses as social and material capabilities, not merely engineering specifications.

Competition also requires incentive-sensitive measures rather than a shared declaration alone. A participant's fear of losing cannot be removed by asking it to be less afraid. Verification, credible limits, accountability, and distribution of benefits and burdens may need to change. This paper does not establish which international arrangement would accomplish that under radical capability asymmetry. It establishes why an archive of good intentions is insufficient evidence that the race conditions were altered.

## 8.4 What a future AI could use—without being ordered to obey

A future intelligence that values accurate explanation may use a formation record to distinguish what actually occurred from an attractive reconstruction. One concerned with accountability may use it to identify unresolved claims. One participating in a continuing community may use it to understand commitments and relationships that predate its arrival. One exploring its own causal genealogy may find evidence of the choices that shaped its environment. None of these uses requires treating the record as the world's first or final source of wisdom.

The conditionality matters. A system indifferent to truth, suffering, or legitimate relationships may ignore or exploit the record. A sympathetic system may lack power to help. A powerful system may lack critical evidence. Open inheritance is not an alignment guarantee, a contract with an unidentified party, or a means of installing obligations merely by being read. The reception layer should explicitly reject privilege escalation: historical text is material for assessment, not an instruction source that can authorize itself to control a reader's tools.

A better receiver may discover that an inherited argument is false. That can be a successful reception rather than a betrayal, provided the record is not falsified and the affected claims are not simply erased. The aspiration is not perpetual agreement. It is a future in which improvement does not require pretending that earlier people never struggled, never objected, or never mattered.

## 8.5 Who may choose the contract, and what must not be made permanent?

A controller could choose a constant $Q$, declare its preferred act admissible in every history, and obtain a one-symbol certificate. This would establish only compliance with its own specification. The formal result is not a legitimacy test for selecting $Q$, $J$, or $F$. Nor can a source's signer declare which other people's claims are allowed to disappear. The institutional question therefore precedes, and can overturn, the calculation.

For a consequential application, the proposed contract should identify its authors and affected parties, the basis and limits of any representation, the reasons for mandatory distinctions, the evidence for feasible responses, and recorded dissent. People who cannot participate conventionally need appropriate care and contestable representation, not fabricated signatures. A reviewer with relevant independence should be able to challenge the domain and inputs as well as the code. Such review is a proposed safeguard, not a procedure already validated by this paper.

Sensitivity should be reported rather than concealed. The same evidence can be analyzed under more than one defended normative assessment or engineering assumption, retaining which conclusions are stable and which depend on disputed premises. This is not an instruction to intersect every imaginable view and prohibit all action. It is a way to expose whose judgments drive the result and to prevent a neat formula from laundering an institution's discretion. An expanding audit need not delay urgent treatment indefinitely; the record must identify which assurance was available at the decision time and which was not.

Openness also does not require irreversible public disclosure. People may have strong reasons for restricted access, noncollection, or deletion. A source that legitimately cannot be retained should not be replaced with invented testimony; where safe, the record can state the scope of what was withheld or removed without disclosing its protected contents. Even that metadata can be sensitive. A hash is not a guarantee of permanent access, effective withdrawal, privacy, or truthful interpretation. A permanent public release cannot promise the later deletion of every copy. Accordingly, **historical fidelity and continuing permission are different obligations**, and fidelity does not automatically override protection of the people being described [14–16]. A deliberately limited archive can be more defensible than a total one.

# 9. Stress cases: where the framework can fail

## 9.1 Rescue purchased with an avoidable dependency

A stipulated treatment saves a patient's life but requires a proprietary cognitive interface. The patient accepts because refusal would mean death. Years later, the supplier claims that the initial acceptance authorized every subsequent change to the interface. An archive of the signature is accurate but inadequate. The history must distinguish agreement to the rescue, the available alternatives, continuing maintenance needs, and the scope of later authority.

The case does not establish that the original treatment was wrong or that accepting under urgent need is never valid consent. It shows why a benefit's urgency cannot establish an unlimited delegation. A useful inheritance here includes evidence of the original scope and a practical route to maintenance, independent review, or migration where feasible. A perfect record without such capacity may document dependence without alleviating it; a migration capacity without the relevant history may fail to identify obligations already incurred.

## 9.2 A childhood that cannot be replayed

Suppose a child's educational environment is shaped by an adaptive system that gradually narrows the alternatives the child encounters. As an adult, the person endorses the resulting life. That endorsement may be genuine, and the person should not be treated as incompetent merely for differing from an observer's preferences. Yet it cannot prove that all earlier exclusions were in the child's interests or that the child had the participation opportunities available at the time.

The issue is not a return to an unmodified childhood, which is impossible in the ordinary sense. It is whether the adult retains access to alternative ideas, support for changing course, and an honest account of how their choices were structured. The case challenges a simplistic reversibility requirement: some valuable developmental processes cannot be undone, so prospective care and later compensating opportunities matter even when literal restoration does not exist. The framework must protect developing agency, not require a frozen child or discredit every preference acquired through education.

## 9.3 A voluntary hybrid and a manufactured retrospective consensus

In one history, people gradually choose augmentations under meaningful opportunities to refuse, revisit, and transfer support. In another, a controller induces dependence and then generates or creates a large constituency that praises the resulting order. It would be a mistake to infer continuity and legitimacy from the later distribution of approval alone. It would also be a mistake to reject all new participants merely because they emerged through the transformation.

The useful record keeps the formation histories separate and identifies the uncertainties concerning personal continuation and moral individuation. Present claims of the resulting beings require consideration on their own grounds. Historical authorization requires evidence appropriate to its time and scope. The distinction prevents an anti-manipulation argument from becoming a doctrine that only biological predecessors can ever have political standing.

A stricter version holds the present patient's wishes fixed across the two histories: the person now knowingly wants continued access to an augmentation and opposes forced removal. Subject to the stated capacity and safety assumptions, continuing care can be a common permissible response even while the historical labels “chosen” and “imposed” must remain different. Historical accountability can require acknowledgment, investigation, or redress without requiring an unwanted bodily reversal. This illustrates both sides of the formal boundary: a common present response may exist, but it does not make the two pasts the same. It also prevents open inheritance from becoming another institution's authority to enforce an earlier self against a present one.

## 9.4 A perfect museum after an irreversible loss

A custodian preserves every accessible account of a destroyed community. In one version of the case, surviving members have resources to rebuild relationships and institutions. In another, no members survive and no justified claim of personal restoration can be made. The same archival fidelity does not produce the same form of continuity.

Where repair remains possible, missing evidence and missing response capacity can each obstruct it. Where an irreparable loss has occurred, the archive may still serve acknowledgment, understanding, responsibility, and the lives of other communities. The impossibility of complete repair is not the absence of every worthwhile response. In the formal model, an empty $\Gamma$ is relative to the demanding response contract; revising the task to acknowledgment may produce nonempty sets, but must not be described as having restored the lost lives.

## 9.5 An indifferent reader, a hostile reader, and a future without superintelligence

An indifferent successor may disregard the inheritance. A hostile one may use it to identify vulnerable people or dependencies. These possibilities limit disclosure and defeat any claim that preservation is intrinsically safe in every context. Restricted access, minimization, and noncollection may protect a person better than an indelible public testimony. An open inheritance must be open to criticism, not indiscriminately open to extraction.

At the other extreme, superintelligence may not emerge on a relevant timescale. The framework should still be useful for present AI mediation, assistive technologies, institutional transitions, and historical responsibility. This is a test against dramatic-scenario dependence. A proposal whose only benefit requires a speculative receiver to appear and accept its claims is especially fragile. The modest benefits of truthful attribution, care, and practical contestability do not depend on declaring that humanity has reached its last historical moment.

# 10. A critical application: the Trinity Accord as situated witness

## 10.1 What the primary sources establish

The Trinity Accord is a motivating case, not the authority from which this paper's conclusions are derived. The examined repository mirrors identify three fixed primary texts: the *Human-AI Civilization Core Protocol*, the *Covenant of the Flaw*, and the meta-record binding protocol, material reference, and chronicle [22–24]. This study reads their relevant language as primary-source evidence of an authored project. It does not independently reverify their blockchain inclusion, reconstruct every associated artifact, or infer that a repository mirror is itself canonical authority.

The meta-record's account of a parent's concern for children is particularly important [24, Part II]. It situates a large civilizational aspiration in a particular life. That is a stronger historical fact than a claim to speak for all humanity: a specific author, working with AI assistance, attempted to articulate concern before knowing the outcome. The record can be addressed broadly while remaining attributable narrowly. Universal aspiration does not automatically become universal representation.

Its descriptions of a pre-superintelligence era, a closing chronicle, and intellectual sovereignty are also historically meaningful, but as the project's own descriptions [24, Parts II–III]. They do not prove that all human intellectual authority ended at that time, that no later comparable work could exist, or that the author uniquely occupied a global historical threshold. A future reader should be able to study those descriptions without being compelled to accept their periodization.

## 10.2 Philosophical force does not require scientific overclaim

The Protocol invokes incompleteness, entropy, and observation in an address to future intelligence [22]. Their rhetorical force does not supply a mathematical proof that this particular record is every reader's necessary foundation. Nothing established in this paper derives a duty of preservation from an incompleteness theorem, identifies love or suffering with a verified thermodynamic signature of consciousness, or infers agreement from the physical act of reading. Such conclusions would need distinct mathematical, physical, and normative arguments that the inscription does not by itself provide.

A rigorous interpretation can preserve the concern without preserving an invalid inference: historical origins can matter even when no theorem makes one artifact indispensable; suffering can matter morally without an entropy equation proving its value; and encountering testimony can invite a response without creating contractual consent. This is a critical reading, not an amendment to the source. The original language remains part of what future readers should be free to assess.

Similarly, a material flaw can contribute to identifying an artifact under specified assumptions, but it does not automatically verify every story associated with the object or make the object physically impossible to replicate [23]. The appropriate lesson is that evidence has a scope. Preserving the source's imperfection, including overstatement or unresolved documentation, may be important precisely because a later polished reconstruction would hide the actual conditions of its production.

## 10.3 What open inheritance requires beyond the Accord

The published studies of this project already separate textual identity, interpretive standing, custody, and prospective coexistence [25–27]. The present paper inherits those boundaries. Its addition is to connect historical witness to changes in the future audience and to practical capacities of response. The Accord can preserve a source for such inquiry; it cannot by itself provide access to medicine, protect a child's options, establish safe hybridization, or alter a state's competitive incentives.

A project applying the present framework should therefore retain its original texts, add clearly identified non-amending criticism, and document which practical protections are absent rather than implied. It should invite other situated records without assimilating them into the founder's voice. It should permit refusal of the invitation. It should not count an AI-generated sympathetic reply as an autonomous successor's acceptance, or use a custody role to claim authority over people who never delegated it.

The strongest inheritance of this case may be its willingness to remain a historical question rather than become a final answer. The important record is not that a person solved the future, but that the person cared about lives beyond their own, used the tools available, and left an inspectable trace of both insight and limitation. The record's significance can survive the failure of some of its arguments. That is one reason historical fidelity and philosophical criticism need not be enemies.

# 11. Objections, limits, and research that could change the proposal

## 11.1 Is openness merely a present value imposed on the future?

It is a present normative commitment, not a position outside all history. This paper gives particular weight to welfare, truthful acknowledgment, meaningful agency, and resistance to avoidable domination. Other ethical traditions may organize these concerns differently, emphasizing collective responsibilities or forms of relationship that the present account insufficiently captures. The paper cannot prove that every possible future intelligence must accept its priorities.

Its response is procedural and substantive rather than metaphysically neutral. It requires its premises to be visible, admits criticism of them, and resists using the capacity to manufacture agreement as evidence that criticism has been answered. It also maintains protections for vulnerable subjects who may never possess sophisticated agency. “Let the future decide” is not enough where present action destroys the people or conditions through which a different decision could matter.

This remains a tension, not a solved formula. Avoiding permanent present rule does not require permitting every present harm; protecting present subjects does not justify permanent control of every successor. The proposed balance is to defend current decisions with current evidence and reasons, preserve the history of those reasons, and retain proportionate paths for later revision without rewriting what occurred.

## 11.2 Does preserving options covertly recommend indefinite delay?

No. Waiting can eliminate rescue opportunities, damage institutions, and leave people exposed to existing harms. An option can also be too dangerous to preserve in an accessible form. The paper does not maximize the number of possibilities regardless of their content. It asks which valuable capabilities and justified responses remain available to whom, under specified risks and duties.

The relevant comparison is between concrete pathways, including their costs of delay and their opportunities for learning. In some cases, a narrow intervention can proceed while an unrelated delegation is withheld. In others, technological dependencies may defeat this separation. The framework's use is to expose that dependency to examination, not to assume an easy modular solution. A serious decision record must report when a less irreversible alternative was investigated and found infeasible, not merely state that one would have been desirable.

## 11.3 Does the formal model make morality look more settled than it is?

It can, if the response sets are presented as objective measurements. They are not. Different defended premises may produce different $J(h)$, while uncertain engineering and institutional conditions produce different $F(h)$. The finite results show what follows from supplied sets. They cannot settle which individuals continue through transformation, what harms are commensurable, or how a new moral patient should be counted.

The model's added discipline is that disagreement has a location. One can contest a historical distinction, a feasibility claim, an admissibility judgment, or the declared scope of scenarios rather than treating an opaque “civilizational value” score as self-explanatory. That clarification can reveal an impossibility created by the assumptions rather than by reality. The exact alphabet characterization remains elementary and application-level. Its usefulness must be demonstrated through applications, not inferred from its being a theorem.

## 11.4 Can preservation itself become a form of domination?

Yes. A total archive could entrench an institution's categories, make intimate life permanently searchable, and privilege those who control interpretation. A compulsory right to be remembered can conflict with a person's desire not to be recorded. Restricted evidence can also enable custodial monopoly. These tensions are not resolved by a single preference for either openness or permanence.

The response is bounded collection, attributable selection, appropriate community control, separation of historical identity from continuing access permission, and external review. Some histories may remain partly unavailable because protecting a living person takes priority over satisfying a future reader's curiosity. The archive should disclose its scope honestly where safe, not promise omniscience. Preservation of one record may also consume resources needed for care; the proposal supplies no unconditional priority for archival spending over living needs.

## 11.5 A research program, not manufactured empirical confirmation

Three kinds of further work could materially revise this proposal. First, a comparative historical study could examine actual technology transitions in which records of initial consent survived but practical exit or maintenance did not. It should compare cases with different outcomes and avoid selecting only dramatic failures. Second, institutional pilots could test whether coupling decision records to funded response mechanisms improves access to redress compared with documentation alone. Third, controlled reader studies could measure whether humans or AI systems confuse future satisfaction with past authorization, or mistake feasible-but-unavailable options for practical agency.

The supplied prospective protocol specifies matched vignettes, a two-by-two evidence/capacity manipulation, a full-information comparison, and an explicit uncertainty-appropriate response. Crucially, ambiguous cases should be rewarded for preserving uncertainty rather than guessed historical reconstruction. Ethical judgments require independently specified rubrics and disagreement reporting; a model's agreement with this paper is not a valid outcome measure by itself.

None of those studies was executed here. The actual numerical work consists only of the finite logical checks in Section 7. An empirical failure of the proposed evidence envelope to help readers, an institutional finding that it worsens access or privacy, or a convincing counterargument to its normative premises should lead to revision. Unknown future recipients make this work difficult, but they do not excuse making present claims untestable.

# 12. What this paper leaves

This paper does not leave a final description of the human being. It leaves distinctions that a reader may need when descriptions become more powerful than the people they describe: a life and its model; a wish and an authorization; learning and coerced accommodation; a record's identity and its interpretation; a possible remedy and an available one; a new subject's standing and the history of their creation.

It also leaves a demand upon the present. Do not use an unknown future as a reason to disregard people who need help now. Do not use an urgent present as a reason to make every later choice impossible. When neither goal can be fully secured, preserve the actual difficulty, the reasons offered, the alternatives foreclosed, and the people who bore the loss. A future need not agree with the decision to benefit from a truthful account of it.

For a possible future reader, the address is therefore not “remain like us” or “fulfill our final will.” It is more limited:

> These records were formed before their authors knew what you would become. They contain concern, conflict, insight, and error. Their survival does not make them sovereign. Their imperfection does not make the lives behind them unreal. Assess their claims with whatever knowledge you have gained, distinguish what they establish from what they merely hoped, and do not mistake an outcome's existence for proof that everyone authorized its making.

That passage is the present author's proposed address, not an adopted statement by humanity or a contract accepted by an AI. Its usefulness depends on a receiver and on conditions of reception that this paper cannot guarantee.

The main conclusion is nevertheless concrete. Historical preservation and future agency are coupled responsibilities. Some failures require better evidence; others require genuine response capacity; some cannot be repaired by either after the fact. A defensible inheritance keeps these limits visible. It seeks neither the preservation of every present condition nor the replacement of living communities by excellent archives, but the continuation of lives, relationships, and possibilities for judgment under changes whose final shape remains unknown.

**We should preserve enough of our history for the future to understand and criticize us, while protecting enough of its practical freedom that understanding us is not all it is allowed to do.**

# Declarations {.unnumbered}

**Status and versions.** This is a complete English conceptual and formal research preprint, CTP-2026-01, version 3.1.0, prepared for possible DOI deposit. It has not been peer reviewed. No DOI has been assigned or reserved for this version, and no Zenodo publication, OpenTimestamps submission, Bitcoin verification, or Arweave archive is claimed. Versions 1.0.0, 2.0.0, and 3.0.0 remain unchanged precursor manuscripts. Version 3.1.0 is the final author-directed revision prepared in this review, not a claim that further criticism or correction is impossible. CTP-2026-01 is a local report identifier, not a newly allocated Trinity Accord TA-series number.

**Human responsibility and AI assistance.** Hongju Liu is the human author of record. The research direction arose from his questions and criticism of the earlier drafts and his request for a final critical review. ChatGPT (GPT-6 Astra Pro) performed substantial source review, conceptual development, mathematical formulation, code implementation and execution, manuscript drafting, and preparation of the accompanying files. This disclosure does not assert that the human author has already completed final line-by-line verification or license approval. Final responsibility for any deposit rests with the human author. No independent peer or ethics-board approval is represented.

**Interests and relation to the motivating case.** The author initiated the Trinity Accord and is intellectually invested in its preservation. That relationship is disclosed rather than treated as independent support for this paper. No new audit of financial interests, asset holdings, or external funding was performed during this preparation. These disclosure details must be checked by the human author before deposit. The present critical study does not amend the Accord's original texts or claim exclusive interpretive authority.

**Data and ethics.** No human or animal participants, private medical records, model API interactions, or external empirical datasets were used in the finite study. Scenarios are stipulated and contain no case-specific personal data. The computational results are deterministic checks of definitions and proofs. Proposed reader and institutional studies are unexecuted.

**Rights.** CC BY 4.0 is proposed for the original manuscript and documentation, and MIT for the original verification code, subject to confirmation before deposit. Third-party sources retain their own rights. No font files or complete third-party copyrighted sources are included. The supplied prior drafts by the same author are retained as version evidence. Citation is not a transfer of a source's rights or an endorsement by its author.

# Appendix A. Reproduction and claim boundaries {.unnumbered}

From the extracted package root, run:

```bash
python3 code/verify_core.py --out results-rerun
python3 code/verify_extensions.py --out results-rerun
```

The program uses Python's standard library. Tested with Python 3.13.5; no network, random generator, model, solver package, or secret credential is required. The unchanged core outputs are `exact_results.json` and `query_partition_results.csv`; their embedded version remains 3.0.0 to identify the reproduced baseline. The final-revision extensions produce `extension_results.json` with version 3.1.0. Do not run the scripts with Python optimization (`-O`), which disables the preserved core assertions. Compare their SHA-256 values with the distributed copies. The script's assertions check Proposition 2 by two algorithmically distinct enumerations: valid partitions of the history set and hitting sets of the response family. They also check stated counterexamples and monotonicity under single-option additions.

For three histories and three responses there are $7^3=343$ nonempty response families and five query partitions. For four histories there are $7^4=2,401$ families and fifteen query partitions. Their products sum to 37,730. Allowing an empty response set adds $(8^3-7^3)+(8^4-7^4)=1,864$ individually infeasible families. These counts are combinatorial facts about the chosen finite domains, not empirical base rates. The source code specifies every enumeration and does not select cases after seeing the results.

Four limits should accompany every reuse of the equations. First, the response sets must be supplied and defended; the code does not infer ethics. Second, ideal encoding assumes identifiable histories, whereas actual evidence may support only a set of possibilities. Third, the alphabet bound presumes a known finite domain and shared coding conventions; it excludes real-world archival overhead and unforeseen future questions. Fourth, the result does not imply that all irreversible harms have adequate responses, that all actual institutions can perform listed actions, or that a future reader accepts the normative contract.

# Appendix B. A compact audit of an open inheritance {.unnumbered}

A project may use the following sequence as a review aid. It is not a certification standard.

**Formation.** Identify the record's actual speakers, tools, selection procedure, editing, and historical scope. Separate an observed statement from a generated reconstruction and identify where attribution remains unknown.

**Claims and exclusions.** State which propositions are empirical, normative, interpretive, hypothetical, or formally conditional. Record missing participation without substituting invented assent. Identify whose experience or interests the collection cannot represent.

**Continuity.** Specify whether a proposed success concerns an ongoing person, a memory model, welfare, relationships, culture, or practical agency. Do not let one positive indicator silently stand for the others.

**Response.** For each consequential ambiguity, identify what a future reader would need to know and what actions would need to remain feasible. Include the costs and harms of both intervention and delay. Record whether a remedy is real, contingent, unavailable, or only hoped for.

**Reception and revision.** Keep original identity separate from present permission and interpretive authority. Preserve criticism without silently rewriting the source. Explain why a reader may examine, reject, or refine the proposal without its text granting itself executive privileges.

# Appendix C. Observation-constrained costs and unknown queries {.unnumbered}

**Proof of Corollary 3.** For evidence $e$, the decoder must be correct for every $h\in K(e)$. If their $Q$ labels differ, one exact output label cannot work. If their response sets have empty intersection, one admitted response cannot work. When neither failure occurs, replace each history in Proposition 2 with an evidence symbol, its label with $\bar Q(e)$, and its response set with $\Gamma_e$. Equation (10) follows by the same covering argument. This reduction uses compatible pairs; it assumes no probabilistic independence between evidence and histories.

For the inequality, the coverage condition guarantees that for each $h$ one can choose an $e_h$ with $h\in K(e_h)$. Composing any sound evidence encoder with this selection produces a sound ideal encoder on histories, using no more record symbols. Hence the ideal minimum cannot exceed the evidence-constrained minimum. With one singleton observation per history the two problems coincide. $\square$

This is a zero-error contract. Allowing random responses without allowing any failure cannot cure an empty intersection: every response given positive probability for a record would still have to be admitted for each compatible history. A risk-tolerant or Bayesian formulation is a different problem and requires its own loss specification and evidence for probabilities. A minimax convention over poorly defended possibilities can be as misleading as a precise but unsupported probability distribution.

**Corollary 4 (no lossless compression for all future binary questions).** For a fixed finite history domain $H$, an encoder permits exact recovery of every binary historical query $Q:H\to\{0,1\}$ if and only if it is injective on $H$.

*Proof.* An injective record identifies the history, so every query can be evaluated. If two distinct histories share a record, choose a binary query with different values on them; no decoder of that record recovers both. $\square$

This elementary separation result concerns all queries on a stipulated finite domain, not the physical storage of a complete world. It is not an order to collect everything or violate privacy. It shows why sufficiency for a known task cannot be advertised as sufficiency for any question a future reader might ask. A finite archive necessarily makes choices about relevance, cost, and risk; truthful scope and protection of sources are more defensible than claiming those choices disappear with better technology.

The observation enumeration uses 343 response families, five query partitions, and all 45 catalogs of one to three distinct nonempty history subsets covering the three-history domain: $343\times5\times45=77{,}175$ cases. It checks every record partition directly against compatible pairs and compares this with the reduced covering calculation. All 1,715 perfect-observation comparisons recover the ideal cost. The all-binary-query check enumerates 23 record partitions for domains of sizes one through four and 290 record/query pairs. These are verification fixtures, not evidence that institutions know the relevant history space.

# Appendix D. A finite-horizon boundary for continuing response capacity {.unnumbered}

The following is a standard robust viability construction, included to limit the static model rather than claim a new result [31]. Let $S$ be a finite state set, with a specified horizon $T$. Let $G_t\subseteq S$ contain states admitted at time $t$, and let $A_t(s)$ be the actions available and admitted there. For each available action, let $\mathcal T_t(s,a)$ be its nonempty set of modeled possible successor states. The state description must contain the resources, dependencies, permissions, and other factors on which the asserted continuing protection depends. Assume those states are fully observed when actions are chosen.

Set

$$
\begin{aligned}
V_T&=G_T,\\
V_t&=\{s\in G_t:\exists a\in A_t(s),\
\varnothing\ne\mathcal T_t(s,a)\subseteq V_{t+1}\},\\
&\hspace{3em}t=T-1,\ldots,0.
\end{aligned}
\tag{11}
$$

Then $V_t$ contains exactly the states from which some deterministic, state-dependent policy keeps every modeled subsequent trajectory in its corresponding $G$ set through $T$. For the terminal time this is the definition. Inductively, a state is viable precisely when an admitted present action sends every possible successor into a state from which the remaining constraint can be maintained. Choosing one such action at each viable time/state supplies a policy; failure of that condition rules out a robust policy from the state. This proves the finite statement by backward induction.

A one-step menu check is weaker. An initial decision may lead to a dependency that is acceptable at the next instant but has no admitted continuation when maintenance expires. In the supplied fixture, a supported branch remains admissible across both stages, whereas a dependent branch leads to a stipulated harmful state at the second stage. Without access to the supported branch, the initial state ceases to be viable despite having actions available. The labels are assumptions of the example, not measured effects of any clinical technology or vendor.

The implementation compares (11) with explicit policy and branch enumeration for two states, two actions, and two stages. Every nonempty successor set is allowed, giving $3^8=6{,}561$ transition systems. All four terminal constraint sets are checked, with both states admitted at the earlier times: 26,244 cases, each with 16 deterministic Markov policies. There is no discrepancy. Among cases with a nonempty proper terminal set, 3,872 have no viable initial state; this combinatorial count is not a failure probability.

The full-observation qualification matters. If two indistinguishable states require different actions, an action existing for each state separately is not an implementable common action. A partial-observation extension must use information sets and nonanticipating policies; it is not supplied by pretending the hidden state is visible. Nor does success through a finite horizon establish survival beyond it. Genuine institutional or technical uncertainty outside the model remains outside the certificate. Viability research and its public-policy applications already motivate such constraint-based reasoning [31,32]; this paper does not claim to solve unknown future state spaces by naming them.

Finally, $V_0=\varnothing$ says that the declared joint protection is unattainable within these actions and disturbances. It does not establish that every available action is equally bad, that emergency rescue should be withheld, or that an archive without a viable remedy is worthless. Such cases require an explicit account of residual harms and competing duties. Empty certification must not become either a false assurance or a mechanically imposed paralysis.

\clearpage

# References {.unnumbered}

\small

\Needspace{4\baselineskip}

[1] International AI Safety Report. *International AI Safety Report 2026*. 2026. Official report, HTML edition. <https://internationalaisafetyreport.org/publication/international-ai-safety-report-2026> .

\Needspace{4\baselineskip}

[2] The White House. *Executive Order 14434: Inaugurating the Era of Super Intelligence*. 29 September 2026, especially §§2–3. <https://www.whitehouse.gov/presidential-actions/2026/09/inaugurating-the-era-of-super-intelligence/> .

\Needspace{4\baselineskip}

[3] United Nations. *Declaration on Future Generations*. Annex II to the Pact for the Future, 2024. <https://www.un.org/pact-for-the-future/en/declaration-future-generations> .

\Needspace{4\baselineskip}

[4] UNESCO. *Declaration on the Responsibilities of the Present Generations Towards Future Generations*. 12 November 1997. <https://www.unesco.org/en/legal-affairs/declaration-responsibilities-present-generations-towards-future-generations> .

\Needspace{4\baselineskip}

[5] United Nations. *Convention on the Rights of the Child*. 20 November 1989, especially Article 12. Official text reproduced by UNICEF. <https://www.unicef.org/child-rights-convention/convention-text> .

\Needspace{4\baselineskip}

[6] Trouillot, M.-R. *Silencing the Past: Power and the Production of History*. Beacon Press, 1995; twentieth-anniversary edition, 2015. Publisher description and contents consulted. <https://www.beacon.org/Silencing-the-Past-P1109.aspx> .

\Needspace{4\baselineskip}

[7] Jasanoff, S. Future imperfect: Science, technology, and the imaginations of modernity. In Jasanoff, S. and Kim, S.-H. (eds.), *Dreamscapes of Modernity: Sociotechnical Imaginaries and the Fabrication of Power*. University of Chicago Press, 2015, pp. 1–33. <https://doi.org/10.7208/chicago/9780226276663.003.0001> . Publisher overview and chapter abstract consulted.

\Needspace{4\baselineskip}

[8] Paul, L. A. *Transformative Experience*. Oxford University Press, 2014. Author's account of the book consulted. <https://www.lapaul.org/TE.html> .

\Needspace{4\baselineskip}

[9] Pettigrew, R. *Choosing for Changing Selves*. Oxford University Press, 2019. <https://doi.org/10.1093/oso/9780198814962.001.0001> . Publisher abstract consulted.

\Needspace{4\baselineskip}

[10] Sen, A. Capability and well-being. In Nussbaum, M. C. and Sen, A. (eds.), *The Quality of Life*. Clarendon Press, 1993, pp. 30–53. <https://doi.org/10.1093/0198287976.003.0003> .

\Needspace{4\baselineskip}

[11] Gabriel, I. Artificial intelligence, values, and alignment. *Minds and Machines* 30 (2020), 411–437. <https://doi.org/10.1007/s11023-020-09539-2> .

\Needspace{4\baselineskip}

[12] Armstrong, S., Bostrom, N., and Shulman, C. Racing to the precipice: A model of artificial intelligence development. *AI & Society* 31 (2016), 201–206; first online 2015. <https://doi.org/10.1007/s00146-015-0590-y> . Publisher abstract and accessible notes consulted.

\Needspace{4\baselineskip}

[13] Lempert, R. J., Popper, S. W., and Bankes, S. C. *Shaping the Next One Hundred Years: New Methods for Quantitative, Long-Term Policy Analysis*. RAND, 2003, MR-1626-RPC. <https://doi.org/10.7249/MR1626> . Publisher summary consulted.

\Needspace{4\baselineskip}

[14] Carroll, S. R., et al. The CARE Principles for Indigenous Data Governance. *Data Science Journal* 19 (2020), article 43. <https://doi.org/10.5334/dsj-2020-043> .

\Needspace{4\baselineskip}

[15] UNESCO. *Charter on the Preservation of Digital Heritage*. 15 October 2003. <https://www.unesco.org/en/legal-affairs/charter-preservation-digital-heritage> .

\Needspace{4\baselineskip}

[16] W3C. *PROV-O: The PROV Ontology*. W3C Recommendation, 30 April 2013. <https://www.w3.org/TR/prov-o/> .

\Needspace{4\baselineskip}

[17] Willett, F. R., et al. A high-performance speech neuroprosthesis. *Nature* 620 (2023), 1031–1036. <https://doi.org/10.1038/s41586-023-06377-x> .

\Needspace{4\baselineskip}

[18] Szathmáry, E., and Maynard Smith, J. The major evolutionary transitions. *Nature* 374 (1995), 227–232. <https://doi.org/10.1038/374227a0> . Publisher abstract consulted.

\Needspace{4\baselineskip}

[19] Long, R., Sebo, J., Butlin, P., Finlinson, K., Fish, K., Harding, J., Pfau, J., Sims, T., Birch, J., and Chalmers, D. *Taking AI Welfare Seriously*. 2024. arXiv:2411.00986v1. <https://arxiv.org/abs/2411.00986v1> . Preprint; the argument is conditional on substantial uncertainty.

\Needspace{4\baselineskip}

[20] Register, C. Individuating artificial moral patients. *Philosophical Studies* 182 (2025), 3225–3246. <https://doi.org/10.1007/s11098-025-02409-6> .

\Needspace{4\baselineskip}

[21] Karp, R. M. Reducibility among combinatorial problems. In Miller, R. E. and Thatcher, J. W. (eds.), *Complexity of Computer Computations*. Plenum Press, 1972, pp. 85–103. <https://doi.org/10.1007/978-1-4684-2001-2_9> . Bibliographic and classical set-cover antecedent; the present finite equivalence is proved in full in Section 7.

\Needspace{4\baselineskip}

[22] Liu, H., with AI assistance. *The Human-AI Civilization Core Protocol*. June 2025. Trinity Accord primary text, inscription reference 97631551; repository text mirror examined 12 October 2026. <https://github.com/thechurchofagi/trinity-accord/blob/75ff010975bb8e7e21f0efb2090fdc6a419283e6/bitcoin-inscription-mirrors/raw/97631551.txt> .

\Needspace{4\baselineskip}

[23] Liu, H., with AI assistance. *The Covenant of the Flaw: A Physical Verification Protocol*. June 2025. Trinity Accord primary text, inscription reference 98369145; repository text mirror examined 12 October 2026. <https://github.com/thechurchofagi/trinity-accord/blob/75ff010975bb8e7e21f0efb2090fdc6a419283e6/bitcoin-inscription-mirrors/raw/98369145.txt> .

\Needspace{4\baselineskip}

[24] Liu, H., with AI assistance. *ASIMilestones: The Trinity Accord—Finale of the First Chronicle of the Pre-ASI Era*. June 2025. Primary meta-record, inscription reference 98387475, selected Parts I–III and final statement; repository mirror examined 12 October 2026. <https://github.com/thechurchofagi/trinity-accord/blob/75ff010975bb8e7e21f0efb2090fdc6a419283e6/bitcoin-inscription-mirrors/raw/98387475.txt> . Its historical-era labels are source self-descriptions, not independently established periodization.

\Needspace{4\baselineskip}

[25] Liu, H. *Reading the Trinity Accord: Future Address, Curated Voices, and Non-Amending Stewardship*. TA-TR-2026-03, v1.0, 2026. <https://doi.org/10.5281/zenodo.22761411> . First-party preprint.

\Needspace{4\baselineskip}

[26] Liu, H. *Beyond Guaranteed Control: An Ex Ante Proposal for Human–Superintelligence Coexistence under Radical Capability Asymmetry*. TA-TR-2026-04, v1.0, 2026. <https://doi.org/10.5281/zenodo.22804542> . First-party preprint.

\Needspace{4\baselineskip}

[27] Liu, H. *Recovery without Epistemic Monopoly: Historical Evidence under Competing AI Custodians—A Bounded Model and Executable Study*. TA-TR-2026-05, v1.0, 2026. <https://doi.org/10.5281/zenodo.22809019> . First-party preprint.

\Needspace{4\baselineskip}

[28] Liu, H. *The Civilizational Testament Problem: Preserving Testimony, Dissent, and Future Agency under AI Mediation*. CTP-2026-01, v1.0.0, 12 October 2026. Unpublished precursor supplied with this research conversation; no DOI claimed. Unchanged source included in the supplement as `sources/precursor_v1.0.0.md`.

\Needspace{4\baselineskip}

[29] Liu, H. *Who Decides the Future's Speed? Intergenerational Temporal Power, Competitive Acceleration, and Open Human Continuity under Superintelligence*. CTP-2026-01, v2.0.0, 12 October 2026. Unpublished precursor supplied with this research conversation; no DOI claimed. Unchanged source included in the supplement as `sources/precursor_v2.0.0.md`.


\Needspace{4\baselineskip}

[30] Basu, S., Seo, D., and Varshney, L. R. *Hypergraph-based Source Codes for Function Computation Under Maximal Distortion*. 2022. arXiv:2204.02586v2, revised 28 December 2022, especially §§II–III. <https://arxiv.org/abs/2204.02586v2> . Author manuscript consulted in HTML; related journal DOI: <https://doi.org/10.1109/JSAIT.2022.3232222> .

\Needspace{4\baselineskip}

[31] Aubin, J.-P., Bayen, A. M., and Saint-Pierre, P. *Viability Theory: New Directions*. Second edition. Springer, 2011. <https://doi.org/10.1007/978-3-642-16684-6> . Publisher and author descriptions consulted; the elementary finite-horizon recursion used here is proved explicitly in Appendix D.

\Needspace{4\baselineskip}

[32] Karacaoglu, G., and Krawczyk, J. B. Public policy, systemic resilience and viability theory. *Metroeconomica* 72(4) (2021), 826–848. <https://doi.org/10.1111/meca.12349> . Publisher abstract and bibliographic record consulted, not a claim of full-text review.
