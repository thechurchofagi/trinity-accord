"""Handwritten arguments. The build must match exactly the 128 R153 inherited rules."""
ENTRIES = {}

def add(rule, argument, boundary, status='MANUAL_ARGUMENT_REVIEWED'):
    assert rule not in ENTRIES
    ENTRIES[rule] = dict(argument=argument, indispensable_boundary=boundary,
                         disposition=status, machine_proof=False)

add('a05',
    'U1 supplies experience for every actual token in its domain. Instantiate it at the same actual token supplied by SELF_WITNESS, which lacks the stipulated conceptual-self organization. This gives an experienced token without that organization, refuting its universal necessity. It does not quantify over unrepresented forms of selfhood.',
    'The witness must be actual and in the U1 domain; absence of a verbal report alone is not absence of conceptual self, and neither is absence of every minimal bodily perspective.')
add('a06',
    'Read U0 as a package whose components are the already separately justified C1 consequences P3, P6, U1, U2 and U3. Conjunction introduction constructs the package; projecting a component recovers its original hypotheses. No new physical or experiential fact is established by renaming this conjunction.',
    'Dependencies and the same-domain witness used for U3 survive compression. This is a dependency audit, not a proof of C1.', 'METADATA_AUDIT_REVIEWED')
add('a07',
    'Let P be the stipulated same-domain actual counterexample to the proposed gate G. U1 gives E(P), whereas necessity of G would give E(P) implies G(P). Together with not G(P) this is a contradiction, so that necessity claim fails under U1 and this witness.',
    'The counterexample is a premise. A merely imagined or out-of-domain system cannot discharge it; sufficient conditions and conditions for a selected experiential character are different claims.')
for rid, detail, boundary in [
    ('a08','An alleged hidden difference is stipulated to leave the complete present organization isomorphic. Compose that isomorphism with the two tokenwise C1 isomorphisms to obtain experiential isomorphism.','If the hidden variable changes constitutive organization, COMPLETE_EQ is false; it cannot simply be declared irrelevant.'),
    ('a09','The before/after probe comparison has equal complete present structures by the probe-only premise. Transport the equality through C1-W. Merely changing the available evidence does not change that comparison.','A physical probe can perturb the process; only probes satisfying the equality premise are covered.'),
    ('a10','The pair agrees in complete organization over the declared present interval and differs only in stipulated future continuations. C1-W maps that present equality to equal present experiential type.','Anticipation, stored predictions and dispositions already present must be included in the present organization. No claim about later experiential equality follows.'),
    ('a11','For the stipulated historical pair, all constitutive present relations, including retained traces and dispositions in the chosen complete signature, are equal. C1-W therefore yields equal experiential type despite unequal external histories.','This is conditional on completeness; an omitted memory trace defeats the premise. Equal type does not identify token or ancestry.'),
    ('a12','The reward-only comparison changes an external annotation while preserving the complete token organization. Apply C1-W to that equality. The external annotation therefore cannot independently determine experiential type in this comparison.','An installed reward signal or changed learning/control mechanism need not preserve the organization; valence is not identified with arbitrary external reward.')]:
    add(rid,detail,boundary)
add('a13',
    'The historical witness has equal experiential types by GHOST_EQ and distinct historical/lineage facts by HISTORY_DIFF. If that lineage fact factored through experiential type, equal input types would force equal lineage values, contradiction. P6 preserves the separate token relation.',
    'This denies identification of token lineage by type; it does not deny that a fixed token has an actual history or that represented history can affect its current type.')
add('a15',
    'Instantiate C1-W at the two actual macro tokens in MACRO_EQ, with the same macro signature. Their given macro-organization isomorphism transports through the tokenwise isomorphisms to an experiential macro-type isomorphism.',
    'A shared analyst quotient is not itself a pair of actual complete macro tokens. Actual macro realization and completeness must be separately supplied.')
add('a16',
    'C1-OI states equivalence of structural and experiential isomorphism in one complete signature. For the actual lower-level pair, an experiential isomorphism would imply a structural one, contradicting MICRO_NONISO. Thus their complete experiential types differ.',
    'The comparison level must be the one at which nonisomorphism is established; it cannot be substituted for an independently compared macro pair.')
add('a24',
    'The physical-transformation premise supplies two actual complete organizations that are not isomorphic. The reverse implication of C1-OI rules out an experiential isomorphism for that pair.',
    'A coordinate relabeling or difference in an incomplete model is insufficient. Complete-type difference supplies no scalar ordering of richness, pain or intelligence.')
add('a25',
    'At fixed u, the linear part of T has rank 1+rank([[0,alpha],[beta,0]]) over F2: its rows become one s row and the independent a/b rows. Thus the four image sizes are 2,4,4,8. With fixed s-boundary forcing, pair differences evolve under M=[[0,alpha],[beta,0]]. Its ranks at positive powers are 0; 1 then 0; 1 then 0; and 2 forever, yielding retention counts 1; 2 then 1; 2 then 1; 4. Conjugate finite maps have equal image cardinality.',
    'The two one-link settings have the same image cardinality and are not distinguished by this invariant. Named-port distinctions would require a separate port-preserving argument.')
add('a26',
    'The s update is s_next=s XOR u and y=s for every alpha,beta. Induction gives s_t=s_0 XOR u_0 XOR ... XOR u_(t-1). Clamps on a,b cannot affect this update; the same prescribed clamp on s has the same effect in every model. Hence all declared s-subprocess responses coincide.',
    'The buffered no-feedback port, same clock/input/clamp family and same boundary are essential; this is not equality of the full three-coordinate mechanisms.')
add('a27',
    'Choose two toy settings whose fixed-input transition images have different cardinalities (2 versus 4, 2 versus 8, or 4 versus 8). A whole-structure isomorphism would conjugate the named transition and preserve its image size, contradiction. ACTUAL_COMPLETE_TOY transfers this distinction to the actual complete organizations; C1-OI then separates their complete experiential types.',
    'The image-size argument does not separate (1,0) from (0,1). The corrected conclusion quantifies only over pairs separated by this invariant. Actual complete realization remains an independent premise.', 'MANUAL_REVIEW_WITH_STATEMENT_REPAIR')
add('a28',
    'The s-subprocess calculation supplies an isomorphism of the same declared sublevel structures. Under ACTUAL_COMPLETE_TOY instantiated at that sublevel, these are actual complete subprocess organizations. Apply C1-W to obtain equal sublevel experiential type.',
    'Whole-token actual realization does not alone certify a complete actual subprocess. The bridge must cover this sublevel and its actual boundary.')
add('a29',
    'The forward operational package is the conjunction of the constitutive axiom, a declared forward prediction rule and a measurement/bridge contract. Constructing that conjunction is legitimate assumption packaging; the latter two components are not inferred from C1.',
    'Prediction and measurement adequacy are supplied hypotheses with their own possible failures.', 'ASSUMPTION_PACKAGE_REVIEWED')
add('a30',
    'Add the independently supplied reflection/reverse-identification component to the forward package. Conjunction introduction forms the two-way operational package without establishing the new reflection component.',
    'A forward implication alone does not justify its converse. All components must apply on the same frozen scope.', 'ASSUMPTION_PACKAGE_REVIEWED')
add('a31',
    'On the frozen scope, the forward package predicts the specified observable relation from the specified structural relation. The measurement premise warrants the observed opposite relation. This contradicts the forward package at that instance by modus tollens.',
    'The falsified object is the joint operational package. Locating failure in C1 rather than the bridge, scope or measurement requires independent grounds.')
add('a32',
    'Use the declared reverse/reflection implication of the two-way package at the frozen comparison. Its antecedent is measured to hold and its structural consequent to fail under the stated adequacy contract, contradicting that implication.',
    'This test does not refute a forward-only package; reverse identification must actually have been committed to before the test.')
