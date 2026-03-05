# Geometry Formulas

## Triangles

### Basic Properties
- Sum of angles = 180°
- Exterior angle = Sum of two opposite interior angles

### Types of Triangles
1. **By sides**: Equilateral, Isosceles, Scalene
2. **By angles**: Acute, Right, Obtuse

### Area Formulas
1. **Base and Height**: A = (1/2) × base × height
2. **Heron's Formula**: A = √[s(s-a)(s-b)(s-c)]
   - Where s = (a+b+c)/2 (semi-perimeter)
3. **Two sides and included angle**: A = (1/2)ab sin C

### Special Triangles

#### Equilateral Triangle
- All sides equal
- All angles = 60°
- Area = (√3/4)a²
- Height = (√3/2)a

#### Right Triangle
- Pythagoras Theorem: a² + b² = c² (c is hypotenuse)
- Area = (1/2) × base × perpendicular

### Triangle Inequalities
1. Sum of any two sides > third side
2. Difference of any two sides < third side

### Special Lines in Triangle

#### Median
Line from vertex to midpoint of opposite side
- Three medians intersect at centroid
- Centroid divides median in ratio 2:1

#### Altitude
Perpendicular from vertex to opposite side
- Three altitudes meet at orthocenter

#### Angle Bisector
Divides opposite side in ratio of adjacent sides

### Congruence Criteria
1. SSS (Side-Side-Side)
2. SAS (Side-Angle-Side)
3. ASA (Angle-Side-Angle)
4. AAS (Angle-Angle-Side)
5. RHS (Right angle-Hypotenuse-Side)

### Similarity Criteria
1. AAA (Angle-Angle-Angle)
2. SSS (Proportional sides)
3. SAS (Two proportional sides and included angle)

## Quadrilaterals

### General Properties
- Sum of angles = 360°
- Area = (1/2) × diagonal × sum of perpendiculars from other vertices

### Parallelogram
- Opposite sides parallel and equal
- Opposite angles equal
- Diagonals bisect each other
- Area = base × height = ab sin θ

### Rectangle
- All angles = 90°
- Diagonals equal
- Area = length × width
- Diagonal = √(l² + w²)

### Square
- All sides equal, all angles = 90°
- Diagonals equal and perpendicular
- Area = a²
- Diagonal = a√2

### Rhombus
- All sides equal
- Opposite angles equal
- Diagonals perpendicular and bisect each other
- Area = (1/2) × d₁ × d₂
- Area = a² sin θ

### Trapezium
- One pair of parallel sides
- Area = (1/2) × (sum of parallel sides) × height

## Circles

### Basic Formulas
- Circumference = 2πr = πd
- Area = πr²
- Arc length = (θ/360°) × 2πr = rθ (θ in radians)
- Sector area = (θ/360°) × πr² = (1/2)r²θ

### Chord Properties
1. Perpendicular from center bisects chord
2. Equal chords equidistant from center
3. Angle in semicircle = 90°

### Tangent Properties
1. Tangent ⊥ radius at point of contact
2. Two tangents from external point are equal
3. Angle between tangent and chord = angle in alternate segment

### Circle Theorems
1. Angles subtended by same arc at circumference are equal
2. Angle at center = 2 × angle at circumference
3. Opposite angles of cyclic quadrilateral = 180°
4. Exterior angle = interior opposite angle (cyclic quad)

## Coordinate Geometry

### Distance Formula
d = √[(x₂-x₁)² + (y₂-y₁)²]

### Section Formula
Point dividing line joining (x₁,y₁) and (x₂,y₂) in ratio m:n:
- Internal: [(mx₂+nx₁)/(m+n), (my₂+ny₁)/(m+n)]
- External: [(mx₂-nx₁)/(m-n), (my₂-ny₁)/(m-n)]

### Midpoint Formula
M = [(x₁+x₂)/2, (y₁+y₂)/2]

### Area of Triangle
A = (1/2)|x₁(y₂-y₃) + x₂(y₃-y₁) + x₃(y₁-y₂)|

### Straight Line

#### Slope
m = (y₂-y₁)/(x₂-x₁) = tan θ

#### Equations of Line
1. Point-slope: y - y₁ = m(x - x₁)
2. Slope-intercept: y = mx + c
3. Two-point: (y-y₁)/(y₂-y₁) = (x-x₁)/(x₂-x₁)
4. Intercept form: x/a + y/b = 1
5. General form: ax + by + c = 0

#### Distance from Point to Line
d = |ax₁ + by₁ + c|/√(a² + b²)

#### Angle Between Lines
tan θ = |(m₁-m₂)/(1+m₁m₂)|

**Parallel lines**: m₁ = m₂
**Perpendicular lines**: m₁m₂ = -1

### Circle Equation

#### Standard Form
(x-h)² + (y-k)² = r²
- Center: (h, k)
- Radius: r

#### General Form
x² + y² + 2gx + 2fy + c = 0
- Center: (-g, -f)
- Radius: √(g² + f² - c)

### Parabola

#### Standard Forms
1. y² = 4ax (opens right)
   - Vertex: (0,0)
   - Focus: (a,0)
   - Directrix: x = -a

2. x² = 4ay (opens up)
   - Vertex: (0,0)
   - Focus: (0,a)
   - Directrix: y = -a

### Ellipse

#### Standard Form
x²/a² + y²/b² = 1 (a > b)
- Center: (0,0)
- Foci: (±c, 0) where c² = a² - b²
- Eccentricity: e = c/a = √(1 - b²/a²)

### Hyperbola

#### Standard Form
x²/a² - y²/b² = 1
- Center: (0,0)
- Foci: (±c, 0) where c² = a² + b²
- Eccentricity: e = c/a = √(1 + b²/a²)
- Asymptotes: y = ±(b/a)x

## 3D Geometry

### Distance Formula
d = √[(x₂-x₁)² + (y₂-y₁)² + (z₂-z₁)²]

### Section Formula
[(mx₂+nx₁)/(m+n), (my₂+ny₁)/(m+n), (mz₂+nz₁)/(m+n)]

### Direction Cosines
For line making angles α, β, γ with x, y, z axes:
- l = cos α, m = cos β, n = cos γ
- l² + m² + n² = 1

### Equation of Line
(x-x₁)/a = (y-y₁)/b = (z-z₁)/c

Where a, b, c are direction ratios

### Equation of Plane
ax + by + cz + d = 0

Where a, b, c are direction ratios of normal
