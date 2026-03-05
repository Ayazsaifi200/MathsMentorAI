# Differential Equations

## Introduction

A differential equation is an equation involving derivatives of an unknown function.

### Order and Degree
- **Order**: The highest order derivative present
- **Degree**: The power of the highest order derivative (when equation is polynomial in derivatives)

Example: (d²y/dx²)³ + (dy/dx)² + y = 0
- Order = 2, Degree = 3

## Ordinary Differential Equations (ODEs)

### First Order, First Degree

#### Variable Separable
Form: f(x)dx + g(y)dy = 0

Solution: ∫f(x)dx + ∫g(y)dy = C

Example: dy/dx = x²y → dy/y = x²dx → ln|y| = x³/3 + C

#### Homogeneous Differential Equations
Form: dy/dx = f(y/x) or M(x,y)dx + N(x,y)dy = 0 where M, N are homogeneous of same degree

Substitution: y = vx, so dy/dx = v + x(dv/dx)

Steps:
1. Substitute y = vx
2. Separate variables v and x
3. Integrate both sides
4. Replace v = y/x

#### Linear Differential Equations
Form: dy/dx + P(x)y = Q(x)

Integrating Factor (IF): μ = e^(∫P(x)dx)

Solution: y × IF = ∫(Q(x) × IF)dx + C

Example: dy/dx + y/x = x²
- P(x) = 1/x, Q(x) = x²
- IF = e^(∫1/x dx) = e^(ln x) = x
- Solution: yx = ∫x³ dx = x⁴/4 + C

#### Exact Differential Equations
Form: M(x,y)dx + N(x,y)dy = 0 is exact if ∂M/∂y = ∂N/∂x

Solution: ∫M dx (treating y as constant) + ∫(terms in N not containing x) dy = C

### Bernoulli's Equation
Form: dy/dx + P(x)y = Q(x)yⁿ, where n ≠ 0, 1

Substitution: v = y^(1-n), transforms to linear equation:
dv/dx + (1-n)P(x)v = (1-n)Q(x)

## Second Order Linear ODEs

### Homogeneous with Constant Coefficients
Form: ay'' + by' + cy = 0

Auxiliary equation: am² + bm + c = 0

Cases:
1. **Distinct real roots** (m₁ ≠ m₂): y = C₁e^(m₁x) + C₂e^(m₂x)
2. **Repeated roots** (m₁ = m₂ = m): y = (C₁ + C₂x)e^(mx)
3. **Complex roots** (m = α ± iβ): y = e^(αx)(C₁cos(βx) + C₂sin(βx))

### Non-Homogeneous: Method of Particular Integrals
Form: ay'' + by' + cy = f(x)

General solution: y = Complementary Function (CF) + Particular Integral (PI)

#### PI for common f(x):
1. f(x) = e^(kx): PI = e^(kx)/φ(k), where φ(D) = aD² + bD + c
2. f(x) = sin(kx) or cos(kx): Replace D² = -k²
3. f(x) = xⁿ (polynomial): Use expansion of 1/φ(D)

## Applications in JEE

### Growth and Decay
dN/dt = kN → N = N₀e^(kt)
- k > 0: Exponential growth
- k < 0: Exponential decay

### Newton's Law of Cooling
dT/dt = -k(T - T₀) → T = T₀ + (Tᵢ - T₀)e^(-kt)

### Orthogonal Trajectories
Given family of curves F(x, y, c) = 0:
1. Find dy/dx from the family
2. Replace dy/dx with -dx/dy
3. Solve the resulting ODE

## Formation of Differential Equations

To form a DE from a family of curves with n parameters:
1. Differentiate n times
2. Eliminate all n parameters

Example: y = Ae^x + Be^(-x) has 2 parameters
- y' = Ae^x - Be^(-x)
- y'' = Ae^x + Be^(-x) = y
- DE: y'' - y = 0

## Important JEE Tips

1. Always check if the equation is separable first — it's the simplest method
2. For homogeneous equations, the substitution y = vx always works
3. The integrating factor method is powerful for linear first-order ODEs
4. In JEE, most second-order problems involve constant coefficients
5. Remember to apply initial/boundary conditions after finding the general solution
6. The degree is defined only when the DE is polynomial in its derivatives
7. Common mistake: forgetting to add the constant of integration C