add('a33',
    'U1 applies separately to the actual whole and every stipulated persisting actual part. P3 distinguishes the whole experiential organization from the relevant product when its structural nonproduct premise holds. Nothing in either statement removes the already actual parts, so these tokens coexist.',
    'Actual persistence of each part is required. Coexistence does not select a unique subject or give an additive measure of experience.')
add('b01',
    'Evaluate a well-typed finite expression by induction on its syntax tree. Leaves have supplied interpretations. At each internal node, the primitive interpretation accepts the interpreted child types and supplies the parent value on its admitted domain. Induction therefore evaluates every declared E_j. EXPRESSIBLE identifies that value with O_j using the same fixed bridge across instances.',
    'The theorem is conditional on expressibility, defined primitives, optimization existence/tie conventions and BAC. It neither proves all theories expressible nor constructs a computable implementation of arbitrary primitives.')
add('b02',
    'Choose the actual same-domain witness in TARGET_DOMAIN that lacks the proposed necessary organization. U1 supplies its experience; the rival necessity implication supplies the contradictory organization claim. This refutes that necessity implication under the combined premises.',
    'The target may instead concern access, selected content or a restricted biological domain. Those quantifiers must not be silently replaced by universal basal existence.')
add('b03',
    'The overlap witness supplies simultaneously actual persisting tokens. U1 gives experience to each; P3 conditionally distinguishes the whole from a product. A rival exclusion rule denying experience to one of those same actual tokens conflicts with U1 at that token.',
    'A rival theory may reject the actual-token premise or use different token individuation; this is an explicit premise conflict, not unconditional experimental falsification.')

add('b_IIT',
    'Given a fixed IIT bridge, the finite view can supply the named system state and intervention-defined repertoires. Supplied IIT conventions then compute intrinsic differences, partitions, system/distinction/relation quantities and their optimizations. This is an instance of B:REP once those expressions and domains are supplied; representation of such quantities does not derive IIT maximal exclusion.',
    'IIT chart, priors, metrics, partition family, maxima/ties and source edition are imported commitments. A complete executable instantiation and validated phenomenal interpretation are not supplied by this schematic edge.', 'CONDITIONAL_REPRESENTATION_SCHEMA_OPEN')
add('b_RPT',
    'The admitted graph view gives directed paths and SCCs; b04/b05 establish the graph-level recurrence primitive. A fixed sensory-content, stabilization and timing bridge can interpret that primitive for an RPT application. Structural representability follows only for the supplied operational target.',
    'Generic feedback is not the entire RPT mechanism or proof of its phenomenal necessity. Biological content/timing correspondence remains a separate obligation.', 'CONDITIONAL_REPRESENTATION_SCHEMA_OPEN')
add('b_GNWT',
    'With fixed content intervention C_c, target modules K_j, delay tau, distances and baseline c0, DoResp and Diff compute each access effect d_j(P(X_j|do(c)),P(X_j|do(c0))). Fixed aggregation/readout rules then yield breadth, coverage, persistence and workspace descriptors. Composition supplies an operational representation.',
    'The module partition, content meaning, thresholds, anatomy and timing are supplied and must be validated. An arbitrary broad broadcast is not automatically the full GNWT claim.', 'CONDITIONAL_REPRESENTATION_SCHEMA_OPEN')
add('b_HOT',
    'A declared hierarchy and fixed tracking/aboutness bridge identify the first-order target and the higher-order state. Admitted response comparisons represent their causal tracking relations. Once semantic roles are independently supplied, B:REP evaluates the resulting higher-order descriptor.',
    'Causal covariance alone does not establish semantic aboutness or a higher-order experiential condition. Those commitments remain explicit external premises.', 'CONDITIONAL_REPRESENTATION_SCHEMA_OPEN')
add('b_AST',
    'Supply a fixed attention variable, an internal model of attention and its use in control. Restriction and response operations identify the model and quantify changes in future attention under its interventions. Their composition represents the stipulated attention-schema operation.',
    'A simplified internal predictor is not by itself an attention schema with the requisite semantic and control roles. The correspondence must be fixed rather than refitted per outcome.', 'CONDITIONAL_REPRESENTATION_SCHEMA_OPEN')
add('b_PP_AI',
    'Given the agent/environment partition, latent variables, generative p, variational q, policy class and preferences, the admitted finite expressions can evaluate prediction errors and specified free-energy/policy objectives. Optimization is representable only on supplied feasible domains with existence/tie rules.',
    'These model and preference choices are imported. Representability does not derive phenomenality, rule out nonpredictive alternatives, or license per-instance target refits.', 'CONDITIONAL_REPRESENTATION_SCHEMA_OPEN')
add('b_DIT',
    'A supplied biological bridge identifies apical, basal, somatic and thalamic variables and their interventions. Joint response differences can express the stipulated dendritic interaction and modulation operations; composition yields a finite operational descriptor.',
    'Generic nonlinearity is not full dendritic integration theory. Compartment identity, bottom-up/top-down roles, modulation and biological-state claims remain source-specific obligations.', 'CONDITIONAL_REPRESENTATION_SCHEMA_OPEN')
add('b_MTOC',
    'Fix an earlier-state intervention and an independently specified later trace target. A nonzero response difference represents causal retention. With supplied memory-type/content conventions this expresses the corresponding operational memory descriptor.',
    'Retention is not every memory construct. Universal memory necessity conflicts with U1 only with an actual same-domain absence witness; necessity for particular remembered contents is a different statement.', 'CONDITIONAL_REPRESENTATION_SCHEMA_OPEN')
add('b_TTC',
    'Supply the relevant windows, grains and operational definitions of nestedness, alignment, expansion and globalization. Restrictions, time-indexed responses and fixed composition rules represent these descriptors within the finite view.',
    'TTC distinguishes predispositions, prerequisites, phenomenal correlates and cognitive consequences. Their representation does not identify these roles or show that an analyst changing grain changes experience.', 'CONDITIONAL_REPRESENTATION_SCHEMA_OPEN')
add('b04',
    'A directed cycle through v implies v is in a nontrivial SCC, unless the cycle is its self-loop. Conversely, in an SCC containing v and w!=v there is a closed walk from v through w back to v. Choose a shortest positive closed walk from v; removing a repeated internal vertex would shorten it, so it is a cycle through v. A singleton SCC supplies a cycle exactly when its self-loop exists.',
    'Finite directed graph, with the self-loop case included. The graph criterion is not retained capacity, robust memory or a phenomenal-existence test.')
add('b05',
    'If the absent edge u->v is added and lies on a new simple cycle, deleting that edge leaves an old path v->u. Conversely an old v->u path, simplified to avoid repeated vertices, closes with the new edge. For u=v the old zero-length path gives the new self-loop.',
    'The edge is absent before addition. This statement concerns a cycle containing that new edge, not every new graph property or nonlinear dynamical stability.')
add('b06',
    'The characteristic polynomial of [[0,2],[3q,0]] is lambda^2-6q, giving rho=sqrt(6q). rho=1 means q=1/6, hence 10(g-1/2)=log((1/6)/(5/6))=-log(5). For every finite g, logistic q>0, so both directed edges are present and the two-cycle exists.',
    'The structural spectral crossing is not a bifurcation proof for the nonlinear workspace. No numerical sweep is certified by this symbolic calculation.')
add('b07',
    'Differentiate the declared synchronous update: J_12=10 sigma_prime(z1), J_21=15q sigma_prime(z2), with zero diagonals and z1,z2 the state-dependent logits. These factors vary with the evaluated fixed point and drive. Local linear stability uses this Jacobian, whose eigenvalues need not equal those of the adjacency matrix.',
    'The fixed point must be specified; unit-modulus eigenvalues require further nonlinear analysis. This rule does not reproduce the archived numerical study.')
