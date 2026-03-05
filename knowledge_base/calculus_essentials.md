# Calculus Essentials

## Limits

### Basic Limits
1. lim(x→a) c = c (constant)
2. lim(x→a) x = a
3. lim(x→a) xⁿ = aⁿ

### Limit Laws
1. lim[f(x) + g(x)] = lim f(x) + lim g(x)
2. lim[f(x) × g(x)] = lim f(x) × lim g(x)
3. lim[f(x)/g(x)] = lim f(x) / lim g(x), if lim g(x) ≠ 0

### Important Limits
1. lim(x→0) (sin x)/x = 1
2. lim(x→0) (1 - cos x)/x = 0
3. lim(x→∞) (1 + 1/x)ˣ = e
4. lim(x→0) (eˣ - 1)/x = 1
5. lim(x→0) (aˣ - 1)/x = ln(a)

### L'Hôpital's Rule
If lim f(x)/g(x) gives 0/0 or ∞/∞:
lim f(x)/g(x) = lim f'(x)/g'(x)

## Differentiation

### Basic Derivatives
1. d/dx (c) = 0
2. d/dx (x) = 1
3. d/dx (xⁿ) = nxⁿ⁻¹
4. d/dx (eˣ) = eˣ
5. d/dx (aˣ) = aˣ ln(a)
6. d/dx (ln x) = 1/x
7. d/dx (log_a x) = 1/(x ln a)

### Trigonometric Derivatives
1. d/dx (sin x) = cos x
2. d/dx (cos x) = -sin x
3. d/dx (tan x) = sec² x
4. d/dx (cot x) = -csc² x
5. d/dx (sec x) = sec x tan x
6. d/dx (csc x) = -csc x cot x

### Inverse Trigonometric Derivatives
1. d/dx (sin⁻¹ x) = 1/√(1-x²)
2. d/dx (cos⁻¹ x) = -1/√(1-x²)
3. d/dx (tan⁻¹ x) = 1/(1+x²)
4. d/dx (cot⁻¹ x) = -1/(1+x²)

### Differentiation Rules
1. **Product Rule**: d/dx[f(x)g(x)] = f'(x)g(x) + f(x)g'(x)
2. **Quotient Rule**: d/dx[f(x)/g(x)] = [f'(x)g(x) - f(x)g'(x)]/[g(x)]²
3. **Chain Rule**: d/dx[f(g(x))] = f'(g(x)) × g'(x)

## Integration

### Basic Integrals
1. ∫ dx = x + C
2. ∫ xⁿ dx = xⁿ⁺¹/(n+1) + C, n ≠ -1
3. ∫ (1/x) dx = ln|x| + C
4. ∫ eˣ dx = eˣ + C
5. ∫ aˣ dx = aˣ/ln(a) + C

### Trigonometric Integrals
1. ∫ sin x dx = -cos x + C
2. ∫ cos x dx = sin x + C
3. ∫ sec² x dx = tan x + C
4. ∫ csc² x dx = -cot x + C
5. ∫ sec x tan x dx = sec x + C
6. ∫ tan x dx = -ln|cos x| + C = ln|sec x| + C

### Integration Techniques

#### Substitution Method
If f(x) = g(h(x))h'(x), then:
∫ f(x) dx = ∫ g(u) du, where u = h(x)

#### Integration by Parts
∫ u dv = uv - ∫ v du

Choose u using ILATE:
- I: Inverse trig
- L: Logarithmic
- A: Algebraic
- T: Trigonometric
- E: Exponential

#### Partial Fractions
For rational functions P(x)/Q(x):
1. Ensure degree(P) < degree(Q)
2. Factor Q(x)
3. Decompose into partial fractions
4. Integrate each term

### Definite Integrals

∫[a to b] f(x) dx = F(b) - F(a)

Where F'(x) = f(x)

### Properties
1. ∫[a to b] f(x) dx = -∫[b to a] f(x) dx
2. ∫[a to b] f(x) dx = ∫[a to c] f(x) dx + ∫[c to b] f(x) dx
3. ∫[a to b] [f(x) ± g(x)] dx = ∫[a to b] f(x) dx ± ∫[a to b] g(x) dx

## Applications of Derivatives

### Maxima and Minima
1. Find critical points: f'(x) = 0
2. Test using:
   - First derivative test
   - Second derivative test: f''(x) < 0 → maximum, f''(x) > 0 → minimum

### Rate of Change
dy/dx represents instantaneous rate of change of y with respect to x

### Tangent and Normal
At point (x₁, y₁):
- Tangent: y - y₁ = f'(x₁)(x - x₁)
- Normal: y - y₁ = -1/f'(x₁) × (x - x₁)

## Applications of Integrals

### Area Under Curve
Area = ∫[a to b] f(x) dx

### Area Between Curves
Area = ∫[a to b] |f(x) - g(x)| dx

### Volume of Revolution
About x-axis: V = π∫[a to b] [f(x)]² dx

About y-axis: V = π∫[c to d] [g(y)]² dy
