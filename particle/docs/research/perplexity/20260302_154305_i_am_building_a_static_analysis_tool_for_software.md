# Perplexity Research: I am building a static analysis tool for software codebases that produces a unified health report fr...

> **Date:** 2026-03-02 15:43:05
> **Model:** sonar-deep-research
> **Query Length:** 3274 chars

---

## Query

I am building a static analysis tool for software codebases that produces a unified health report from heterogeneous metrics. The metrics come from fundamentally different domains:

1. **Graph-theoretic metrics**: Betti numbers (b0 = connected components, b1 = cycle complexity), PageRank centrality, betweenness centrality, Markov chain stationary distributions, modularity scores, spectral gap
2. **Purpose/semantic metrics**: cosine similarity of purpose vectors, Q-scores (purpose clarity 0-1), role classification confidence, alignment scores
3. **Constraint/testing metrics**: test coverage percentage, dead code ratio, constraint satisfaction booleans
4. **Performance/flow metrics**: cyclomatic complexity, fan-in/fan-out, coupling scores, hotspot detection
5. **Concordance metrics**: code-documentation alignment states (symmetric, orphan, phantom, drift)

**The core problem**: How do you combine these into a single meaningful composite score WITHOUT just normalizing everything to [0,1] and averaging (which destroys meaning)?

I'm exploring an approach inspired by physics Lagrangians: define an "Incoherence Functional" I(C) = I_struct + I_telic + I_sym + I_bound + I_flow, where each term maps metrics from one domain into a common "incoherence" dimension using domain-specific transfer functions. Health = 10 * (1 - I(C)).

**What I need research on:**

1. **Multi-criteria decision analysis (MCDA)** approaches that handle incommensurable metrics -- specifically methods beyond simple weighted averaging (TOPSIS, ELECTRE, PROMETHEE, AHP). Which are most appropriate for software quality measurement?

2. **Transfer function design**: What mathematical forms work best for mapping heterogeneous metrics to a common scale while preserving sensitivity? Sigmoid, log-transform, exponential decay, piecewise linear? What does the literature say about calibrating these for software metrics specifically?

3. **Dimensional reduction vs. dimensional separation**: Is it better to combine into one score (like my I(C) approach) or keep dimensions separate and use Pareto-dominance / multi-objective optimization to compare states? What are the trade-offs?

4. **Coupling terms / interaction effects**: In physics Lagrangians, cross-terms capture how fields interact. For software metrics, are there known interaction effects? (e.g., "high complexity + low test coverage is worse than the sum of each alone" -- superlinear risk). Any formal models?

5. **Existing composite software quality models**: How do SonarQube, SQALE, ISO 25010, CISQ, Quamoco, and similar frameworks handle multi-source metric combination? What lessons have they learned?

6. **Information-theoretic approaches**: Can mutual information, KL-divergence, or entropy-based measures help quantify how much "information" each metric adds to the composite, avoiding redundancy?

7. **Calibration and validation**: How do you validate that a composite metric actually predicts outcomes (defect density, maintenance cost, developer productivity)? What ground-truth data is available?

Please provide specific mathematical formulations, named methods with citations where possible, and practical recommendations for a tool that needs to produce actionable reports for AI agents consuming the output.

---

## Response

# Composite Software Health Metrics from Heterogeneous Domains: A Comprehensive Framework for Multi-Dimensional Quality Integration

This report synthesizes research on combining heterogeneous software metrics across graph-theoretic, semantic, testing, performance, and concordance domains into a unified health score. Rather than simple normalization and averaging, we examine principled approaches including multi-criteria decision analysis (MCDA), information-theoretic methods, and physics-inspired functional formulations. The analysis draws on decision theory, software engineering standards, and empirical validation methodologies to provide mathematically rigorous and practically implementable recommendations for building health reports that preserve metric semantics while enabling coherent quality assessment.

## Multi-Criteria Decision Analysis: Beyond Weighted Averaging

The fundamental challenge of combining incommensurable metrics is not novel—it is the central problem addressed by multi-criteria decision analysis (MCDA) and multi-objective optimization research. Simple weighted averaging destroys information because it treats all metrics as commensurable (belonging to the same measurement dimension), which your heterogeneous sources are not[1]. MCDA methods provide structured approaches for handling conflicting objectives with different measurement scales.

### The Limitations of Weighted Summation Models

Standard weighted averaging implements a linear additive model of the form \( S = \sum_{i=1}^{n} w_i \cdot x_i \) where weights sum to one[1][4]. This approach makes several problematic assumptions for software quality. First, it assumes **compensatory preference structure**: poor performance on one criterion can be completely offset by excellence in another. For software health, this is demonstrably false—a module with extreme complexity cannot be "fixed" by perfect test coverage alone, because the underlying testability remains compromised[19]. Second, weighted summation assumes **metric independence**, but software metrics exhibit significant intercorrelation; high cyclomatic complexity, deep nesting, and extensive branching create compound complexity where the whole is more dangerous than the sum of parts[19]. Third, simple weighting discards information about the **decision-maker's cardinal preferences**—the difference between "slightly better" and "dramatically better" performance on each criterion[4].

