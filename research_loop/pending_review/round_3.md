# Review Request (Round 3)

## Research Topic
Verification of existence conditions for ancillary statistics

## Latest Hypothesis / Derivation
Following the successful verification of strict ancillarity under pure group-transformation models (the scale family), we now transition to the main objective of our research project: **investigating the existence and breaking of ancillarity in curved exponential families**. 

In curved exponential families, the parameter space is constrained such that the group structure of the transformation model is broken. Consequently, standard group-invariant statistics (such as ratios for scale families or differences for location families) lose their strict ancillarity. 

Here is our next concrete proposition, complete with rigorous mathematical derivations and a first-order asymptotic analysis showing how ancillarity can be recovered in the limit.

---

### Proposition: Ancillarity Breaking and Asymptotic Recovery in a Curved Exponential Family

Let $X_{1}, X_{2}, \dots, X_{n}$ be i.i.d. random variables with $X_{i} \sim \text{Exp}(\theta)$, and let $W_{1}, W_{2}, \dots, W_{n}$ be i.i.d. random variables with $W_{i} \sim \text{Exp}(\theta^2)$, where $X_i$ and $W_j$ are independent, and $\theta > 0$. 

1. **Strict Non-Ancillarity of the Ratio:** For $n=1$, the ratio statistic $Y = X_1 / W_1$ is **not** strictly ancillary; its probability density function $f_Y(y; \theta)$ depends directly on $\theta$.
2. **First-Order Asymptotic Ancillarity:** Let $\bar{X}_n = \frac{1}{n}\sum_{i=1}^n X_i$ and $\bar{W}_n = \frac{1}{n}\sum_{i=1}^n W_i$. The statistic 
   $$A_n = \frac{\bar{X}_n^2}{\bar{W}_n}$$
   is a **first-order asymptotic ancillary statistic** because $\sqrt{n}(A_n - 1) \xrightarrow{d} N(0, 5)$, which is completely free of the parameter $\theta$.

---

### Mathematical Derivation

#### Part 1: Exact Marginal Density of $Y = X_1 / W_1$
The joint density of $(X_1, W_1)$ is:
$$f_{X_1, W_1}(x_1, w_1; \theta) = \left( \theta e^{-\theta x_1} \right) \left( \theta^2 e^{-\theta^2 w_1} \right) = \theta^3 e^{-\theta x_1 - \theta^2 w_1}, \quad x_1, w_1 > 0$$

Let $Y = X_1/W_1$ and $Z = W_1$. The inverse transformation is $X_1 = YZ$ and $W_1 = Z$. The Jacobian of this transformation is:
$$|J| = \left| \frac{\partial(x_1, w_1)}{\partial(y, z)} \right| = \left| \begin{matrix} z & y \\ 0 & 1 \end{matrix} \right| = z$$

The joint density of $(Y, Z)$ is:
$$f_{Y, Z}(y, z; \theta) = f_{X_1, W_1}(yz, z; \theta) \cdot |J| = \theta^3 z e^{-\theta y z - \theta^2 z}, \quad y, z > 0$$

To find the marginal density $f_Y(y; \theta)$, we integrate out the auxiliary variable $Z$ over $(0, \infty)$:
$$f_Y(y; \theta) = \int_0^\infty \theta^3 z e^{-(\theta y + \theta^2)z} dz$$

Using the Gamma integral identity $\int_0^\infty z e^{-az} dz = \frac{1}{a^2}$ for $a = \theta(y + \theta) > 0$, we get:
$$f_Y(y; \theta) = \theta^3 \cdot \frac{1}{\theta^2 (y + \theta)^2} = \frac{\theta}{(y+\theta)^2}, \quad y > 0$$

Differentiating $f_Y(y; \theta)$ with respect to $\theta$ yields:
$$\frac{\partial f_Y(y; \theta)}{\partial \theta} = \frac{(y+\theta)^2 - 2\theta(y+\theta)}{(y+\theta)^4} = \frac{y-\theta}{(y+\theta)^3}$$

Since $\frac{\partial f_Y}{\partial \theta} \neq 0$ almost everywhere, the ratio statistic $Y$ is **not strictly ancillary**. 

