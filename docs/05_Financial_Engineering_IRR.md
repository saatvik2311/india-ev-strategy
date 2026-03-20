# [Chapter 05] Financial Engineering II: The Bisection IRR Engine

## 1. IRR: The Compounded Truth
The **Internal Rate of Return (IRR)** is the single most important number for investors. It answers: **"What annual percentage return is this project giving me?"** 

### 🧠 Compounded, Not Simple
It is critical to understand that IRR is a **Compounded Annual Return**, not a simple rate. 
- **Simple 20%:** You earn ₹20 on ₹100 every year (100 -> 120 -> 140...). This is linear growth.
- **IRR 20%:** Each year builds on the previous year (100 -> 120 -> 144...). This is exponential growth. 

IRR behaves like an investment growing in a high-yield bank account. It is a "mathematical equivalent rate" that compresses 20 years of messy, unequal cash flows into one easily comparable percent.

## 2. Why we Solve for Zero (NPV = 0)
This is often asked in top-tier interviews. 
- **The Definition:** IRR is defined as the **exact discount rate where the NPV equals zero**.
- **The Intuition:** At this rate, the future profits exactly cancel out the initial investment when viewed in today's money. It is the "break-even point" for the cost of capital.
- **Business Interpretation:** "The project is neither good nor bad—it’s exactly fair." Finding this boundary tells you how high your profit margin is against your cost of funding.

## 3. The Algorithmic Challenge
Because the discount rate (**r**) is inside the denominator of 20 different polynomial fractions (one for each year), you cannot solve for it using basic high-school algebra. Most people simply use `import numpy_financial`. **I decided to build it from scratch.**

## 4. The Bisection Method (Binary Search)
I implemented a **Bisection Search Algorithm** to find the IRR. This is where high-level corporate finance meets deep algorithmic skills.

### 🧠 How it works:
1. **The Bounds:** The algorithm starts by guessing two extremes for the IRR: **0.1% (Low)** and **500% (High)**.
2. **The Guess:** It tests the midpoint (e.g., 250%).
3. **The Calculation:** It runs the NPV calculation using that 250% rate.
4. **The Decision Rule:**
    - If NPV(250%) is **positive**, it means our guess was too low (the project is even BETTER than 250%). It moves the "low" bound to 250% and cuts the search space in half.
    - If NPV(250%) is **negative**, it means the guess was too high. It moves the "high" bound to 250%.
5. **Convergence:** It repeats this bisection **80 times**. 

### 🧠 Performance:
Because it halves the search space every single loop (**O(log n)** time complexity), it mathematically converges on the exact, hyper-accurate IRR in milliseconds. This custom implementation guarantees the model won't fail or throw a "NaN" error, which often happens with standard black-box libraries when dealing with weird policy-adjusted cash flows.

---
*Next Chapter: The Policy Layer — Subsidies & Subsidy Stacking.*