add('a35',
    'Inspect the construction of B:REP: its recursion uses VIEW, LANGUAGE, BAC and EXPRESSIBLE, with TFR supplying the fidelity discipline when applying it to a rival. C1 does not occur among the mathematical evaluation premises. Thus this route reconstructs operational descriptors without deriving an experiential axiom.',
    'C1-free evaluation does not prove BAC, expressibility, target fidelity or the rival phenomenal claims.', 'METADATA_AUDIT_REVIEWED')
add('a36',
    'Apply the same witness argument as b02 with precisely the domain recorded in the current UCT-II gate statement: U1 gives E(P), the proposed necessity would give G(P), and the same actual witness gives not G(P).',
    'This duplicate application must preserve the witness/domain binding. It is not an additional independent empirical confirmation.')
add('c05',
    'For J:U subset R^n -> R^m of class C1 with rank r constant on a neighborhood, select an invertible r-by-r derivative minor. The inverse function theorem makes those r output coordinates and n-r complementary input coordinates a local coordinate chart. Rank r forces derivatives of every remaining output in the latter directions to vanish locally; after output reparameterization J has form (x1,...,xr,0,...,0). Thus each nonempty local fiber is an (n-r)-dimensional C1 submanifold.',
    'Rank at a single point is insufficient: J(x)=x^2 has rank zero at 0 but a zero-dimensional zero fiber. The result is local, not global connectedness or actual phenomenal dimensionality.')
add('c06',
    'On S={0,1}^2 let the full type be the ordered pair, J(x,y)=x and c(x,y)=y. The change (0,1)->(1,0) increases J from 0 to 1 and decreases c from 1 to 0. This is an explicit countermodel to universal monotonicity of an arbitrary coordinate with capability.',
    'The stipulated c is an abstract coordinate, not an independently validated richness or valence measure. Existence of one countermodel does not assert all actual changes behave this way.')
add('c07',
    'For differentiable w=F composed with J, the chain rule gives Dw_s[v]=DF_(J(s))[DJ_s[v]]=0 whenever v lies in ker DJ_s. If an entire path stays in one J-fiber, its w-value is constant by substitution, without needing a differential argument.',
    'An infinitesimal kernel direction alone need not remain in a fiber for a finite step. Nor does selection through J alone exclude other selection or transmission mechanisms.')
add('c13',
    'After warm-up, an unmasked stored output is X_(t-1) XOR E_(t-1), correct with probability 1-epsilon. Masking by an independent fair N makes it independent of the target, hence accuracy 1/2. Current X_t is also independent of X_(t-1), so readout r=0 scores 1/2. Mutating r from 0 to 1 in an unmasked lineage with probability mu gives (1-mu)/2+mu(1-epsilon), gain mu(1/2-epsilon).',
    'Output is scored before the update. IID inputs, independent noise, fixed inheritance and absence of another delayed channel are essential; architecture size alone does not prove equal cost.')
add('c14',
    'For the fair stationary symmetric chain, P(M=X_t)=alpha(1-epsilon)+(1-alpha)epsilon=q. Symmetry makes the two observed memory cells have the same reliability. Copying M scores q and flipping it scores 1-q; randomization cannot beat their maximum. Thus V=max(q,1-q)=1/2+|2alpha-1|(1/2-epsilon).',
    'The optimal flip matters when alpha<1/2. This is a supplied noisily observed Markov prediction task, not a universal value of memory.')
add('c15',
    'Let p in (0,1) be memory-architecture frequency and barW=p W1+(1-p)W0>0. Selection gives p_prime=pW1/barW, so p_prime-p=p(1-p)(W1-W0)/barW. Its sign is the sign of beta(V_XM-V_X)-c, proving the exact criterion.',
    'Interior frequency and positive supplied weights are needed for this strict sign statement. It concerns selection-only frequency, not mutation, transmission or experiential worth.')

add('c16',
    'C1 identifies each complete structural type in the fixed actual ensemble with its experiential type. If the compared coordinates and order are transported by that identification, the coordinate-value sets are the same. A point is undominated in one repertoire exactly when its transported point is undominated in the other, so their frontiers agree.',
    'The ensemble, coordinates and order must be identical under transport. Equality of frontiers at one time does not imply improvement of a changing ensemble over time.')
add('c17',
    'For any two indices i,j in the common indexed actual family, C1-OI gives D_i isomorphic to D_j iff Phi_i isomorphic to Phi_j. Hence the two equivalence relations on indices, and therefore their partitions, coincide.',
    'This compares complete-type equivalence. Equality of selected reports, coordinates or finite views supplies a generally coarser partition.')
add('c18',
    'The rival completeness commitment says its fixed descriptor r determines the target full experiential type. The witness pair has equal r but nonisomorphic complete organizations. C1-OI makes their experiential types unequal, while the rival sufficiency implication makes them equal, contradiction.',
    'TFR must preserve the rival claimed target and quantifiers. A descriptor intended only for access or a selected coordinate is not thereby contradicted.')
add('c23',
    'Each total-variation distance between corresponding response laws is nonnegative, symmetric and obeys the triangle inequality. Multiplying by fixed nonnegative weights and summing preserves those three properties and gives zero self-distance. Distinct structures can have equal probed laws, so separation is not automatic.',
    'Weights and response coordinates are fixed across comparisons. Zero-weight probes and observational aliasing make this a pseudometric; no constitutive or experiential metric follows without an additional bridge.')
add('r126_1',
    'Given the tokenwise isomorphism h:D->Phi and structural projection p:D->E, define the transported projection p_E=p composed with h_inverse on Phi. For every d, p_E(h(d))=p(d), so the square commutes by cancellation.',
    'This transported mathematical coordinate exists conditionally on h; it does not select a phenomenologically meaningful content, identify an installed decoder or establish actual support of an arbitrary abstraction.')
add('r126_3',
    'If one decoder value z represents every target in an observation fiber, for any targets x,y in that fiber the triangle inequality gives d(x,y)<=d(x,z)+d(z,y)<=2 error. Taking the supremum over pairs gives error>=diameter/2. For a finite fiber the diameter is attained.',
    'A necessary worst-case lower bound, not a sufficient radius formula or an average-error guarantee. A three-point equilateral or point-mass family need not attain half the diameter.')
add('r126_4',
    'Start from equality of o=(p,r). At stage k split states by their current block and successor block for every input. Each strict split increases the block count, hence at most |S|-|P0| strict stages. At termination successors respect equivalence, so the quotient is deterministic and observation-preserving. Any stable partition refining P0 refines every stage by induction; therefore the final partition is the unique coarsest such refinement.',
    'Both p and r belong to the initial observation. Finite state/input sets and a fixed total deterministic model are used; dropping p changes the theorem.')
add('r127_1',
    'Necessity: a deterministic response decoder after an encoder must return the same profile for two states with the same code, so unequal required profiles need distinct codes. Sufficiency: encode each distinct profile by its equivalence-class label and decode that profile. Thus the minimum used-code count equals the number of response-profile classes.',
    'The encoder is an abstract existence construction with access to the state/profile. It does not establish a physically installed sensor or decoder.')
add('r127_1a',
    'If two states agree on all queries in Q2, they agree on every member of Q1 subset Q2. Thus the Q2 equivalence relation is contained in the Q1 relation, so its partition refines the latter.',
    'Refinement can be equality: extra queries may repeat existing information. The same states and response semantics must be used.')
add('r127_1b',
    'Define s~t iff o(F_w(s))=o(F_w(t)) for every finite word w, including the empty word. Empty-word agreement gives initial (p,r) agreement. Prefixing any input shows successor stability. Conversely any stable observation-preserving equivalence gives all-word agreement by induction on word length. Therefore this relation equals the terminal coarsest stable partition of R126.',
    'Without the empty word or the p component, the claimed equality can fail even for identity dynamics on two states.')