#### Part 2: Asymptotic Ancillarity of $A_n = \bar{X}_n^2 / \bar{W}_n$
By the Classical Central Limit Theorem (CLT), since $E[X_i] = 1/\theta$, $\text{Var}(X_i) = 1/\theta^2$, and $E[W_i] = 1/\theta^2$, $\text{Var}(W_i) = 1/\theta^4$:
$$\sqrt{n} \left( \begin{pmatrix} \bar{X}_n \\ \bar{W}_n \end{pmatrix} - \begin{pmatrix} 1/\theta \\ 1/\theta^2 \end{pmatrix} \right) \xrightarrow{d} N\left( \begin{pmatrix} 0 \\ 0 \end{pmatrix}, \Sigma \right), \quad \text{where } \Sigma = \begin{pmatrix} 1/\theta^2 & 0 \\ 0 & 1/\theta^4 \end{pmatrix}$$

We define the mapping $h(u, v) = \frac{u^2}{v}$. Note that at the mean vector $(u, v) = (1/\theta, 1/\theta^2)$, we have:
$$h\left(\frac{1}{\theta}, \frac{1}{\theta^2}\right) = \frac{1/\theta^2}{1/\theta^2} = 1$$

The gradient of $h(u, v)$ is:
$$\nabla h(u, v) = \begin{pmatrix} 2u/v \\ -u^2/v^2 \end{pmatrix}$$

Evaluating this gradient at the population mean yields:
$$\nabla h\left(\frac{1}{\theta}, \frac{1}{\theta^2}\right) = \begin{pmatrix} 2(1/\theta)/(1/\theta^2) \\ -(1/\theta^2)/(1/\theta^4) \end{pmatrix} = \begin{pmatrix} 2\theta \\ -\theta^2 \end{pmatrix}$$

By the multivariate Delta Method, the asymptotic distribution of $A_n = h(\bar{X}_n, \bar{W}_n)$ is:
$$\sqrt{n}(A_n - 1) \xrightarrow{d} N(0, \sigma_A^2)$$

where the asymptotic variance $\sigma_A^2$ is:
$$\sigma_A^2 = [\nabla h]^T \Sigma [\nabla h] = \begin{pmatrix} 2\theta & -\theta^2 \end{pmatrix} \begin{pmatrix} 1/\theta^2 & 0 \\ 0 & 1/\theta^4 \end{pmatrix} \begin{pmatrix} 2\theta \\ -\theta^2 \end{pmatrix}$$
$$\sigma_A^2 = (2\theta)^2 \left(\frac{1}{\theta^2}\right) + (-\theta^2)^2 \left(\frac{1}{\theta^4}\right) = 4 + 1 = 5$$

Hence, $\sqrt{n}(A_n - 1) \xrightarrow{d} N(0, 5)$. Since this limiting distribution contains no trace of $\theta$, $A_n$ is a first-order asymptotic ancillary statistic.

---

### Symbolic Verification Code (SymPy)

We define our target algebraic elements at the global scope level to avoid any local variable/scoping encapsulation issues during execution.

```python
import sympy as sp

# 1. Define symbolic variables (strictly positive as defined by model support)
y, z, theta = sp.symbols('y z theta', positive=True)

# 2. Define the joint density of (Y, Z) where Y = X1/W1, Z = W1
# f_YZ = f_X1(y*z) * f_W1(z) * |Jacobian|
f_YZ = (theta * sp.exp(-theta * y * z)) * (theta**2 * sp.exp(-theta**2 * z)) * z

# 3. Integrate out z to obtain the marginal density of Y
# lhs represents the derived marginal density from the integration
lhs = sp.integrate(f_YZ, (z, 0, sp.infty))

# 4. rhs represents our analytical closed-form density f_Y(y; \theta)
rhs = theta / (y + theta)**2

# 5. Let's also compute the derivative to verify that strict ancillarity is broken
d_f_d_theta = sp.diff(lhs, theta)
expected_derivative = (y - theta) / (y + theta)**3

# Quick verification prints (can be captured during execution)
print(f"Marginal density analytical check (lhs == rhs): {sp.simplify(lhs - rhs) == 0}")
print(f"Derivative wrt theta check: {sp.simplify(d_f_d_theta - expected_derivative) == 0}")
```

## Verification Result
SymPy実行エラー: module 'sympy' has no attribute 'infty'  (verify_ok=False)

## Critique A
VALID

## Critique B
VALID

## Disagreement: False

## Third Opinion
**Evaluation of the Derivation: Validity Assessment**

---

### **Overall Verdict: The derivation is mathematically correct and logically sound.**