MCDA methods address these limitations through three principal mechanisms. First, they explicitly separate **performance assessment** from **value judgment**: metrics establish how well each component performs on each criterion, while value functions translate those performances into commensurate scores without destroying original information[4]. Second, they accommodate **multi-attribute utility theory (MAUT)** or **value hierarchy theory**, which can express non-linear value curves and interaction terms[17]. Third, they provide **consistency checking** and **sensitivity analysis** to validate that composite rankings are robust across reasonable variations in preference specifications.

### Analytic Hierarchy Process (AHP)

The Analytic Hierarchy Process provides a structured decomposition method particularly suitable for defining hierarchical quality models[2][50]. In AHP, the decision problem is structured as a hierarchy with a goal at the top, criteria and sub-criteria in the middle, and alternatives at the bottom[50]. Rather than directly assigning weights, decision-makers make pairwise comparisons using Saaty's 9-point scale, comparing the relative importance of each criterion pair[50]. These comparisons are aggregated through eigenvector calculation, which derives numerical weights that reflect the decision-maker's (or domain expert's) implicit preference structure[50].

The mathematical procedure involves constructing a pairwise comparison matrix \( A \) where entry \( a_{ij} \) represents the ratio of preference for criterion \( i \) relative to criterion \( j \). The weight vector \( w \) is calculated as the principal eigenvector of this matrix, normalized to sum to one[50]. For your software quality problem, this means you would create pairwise comparisons not of software artifacts themselves, but of the relative importance of different quality dimensions (graph structure, semantic clarity, testing adequacy, performance, concordance).

A worked example from the search results illustrates the process: when comparing camera quality, storage, appearance, and price in a smartphone selection, the eigenvector calculation yields priority weights—storage might emerge as 0.667 (most important), camera 0.193, appearance 0.081, and price 0.058. These weights reflect not arbitrary assignment but the mathematical consequence of consistent preference ratios. For your tool, AHP would mean having domain experts (or developer consensus) specify that, for instance, a 3:1 ratio of importance between cyclomatic complexity versus test coverage, another ratio between graph modularity versus coupling scores, and so forth. The eigenvector method ensures internal consistency and provides a consistency ratio that indicates whether pairwise comparisons contain contradictions[50].

AHP's primary strength for heterogeneous software metrics is that it can incorporate both quantitative metrics (which have natural scales) and qualitative judgments (purpose clarity, role classification confidence) within a unified framework[1][2]. Its limitations include susceptibility to rank reversal (adding alternatives can change the ranking of existing ones) and potential inconsistency in very large hierarchies, though for software quality's typical 4-7 main criteria, these concerns are minimal[50].

### TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)

TOPSIS offers an alternative MCDA method that ranks alternatives by measuring their distance to an ideal (best possible) solution and distance from a negative ideal (worst possible) solution[2][5]. For each criterion, TOPSIS identifies the maximum achievable value (positive ideal \( v_j^+ \)) and minimum achievable value (negative ideal \( v_j^- \)). Each alternative's performance is then normalized and weighted, creating a score that reflects proximity to the ideal[5].

The mathematical formulation involves several steps. First, construct a **decision matrix** \( D \) with rows representing alternatives (code components) and columns representing criteria. Second, normalize the decision matrix to handle different scales[5]. Third, apply criterion weights to the normalized matrix, creating a **weighted normalized decision matrix**[2][5]. Fourth, identify the positive ideal solution \( A^+ = \{v_1^+, v_2^+, \ldots, v_m^+\} \) and negative ideal solution \( A^- = \{v_1^-, v_2^-, \ldots, v_m^-\} \) where the positive ideal consists of best performances and the negative ideal consists of worst performances across all alternatives[5]. Finally, calculate the Euclidean distance from each alternative to both ideals[5]:

\[ S_i^+ = \sqrt{\sum_{j=1}^{n} (v_{ij} - v_j^+)^2} \]

\[ S_i^- = \sqrt{\sum_{j=1}^{n} (v_{ij} - v_j^-)^2} \]

The closeness coefficient \( C_i \) for alternative \( i \) is then[5]:

\[ C_i = \frac{S_i^-}{S_i^+ + S_i^-} \]

where \( C_i \in [0,1] \), with values closer to 1 indicating better performance. A key advantage of TOPSIS is that it naturally handles **Pareto optimality**: an alternative cannot be simultaneously worse than another alternative on all criteria[5][15]. This is valuable for software quality because it prevents pathological cases where a component is genuinely worse in every way (which should trigger prioritization, not mixed signals).

TOPSIS has been successfully applied to software engineering problems, including ETL software selection where AHP weights were calculated and then fed into TOPSIS rankings[2]. The method's strength lies in its intuitive appeal (proximity to ideal solutions) and computational efficiency. However, it assumes that all criterion dimensions can be meaningfully ordered from worst to best, which is less problematic for your quantitative metrics but requires care for categorical concordance states.

### ELECTRE and PROMETHEE: Outranking Methods

ELECTRE (ELimination Et Choix Traduisant la REalité) and PROMETHEE (Preference Ranking Organisation METHod for Enrichment Evaluation) belong to the **outranking** family of MCDA methods, which operate differently from AHP and TOPSIS. Rather than aggregating all criteria into a single score, outranking methods build a preference order through pairwise comparisons of alternatives[1][5]. Alternative A is said to outrank alternative B if A is at least as good as B on most criteria and strictly better on at least some criterion, with no criterion where B is substantially better than A[1].

ELECTRE constructs a **concordance matrix** (how many criteria favor each pairwise comparison) and a **discordance matrix** (how strongly any criterion opposes a comparison)[1]. These are combined using concordance and discordance thresholds to build a directed graph of pairwise preferences, which is then analyzed to identify non-dominated alternatives. PROMETHEE similarly constructs preference flows but uses preference functions that specify for each criterion how much better one alternative must be to create a meaningful preference difference[1].

These methods are particularly valuable when you have **veto criteria**—metrics that, if they reach a threshold failure, invalidate other strengths. For instance, you might define that if cyclomatic complexity exceeds a critical value, a module cannot be considered healthy regardless of other metrics. Outranking methods naturally express such constraints, whereas weighted averaging does not.

The primary limitation of outranking methods for your use case is that they typically produce preference orderings rather than single numerical scores. This is actually an advantage for some applications (it prevents false precision), but if your goal is to produce a unified health score for consumption by AI agents, TOPSIS or AHP may be more practical. However, the **partial order** produced by outranking methods could inform a final health score that reflects genuine incomparability—flagging when two components have different strengths and weaknesses that cannot be reduced to a single ordering.

## Transfer Functions: Mapping Heterogeneous Metrics to Commensurate Scales

The challenge of transfer functions is central to your Lagrangian approach. Once you commit to aggregating metrics, you must map each heterogeneous source into a common **incoherence** or **health** space. The mathematical form of these transfer functions critically affects the resulting composite score, but the literature on software metrics provides limited explicit guidance.

### Sigmoid and Logistic Transfer Functions

Sigmoid functions provide a mathematically principled approach to mapping bounded metrics into normalized scales while preserving sensitivity distinctions[11]. A standard logistic sigmoid has the form[11]:

\[ s(x) = \frac{1}{1 + e^{-k(x-x_0)}} \]

where \( x_0 \) is the inflection point (the metric value at which concern is neutral) and \( k \) controls steepness. Values of \( k > 0 \) map values well below \( x_0 \) toward 0 and values well above \( x_0 \) toward 1, with the transition concentrated around \( x_0 \)[11].

For software metrics, sigmoid transfer functions are attractive because they naturally express **decision thresholds**. For instance, test coverage below 50% might be considered severely problematic (near 0), coverage between 50-80% enters a zone of increasing confidence, and coverage above 80% provides high confidence, all mapped through a smooth function rather than discontinuous levels. The parameter \( k \) can be calibrated from expert opinion or empirical data: if domain experts agree that the transition from "problematic" to "adequate" occurs over a 20% range, you set \( k \) such that the function steepens over that range[11].

A practical advantage: sigmoid functions are **differentiable**, which is essential if you want to apply optimization techniques or sensitivity analysis to your composite score. The derivative \( s'(x) = k \cdot s(x) \cdot (1 - s(x)) \) tells you how much the transferred value changes with small changes in the original metric—a measure of sensitivity that aids calibration.

### Piecewise Linear Transfer Functions

Where domain knowledge provides discrete quality thresholds, piecewise linear functions may be more transparent than sigmoids. For cyclomatic complexity, for instance, common thresholds are: 1-10 (simple), 11-20 (moderate), 21-50 (complex), 50+ (very complex)[33]. A piecewise linear transfer function could map these ranges to incoherence scores directly:

\[ I_{\text{complexity}}(cc) = \begin{cases} 0 & \text{if } cc \leq 10 \\ \frac{cc - 10}{10} & \text{if } 10 < cc \leq 20 \\ \frac{cc - 20}{30} + 0.1 & \text{if } 20 < cc \leq 50 \\ 1 & \text{if } cc > 50 \end{cases} \]

This function maps simple code (cc ≤ 10) to zero incoherence, gradually increases incoherence as complexity grows, and reaches maximum incoherence at the threshold where code becomes empirically unmaintainable. The advantage is transparency: stakeholders can understand exactly what metric values trigger concern. The disadvantage is discontinuous derivatives at breakpoints, which complicates sensitivity analysis.

### Logarithmic and Exponential Transformations

For metrics with **heavy-tailed distributions** (many small values, few extremely large ones), logarithmic transfer functions can compress scale. Test coverage ratios, for instance, often cluster near 70-90% with outliers at both extremes. A logarithmic transform:

\[ I_{\text{coverage}}(c) = \frac{\log(1 + (100 - c))}{\log(101)} \]

maps coverage of 100% to 0 incoherence, coverage of 50% to moderate incoherence, and coverage of 0% to maximum incoherence, with the mapping compressed logarithmically so that the jump from 95% to 90% has smaller impact than the jump from 40% to 35%.

Exponential functions work in the opposite direction: where you want small deviations from a target to be tolerated but large deviations to trigger rapid escalation of concern. For instance, if Betti number b0 (number of connected components) should ideally be 1, you might use:

\[ I_{\text{connectivity}}(b_0) = 1 - e^{-\alpha(b_0 - 1)^2} \]

which maps b0 = 1 to zero incoherence, but exponentially increases incoherence as b0 deviates from 1, reflecting the empirical fact that fragmented component structure has superlinear costs.

### Calibration Against Empirical Data

The critical practical problem is **parameterizing** these transfer functions. The literature on software metrics quality models addresses this partially. The SQALE method, for instance, defines remediation functions for each weakness type—essentially, transfer functions mapping the count of violations to effort (in hours or currency) required to remediate[49]. These are based on expert assessment and, where available, empirical data on how many violations of each type typically appear in projects of different quality levels[49].

For your tool, the calibration strategy should be: (1) collect historical data on code components you have assessed and their outcomes (defect density, maintenance time, developer satisfaction); (2) for each metric, fit a transfer function whose parameters maximize correlation with those outcomes; (3) validate the fit on held-out data. This is the essence of supervised learning, but applied to transfer function design rather than black-box model fitting. The advantage is that interpretability is preserved—you can explain to users why a particular metric value maps to a particular incoherence score.

## Dimensional Architecture: Single Score Versus Pareto Separation

Your Lagrangian approach seeks to reduce all dimensions to a single incoherence functional \( I(C) \) producing a scalar health score. An alternative architectural choice is to maintain **Pareto separation**: compute the vector of incoherence scores across domains \( (I_{\text{struct}}, I_{\text{telic}}, I_{\text{sym}}, I_{\text{bound}}, I_{\text{flow}}) \) and use **Pareto dominance** to characterize which components are genuinely worse versus those that have different strengths and weaknesses[15].

### The Case for Unified Scoring

A single scalar health score offers decisive advantages for operational deployment: it enables immediate prioritization ("fix the 10 worst modules first"), it facilitates trend analysis (is health improving over time?), and it reduces cognitive load on consumers of the report[3][13]. A unified score is also necessary for **composite measure validation**: you can correlate the composite against ground truth outcomes (defect rates, maintenance costs) and demonstrate that the score predicts what matters[3].

The physics analogy supports unification as well. In physics, a Lagrangian does reduce a system with many degrees of freedom to a single functional whose extremization yields equations of motion. Your approach of defining \( I(C) = I_{\text{struct}} + I_{\text{telic}} + I_{\text{sym}} + I_{\text{bound}} + I_{\text{flow}} \) mirrors this: each domain contributes an incoherence term, and the total incoherence characterizes system health.

However, CMS guidance on composite measures emphasizes a critical requirement: even if you produce a single composite score, the component scores must remain **transparent and available**[3]. Composite measures that mask individual component information are prone to masking differences and relationships in the underlying data[3]. This means your report should show the full vector \( (I_{\text{struct}}, I_{\text{telic}}, I_{\text{sym}}, I_{\text{bound}}, I_{\text{flow}}) \) alongside the unified score, enabling AI agents or human analysts to understand how the composite arose.

### The Pareto Approach: Multi-Objective Optimization

Alternatively, you could adopt a **multi-objective optimization** framework that does not reduce to a single score. In this view, a software component defines a point in a 5-dimensional incoherence space. A **Pareto front** is the set of components for which no other component is simultaneously better on all dimensions[15][18]. Components on the Pareto front represent genuine trade-offs—improving one dimension requires accepting degradation in another. Components not on the Pareto front are **dominated**—there exists another component strictly better on all or most dimensions, making it a clear prioritization target[15].

The mathematical definition: a component \( x_1 \) **Pareto dominates** \( x_2 \) if \( x_1 \) is at least as good as \( x_2 \) on all dimensions and strictly better on at least one dimension[15]. The advantage of this approach is that it avoids **false commensurability**—the claim that you can meaningfully add incoherence from different domains. Instead, it acknowledges that some components have lower structural incoherence but higher semantic incoherence, and lets the decision-maker decide whether that trade-off is acceptable.

For AI agents consuming your reports, Pareto separation is powerful: instead of producing a single number, you produce a dominance relation—"this module is worse than that module on every important dimension, so fix it first." This is more informative than a scalar comparison, though it requires algorithms that handle partial orders rather than total orders.

In practice, many organizations adopt **hybrid approaches**: use Pareto analysis to identify dominated (clearly problematic) components for immediate action, and use a composite score to rank the Pareto-efficient set[18]. This combines the decisiveness of a scalar score with the insight of multi-objective reasoning.

## Coupling Terms and Interaction Effects

Physics Lagrangians include **cross-terms** capturing how fields interact: the electromagnetic Lagrangian includes terms coupling the four-potential and the current density. For software metrics, the question is: are there known interaction effects where two weak metrics together are worse than their linear sum?

### Empirical Evidence for Compound Complexity

Yes, empirical research confirms non-linear interactions in software metrics[19]. The most extensively documented is **compound complexity**: a module with high cyclomatic complexity, deep nesting, and extensive branching is far more dangerous than one scoring highly on only one dimension[19]. Testing such code requires exponentially more test cases, as the number of meaningful branch combinations grows beyond practical limits[19].

Additionally, **change coupling and ripple effects** create interactions: components that change frequently together develop implicit coupling not captured in static dependency graphs[19]. A module with moderate complexity and moderate coupling might be safer than one with extreme values in a single dimension, because stability mitigates risk[19].

The practical implication for your Lagrangian formulation: consider adding cross-terms to capture these interactions:

\[ I(C) = I_{\text{struct}} + I_{\text{telic}} + I_{\text{sym}} + I_{\text{bound}} + I_{\text{flow}} + \lambda_1 \cdot I_{\text{struct}} \cdot I_{\text{bound}} + \lambda_2 \cdot I_{\text{flow}} \cdot I_{\text{bound}} \]

The term \( I_{\text{struct}} \cdot I_{\text{bound}} \) captures that high structural complexity combined with low test coverage creates multiplicative risk. The coefficients \( \lambda_1, \lambda_2 \) quantify the strength of these interactions—to be calibrated against empirical defect data.

The complication is that determining these interaction coefficients requires sufficient historical data to fit reliably. A rule of thumb from machine learning: fitting \( n \) interaction terms reliably requires at least \( 10n \) to \( 100n \) training examples[32]. If you have hundreds of components with tracked defect outcomes, interaction fitting is feasible. If not, stick to the additive main effects model.

### Veto Effects and Threshold Interactions

A more pragmatic form of interaction is the **veto**: a metric reaching a critical threshold invalidates the adequacy of other metrics. For instance, you might define that if cyclomatic complexity exceeds 50, the module is "incoherent" regardless of perfect test coverage—because even tested code at that complexity is unmaintainable.

A veto can be modeled as a multiplicative term:

\[ I_{\text{total}}(C) = (1 + V(C)) \cdot I_{\text{additive}}(C) \]

where \( V(C) \) is a veto factor—zero if no threshold is exceeded, but large (say, 10) if critical complexity is reached. This preserves the additive structure but allows catastrophic failure when critical thresholds are crossed.

## Existing Software Quality Frameworks: Lessons Learned

Your question asks what lessons have been learned from existing composite quality models. The major frameworks (SQALE, ISO 25010, Quamoco, CISQ/ISO 5055, SonarQube) offer both theoretical principles and practical insights.

### SQALE: Technical Debt Aggregation

SQALE (Software Quality Assessment based on Life-Cycle Expectations) defines a hierarchical quality model rooted in the software development lifecycle[49]. Quality issues are classified by their lifecycle impact: design quality, requirement quality, etc. Each issue type is assigned a **remediation function** mapping count of violations to estimated effort (in hours or monetary cost) required to fix[49].

The key insight is that SQALE treats aggregation explicitly as **effort estimation**, not just numerical combination[49]. A critical design flaw costs more to remediate than a style violation, so violations are weighted by their remediation effort rather than treating all violations equally[49]. The model then aggregates into an index that can be expressed in monetary terms—"this component contains X hours of remediation work"—making the composite meaningful to non-technical stakeholders[49].

For your tool, this suggests a metric-to-effort transfer function: rather than mapping metrics to abstract "incoherence," map them to estimated remediation effort, which has intrinsic meaning. An alternative health score could be: "expected hours of development time to bring this component to quality standard X."

### Quamoco: Explicit Value Functions and Aggregation

Quamoco applies **Multiple-Attribute Utility/Value Theory (MAUT/MAVT)** to software quality, explicitly separating measurement (how well does the component perform on each criterion?) from valuation (what is the worth of that performance?)[17]. Individual measures feed into product factors, which aggregate into quality attributes, which ultimately map to organizational quality goals[17].

The crucial technical detail: Quamoco uses **component value functions** to explicitly model how performance on each criterion translates into value[17]. These are not linear—a component with coverage 100% is not infinitely better than 99%; diminishing returns apply. The value functions are elicited from stakeholders or fit to empirical data[4][17]. Multiple measures can feed into a single product factor, with aggregation using MAVT principles—again, not simple averaging[17].

The aggregation method in Quamoco is weighted sum after value function transformation:

\[ V = \sum_{i=1}^{n} w_i \cdot v_i(x_i) \]

where \( v_i \) is the value function for criterion \( i \), \( x_i \) is the measured performance, and \( w_i \) are the weights (determined via pairwise comparisons similar to AHP)[17]. This is the mathematically principled version of your intuition: first transform heterogeneous metrics through domain-specific value functions, then aggregate using weighted combination.

### ISO 25010 and CISQ: Standardized Weakness Mapping

ISO/IEC 25010 defines eight quality characteristics (reliability, security, performance efficiency, maintainability, etc.), while CISQ/ISO 5055 operationalizes four of these through **weakness detection** and aggregation[13]. Each weakness (e.g., SQL injection, buffer overflow) is mapped to one or more quality characteristics. The score for each characteristic is computed by counting weaknesses and optionally normalizing by code size[13].

The insight is that weakness-based aggregation is **domain-separable**: you detect weaknesses within each domain (security weaknesses, reliability weaknesses, etc.) using specialized tools, then aggregate weaknesses within each dimension independently. This respects the distinct nature of different quality aspects[13].

For your tool, this suggests a **hierarchical aggregation architecture**: compute incoherence scores for each domain (graph-theoretic, semantic, testing, performance, concordance) using domain-specific methods and transfer functions, then combine domain scores using MCDA methods.

### SonarQube's Pragmatic Approach

SonarQube, widely used in industry, employs weighted averaging of individual measures normalized to 0-100 scales, with configurable weights and thresholds[16]. While not theoretically sophisticated, its practical effectiveness emerges from: (1) extensive calibration against real-world projects; (2) transparency (users see the component measures and weights); (3) integration with development workflows (issues are actionable, not just scores)[16].

A critical lesson: **transparency and actionability matter more than mathematical elegance**. A composite score that users cannot understand or act upon is less valuable than a transparent set of component scores, even if the latter requires more cognitive effort to interpret.

## Information-Theoretic Approaches: Quantifying Metric Contribution and Redundancy

Information theory provides tools to quantify how much new information each metric contributes, avoiding redundancy in aggregation. The key concepts are **entropy**, **mutual information**, and **Kullback-Leibler divergence**.

### Entropy and Uncertainty

For a discrete variable (e.g., a quality state: {defective, at-risk, adequate, excellent}), entropy measures uncertainty:

\[ H(X) = -\sum_{x} P(x) \log P(x) \]

High entropy means the variable is highly unpredictable; low entropy means it clusters on few outcomes. For your composite score, a useful question is: how much does knowing metric \( i \) reduce uncertainty about overall quality outcome?

### Mutual Information: Metric Contribution

Mutual information between a metric \( M_i \) and the outcome \( Y \) (e.g., whether a component develops defects) is:

\[ I(M_i; Y) = H(Y) - H(Y | M_i) \]

This quantifies how much entropy about \( Y \) is reduced by observing \( M_i \). Metrics with high mutual information with outcomes are informative; metrics with low mutual information provide little signal[20][23].

You can use mutual information to **weight metrics automatically**: \( w_i = \frac{I(M_i; Y)}{\sum_j I(M_j; Y)} \). This is the information-theoretic justification for differential weighting—metrics that matter more for predicting outcomes should contribute more to the composite score. The advantage over subjective weighting is that it is empirically grounded: if you have historical data on outcomes, mutual information is objectively computable[20][23].

### Kullback-Leibler Divergence: Distribution Distance

KL divergence measures how much a predicted distribution differs from the true distribution. If your composite score produces a probability distribution over quality outcomes, you can compute KL divergence between the predicted and true distributions, quantifying how well calibrated your metric is[23]. Well-calibrated metrics have low KL divergence to true outcomes; poorly calibrated metrics have high divergence[9].

In practice, for software metrics, KL divergence is relevant for **calibration validation**: after constructing your composite score, test whether a component scored as "80% likely to be defect-free" actually is defect-free 80% of the time. If not, your score is miscalibrated, and you can adjust transfer functions to improve calibration[9].

## Calibration and Validation Methodologies

The ultimate test of any composite metric is predictive validity: does it correlate with outcomes that matter? The literature on software quality metrics provides guidance on validation approaches.

### Ground Truth and Outcome Metrics

First, define ground truth outcomes. Options include: (1) **defect density** (post-release bugs per thousand lines of code); (2) **maintenance time** (hours required to fix issues); (3) **developer satisfaction** (survey-based); (4) **change frequency and difficulty** (volatility of refactoring). Each ground truth has strengths and limitations[22][34].

Defect density is empirically measurable but suffers from the problem that not all defects are equally important—a critical security flaw is one defect, but so is a typo in a comment[34]. Maintenance time requires careful measurement but directly reflects developer experience. Developer satisfaction is subjective but captures what practitioners care about[22].

### Correlation Analysis and Predictive Accuracy

Given ground truth, compute correlation between your composite score and outcomes. For continuous outcomes (maintenance time), use Pearson or Spearman correlation. For categorical outcomes (defect-prone vs. not), use receiver operating characteristic (ROC) curves and area under the curve (AUC)[9][22]. A composite metric with AUC ≥ 0.7 is considered useful for prediction[22].

A sophisticated approach: **cross-validated prediction**. Divide your dataset into training and test sets. On training data, fit your metric's transfer functions and weights to best predict outcomes. On test data (held out during fitting), evaluate predictive accuracy. This prevents overfitting and produces realistic estimates of generalization.

The literature on software defect prediction has established that ensemble methods (combining multiple metrics via voting or stacking) outperform single metrics[32][44]. Similarly, your composite metric should incorporate multiple domains—not trying to squeeze all information into a single formula, but combining informed predictions from different technical perspectives[44].

### Practical Considerations: Effort Awareness

A critical lesson from software metrics research is that actionability matters. A metric that perfectly predicts defect-prone code but identifies 50% of the codebase as "problematic" is useless—developers cannot fix everything[3][34]. Instead, composite metrics should be **effort-aware**: they should rank components by the ratio of benefit (likely bugs prevented) to cost (effort to fix)[43].

This can be incorporated via:

\[ \text{Prioritization} = \frac{\text{Predicted Defect Reduction}}{I(C) \cdot \text{Estimated Remediation Effort}} \]

Components with high expected defect reduction relative to remediation cost float to the top of the prioritization list[43]. This combines your incoherence functional with actionability—the metric not only scores components but suggests which to address first.

## Practical Implementation Recommendations

Synthesizing the research, here are concrete recommendations for building your tool:

**1. Adopt a hierarchical MCDA architecture:**
   - Use **pairwise comparison (AHP-style)** to derive weights for the five domains from domain expert consensus
   - Within each domain, compute incoherence using domain-specific transfer functions
   - Aggregate domain scores via weighted combination (weighted sum or TOPSIS)
   - Produce both the unified score and the component vector for transparency

**2. Design transfer functions as follows:**
   - For **bounded metrics** (coverage percentages, Q-scores): use sigmoid functions with inflection points at expert-defined thresholds
   - For **count metrics** (test violations, dead code ratio): use logarithmic or piecewise linear functions reflecting empirical concern thresholds
   - For **graph metrics** (Betti numbers, PageRank): use relative scales within your codebase (0 = best observed, 1 = worst observed) rather than absolute thresholds
   - **Calibrate parameters** using historical data: fit transfer functions to maximize correlation with defect outcomes

**3. Model interaction effects pragmatically:**
   - If you have sufficient historical data (hundreds of components), fit multiplicative or additive cross-terms
   - Otherwise, use simple veto thresholds for critical metrics (e.g., complexity exceeding absolute limits)
   - Document all interaction terms explicitly in the report

**4. Validate via ground truth:**
   - Collect or obtain data on component outcomes (defects, maintenance time, developer feedback)
   - Use cross-validated correlation analysis to estimate predictive accuracy
   - If AUC < 0.7, revisit weight assignment and transfer functions
   - Report confidence intervals around composite scores, not point estimates

**5. Design reports for AI consumption:**
   - Produce both machine-readable (JSON) and human-readable (HTML/PDF) formats
   - Include the full metric vector: incoherence scores for each domain, not just the unified score
   - Provide confidence/uncertainty measures, not just point values
   - Include dominance relations: which components are Pareto-dominated (clear improvement targets)
   - Rank components by effort-adjusted priority, not just health score

**6. Iterate with stakeholder feedback:**
   - After deploying the metric, solicit feedback from developers on its usefulness
   - Track whether recommended remediations actually reduce downstream defects
   - Use empirical feedback to refine weights, transfer functions, and interaction terms
   - Treat the metric as a hypothesis to be tested, not a final truth

## Conclusion

Combining heterogeneous software metrics into a unified health score requires moving beyond simple normalization and averaging. Multi-criteria decision analysis methods—particularly AHP for weight derivation and TOPSIS or weighted value functions for aggregation—provide mathematically principled frameworks that preserve metric semantics while enabling coherent integration. Transfer functions (sigmoids, piecewise linear, logarithmic) map domain-specific metrics into commensurate incoherence scales, with calibration against empirical outcome data ensuring predictive validity.

Your Lagrangian approach is mathematically sound and aligns with established frameworks like Quamoco. The addition of cross-terms to capture compound complexity and interaction effects is justified by empirical research showing non-linear risks. Information-theoretic tools (mutual information, KL divergence) enable automatic weighting and validation of calibration without requiring subjective judgment.

The deepest lesson from existing frameworks like SQALE, ISO 25010, and SonarQube is that **transparency and actionability matter as much as mathematical sophistication**. A health report that clearly shows what contributes to the composite score, acknowledges uncertainty, and suggests specific actions produces value in practice—regardless of whether it uses AHP or weighted averaging under the hood.

For an AI agent consuming the output, provide the full incoherence vector alongside the unified score, include Pareto dominance analysis to identify unambiguously problematic components, and rank remediation priorities by effort-adjusted benefit. This combination—mathematical rigor in aggregation, transparent decomposition, and practical actionability—produces composite metrics that are both theoretically sound and practically useful.

---

## Citations

1. https://www.1000minds.com/decision-making/what-is-mcdm-mcda
2. https://pmc.ncbi.nlm.nih.gov/articles/PMC4775722/
3. https://www.cms.gov/medicare/quality-initiatives-patient-assessment-instruments/mms/downloads/composite-measures.pdf
4. https://analysisfunction.civilservice.gov.uk/policy-store/an-introductory-guide-to-mcda/
5. https://pubs.sciepub.com/ajie/4/1/2/
6. https://ui.adsabs.harvard.edu/abs/2024SoftX..2601660R/abstract
7. https://www.iieta.org/journals/isi/paper/10.18280/isi.290416
8. https://jedm.educationaldatamining.org/index.php/JEDM/article/download/714/196
9. https://arxiv.org/html/2504.12051v1
10. https://pmc.ncbi.nlm.nih.gov/articles/PMC12539960/
11. https://www.biomath.bg/s%20markov%20publications/B2015-Kyurkchiev_Markov_Lambert.pdf
12. https://users.monash.edu.au/~gholamrh/lab/hon2015-nhat-thesis.pdf
13. https://www.it-cisq.org/wp-content/uploads/sites/6/2022/09/Measuring-the-Structural-Quality-of-Software-Systems.pdf
14. https://dl.acm.org/doi/10.1145/1985793.1985977
15. https://en.wikipedia.org/wiki/Multi-objective_optimization
16. https://community.sonarsource.com/t/sonarqube-enterprise-architecture-compliant-to-iso-25010-square-standard/2617
17. https://teamscale.com/hubfs/26978363/Publications/2012-the-quamoco-product-quality-modelling-and-assessment-approach.pdf
18. https://www.egr.msu.edu/~kdeb/papers/c2016001.pdf
19. https://www.in-com.com/blog/software-performance-metrics-you-need-to-track/
20. https://pmc.ncbi.nlm.nih.gov/articles/PMC7517148/
21. https://pmc.ncbi.nlm.nih.gov/articles/PMC11157603/
22. https://getdx.com/blog/software-quality-metrics/
23. https://tungmphung.com/information-theory-concepts-entropy-mutual-information-kl-divergence-and-more/
24. https://wires.onlinelibrary.wiley.com/doi/10.1002/widm.70022
25. https://encord.com/blog/dimentionality-reduction-techniques-machine-learning/
26. https://en.wikipedia.org/wiki/Lagrangian_(field_theory)
27. https://arxiv.org/abs/2205.02521
28. https://www.geeksforgeeks.org/machine-learning/dimensionality-reduction/
29. https://www.diva-portal.org/smash/get/diva2:1232457/FULLTEXT01.pdf
30. https://link.aps.org/doi/10.1103/PhysRevApplied.19.044090
31. https://arxiv.org/abs/1402.3873
32. https://arxiv.org/abs/2101.10658
33. https://www.geeksforgeeks.org/dsa/cyclomatic-complexity/
34. https://www.inf.usi.ch/faculty/lanza/Hose/hose1p.pdf
35. https://vadimkravcenko.com/shorts/project-estimates/
36. https://linearb.io/blog/cyclomatic-complexity
37. https://www2.perimeterinstitute.ca/personal/jfeldbrugge/Job_Feldbrugge_files/Literature/1908.01619.pdf
38. https://pmc.ncbi.nlm.nih.gov/articles/PMC3984771/
39. https://pmc.ncbi.nlm.nih.gov/articles/PMC1482622/
40. https://en.wikipedia.org/wiki/Betti_number
41. https://memgraph.com/blog/betweenness-centrality-and-other-centrality-measures-network-analysis
42. https://link.aps.org/doi/10.1103/7sjf-c6jz
43. http://www.diva-portal.org/smash/get/diva2:1580451/FULLTEXT01.pdf
44. https://pmc.ncbi.nlm.nih.gov/articles/PMC12527178/
45. https://arxiv.org/abs/2403.02780
46. https://web.math.utk.edu/~cwagner/papers/weighted.pdf
47. https://www.cureusjournals.com/articles/11375-machine-learning-approaches-in-software-fault-prediction-a-review
48. https://optimization-online.org/wp-content/uploads/2024/03/Orthonormal_Data_Collaboration.pdf
49. https://www.agilealliance.org/wp-content/uploads/2016/01/SQALE-Meaningful-Insights-into-your-Technical-Debt.pdf
50. https://www.6sigma.us/six-sigma-in-focus/analytic-hierarchy-process-ahp/

---

## Usage Stats

- Input tokens: 669
- Output tokens: 7637