add('r127_3',
    'Let X have m>=2 values and estimator Xhat=f(C,B,R), with private R conditionally independent of X given (C,B). Conditional data processing gives I(X;C|B)>=I(X;Xhat|B). For E=1[Xhat!=X], chain rules give H(X|Xhat,B)<=H(E)+P(E)log(m-1)<=h2(epsilon)+epsilon log(m-1), where epsilon is the actual error probability. Subtract from H(X|B). Finally I(X;C|B)<=H(C|B)<=log|C| for finite C.',
    'Use actual epsilon, or a monotonic upper-error substitution restricted to [0,1-1/m]. Side information B and independent coins are part of the decoder contract; unconditional I(X;C) need not obey the same lower bound.')
add('r127_3b',
    'Suppose two implementations induce the same complete allowed interface-history law under every adaptive protocol, while the relevant state is stored internally in one and externally in the other. Any interface-only statistic or randomized decision is a common stochastic function of that law, so its distribution is identical in both. It cannot identify which storage location holds.',
    'The equivalence premise must include all allowed side channels, interventions and deadlines. This is a nonidentification result, not proof that actual storage location is meaningless.')
add('r127_4',
    'Instantiate the declared actual-token criterion with the event-grounded subhistory: the selected bearer, interval and causal support satisfy the criterion precisely because those facts are supplied. This is definition application, not a deduction from response similarity.',
    'The actual support is an independent premise. It must not be turned into an additional basal experience gate.', 'DEFINITION_APPLICATION_REVIEWED')
add('r127_5',
    'For each retained relation symbol R of the common relational signature, the tokenwise isomorphism h satisfies R_D(a1,...,ak) iff R_Phi(h(a1),...,h(ak)). Restricting the carriers to the supplied actual support and its h-image preserves that biconditional for tuples in the restriction.',
    'For function symbols a substructure requires closure under those functions; arbitrary subsets support only relational restriction unless closure is supplied. No private phenomenal label is identified by this transport.')
add('a38',
    'The finite representation route supplies a selected descriptor with its fixed bridge, while the actual-support premise and relational C1 transport place the stipulated constitutive relations in the corresponding experiential structure. Under those supplied identifications one may interpret that descriptor as referring to those relations.',
    'This is conditional interpretation. BAC/TFR, actual realization and constitutive grounding are not produced by representation syntax; no particular qualitative feel is decoded.', 'CONDITIONAL_INTERPRETATION_REVIEWED')
add('d129_bundled',
    'The two bundled design rows (1,0,1,1,0) and (0,1,1,0,1) are independent, so the two-by-five design has rank 2 and a three-dimensional kernel. For example a unit Q coefficient and a unit QG coefficient both produce (1,0). On {-1,0,1}^5, direct finite enumeration gives 43 distinct output pairs and maximum fiber size 17; those are finite-grid counts, not dimensions.',
    'The behavioral model, coefficient coordinates and interventions are fixed. A rank result for this model does not identify a psychological motive or reproduce empirical agent data.')
add('d129_direct',
    'Add the three unit rows selecting Q, O and G. Their outputs identify those coefficients. Subtract Q and G from the first bundled output to recover QG; subtract O and G from the second to recover OG. This constructs a left inverse and establishes rank 5.',
    'Observed choice probabilities must determine calibrated logits under a known positive beta. Deterministic choices, unknown temperature or saturated/undersampled probabilities do not supply exact logits.')
add('d129_payoff',
    'For binary Q,O evaluate f at the four corners. Set alpha=f00, b=f10-f00, c=f01-f00, d=f11-f10-f01+f00. The multilinear polynomial alpha+bQ+cO+dQO matches all four values, hence every value on the binary domain. Taking expectation gives alpha+bq+co+dj and subtracting the declared action cost gives the formula.',
    'j=P(Q=1,O=1) is a joint probability. Replacing it by qo needs an independence premise; the polynomial identity alone supplies none.')
add('d129_marginal_counter',
    'For OR reward f=Q+O-QO and the specified costs, action 0 has value q0+o0-j0 and action 1 value q1+o1-j1-1/4. With q0=1/4,q1=3/4,o0=o1=1/2, context A j0=j1=1/4 yields (1/2,3/4); context B j0=0,j1=1/2 yields (3/4,1/2). All joint cells are nonnegative and the marginals match.',
    'This is an existence witness with action-specific joint laws. It does not assert any measured system has these contexts.')
add('d129_value_gap',
    'Let a marginal-only policy choose action 0 with probability p. Under equal prior on the two indistinguishable contexts its average value is one half of [p/2+(1-p)3/4+p3/4+(1-p)/2]=5/8, independent of p. A context-informed policy selects the better action and attains 3/4, leaving regret 1/8.',
    'The equal prior, identical marginal observations and absence of distinguishing side information are required. Worst-case and average-case claims are not interchangeable.')
add('d129_frechet',
    'A binary joint law with marginals q,o is determined by j; nonnegativity of its four cells gives max(0,q+o-1)<=j<=min(q,o). When action-specific laws can be chosen independently, j1-j0 ranges exactly over [ell1-u0,u1-ell0]. Apply the affine map t->B+dt, reversing endpoints when d<0, to obtain the sharp advantage interval.',
    'Cross-action coupling restrictions can shrink this interval. Sharpness requires independent admissibility of the two action-specific joints, not merely separate marginal bounds.')
add('d129_grid',
    'For a boundary-covering rectangular three-dimensional grid with maximum coordinate gap h, every point has a grid neighbor at Euclidean distance at most sqrt(3)h/2. The supplied global Lipschitz constant gives |e(x)|<=|e(grid neighbor)|+L_e sqrt(3)h/2. Maximize over x.',
    'The domain coverage, boundary inclusion, Euclidean norm and independently justified global Lipschitz constant are essential. Good sampled fit cannot establish that constant.')
add('d129_separable',
    'Subtract z(q0,o,g)=fQ(q0)+fO(o)+fG(g)+b from z(q1,o,g). All non-Q terms cancel, leaving fQ(q1)-fQ(q0), independently of o,g.',
    'This is additive separability, not linearity of fQ. Interactions or changed background coordinates invalidate the cancellation premise.')
add('d129_uct',
    'The actual-complete bridge supplies nonisomorphic organizations in the same constitutive signature. If their experiential types were equal, C1-OI would give the forbidden organizational isomorphism. Hence the full experiential types differ.',
    'Finite behavioral identifiability alone does not establish the complete bridge. No conclusion about valence, pain or a scalar amount of experience is licensed.')
add('r131_target',
    'If g is in row(A), write g=c^T A, so g^T mu=c^T y(mu) and the target factors through probes. Otherwise linear algebra gives d in ker(A) with g^T d!=0. Since the normalization row belongs to A, sum d=0 and the nonzero positive/negative parts have equal mass t>0. The distributions d_plus/t and d_minus/t have equal A observations and unequal g means, disproving factorization.',
    'All probability laws on the fixed finite Z are admissible. Restricted model classes may identify a target even with deficient A.')
add('r131_complete',
    'If rank A=n, a left inverse reconstructs every mu from A mu. If rank A<n, choose nonzero d in ker A and normalize its positive/negative parts as in r131_target. Their supports are disjoint, their probe outputs equal and their TV distance is 1. Thus universal identification is equivalent to full column rank; besides normalization it requires at least n-1 independent probe rows.',
    'The worst-case aliasing is existential over the full simplex. It is not the error of every actual experiment or a claim about sampled statistical uncertainty.')
add('r131_closure',
    'For each fixed fiber and legal action, let mu_s be its declared joint next-summary/output row on the same finite outcome alphabet. Exact closure means these rows agree. Agreement implies equal probes. Conversely full column rank and equal A mu_s imply mu_s=mu_t by a left inverse. Repeat for every fiber/action while preserving the common menus.',
    'Probes must separate the JOINT outcome alphabet and share labels and action meanings. State and output marginals separately do not suffice; menu agreement is separate from row equality.')
