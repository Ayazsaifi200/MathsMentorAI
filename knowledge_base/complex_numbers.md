# Complex Numbers

## Basic Definitions

### Complex Number
z = a + ib

Where:
- a = real part = Re(z)
- b = imaginary part = Im(z)
- i = imaginary unit, i² = -1

### Imaginary Unit
i = √(-1)
i² = -1
i³ = -i
i⁴ = 1

### Equality of Complex Numbers
a + ib = c + id ⟺ a = c and b = d

### Conjugate
If z = a + ib, then z̄ = a - ib

**Properties**:
1. z + z̄ = 2Re(z) = 2a
2. z - z̄ = 2iIm(z) = 2ib
3. zz̄ = a² + b² (always real and ≥ 0)
4. (z̄) = z
5. (z₁ + z₂) = z̄₁ + z̄₂
6. (z₁z₂) = z̄₁z̄₂

## Algebra of Complex Numbers

### Addition
(a + ib) + (c + id) = (a + c) + i(b + d)

**Properties**: Commutative, Associative

### Subtraction
(a + ib) - (c + id) = (a - c) + i(b - d)

### Multiplication
(a + ib)(c + id) = (ac - bd) + i(ad + bc)

**Properties**: Commutative, Associative, Distributive

### Division
(a + ib)/(c + id) = [(a + ib)(c - id)]/[(c + id)(c - id)]
                   = [(ac + bd) + i(bc - ad)]/(c² + d²)

## Modulus and Argument

### Modulus
|z| = |a + ib| = √(a² + b²)

**Properties**:
1. |z| ≥ 0, |z| = 0 ⟺ z = 0
2. |z̄| = |z|
3. |z₁z₂| = |z₁||z₂|
4. |z₁/z₂| = |z₁|/|z₂|
5. |z₁ + z₂| ≤ |z₁| + |z₂| (Triangular inequality)
6. ||z₁| - |z₂|| ≤ |z₁ - z₂|

### Argument
arg(z) = θ = tan⁻¹(b/a)

Principal argument: -π < θ ≤ π

**Properties**:
1. arg(z₁z₂) = arg(z₁) + arg(z₂)
2. arg(z₁/z₂) = arg(z₁) - arg(z₂)
3. arg(z̄) = -arg(z)
4. arg(zⁿ) = n arg(z)

## Polar Form

### Representation
z = r(cos θ + i sin θ) = r cis θ

Where:
- r = |z| (modulus)
- θ = arg(z) (argument)

### Conversion
- From rectangular: r = √(a² + b²), θ = tan⁻¹(b/a)
- To rectangular: a = r cos θ, b = r sin θ

### Euler's Formula
e^(iθ) = cos θ + i sin θ

Therefore: z = re^(iθ)

## De Moivre's Theorem

### Statement
(cos θ + i sin θ)ⁿ = cos(nθ) + i sin(nθ)

Or: (cis θ)ⁿ = cis(nθ)

### Applications
1. Finding powers of complex numbers
2. Finding roots of complex numbers
3. Proving trigonometric identities

## Roots of Complex Numbers

### nth Roots of Unity
Solutions of zⁿ = 1:

zₖ = cos(2πk/n) + i sin(2πk/n), k = 0, 1, 2, ..., n-1

Or: zₖ = e^(2πik/n)

**Properties**:
1. Sum of nth roots of unity = 0
2. Product of nth roots of unity = (-1)^(n-1)
3. Roots are vertices of regular n-gon on unit circle

### Cube Roots of Unity
1, ω, ω²

Where ω = e^(2πi/3) = cos(2π/3) + i sin(2π/3) = -1/2 + i√3/2

**Properties**:
1. 1 + ω + ω² = 0
2. ω³ = 1
3. ω² = ω̄

### nth Roots of Complex Number
For z = r(cos θ + i sin θ), the n roots are:

zₖ = r^(1/n)[cos((θ + 2πk)/n) + i sin((θ + 2πk)/n)]

k = 0, 1, 2, ..., n-1

## Quadratic Equations with Complex Coefficients

### General Form
az² + bz + c = 0

### Solution
z = (-b ± √(b² - 4ac))/(2a)

### Nature of Roots
- If coefficients are real:
  - Discriminant > 0: Two distinct real roots
  - Discriminant = 0: One repeated real root
  - Discriminant < 0: Two complex conjugate roots

## Geometric Representation

### Argand Plane
Complex number z = a + ib represented as point (a, b)

### Distance
Distance between z₁ and z₂:
|z₁ - z₂| = √[(a₁-a₂)² + (b₁-b₂)²]

### Collinearity
z₁, z₂, z₃ are collinear if:
|(z₁ - z₃)/(z₂ - z₃)| is purely real

## Important Loci

### Circle
|z - z₀| = r
Circle with center z₀ and radius r

### Perpendicular Bisector
|z - z₁| = |z - z₂|
Perpendicular bisector of line joining z₁ and z₂

### Apollonius Circle
|z - z₁|/|z - z₂| = k (k ≠ 1)

### Half-Plane
Re(z) > a or Im(z) > b

## Triangle Inequality

### Basic Form
|z₁ + z₂| ≤ |z₁| + |z₂|

Equality when arg(z₁) = arg(z₂)

### Extended Forms
1. |z₁ - z₂| ≥ ||z₁| - |z₂||
2. |z₁ + z₂ + ... + zₙ| ≤ |z₁| + |z₂| + ... + |zₙ|

## Important Formulas

### Powers of i
i¹ = i
i² = -1
i³ = -i
i⁴ = 1
i^(4n+k) = i^k

### Rotation
Multiplication by e^(iθ) rotates by angle θ

### Reflection
- About real axis: z → z̄
- About imaginary axis: z → -z̄
- About origin: z → -z

## Logarithm of Complex Number

### Definition
ln(z) = ln|z| + i arg(z)

### General Form
ln(z) = ln|z| + i(arg(z) + 2nπ), n ∈ Z

## Applications

### Solving Equations
Use polar form and De Moivre's theorem

### Trigonometric Identities
Express sin θ, cos θ in exponential form

### Integration and Differentiation
Use complex exponentials for simplification
