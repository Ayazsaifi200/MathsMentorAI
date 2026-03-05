# Matrices and Determinants

## Matrices

### Matrix Definition
A rectangular array of numbers arranged in rows and columns

Order: m × n (m rows, n columns)

A = [aᵢⱼ], where i = row, j = column

### Types of Matrices

#### Row Matrix
Single row: [1 × n]

#### Column Matrix
Single column: [m × 1]

#### Square Matrix
Equal rows and columns: [n × n]

#### Diagonal Matrix
Square matrix with all non-diagonal elements = 0

#### Identity Matrix (I)
Diagonal matrix with all diagonal elements = 1
- I₂ = [[1,0],[0,1]]
- I₃ = [[1,0,0],[0,1,0],[0,0,1]]

#### Null/Zero Matrix
All elements = 0

#### Symmetric Matrix
A = Aᵀ (aᵢⱼ = aⱼᵢ)

#### Skew-Symmetric Matrix
Aᵀ = -A (aᵢⱼ = -aⱼᵢ)
Diagonal elements = 0

### Matrix Operations

#### Addition/Subtraction
Only for matrices of same order
(A ± B)ᵢⱼ = aᵢⱼ ± bᵢⱼ

#### Scalar Multiplication
(kA)ᵢⱼ = k × aᵢⱼ

#### Matrix Multiplication
For A[m×n] and B[n×p], product C = AB is [m×p]
cᵢⱼ = Σ(k=1 to n) aᵢₖ × bₖⱼ

**Properties**:
1. AB ≠ BA (not commutative)
2. (AB)C = A(BC) (associative)
3. A(B+C) = AB + AC (distributive)
4. IA = AI = A

#### Transpose
Aᵀ[n×m] obtained by interchanging rows and columns of A[m×n]

**Properties**:
1. (Aᵀ)ᵀ = A
2. (A+B)ᵀ = Aᵀ + Bᵀ
3. (AB)ᵀ = BᵀAᵀ
4. (kA)ᵀ = kAᵀ

### Adjoint and Inverse

#### Adjoint Matrix
adj(A) = [Cᵢⱼ]ᵀ

Where Cᵢⱼ = cofactor of aᵢⱼ

#### Inverse Matrix
A⁻¹ = adj(A)/|A|, if |A| ≠ 0

**Properties**:
1. AA⁻¹ = A⁻¹A = I
2. (A⁻¹)⁻¹ = A
3. (AB)⁻¹ = B⁻¹A⁻¹
4. (Aᵀ)⁻¹ = (A⁻¹)ᵀ
5. |A⁻¹| = 1/|A|

## Determinants

### 2×2 Determinant
|A| = |a b|
      |c d| = ad - bc

### 3×3 Determinant
|A| = |a₁ b₁ c₁|
      |a₂ b₂ c₂|
      |a₃ b₃ c₃|

= a₁(b₂c₃ - b₃c₂) - b₁(a₂c₃ - a₃c₂) + c₁(a₂b₃ - a₃b₂)

### Properties of Determinants

1. **Row-Column Interchange**: |Aᵀ| = |A|

2. **Row/Column Interchange**: Swapping two rows/columns changes sign
   
3. **Scalar Multiplication**: 
   - Multiplying one row/column by k: |kA| = k|A|
   - Multiplying all elements by k: |kA| = kⁿ|A| for n×n matrix

4. **Zero Determinant**:
   - If any row/column is all zeros: |A| = 0
   - If two rows/columns are identical: |A| = 0
   - If two rows/columns are proportional: |A| = 0

5. **Row Operations**:
   - Adding k times one row to another: |A| unchanged

6. **Triangular Matrix**: 
   |A| = product of diagonal elements

7. **Product Rule**: |AB| = |A| × |B|

8. **Cofactor Expansion**:
   Along row i: |A| = Σ aᵢⱼCᵢⱼ
   Along column j: |A| = Σ aᵢⱼCᵢⱼ

### Minors and Cofactors

#### Minor
Mᵢⱼ = determinant after removing row i and column j

#### Cofactor
Cᵢⱼ = (-1)^(i+j) × Mᵢⱼ

### Applications

#### System of Linear Equations
For AX = B:

**Cramer's Rule** (when |A| ≠ 0):
xᵢ = |Aᵢ|/|A|

Where Aᵢ is A with column i replaced by B

**Unique Solution**: |A| ≠ 0
**Infinite Solutions**: |A| = 0 and (adj A)B = 0
**No Solution**: |A| = 0 and (adj A)B ≠ 0

#### Area of Triangle
With vertices (x₁,y₁), (x₂,y₂), (x₃,y₃):

Area = (1/2)|x₁(y₂-y₃) + x₂(y₃-y₁) + x₃(y₁-y₂)|

= (1/2)|x₁ y₁ 1|
        |x₂ y₂ 1|
        |x₃ y₃ 1|

#### Collinearity of Points
Three points are collinear if:
|x₁ y₁ 1|
|x₂ y₂ 1| = 0
|x₃ y₃ 1|

## Rank of Matrix

### Definition
Rank(A) = maximum number of linearly independent rows (or columns)

### Properties
1. rank(A) ≤ min(m, n) for m×n matrix
2. rank(A) = rank(Aᵀ)
3. rank(AB) ≤ min(rank(A), rank(B))

## Eigenvalues and Eigenvectors

### Characteristic Equation
|A - λI| = 0

Roots give eigenvalues

### Eigenvector
For eigenvalue λ:
(A - λI)X = 0

Non-zero solution X is eigenvector

### Properties
1. Sum of eigenvalues = trace(A)
2. Product of eigenvalues = |A|
3. Eigenvalues of Aⁿ = (eigenvalues of A)ⁿ

## Special Matrix Operations

### Trace
tr(A) = sum of diagonal elements = Σ aᵢᵢ

**Properties**:
1. tr(A + B) = tr(A) + tr(B)
2. tr(kA) = k × tr(A)
3. tr(AB) = tr(BA)

### Symmetric and Skew-Symmetric Decomposition
Any matrix A can be written as:
A = (1/2)(A + Aᵀ) + (1/2)(A - Aᵀ)

Where:
- (1/2)(A + Aᵀ) is symmetric
- (1/2)(A - Aᵀ) is skew-symmetric