add('r131_blind',
    'Take the disjoint distributions u,v in a deficient-probe fiber. Add a persistent hidden bit b and let the next visible outcome be sampled from u if b=0 and v if b=1, while preserving b. Project away b. Probes agree at every projected state/action but the two joint rows have TV 1, so exact projected closure fails.',
    'This constructs a failing model; rank deficiency does not force every supplied kernel to fail closure. Hidden b persists rather than being reselected each time.')
add('r131_decision',
    'In the preceding witness the supports of u,v are disjoint. With fair hidden b, a full-outcome observer identifies b and selects the correct one of two rewarded actions with probability 1. The equal probe result gives no b-information, so any probe-only action law has average success (p+(1-p))/2=1/2.',
    'The decision is made from the declared observation, without another channel. This is a particular decision witness, not universal utility of every additional probe.')
add('r131_robust',
    'Since LA=I, mu-nu=L A(mu-nu). Its normalization coordinate is zero, leaving B times the vector of probe expectation differences. Hence ||mu-nu||1<=||B||_(infinity->1) epsilon; divide by 2 for TV and cap at its universal upper bound 1.',
    'epsilon bounds true expectation error. Sampling confidence and selection of a numerically stable left inverse require additional analysis.')
add('r132_hall',
    'An injective assignment sends each task coalition J into its neighborhood, so |N(J)|>=|J| is necessary. For sufficiency induct on task count. If a nonempty proper J is tight, match J by induction and match its complement after removing N(J); Hall for the remainder follows by applying the original condition to J union K. If no proper coalition is tight, every such coalition has surplus at least one; match any task to any neighbor and delete both, leaving Hall for the remaining tasks. The one-task case is immediate.',
    'Finite bipartite assignment with one slot per task and injectivity; capacities, noisy execution or temporal reuse are different models. Empty task family is trivially matched.')
add('r132_deficit',
    'Let delta=max_J(|J|-|N(J)|), including the empty J. Every matching leaves at least delta tasks unmatched. Add delta universal dummy slots: every coalition now satisfies Hall, so all n tasks can be matched and at most delta use dummies. Removing dummies proves maximum matching size n-delta. Any random allocation completes at most n-delta tasks per outcome; within J its total completion count is at most |N(J)|, so at least one task has probability <=|N(J)|/|J|.',
    'The coalition ratio uses nonempty J. Bounds concern simultaneous distinct-slot assignments; independently optimizing each task changes the feasible set.')
add('r132_high',
    'With n tasks and n-1 universally compatible slots, every proper task subset has size at most n-1 and is matchable, but the full family violates Hall. Uniformly omit one task and injectively assign the remainder: each task succeeds with probability 1-1/n, while probability of all n succeeding is zero.',
    'For n>=3 this exhibits a genuinely higher-order obstruction beyond pairwise checks. High individual success is not a high probability of joint success.')
add('r132_probes',
    'Equal enabled menus allow the same partial actions at all representatives. For each enabled action, full-rank probes of its joint (next block,output) law identify that law by r131_complete. Probe agreement is therefore equivalent to the equal-row condition defining exact partial closure.',
    'Probe rank is taken on the joint alphabet. Legal menus must agree before comparing rows; impossible actions have no probability law to infer.')
add('r132_obstructions',
    'First, the two-slot and three-slot mechanisms can agree on every request supported by both but differ on whether the full three-task request is enabled, so common-row equality omits menu equality. Second, laws supported uniformly on (0,0),(1,1) versus (0,1),(1,0) have identical separate binary marginals and disjoint joint supports, hence joint TV 1.',
    'These are distinct counterexamples: enabledness cannot be repaired by matching existing rows, and a joint law cannot be inferred from its two marginals.')
add('r132_refine',
    'At each step split a block by its enabled menu and the masses to every current block/output pair under each enabled action. Strict splitting increases the finite block count. Any stable refinement of P0 refines the next split whenever it refines the current one: coarse masses are sums of equal finer masses, and menus already agree. Induction shows the terminal stable partition is coarser than every stable refinement of P0, hence unique and coarsest; at most |S|-|P0| strict stages occur.',
    'Keep the same scheduler, labels, exact probabilities and represented states throughout. Empirical approximate equality or support-only filtering defines another problem.')
add('r133_support',
    'For an empty history B is the supplied attainable set. Inductively, a pair (m,s_prime) is attainable after (a,o) iff some attainable predecessor with that same m has K_m(s,a;s_prime,o)>0. Necessity follows by conditioning a positive-probability finite path on its penultimate state; sufficiency concatenates its positive-probability prefix and positive transition. This is exactly the specified update.',
    'The hidden model is immutable. The support is a possibility set, not a posterior probability or a sufficient statistic for arbitrary quantitative value.')
add('r133_common',
    'At horizon zero universal success means B subset G. Otherwise a successful policy either stops in a goal-contained support or chooses a common-enabled action. Every nonempty successor support corresponds to a possible positive-probability branch and must admit a successful remaining policy. Conversely choose that common action and its output-indexed successful subpolicies. Induction proves the recursion. If a randomized tree succeeds with probability one in every finite initial coordinate, each positive-weight pure tree must also succeed in every coordinate, so one deterministic tree suffices.',
    'Finite horizon, finite branching, closed goal or persistent success flag, and universal action legality are essential. This is not infinite-horizon almost-sure control.')
add('r133_cell',
    'A deterministic observation rule chooses one action on each nonempty h-fiber. It succeeds throughout that cell iff this action belongs to every G_m in the cell. Choose one element of each nonempty intersection for sufficiency. A probability-one randomized rule must put all its mass on this same intersection, so an empty intersection cannot be repaired by mixing.',
    'All good-action sets in the cell must intersect simultaneously. Pairwise intersection and per-model solvability are weaker.')
add('r133_cover',
    'Each used message is decoded to one action and its entire message cell lies in that action cover C_a. Thus its decoded actions cover M, giving at least tau messages. Conversely select a minimum action cover and assign each m to one covering action; transmitting its index succeeds. Fixed-length binary codewords for tau messages require and suffice ceil(log2 tau) bits.',
    'M is finite nonempty and all G_m nonempty. The ideal encoder can inspect m; no sensing implementation, noise, variable-length protocol or entropy claim is inferred.')
add('r133_avoid',
    'For candidate subset J, intersecting U minus {m} over m in J gives U minus J, nonempty exactly when J is proper. A blind action law p succeeds at model m with probability 1-p_m; its worst value is 1-max p_m<=1-1/n, attained uniformly. The two cells {1} and its complement can choose actions 2 and 1, yielding perfect success with two messages. One message fails; full model identification needs n distinct codes.',
    'n>=2 and the signal precedes commitment without altering opportunities. The candidate models are mutually exclusive, unlike simultaneous task coalitions.')
add('r133_nonunique',
    'For n=3, each partition consisting of one singleton and its complementary pair has proper cells and therefore admits successful actions. Each is a two-block partition; no two refine one another. A common coarsening must merge both pairs connected by these partitions, hence all three models, whose good-action intersection is empty.',
    'This disproves a universal unique coarsest task-sufficient observation. It does not contradict uniqueness of a stable full-interface quotient with a fixed initial partition.')
add('r133_probe',
    'At H=2, a preserving diagnostic consumes one step, identifies m and leaves the correct one-step terminal action, giving value 1. An uninformative probe leaves identical terminal-action laws in the two models, so their success probabilities sum to at most 1; blind half-half mixing attains 1/2. A destructive probe reaches absorbing failure and scores zero conditional on use; allowing it cannot improve the blind optimum. At H=1 the preserving probe leaves no step for commitment.',
    'The time, preservation and action contracts are part of the model. Information delivered after destroying the opportunity is not interchangeable with a free observation.')
