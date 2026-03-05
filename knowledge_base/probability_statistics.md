# Probability and Statistics

## Basic Probability

### Fundamental Concepts
- **Sample Space (S)**: Set of all possible outcomes
- **Event (E)**: Subset of sample space
- **Probability**: P(E) = n(E)/n(S), where 0 ≤ P(E) ≤ 1

### Probability Axioms
1. P(S) = 1
2. 0 ≤ P(E) ≤ 1 for any event E
3. For mutually exclusive events: P(A ∪ B) = P(A) + P(B)

### Complement Rule
P(A') = 1 - P(A)

Where A' is the complement of A

## Probability Rules

### Addition Rule
P(A ∪ B) = P(A) + P(B) - P(A ∩ B)

For mutually exclusive events:
P(A ∪ B) = P(A) + P(B)

### Multiplication Rule
For independent events:
P(A ∩ B) = P(A) × P(B)

For dependent events:
P(A ∩ B) = P(A) × P(B|A)

### Conditional Probability
P(B|A) = P(A ∩ B) / P(A), if P(A) > 0

## Bayes' Theorem

P(A|B) = [P(B|A) × P(A)] / P(B)

Extended form:
P(Aᵢ|B) = [P(B|Aᵢ) × P(Aᵢ)] / Σ[P(B|Aⱼ) × P(Aⱼ)]

## Combinatorics

### Permutations
Number of ways to arrange n objects taken r at a time:
P(n, r) = n!/(n-r)!

Circular permutations: (n-1)!

### Combinations
Number of ways to select r objects from n objects:
C(n, r) = n!/(r!(n-r)!)

### Important Identities
1. C(n, r) = C(n, n-r)
2. C(n, r) + C(n, r-1) = C(n+1, r)
3. C(n, 0) + C(n, 1) + ... + C(n, n) = 2ⁿ

## Probability Distributions

### Binomial Distribution
For n independent trials with probability p of success:
P(X = r) = C(n, r) × pʳ × (1-p)ⁿ⁻ʳ

**Mean**: μ = np
**Variance**: σ² = np(1-p)

### Poisson Distribution
P(X = r) = (e⁻λ × λʳ) / r!

Where λ is the average rate

**Mean**: μ = λ
**Variance**: σ² = λ

### Normal Distribution
Probability density function:
f(x) = (1/(σ√(2π))) × e^(-(x-μ)²/(2σ²))

**Standard Normal Distribution**: μ = 0, σ = 1

**Z-score**: Z = (X - μ)/σ

## Statistics

### Measures of Central Tendency

#### Mean
Arithmetic mean: x̄ = (Σxᵢ)/n

Weighted mean: x̄ = (Σwᵢxᵢ)/(Σwᵢ)

#### Median
- Middle value when data is ordered
- For even n: average of two middle values

#### Mode
- Most frequently occurring value

### Measures of Dispersion

#### Range
Range = Maximum value - Minimum value

#### Variance
Sample variance: s² = Σ(xᵢ - x̄)²/(n-1)

Population variance: σ² = Σ(xᵢ - μ)²/n

#### Standard Deviation
s = √(variance)

#### Coefficient of Variation
CV = (s/x̄) × 100%

### Correlation and Regression

#### Correlation Coefficient
r = Σ[(xᵢ - x̄)(yᵢ - ȳ)] / √[Σ(xᵢ - x̄)² × Σ(yᵢ - ȳ)²]

Where -1 ≤ r ≤ 1

#### Linear Regression
y = a + bx

Where:
- b = r × (sᵧ/sₓ)
- a = ȳ - bx̄

## Random Variables

### Expected Value
E(X) = Σ xᵢ × P(xᵢ) for discrete
E(X) = ∫ x × f(x) dx for continuous

### Properties
1. E(aX + b) = aE(X) + b
2. E(X + Y) = E(X) + E(Y)
3. If X and Y are independent: E(XY) = E(X) × E(Y)

### Variance
Var(X) = E[(X - μ)²] = E(X²) - [E(X)]²

### Properties
1. Var(aX + b) = a²Var(X)
2. If X and Y are independent: Var(X + Y) = Var(X) + Var(Y)

## Hypothesis Testing

### Null Hypothesis (H₀)
Statement to be tested

### Alternative Hypothesis (H₁)
Statement accepted if H₀ is rejected

### Type I Error
Rejecting H₀ when it is true (α = significance level)

### Type II Error
Accepting H₀ when it is false (β)

### Z-test
Z = (x̄ - μ)/(σ/√n)

### t-test
t = (x̄ - μ)/(s/√n)

Used when population variance is unknown
