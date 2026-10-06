# College Attendance Predictor: Mathematical Formulation & Derivations

This document specifies the exact deterministic algorithms and formulas utilized by the `AttendanceEngine`, `TimetableEngine`, and `SimulationEngine`.

---

## 1. Primary Notation & Variables

| Symbol | Definition |
|---|---|
| $A$ | Total classes (or weighted units) attended to date |
| $C$ | Total classes (or weighted units) conducted to date ($C \ge A \ge 0$) |
| $P$ | Current attendance percentage ($0 \le P \le 100$) |
| $T$ | Required target attendance percentage (default $75\%$, configurable per subject/college) |
| $B$ | Safe bunk count: maximum future classes that can be missed while keeping $P \ge T$ |
| $N$ | Classes needed: minimum consecutive future classes that must be attended to reach $P \ge T$ |
| $R$ | Total remaining scheduled classes in the semester derived from timetable |
| $w_i$ | Weighting factor (periods / credit hours / lab multiplier) for class session $i$ |

---

## 2. Basic Attendance Percentage

For unweighted sessions:
$$P = \begin{cases} 100.0, & \text{if } C = 0 \\ \frac{A}{C} \times 100, & \text{if } C > 0 \end{cases}$$

For weighted sessions (accounting for lab hours or credit weighting):
$$P_{\text{weighted}} = \frac{\sum_{i=1}^{M} a_i \cdot w_i}{\sum_{i=1}^{M} c_i \cdot w_i} \times 100$$
where $a_i \in \{0, 1\}$ denotes attendance status and $c_i = 1$ denotes a conducted class.

---

## 3. Safe-Bunk Derivation

The safe bunk count $B$ answers: **"How many upcoming classes can I miss before my attendance falls below target $T$?"**

Suppose the student misses $B$ additional consecutive classes.
- New attended count: $A' = A$
- New conducted count: $C' = C + B$
- Requirement:
$$\frac{A}{C + B} \ge \frac{T}{100}$$

Cross-multiplying (since $C + B > 0$ and $T > 0$):
$$100 \cdot A \ge T \cdot (C + B)$$
$$100 \cdot A \ge T \cdot C + T \cdot B$$
$$T \cdot B \le 100 \cdot A - T \cdot C$$
$$B \le \frac{100 \cdot A - T \cdot C}{T} = \frac{100 \cdot A}{T} - C$$

Since bunks must be integral classes:
$$B = \max\left(0, \left\lfloor \frac{100 \cdot A - T \cdot C}{T} \right\rfloor\right)$$

### Semester-Bounded Safe Bunk:
If remaining scheduled classes $R$ are known:
$$B_{\text{bounded}} = \min(B, R)$$

---

## 4. Classes-Needed (Recovery) Derivation

The classes-needed count $N$ answers: **"If my attendance is currently below target ($P < T$), how many consecutive future classes must I attend to recover to $T$?"**

Suppose the student attends $N$ consecutive future classes without absence.
- New attended count: $A' = A + N$
- New conducted count: $C' = C + N$
- Requirement:
$$\frac{A + N}{C + N} \ge \frac{T}{100}$$

Cross-multiplying:
$$100 \cdot (A + N) \ge T \cdot (C + N)$$
$$100 \cdot A + 100 \cdot N \ge T \cdot C + T \cdot N$$
$$(100 - T) \cdot N \ge T \cdot C - 100 \cdot A$$

For any target $T < 100$:
$$N \ge \frac{T \cdot C - 100 \cdot A}{100 - T}$$

Since classes are discrete non-negative integers:
$$N = \max\left(0, \left\lceil \frac{T \cdot C - 100 \cdot A}{100 - T} \right\rceil\right)$$

### Feasibility & Impossibility Boundaries:
1. **Target $T = 100\%$**:
   - If $C > A$ (already missed at least 1 class), $100 - T = 0$. It is mathematically impossible to reach $100\%$ attendance. The engine flags `recovery_possible = False`.
2. **Semester Horizon Constraint ($N > R$)**:
   - If $N > R$, even attending $100\%$ of all remaining classes in the semester will not suffice to hit $T\%$.
   - The maximum attainable semester-end attendance is:
   $$P_{\max} = \frac{A + R}{C + R} \times 100$$

---

## 5. What-If Scenario Simulation

Given a planned simulation of attending $a_{\text{sim}}$ classes and missing $b_{\text{sim}}$ classes over the next $k = a_{\text{sim}} + b_{\text{sim}}$ sessions:

$$P_{\text{sim}} = \frac{A + a_{\text{sim}}}{C + k} \times 100$$
$$\Delta P = P_{\text{sim}} - P$$

---

## 6. Timetable Schedule Projections & Remaining Classes

Let the active semester date range be $[D_{\text{start}}, D_{\text{end}}]$.
For current calendar date $D_{\text{now}}$:
$$R_{\text{subject}} = \sum_{d = D_{\text{now}} + 1}^{D_{\text{end}}} \mathbb{I}(\text{scheduled}(d, \text{subject})) \times \text{periods}(d, \text{subject})$$
where $\mathbb{I}(\cdot)$ is the indicator function matching calendar day-of-week to the student's timetable.

---

## 7. Projected Shortage Date

For a student whose recent rolling attendance rate is $p_{\text{trend}}$ (or under a simulated absence schedule):
The engine advances date-by-date $d \in [D_{\text{now}} + 1, D_{\text{end}}]$ accumulating projected conducted and attended classes.
The projected shortage date $D_{\text{shortage}}$ is defined as:
$$D_{\text{shortage}} = \min \left\{ d \in [D_{\text{now}} + 1, D_{\text{end}}] \;\middle|\; \frac{A_{\text{proj}}(d)}{C_{\text{proj}}(d)} \times 100 < T \right\}$$
If no such date crosses below $T$, $D_{\text{shortage}} = \text{None}$.