add('r133_persistence',
    'The two allowed fixed-model traces are (1,0) and (0,1), each containing a 1. After observing first output 0, the support update retains only the second model, whose next output must be 1. Combining the two stagewise possible-output sets would additionally allow (0,0), but that requires switching model identities between stages.',
    'A product of marginal possibility sets is not the feasible history set of a persistent mechanism. Persistence must also be preserved in policy recursion.')
add('r134_vectors',
    'Every pure H+1-step tree first stops or chooses a common action and one H-step continuation for each output. Conditioning on the joint successor/output law gives the displayed linear backup vector, proving one inclusion. Conversely attach any allowed tuple of continuation trees to the first action to realize that vector. Induction starts with the goal-indicator vector. Independent private sampling of complete pure trees realizes their convex hull; expanding independent branch mixtures as a product distribution on complete trees proves the converse convex backup claim.',
    'One policy tree supplies the entire initial-state vector. Taking each coordinate maximum from a different tree is not an executable common policy.')
add('r134_lp',
    'Let columns of A be the finite pure-policy vectors. A mixture lambda produces A lambda, so a uniform threshold is feasible exactly when A lambda dominates it. Maximize t subject to A lambda>=t1, lambda>=0, sum lambda=1. The dual weights q on these coordinate constraints are nonnegative and sum to one, yielding min_q max_j q dot v_j by finite feasible bounded LP duality.',
    'The initial-coordinate set and complete pure-policy family are fixed and finite. The adversarial q is a dual certificate, not an empirically inferred prior.')
add('r134_zero',
    'An all-one convex combination of vectors in [0,1]^B forces every positive-weight vector to equal one in each coordinate: otherwise that coordinate average is below one. Finite B allows one common positive-weight vector for all coordinates. Conversely an all-one pure profile gives robust value one. Apply r133_common to identify its qualitative criterion.',
    'The purification is specific to probability-one success. At lower guarantees randomization can improve minimax value.')
add('r134_scalar',
    'The blind pure profiles are (1,0),(0,1), whose coordinatewise supremum (1,1) is outside their segment; its midpoint achieves only (1/2,1/2). In the signal example, choose the model named by the binary signal; each coordinate success is 3/4. Both observations leave the same possibility support, so a policy retaining only support/time chooses a signal-independent terminal law, whose two success probabilities sum to one.',
    'Possibility support is sufficient for the specified qualitative recursion, not for all quantitative decision problems; probabilities or retained observations may matter.')
add('r134_probe',
    'For a prior/dual weight q, the contribution of decision d_y is q a_y d_y+(1-q)b_y(1-d_y). Maximizing independently over 0<=d_y<=1 gives max(q a_y,(1-q)b_y), then sum over y. Finite minimax swaps the decoder maximum and q minimum. The resulting convex piecewise-affine F has an optimum at an endpoint or a slope-change point q=b_y/(a_y+b_y) when the denominator is positive; a flat interval has an optimal endpoint.',
    'Zero-zero rows contribute zero and no breakpoint. The weighted masses already include conditional survival; raw diagnostic accuracy alone is insufficient.')
add('r134_tv',
    'The forced optimum min_q F(q) is at most F(1/2)=sum max(a_y,b_y)/2=(sum a+sum b+||a-b||1)/4. With common survival rho, a=rho P0,b=rho P1, giving rho(1+TV(P0,P1))/2. Symmetric binary experiments admit a balanced decoder attaining this bound. The asymmetric (1,0) versus (1/2,1/2) experiment instead attains 2rho/3 although its TV is 1/2.',
    'The bound need not be attained. Equal TV fixes the equal-prior optimum, not generally the robust minimax optimum or opportunity cost.')
add('r134_optional',
    'The allowed profile set is the convex hull of immediate profiles (1,0),(0,1) and all probe profiles. At fixed q its support value is max(q,1-q,F(q)). Finite minimax therefore gives min_q of that maximum. The asymmetric example in r134_mix shows a mixture can outperform both separately optimized blind and forced-probe strategies.',
    'The decision whether to probe precedes the signal, and blind actions avoid its cost. Changing that order or the payoff changes the feasible profile set.')
add('r134_mix',
    'For P0=(1,0),P1=(1/2,1/2), choose model 1 on the second output and randomize with probability d for model 0 on the first. Forced profiles are (rho d,rho(1-d/2)); equalizing gives d=2/3 and value 2rho/3. Optional nondominated candidates include (1,0),(0,1),(rho,rho/2). For rho<=2/3 their sums are at most 1, so value 1/2 is optimal. For rho>2/3 mix the third with (0,1) at weight 2/(2+rho), giving both coordinates 2rho/(2+rho); dual q=(2-rho)/(2+rho) matches it. At rho=7/10 these are 14/27,20/27,13/27.',
    'This supplied binary family establishes an existential mixing advantage for 2/3<rho<3/4. It is not a universal numerical law for diagnostic systems.')

add('r135_deficiency',
    'For fixed v, write max_i(v_i-w_i)_+=max_{q>=0,sum q<=1} q dot (v-w), using q=0 for the zero option. The compact convex minimax theorem interchanges min_w and max_q, giving max_q[q dot v-h_D(q)]. Maximize over compact C and commute the two maxima to get max_q[h_C(q)-h_D(q)]. Positive homogeneity writes q=t p with 0<=t<=1 and p in Delta_n, so optimizing t gives max_p[h_C(p)-h_D(p)]_+.',
    'The subprobability simplex makes the positive-part step explicit. Compactness gives attainment; convexity and one common target vector are essential. Weights of either sign would compare a different object.')
add('r135_equality',
    'If G(C) is included in G(D), each v in C is itself a threshold in G(C), hence is dominated by some w in D, giving zero directed loss. Conversely zero attained loss supplies such a w for every v, and therefore transfers every threshold dominated by v. Apply r135_deficiency for the support-function inequality. Apply this equivalence in both directions for equality.',
    'Equality of downward guarantee regions is weaker than equality of exact profiles or physical organizations. Convexity is required for the support-function characterization used here.')
add('r135_value',
    'For every v choose w with w>=v-epsilon 1. Then w dominates max(0,b-epsilon 1) whenever v dominates b. Put u=min(v,w) componentwise: ||v-u||infinity<=epsilon, so monotone L-Lipschitz F gives F(v)<=F(u)+L epsilon<=F(w)+L epsilon. Maximize over v. Composing two componentwise matches adds their errors, proving the directed triangle inequality.',
    'F is monotone and Lipschitz in maximum norm on the common cube. The result does not preserve signed diagnostics or exact policy distributions.')
add('r135_hierarchy',
    'For C1 the coordinate sum is at most 1 and (1/2,1/2) is feasible, giving robust value 1/2. D1 has the same optimum. Matching (1,0) from C1 to D1 incurs at least 1/2, and its top point matches every C1 point within 1/2; reverse loss is zero since D1 subset C1. For C2,D2 the point (1,1) dominates the entire cube, so both guarantee regions are the cube, but (1,0) belongs only to D2.',
    'These are finite abstract profile sets. They separate robust value, guarantees and exact profiles without asserting actual experiential noninjectivity.')
add('r135_policy',
    'Couple controller private seeds. While the mapped state and observed histories agree, both controllers choose the same legal action. Maximally couple the next mapped-state/output rows; conditional match probability is at least 1-epsilon. Lift the concrete projected outcome to its actual next state using finite conditional probabilities. Induction gives path agreement probability at least (1-epsilon)^H, hence TV and terminal [0,1] payoff error at most beta_H. A concrete absorbing success hazard epsilon versus an abstract never-success process has success gap 1-(1-epsilon)^H, proving sharpness.',
    'Same total actions or a globally safe supplied subset and exact payoff pullback are required. Pointwise menus alone do not preserve support-based hard legality.')
