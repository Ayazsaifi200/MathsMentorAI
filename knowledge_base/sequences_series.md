# Sequences and Series

## Arithmetic Progression (AP)

### Definition
A sequence where the difference between consecutive terms is constant.

General term: aₙ = a + (n-1)d
- a = first term
- d = common difference
- n = number of terms

### Sum of n Terms
Sₙ = n/2 × [2a + (n-1)d]
Sₙ = n/2 × (a + l), where l = last term

### Properties
1. If a, b, c are in AP, then 2b = a + c (b is the arithmetic mean)
2. Arithmetic Mean of a and b: AM = (a + b)/2
3. If a₁, a₂, ..., aₙ are in AP, then aᵢ + aₙ₊₁₋ᵢ = a₁ + aₙ for all i
4. Common difference: d = aₙ - aₙ₋₁

### Inserting n Arithmetic Means Between a and b
Common difference: d = (b - a)/(n + 1)
Means: a + d, a + 2d, ..., a + nd

## Geometric Progression (GP)

### Definition
A sequence where the ratio between consecutive terms is constant.

General term: aₙ = arⁿ⁻¹
- a = first term
- r = common ratio

### Sum of n Terms
- If r ≠ 1: Sₙ = a(1 - rⁿ)/(1 - r) = a(rⁿ - 1)/(r - 1)
- If r = 1: Sₙ = na

### Sum to Infinity (|r| < 1)
S∞ = a/(1 - r)

### Properties
1. If a, b, c are in GP, then b² = ac (b is the geometric mean)
2. Geometric Mean of a and b: GM = √(ab)
3. Product of n terms: P = (a₁ × aₙ)^(n/2)
4. For three terms in GP, take: a/r, a, ar
5. For four terms in GP, take: a/r³, a/r, ar, ar³

## Harmonic Progression (HP)

### Definition
A sequence whose reciprocals form an AP.

If a₁, a₂, a₃, ... are in HP, then 1/a₁, 1/a₂, 1/a₃, ... are in AP.

### Harmonic Mean
HM of a and b: HM = 2ab/(a + b)

### Relation Between AM, GM, HM
For positive numbers a and b:
- AM ≥ GM ≥ HM
- AM × HM = GM²
- Equality holds when a = b

## Arithmetico-Geometric Progression (AGP)

### Definition
A sequence where each term is the product of corresponding AP and GP terms.
Form: ab, (a+d)br, (a+2d)br², ...

### Sum of n Terms
Sₙ = ab/(1-r) + dbr(1-rⁿ⁻¹)/((1-r)²) - (a+(n-1)d)brⁿ/(1-r)

### Sum to Infinity (|r| < 1)
S∞ = ab/(1-r) + dbr/(1-r)²

## Special Series and Summations

### Sum of First n Natural Numbers
Σk = n(n+1)/2

### Sum of Squares
Σk² = n(n+1)(2n+1)/6

### Sum of Cubes
Σk³ = [n(n+1)/2]² = (Σk)²

### Sum of Powers
Σk⁴ = n(n+1)(2n+1)(3n²+3n-1)/30

### Telescoping Series
Σ[f(k) - f(k+1)] = f(1) - f(n+1)

Method of differences: If tₙ = f(n) - f(n-1), then Sₙ = f(n) - f(0)

### Partial Fractions in Series
1/(k(k+1)) = 1/k - 1/(k+1)
1/(k(k+1)(k+2)) = (1/2)[1/(k(k+1)) - 1/((k+1)(k+2))]

## Convergence Tests

### Geometric Series
Σarⁿ converges if |r| < 1, diverges if |r| ≥ 1

### Ratio Test
If lim|aₙ₊₁/aₙ| = L:
- L < 1: Converges
- L > 1: Diverges
- L = 1: Inconclusive

### Comparison Test
If 0 ≤ aₙ ≤ bₙ:
- If Σbₙ converges, then Σaₙ converges
- If Σaₙ diverges, then Σbₙ diverges

## Inequalities Involving Sequences

### AM-GM Inequality
For positive numbers a₁, a₂, ..., aₙ:
(a₁ + a₂ + ... + aₙ)/n ≥ (a₁ × a₂ × ... × aₙ)^(1/n)

### Cauchy-Schwarz Inequality
(Σaᵢbᵢ)² ≤ (Σaᵢ²)(Σbᵢ²)

### Power Mean Inequality
HM ≤ GM ≤ AM ≤ QM (Quadratic Mean)

## Important JEE Tips

1. For problems involving 3 terms in AP, take: a-d, a, a+d
2. For problems involving 3 terms in GP, take: a/r, a, ar
3. The AM-GM inequality is extremely powerful for optimization problems
4. Telescoping is the key technique for summing series with partial fractions
5. Always check whether a series is AP, GP, or AGP before attempting summation
6. Σk³ = (Σk)² is a frequently tested identity
7. For sum to infinity of GP, always verify |r| < 1
8. When finding the nth term from Sₙ: tₙ = Sₙ - Sₙ₋₁ (for n ≥ 2), t₁ = S₁