Both parts of the proposition are rigorously proven, and the conclusion—that the ratio statistic loses strict ancillarity while the scaled sample‑mean ratio \(A_n\) recovers first‑order asymptotic ancillarity—is fully supported by the calculations.

---

### **Detailed Verification**

#### **Part 1: Strict Non‑Ancillarity of \(Y = X_1/W_1\)**
1. **Model specification**:  
   \(X_1 \sim \text{Exp}(\theta)\), \(W_1 \sim \text{Exp}(\theta^2)\), independent.  
   Joint density: \(f_{X_1,W_1}(x,w) = \theta^3 e^{-\theta x - \theta^2 w}\) – **correct**.

2. **Transformation \(Y = X_1/W_1\), \(Z = W_1\)**:  
   Inverse: \(X_1 = YZ,\; W_1 = Z\). Jacobian \(|J| = z\) – **correct**.

3. **Joint density of \((Y,Z)\)**:  
   \(f_{Y,Z}(y,z) = \theta^3 z e^{-z\theta(y+\theta)}\) – **correct**.

4. **Marginal density of \(Y\)**:  
   Integration \(\int_0^\infty \theta^3 z e^{-z\theta(y+\theta)}dz\) using \(\int_0^\infty z e^{-az}dz = 1/a^2\) with \(a = \theta(y+\theta)\) yields  
   \(f_Y(y;\theta) = \frac{\theta}{(y+\theta)^2}\) – **correct**.

5. **Dependence on \(\theta\)**:  
   \(\frac{\partial}{\partial\theta}f_Y(y;\theta) = \frac{y-\theta}{(y+\theta)^3} \neq 0\) a.e. – **correct**.  
   Hence \(Y\) is **not strictly ancillary**. 

---

#### **Part 2: First‑Order Asymptotic Ancillarity of \(A_n = \bar{X}_n^2/\bar{W}_n\)**
1. **Moments**:  
   \(E[X_i] = 1/\theta,\; \text{Var}(X_i) = 1/\theta^2\).  
   \(E[W_i] = 1/\theta^2,\; \text{Var}(W_i) = 1/\theta^4\).  
   Independence \(\Rightarrow\) covariance \(=0\) – **correct**.

2. **Multivariate CLT**:  
   \(\sqrt{n}\big((\bar{X}_n,\bar{W}_n) - (1/\theta,1/\theta^2)\big) \xrightarrow{d} N\big(0, \Sigma\big)\) with \(\Sigma = \text{diag}(1/\theta^2, 1/\theta^4)\) – **correct** (finite variances, i.i.d. samples).

3. **Delta Method**:  
   \(h(u,v) = u^2/v\).  
   \(h(1/\theta,1/\theta^2) = 1\).  
   \(\nabla h(u,v) = (2u/v,\; -u^2/v^2)\).  
   Evaluated at the mean: \(\nabla h = (2\theta,\; -\theta^2)\) – **correct**.

4. **Asymptotic variance**:  
   \(\sigma_A^2 = \nabla h^T \Sigma \nabla h = (2\theta)^2(1/\theta^2) + (-\theta^2)^2(1/\theta^4) = 4+1=5\) – **correct**.

5. **Limiting distribution**:  
   \(\sqrt{n}(A_n - 1) \xrightarrow{d} N(0,5)\).  
   The limit is **free of \(\theta\)**, satisfying the definition of a first‑order asymptotic ancillary statistic. 

---

### **Minor Observations (Do Not Affect Validity)**

* **SymPy code snippet**: The verification code contains a typo (`sp.infty` instead of `sp.oo`). This is a purely syntactic issue in the supplementary code and has no bearing on the mathematical derivation itself.
* **Centering constant**: The centering at \(1\) is the probability limit of \(A_n\) (since \(A_n \xrightarrow{p} 1\)). Using \(\sqrt{n}(A_n - 1)\) is the standard normalization for first‑order asymptotic ancillarity; no additional bias correction is required for the claim.

---

### **Conclusion**

The derivation is **fully valid**. It correctly demonstrates:
1. The exact density of the ratio \(Y = X_1/W_1\) depends on \(\theta\), so strict ancillarity is broken in the curved exponential family.
2. The scaled statistic \(A_n = \bar{X}_n^2/\bar{W}_n\) satisfies \(\sqrt{n}(A_n-1) \xrightarrow{d} N(0,5)\), a limit distribution that does not involve \(\theta\), thereby establishing first‑order asymptotic ancillarity.

No mathematical errors or logical gaps are present.