add('r135_transfer',
    'Copy every common-history policy in either direction and apply r135_policy to its entire comparable profile vector. Each directed profile loss is at most beta_H; the monotone minimum-coordinate optimum therefore differs by at most beta_H. If the copied abstract policy is eta-optimal, concrete value is at least abstract optimum-eta-beta_H, which is at least concrete optimum-eta-2beta_H.',
    'The two-error bound compares a chosen policy with the concrete optimum. A supplied guarantee for that particular abstract policy loses only one beta_H.')
add('r135_legality',
    'After p, K0 leaves only good possible, so action a is universally legal and succeeds within two steps. For any delta>0 the identical observation leaves both good and bad possible. No non-stop action is legal at both, so the only legal continuation fails, giving value zero. If a at bad is explicitly made legal with failure, it is now executable and succeeds with probability 1-delta.',
    'Totalization changes the protocol. This witness violates r135_policy total-action/safe-subset premises, so it is not a counterexample to the coupling theorem or an experience threshold.')
add('r135_uct',
    'The actual-profile premise makes G a well-defined invariant on complete structural types. Hence unequal G values imply unequal structural types, and C1-OI gives unequal experiential types. Full experiential type factors through G exactly when G is injective on this realized complete-type set; a selected coordinate factors through G exactly when it is constant on each G-fiber.',
    'The actual, complete, isomorphism-invariant profile map is supplied separately. Equality of a measured finite task score does not meet those premises.')
add('r136_blackwell',
    'If P=QR, concatenate R with any P decision rule to obtain an equal-value Q rule. Conversely S={QR:R stochastic} is compact convex. If P is outside S, strict separation gives a finite table c with <c,P> greater than every <c,QR>. With full-support prior p choose actions X and utility u(theta,x)=c(theta,x)/p_theta. The identity decision after P attains the left side, while every Q decision is a stochastic R and is bounded by the right, contradicting universal value dominance. A common positive affine normalization of this finite table puts it in [0,1].',
    'One fixed pair of experiments and full-support prior are essential. The universal utility quantifier is stronger than varying weights over one task family; a stochastic translator is not an organization isomorphism.')
add('r136_causal',
    'A causal translator yields prefix-output marginals depending only on the corresponding input prefix, giving the linear nonanticipation constraints. Conversely denote those consistent marginals by R_t. At positive prefixes define r_t=R_t/R_(t-1); summing x_t gives one by prefix consistency. At zero denominators any stochastic row is harmless because that prefix is unreachable. Products telescope to R for every full input path. Compactness of the nonempty causal polytope and continuity of TV give attainment; absolute-value epigraphs and a shared maximum-error variable give the finite LP.',
    'Input streams are exogenous and translator coins independent of them and theta. Matching a passive path law is insufficient when emitted actions change future inputs.')
add('r136_composition',
    'Sequentially run a W-to-Q and Q-to-P causal translator using independent seeds at each time; their matrix product is causal on the common clock. TV(P,WSR)<=TV(P,QR)+TV(QR,WSR)<=epsilon1+epsilon2 by triangle inequality and stochastic contraction. Minimize over attained optimizers. Append any common causal no-feedback downstream decision kernel and contract again to bound every common [0,1] payoff.',
    'Payoffs use the translated stream and decision path, with unchanged legal actions. An omitted correlation with raw Y, feedback or translator cost is outside the theorem.')
add('r136_prefix',
    'Necessity: equal available y-prefixes force equal translated prefix laws; since desired laws are point masses, their desired x-prefixes must coincide. Sufficiency: on every observed input-prefix class define the next x symbol from any represented theta; prefix constancy makes it well-defined and consistent with the previously defined symbols. On unused prefixes extend one time step at a time with arbitrary symbols, retaining prior outputs. This yields a deterministic causal translator on the whole alphabet.',
    'Unused full paths cannot be filled independently if they share used prefixes. The extension must be sequentially prefix-consistent, as constructed here.')
add('r136_delay',
    'Offline translation reads y2=theta and returns (theta,blank), exactly. A causal translator sees the same first input in both models, so its first-bit probability p is common; the two error probabilities are at least p and 1-p, giving worst error at least 1/2. A fair first-bit guess and blank second output attain path TV 1/2 in both models.',
    'The first deadline is fixed. Waiting for y2 changes the task and cannot serve as a causal implementation of the earlier output.')
add('r136_query',
    'For an upper bound average over independent uniform b and q. Conditional on any private seed and adaptive read transcript, each unqueried bit is still fair, since the transcript depends only on inspected bits. The uniform later q lands in the distinct inspected set with probability at most k/n. Thus average success is at most k/n+(1-k/n)/2, bounding worst-case success. Uniformly selecting k distinct coordinates and guessing fairly on an unread query attains this probability for every fixed b,q.',
    'Reads precede q, the total distinct read budget is at most k, and no side channel reveals unread bits. Adaptive preparation is included but query-first reading is a different protocol.')
add('r136_order',
    'For pre-announced q and k>=1, read that coordinate; the all-one profile dominates every threshold. With delayed q, the full reader still has all ones, while the restricted reader robust optimum is 1/2+k/(2n). Its loss in matching the full all-one profile is therefore (n-k)/(2n), and no other full-reader profile has greater directed loss. The full reader can ignore information to emulate every restricted policy, giving reverse loss zero. An exact admissible translator would copy the all-one response and contradict this loss.',
    'Use the same delayed (b,q) coordinates and read/deadline contract for the directional comparison. Task-specific pre-announced optima cannot be pasted into one delayed policy.')
add('r137_obstruction',
    'Each W_s is convex in the (m-1)-dimensional action simplex, m>=1. Choose a minimal empty finite subfamily of size k; for each member i choose a point x_i in the intersection of all other members. If k>m, the k points are affinely dependent. Separate positive and negative coefficients and normalize to express one point z as a convex combination on both sides. For any constraint j, choose the side excluding j; all its points satisfy constraint j, so z does too. Thus z belongs to the allegedly empty intersection, contradiction. Therefore k<=m.',
    'The action alphabet is finite nonempty, as in the source contract. The convex decoder class matters; no same bound is proved for arbitrary nonconvex controller families.')
add('r137_sharp',
    'At state i, a mixture fails with probability w_i; its row-TV distance from certain success is w_i. Exact matching forces w_i=0. Every proper subset of states admits a point mass on an omitted action, but all m conditions contradict sum w=1. Minimizing max_i w_i gives 1/m, since the maximum is at least the average and uniform weights attain it; success is 1-1/m.',
    'All actions are legal here, so the obstruction is accuracy rather than menus. This makes the m-state Helly bound sharp within the supplied model.')
add('r145_transport',
    'Fiber constancy defines the common descended map for every admitted operation. Start at paired equal logical states and couple controller randomness. Equal observed histories produce the same next operation distribution; its common descended map produces the same next logical state. Induct on the finite history and then average over controller seeds.',
    'The observer sees only the declared logical state, operations genuinely descend, and the same policy class is used. Adding only further descending operations need not identify hidden implementation details.')
add('r145_separation',
    'Compute pi(T_u^k(x,y))=x+y+u, independent of k. Two updates give T_v^k T_u^k(x,y)=(x+u,y+v), so every state is reached from zero in two steps and updates are bijections. Zero-input fixed points satisfy x=y+k and thus have output k; fixed labels therefore separate distinct k. At the pointed zero state an input self-loop exists iff k=0, separating zero from nonzero even without input labels. After T_0^k(0,0)=(k,k), resetting x and reading pi returns k. Same-pi diagonal states produce different outputs after this reset, so it does not descend.',
    'Nonzero k pairs need not be distinguished by the unlabeled self-loop invariant. Complete physical distinction needs the separate actual bridge; operational blindness alone does not supply it.')
