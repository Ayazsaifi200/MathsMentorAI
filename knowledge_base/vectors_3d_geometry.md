# Vectors and 3D Geometry

## Vectors - Basic Concepts

### Vector Definition
A quantity with both magnitude and direction

Notation: **a**, ā, or →a

### Position Vector
Vector from origin to point P(x, y, z):
**r** = x**i** + y**j** + z**k**

Where **i**, **j**, **k** are unit vectors along x, y, z axes

### Magnitude
|**a**| = √(x² + y² + z²)

For **a** = x**i** + y**j** + z**k**

### Unit Vector
â = **a**/|**a**|

Magnitude = 1, same direction as **a**

### Zero Vector
**0** = 0**i** + 0**j** + 0**k**
Magnitude = 0, no specific direction

## Vector Operations

### Addition
**a** + **b** = (a₁+b₁)**i** + (a₂+b₂)**j** + (a₃+b₃)**k**

**Properties**:
1. Commutative: **a** + **b** = **b** + **a**
2. Associative: (**a** + **b**) + **c** = **a** + (**b** + **c**)
3. **a** + **0** = **a**

### Subtraction
**a** - **b** = (a₁-b₁)**i** + (a₂-b₂)**j** + (a₃-b₃)**k**

### Scalar Multiplication
k**a** = ka₁**i** + ka₂**j** + ka₃**k**

**Properties**:
1. k(m**a**) = (km)**a**
2. (k+m)**a** = k**a** + m**a**
3. k(**a** + **b**) = k**a** + k**b**

### Section Formula
Point dividing line joining A(**a**) and B(**b**) in ratio m:n:

**Internal Division**: **r** = (m**b** + n**a**)/(m+n)

**External Division**: **r** = (m**b** - n**a**)/(m-n)

## Dot Product (Scalar Product)

### Definition
**a** · **b** = |**a**| |**b**| cos θ

Where θ is angle between vectors

### Component Form
**a** · **b** = a₁b₁ + a₂b₂ + a₃b₃

### Properties
1. Commutative: **a** · **b** = **b** · **a**
2. Distributive: **a** · (**b** + **c**) = **a** · **b** + **a** · **c**
3. **a** · **a** = |**a**|²
4. **i** · **i** = **j** · **j** = **k** · **k** = 1
5. **i** · **j** = **j** · **k** = **k** · **i** = 0

### Angle Between Vectors
cos θ = (**a** · **b**)/(|**a**| |**b**|)

### Perpendicular Vectors
**a** ⊥ **b** ⟺ **a** · **b** = 0

### Projection
Projection of **a** on **b** = (**a** · **b**)/|**b**|

## Cross Product (Vector Product)

### Definition
|**a** × **b**| = |**a**| |**b**| sin θ

Direction: perpendicular to both **a** and **b** (right-hand rule)

### Component Form
**a** × **b** = |**i**  **j**  **k**|
              |a₁  a₂  a₃|
              |b₁  b₂  b₃|

= (a₂b₃ - a₃b₂)**i** - (a₁b₃ - a₃b₁)**j** + (a₁b₂ - a₂b₁)**k**

### Properties
1. Not commutative: **a** × **b** = -**b** × **a**
2. Distributive: **a** × (**b** + **c**) = **a** × **b** + **a** × **c**
3. **a** × **a** = **0**
4. **i** × **j** = **k**, **j** × **k** = **i**, **k** × **i** = **j**
5. **j** × **i** = -**k**, **k** × **j** = -**i**, **i** × **k** = -**j**

### Parallel Vectors
**a** ∥ **b** ⟺ **a** × **b** = **0**

### Area of Parallelogram
Area = |**a** × **b**|

### Area of Triangle
Area = (1/2)|**a** × **b**|

## Scalar Triple Product

### Definition
[**a** **b** **c**] = **a** · (**b** × **c**)

### Component Form
= |a₁ a₂ a₃|
  |b₁ b₂ b₃|
  |c₁ c₂ c₃|

### Properties
1. [**a** **b** **c**] = [**b** **c** **a**] = [**c** **a** **b**]
2. [**a** **b** **c**] = -[**b** **a** **c**]
3. Coplanar vectors: [**a** **b** **c**] = 0

### Volume of Parallelepiped
V = |**a** · (**b** × **c**)|

### Volume of Tetrahedron
V = (1/6)|**a** · (**b** × **c**)|

## Vector Triple Product

### Formula
**a** × (**b** × **c**) = (**a** · **c**)**b** - (**a** · **b**)**c**

### Property
(**a** × **b**) × **c** = (**a** · **c**)**b** - (**b** · **c**)**a**

## Lines in 3D

### Vector Equation
**r** = **a** + λ**b**

Where:
- **a**: position vector of point on line
- **b**: direction vector
- λ: parameter

### Cartesian Equation
(x - x₁)/l = (y - y₁)/m = (z - z₁)/n

Where (l, m, n) are direction ratios

### Angle Between Lines
cos θ = |(**b₁** · **b₂**)/(|**b₁**| |**b₂**|)|

### Parallel Lines
**b₁** × **b₂** = **0** or l₁/l₂ = m₁/m₂ = n₁/n₂

### Perpendicular Lines
**b₁** · **b₂** = 0 or l₁l₂ + m₁m₂ + n₁n₂ = 0

### Shortest Distance Between Skew Lines
d = |(**a₂** - **a₁**) · (**b₁** × **b₂**)|/|**b₁** × **b₂**|

## Planes in 3D

### Vector Equation
**r** · **n** = d

Where **n** is normal vector to plane

### Cartesian Equation
ax + by + cz + d = 0

Where (a, b, c) are direction ratios of normal

### Intercept Form
x/a + y/b + z/c = 1

### Distance from Point to Plane
Distance from P(x₁, y₁, z₁) to ax + by + cz + d = 0:

d = |ax₁ + by₁ + cz₁ + d|/√(a² + b² + c²)

### Angle Between Planes
cos θ = |(**n₁** · **n₂**)/(|**n₁**| |**n₂**|)|

= |(a₁a₂ + b₁b₂ + c₁c₂)|/√[(a₁² + b₁² + c₁²)(a₂² + b₂² + c₂²)]

### Parallel Planes
**n₁** × **n₂** = **0** or a₁/a₂ = b₁/b₂ = c₁/c₂

### Perpendicular Planes
**n₁** · **n₂** = 0 or a₁a₂ + b₁b₂ + c₁c₂ = 0

### Angle Between Line and Plane
sin θ = |(**b** · **n**)/(|**b**| |**n**|)|

### Line Parallel to Plane
**b** · **n** = 0 or al + bm + cn = 0

### Line Perpendicular to Plane
**b** × **n** = **0** or l/a = m/b = n/c

## Sphere

### Equation
(x - a)² + (y - b)² + (z - c)² = r²

Center: (a, b, c), Radius: r

### General Form
x² + y² + z² + 2ux + 2vy + 2wz + d = 0

Center: (-u, -v, -w)
Radius: √(u² + v² + w² - d)

## Direction Cosines and Direction Ratios

### Direction Cosines
l = cos α, m = cos β, n = cos γ

Where α, β, γ are angles with x, y, z axes

**Relation**: l² + m² + n² = 1

### Direction Ratios
Proportional to direction cosines: (a, b, c)

**Finding Direction Cosines**:
l = a/√(a² + b² + c²)
m = b/√(a² + b² + c²)
n = c/√(a² + b² + c²)