add('r145_affine',
    'Two states lie in one pi-fiber iff their difference is (h,h). Their output difference after affine J is (A+B+C+D)h=L_J h, so descent holds exactly when L_J=0. At the prepared state (k,k), readout is L_J k+a+b. Subtract known offsets and stack the probe matrices to get L k=r. Full rank n gives unique k; otherwise each consistent response is a coset of ker L, with 2^(n-rank L) members.',
    'Trials reset to the stipulated initial state and use the same fixed k. Rank of a chosen probe list is not an automatic physically available diagnostic.')
add('r145_type',
    'Suppose the actual complete organizations were isomorphic. ACTUAL_BRIDGE would induce an isomorphism of their represented pointed update/port structures, contradicting the applicable nonisomorphism in SEPARATION. Hence actual complete types differ; C1-OI transfers that distinction to full experiential types.',
    'Faithful actual realization and preservation of the represented invariant by every admitted complete isomorphism are indispensable. A common quotient does not prove an actual equal macro experiential token.')
add('r146_duplicate',
    'Substituting m_i=z_i gives the true local next-state law delta_(m_i XOR a_i), so prediction error is zero. Simultaneously permuting the cells, their states, inputs and sensors commutes with the componentwise update. In the separate label protocol, condition on H,R: independent uniform B makes every chosen label correct with probability 1/n. Finally independently complementing the external task output and the local point-mass prediction realizes all four accuracy/error pairs.',
    'The external label is deliberately independent of complete available history. This does not assert every real self-location problem is unidentifiable, or that local prediction establishes actual ownership.')
add('r149_ta15_nonident',
    'Any allowed adaptive decision, including its randomized stopping and private coins, is a measurable function/kernel of the complete transcript. Equal transcript laws in m0,m1 therefore give equal decision laws. If it is almost surely 0 in m0 it is also almost surely 0 in m1, so it cannot be almost surely correct for opposite binary truths in both.',
    'Equivalence must cover the complete allowed protocols, not merely one sample or passive distribution. This is relative nonidentification, not a global assertion that no evidence is possible.')
add('r149_ta16_causal_limits',
    'For every nontrivial cut and every vertex i, strong connectivity gives a path from i to an opposite-block vertex and back, each of length <=n-1. Their positive closed-walk weight contributes to (W^k-W_cut^k)_ii, and nonnegativity prevents cancellation. Conversely cut a source SCC from the rest: no closed walk crosses it, so all such differences vanish. Five-bit parity broadcast has two image states at every positive horizon (one bit capacity), while the invertible four-bit shift-XOR has 16. Identity/parity modes separately witness five-bit retention/complete dependencies but no single mode witnesses both. Recoding conjugates dynamics and transports interventions. For the repetition wrapper, DE=id implies Ftilde E=EF and induction gives all horizons; <=r pre-update flips per odd 2r+1 block leave majority decoding unchanged.',
    'The all-cut quantifiers are for every cut, every vertex, exists k<=2(n-1). Signed weights, n=1, mixed regimes and noise within decoder/update hardware are excluded. These causal results do not validate historical RRH-E.', 'MANUAL_REVIEW_WITH_STATEMENT_REPAIR')
add('r149_ta17_quotient',
    'Equality of all declared future response laws is reflexive, symmetric and transitive, so defines a quotient. A bijective recoding transporting interventions and outputs preserves exactly this equality and induces a quotient bijection. By the nuisance premise same-Z histories have equal responses, so collapse. For any noninjective abstraction choose two collapsed histories and a consumer whose payoff/required output differs on that pair; no decoder of their common code can preserve that consumer.',
    'The quotient is relative to the fixed intervention/output family. A behaviorally null nuisance is null for that family, not for every conceivable later consumer.')
add('r149_ta17_inheritance',
    'For S subset T, Y_S is a projection of Y_T, so data processing gives I(U;Y_S)<=I(U;Y_T); dividing by the same H(U)>0 proves monotonicity. Bijective recodings preserve entropy and joint entropy. Under U->Y->O, I(U;O)<=I(U;Y), and under the stipulated closed-lineage Markov chain successive MI cannot increase. A shared-upstream counterexample stores the same fair bit independently in A,C; after separation a current intervention on A leaves C unchanged despite their observational MI of one bit.',
    'Intervention timing and distribution are fixed and transported with coordinates. Observational shared information is not current-process causal descent; no-side-channel Markov assumptions must actually hold.')
add('r149_ta17_set_limits',
    'An individual-only categorical label cannot name empty/multiple-member sets without enlarging its state space. For normalization, explicitly assume full unique continuation has q(A,B)=1; adding an equally full successor preserves that value and symmetry gives q(A,C)=1, contradicting a nonnegative unit sum. Without this calibration the displayed three conditions alone permit a family-dependent total below one. For marginals use muE(10)=muE(01)=1/2 versus muJ(00)=muJ(11)=1/2. For inheritance use U=(U1,U2), duplicated U1 versus separate U1,U2: singleton Gamma is 1/2 in both but joint Gamma is 1/2 versus 1. Secret shares R,U XOR R have singleton zero and joint one; full copies have singleton one each and joint one, violating respectively universal submodularity and supermodularity/conserved mass.',
    'Unique-full-continuation calibration and comparison across the singleton/fission scenarios are now explicit. Nonexclusive inheritance and set-membership probabilities are not mutually exclusive probabilities of a single surviving individual.', 'MANUAL_REVIEW_WITH_STATEMENT_REPAIR')
add('r149_ta17_kl_cost',
    'Expand KL(mu||product_i q_i) as -H(mu)-sum_i E_mu log q_i(X_i). Add and subtract sum_i H(mu_i) to obtain [sum_i H(mu_i)-H(mu)]+sum_i KL(mu_i||q_i). Each term is nonnegative and is minimized at q_i=mu_i, with the usual zero-mass conventions; incompatible support gives infinity. Linearity gives E sum_i 1[i in S]=sum_i P(i in S)=E|S|.',
    'Finite binary inclusion variables and one common logarithm base. The irreducible cost is total correlation, not evidence that the true joint law is independent.')
add('r149_ta17_regret',
    'The two full set posteriors have the same observable singleton vector. Hence a restricted policy chooses the exactly-one action with a common probability p. Its average reward under the equal context prior is [p+(1-p)]/2=1/2. Access to the full posterior identifies which support class applies and chooses the correct action with reward one.',
    'No additional distinguishing observation is allowed. This is the fixed average-reward witness, not a claim that all marginal-only decisions lose one half.')
add('r149_ta18_underdetermination',
    'Construct two physical classes a,b and two output types 0,1, with only identity symmetries and identity scale maps. Both the constant-zero map and the map a->0,b->1 commute with all those maps and satisfy invariance, yet disagree at b. Thus invariance/scale consistency alone do not universally select a unique bridge.',
    'This is an existential countermodel to sufficiency of those weak requirements. If a,b are distinct complete actual types, the constant map is incompatible with current C1-OI; adding C1 changes the premise set.')
add('r149_ta19_regularity',
    'For negative lambda, an exact-top-tier supported probability law is delta_Q; for positive lambda it is delta_P. Distinct Hausdorff labels have distinguishable point masses, so unequal one-sided limits prevent continuity at zero. A closed graph must contain both limits (0,Q),(0,P). Separately, for a locally fixed finite labeled candidate set, match each branch to itself. Its Hausdorff distance is at most max_P min(1,d_P(z_P(x),z_P(x0))), which tends to zero by finiteness and each branch continuity.',
    'The finite landscape includes losing candidates and is a different object from a winner-only selection. Infinite candidate families need uniform conditions; changing births/deaths needs additional analysis. No unread TA19 main-PDF section is claimed reviewed.')
