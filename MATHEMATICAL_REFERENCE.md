# SimPulse Mathematical Reference

**Complete compilation of all mathematical equations used in the Formula E simulator**

---

## Table of Contents
1. [Core State Evolution](#1-core-state-evolution)
2. [Vehicle Dynamics](#2-vehicle-dynamics)
3. [Energy System](#3-energy-system)
4. [Tire Model](#4-tire-model)
5. [Thermal Dynamics](#5-thermal-dynamics)
6. [Driver Control](#6-driver-control)
7. [Stochastic Dynamics](#7-stochastic-dynamics)
8. [Event Probabilities](#8-event-probabilities)
9. [Performance Metrics](#9-performance-metrics)
10. [GPU Vectorization](#10-gpu-vectorization)

---

## 1. Core State Evolution

### 1.1 Fundamental Transition Equation

$$\mathbf{x}(t+1) = f(\mathbf{x}(t), \mathbf{u}(t), \boldsymbol{\theta}(t)) + \boldsymbol{\varepsilon}(t)$$

**Parameters:**
- $\mathbf{x}(t) \in \mathbb{R}^{20}$: State vector at time $t$
- $f: \mathbb{R}^{20} \times \mathbb{R}^{4} \times \mathbb{R}^{k} \to \mathbb{R}^{20}$: Deterministic physics function
- $\mathbf{u}(t) \in \mathbb{R}^{4}$: Control vector $[\theta, \beta, \delta, \text{AM}]$
- $\boldsymbol{\theta}(t)$: Environmental parameters (weather, track conditions)
- $\boldsymbol{\varepsilon}(t) \sim \mathcal{N}(0, \boldsymbol{\Sigma})$: Gaussian process noise
- $\Delta t = 0.01$ s: Simulation timestep (100 Hz)

### 1.2 State Vector Components

$$\mathbf{x}_i = \begin{bmatrix}
v_x \\ v_y \\ p_x \\ p_y \\ E_{\%} \\ T_{\text{batt}} \\ \tau \\ \mu \\ \text{AM}_{\text{active}} \\ t_{\text{AM}} \\ d_{\text{lap}} \\ d_{\text{total}} \\ L \\ P \\ \theta \\ \beta \\ \delta \\ a_{\text{lat}} \\ a \\ P_i
\end{bmatrix} \in \mathbb{R}^{20}$$

**Component Definitions:**
- $v_x$: Longitudinal velocity (m/s)
- $v_y$: Lateral velocity (m/s)
- $p_x, p_y$: Position coordinates (m)
- $E_{\%}$: Battery percentage (0-100%)
- $T_{\text{batt}}$: Battery temperature (°C)
- $\tau$: Tire degradation (0-1)
- $\mu$: Grip coefficient (0.9-1.2)
- $\text{AM}_{\text{active}}$: Attack mode status (binary)
- $t_{\text{AM}}$: Attack mode remaining time (s)
- $d_{\text{lap}}$: Lap distance (m)
- $d_{\text{total}}$: Total distance (m)
- $L$: Current lap number
- $P$: Race position (rank)
- $\theta$: Throttle input (0-1)
- $\beta$: Brake input (0-1)
- $\delta$: Steering angle (rad)
- $a_{\text{lat}}$: Lateral acceleration (m/s²)
- $a$: Longitudinal acceleration (m/s²)
- $P_i$: Performance index (0-1)

### 1.3 Multi-Car State Matrix

$$\mathbf{X}(t) = \begin{bmatrix}
\mathbf{x}_1(t) \\
\mathbf{x}_2(t) \\
\vdots \\
\mathbf{x}_N(t)
\end{bmatrix} \in \mathbb{R}^{N \times 20}$$

**Parameters:**
- $N$: Number of cars in simulation
- Each row represents one car's complete state

---

## 2. Vehicle Dynamics

### 2.1 Longitudinal Force Balance

$$F_{\text{net}} = F_{\text{motor}} - F_{\text{drag}} - F_{\text{roll}} - F_{\text{brake}} - F_{\text{gradient}}$$

**Parameters:**
- $F_{\text{net}}$: Net longitudinal force (N)
- All force components in Newtons (N)

### 2.2 Motor Force

$$F_{\text{motor}} = \frac{P_{\text{motor}} \cdot \eta_{\text{motor}}}{v}$$

$$P_{\text{motor}} = \begin{cases}
(P_{\max} + P_{\text{boost}}) \cdot \theta & \text{if AM active} \\
P_{\max} \cdot \theta & \text{otherwise}
\end{cases}$$

**Parameters:**
- $P_{\text{motor}}$: Motor power (W)
- $P_{\max} = 350$ kW: Maximum power (Gen3)
- $P_{\text{boost}} = 50$ kW: Attack mode boost
- $\theta \in [0, 1]$: Throttle input
- $\eta_{\text{motor}} = 0.97$: Motor efficiency
- $v$: Current velocity (m/s)

### 2.3 Aerodynamic Drag

$$F_{\text{drag}} = \frac{1}{2} \rho C_d A v^2$$

**Parameters:**
- $\rho = 1.225$ kg/m³: Air density (sea level, 15°C)
- $C_d = 0.32$: Drag coefficient (Gen3)
- $A = 1.5$ m²: Frontal area
- $v$: Current speed (m/s)

### 2.4 Rolling Resistance

$$F_{\text{roll}} = C_r \cdot N$$

$$N = m \cdot g + F_{\text{down}}$$

$$F_{\text{down}} = \frac{1}{2} \rho C_l A v^2$$

**Parameters:**
- $C_r = 0.015$: Rolling resistance coefficient
- $N$: Normal force (N)
- $m = 920$ kg: Total mass (car + driver)
- $g = 9.81$ m/s²: Gravitational acceleration
- $F_{\text{down}}$: Downforce (N)
- $C_l = 1.8$: Lift coefficient (downforce)

### 2.5 Brake Force

$$F_{\text{brake}} = \beta \cdot m \cdot a_{\max,\text{brake}}$$

$$F_{\text{regen}} = \min\left(0.7 \cdot F_{\text{brake}}, \frac{P_{\text{regen,max}}}{v}\right)$$

**Parameters:**
- $\beta \in [0, 1]$: Brake input
- $a_{\max,\text{brake}} = 5.5$ m/s²: Maximum deceleration
- $F_{\text{regen}}$: Regenerative braking force (N)
- $P_{\text{regen,max}} = 600$ kW: Maximum regen power (Gen3)

### 2.6 Gradient Force

$$F_{\text{gradient}} = m \cdot g \cdot \sin(\alpha)$$

$$\alpha = \arctan\left(\frac{\Delta h}{L_{\text{segment}}}\right)$$

**Parameters:**
- $\alpha$: Road gradient angle (rad)
- $\Delta h$: Elevation change of segment (m)
- $L_{\text{segment}}$: Segment length (m)

### 2.7 Acceleration and Velocity

$$a = \frac{F_{\text{net}}}{m}$$

$$v_x(t+\Delta t) = v_x(t) + a \cdot \Delta t$$

$$v_x \in [0, v_{\max}], \quad v_{\max} = \frac{322}{3.6} = 89.44 \text{ m/s}$$

**Parameters:**
- $a$: Longitudinal acceleration (m/s²)
- $v_{\max}$: Maximum speed (322 km/h for Gen3)

### 2.8 Position Update

$$p_x(t+\Delta t) = p_x(t) + v_x(t) \cdot \Delta t + \frac{1}{2}a(\Delta t)^2$$

$$d_{\text{total}}(t+\Delta t) = d_{\text{total}}(t) + v(t) \cdot \Delta t$$

**Parameters:**
- $p_x$: X-coordinate position (m)
- $d_{\text{total}}$: Cumulative distance traveled (m)

### 2.9 Cornering Speed Limit

$$v_{\max,\text{corner}} = \sqrt{\mu_{\text{eff}} \cdot g \cdot r}$$

$$\mu_{\text{eff}} = \mu \cdot \mu_{\text{segment}} \cdot (1 + 0.3\tan\gamma) \cdot (1 + k_{\text{df}}v_{\text{factor}})$$

**Parameters:**
- $v_{\max,\text{corner}}$: Maximum safe corner speed (m/s)
- $\mu$: Tire grip coefficient
- $\mu_{\text{segment}}$: Track segment grip multiplier (0.9-1.1)
- $r$: Corner radius (m)
- $\gamma$: Banking angle (degrees)
- $k_{\text{df}} = 0.05$: Downforce contribution factor
- $v_{\text{factor}} = \min(v/80, 1)$: Speed-dependent downforce

### 2.10 Lateral Dynamics

$$a_{\text{lat}} = \frac{v^2}{r} \cdot \tan(\delta)$$

$$a_{\text{lat}} \in [-a_{\text{lat,max}}, a_{\text{lat,max}}], \quad a_{\text{lat,max}} = \mu \cdot g$$

**Parameters:**
- $a_{\text{lat}}$: Lateral acceleration (m/s²)
- $\delta$: Steering angle (rad)
- $r$: Path radius (m)

### 2.11 Ackermann Steering

$$\delta_{\text{ideal}} = \arctan\left(\frac{L_{\text{wb}}}{r}\right)$$

**Parameters:**
- $L_{\text{wb}} = 2.97$ m: Wheelbase (Gen3)
- $\delta \in [-0.52, 0.52]$ rad: Steering angle limits (≈±30°)

---

## 3. Energy System

### 3.1 Battery State Update

$$E(t+\Delta t) = E(t) - E_{\text{consumed}}(t) + E_{\text{regen}}(t)$$

$$E_{\%}(t) = \frac{E(t)}{E_{\text{capacity}}} \times 100$$

**Parameters:**
- $E(t)$: Battery energy (Joules)
- $E_{\text{capacity}} = 51 \times 3.6 \times 10^6 = 183.6$ MJ: Battery capacity
- $E_{\%}$: Battery percentage (0-100%)

### 3.2 Energy Consumption

$$E_{\text{consumed}} = \frac{P_{\text{motor}}}{\eta_{\text{motor}}} \cdot \Delta t$$

$$E_{\text{consumed}} = \begin{cases}
\gamma_{\text{AM}} \cdot E_{\text{base}} & \text{if AM active} \\
E_{\text{base}} & \text{otherwise}
\end{cases}$$

**Parameters:**
- $P_{\text{motor}}$: Motor power demand (W)
- $\eta_{\text{motor}} = 0.97$: Motor efficiency
- $\gamma_{\text{AM}} = 1.3$: Attack mode energy multiplier (30% more)

### 3.3 Energy Recovery (Regeneration)

$$E_{\text{regen}} = P_{\text{regen}} \cdot \eta_{\text{regen}} \cdot \Delta t$$

$$P_{\text{regen}} = \min\left(F_{\text{brake}} \cdot v, P_{\text{regen,max}}\right)$$

**Parameters:**
- $P_{\text{regen}}$: Regenerative power (W)
- $\eta_{\text{regen}} = 0.40$: Regeneration efficiency (40% recovery)
- $P_{\text{regen,max}} = 600$ kW: Maximum regen power
- Limited to 70% of total braking force

### 3.4 Energy Management Modifier

$$\theta_{\text{modified}} = \theta \times k_E$$

$$k_E = \begin{cases}
0.92 & E_{\%} < 15\% \\
0.95 & 15\% \leq E_{\%} < 30\% \\
1.00 & E_{\%} \geq 30\%
\end{cases}$$

**Parameters:**
- $k_E$: Energy conservation multiplier
- Reduces throttle when battery is low

---

## 4. Tire Model

### 4.1 Tire Degradation Rate

$$\frac{d\tau}{dt} = k_{\text{base}} + k_{\text{temp}}|T_{\text{tire}} - T_{\text{opt}}| + k_{\text{speed}}v^2 + k_{\text{lat}}|a_{\text{lat}}|^2 + k_{\text{lock}}\mathbb{I}_{\text{lock}}$$

**Parameters:**
- $\tau \in [0, 1]$: Tire degradation (0=new, 1=worn)
- $k_{\text{base}} = 0.002$: Base degradation rate (per second)
- $k_{\text{temp}} = 0.00005$: Temperature sensitivity
- $T_{\text{tire}}$: Tire temperature (°C)
- $T_{\text{opt}} = 90$ °C: Optimal tire temperature
- $k_{\text{speed}} = 0.00003$: Speed degradation factor
- $k_{\text{lat}} = 0.0004$: Lateral acceleration factor
- $k_{\text{lock}} = 0.01$: Wheel lock penalty
- $\mathbb{I}_{\text{lock}}$: Binary indicator (1 if locked, 0 otherwise)

### 4.2 Grip Coefficient Evolution

$$\mu(\tau) = \mu_{\max} - (\mu_{\max} - \mu_{\min}) \cdot \tau$$

**Parameters:**
- $\mu_{\max} = 1.2$: Maximum grip (new tires)
- $\mu_{\min} = 0.9$: Minimum grip (worn tires)
- Linear degradation model

### 4.3 Weather Effect on Grip

$$\mu_{\text{wet}} = \mu \cdot (1 - 0.25 \cdot I_{\text{rain}})$$

**Parameters:**
- $I_{\text{rain}} \in [0, 1]$: Rain intensity (0=dry, 1=heavy)
- 25% grip loss in heavy rain

### 4.4 Tire Temperature Evolution

$$\frac{dT_{\text{tire}}}{dt} = Q_{\text{friction}} - Q_{\text{cooling}}$$

$$Q_{\text{friction}} = k_f(|a_{\text{lat}}| \cdot 0.5 + |a| \cdot 0.3)$$

$$Q_{\text{cooling}} = k_c(T_{\text{tire}} - T_{\text{ambient}})$$

**Parameters:**
- $T_{\text{tire}}$: Tire temperature (°C)
- $k_f$: Friction heating coefficient
- $k_c = 0.1$: Cooling coefficient
- $T_{\text{ambient}}$: Ambient air temperature (°C)
- $T_{\text{tire}} \in [T_{\text{ambient}}, 130]$ °C: Temperature bounds

---

## 5. Thermal Dynamics

### 5.1 Battery Temperature

$$\frac{dT_{\text{batt}}}{dt} = Q_{\text{gen}} - Q_{\text{cool,active}} - Q_{\text{cool,passive}}$$

$$Q_{\text{gen}} = \frac{P_{\text{loss}}}{m_{\text{batt}} \cdot c_p}$$

$$P_{\text{loss}} = |E_{\text{consumed}} - E_{\text{regen}}| \cdot (1 - \eta)$$

**Parameters:**
- $T_{\text{batt}}$: Battery temperature (°C)
- $Q_{\text{gen}}$: Heat generation rate (°C/s)
- $m_{\text{batt}} = 200$ kg: Battery mass
- $c_p = 850$ J/(kg·K): Specific heat capacity
- $P_{\text{loss}}$: Waste heat power (W)
- $\eta$: System efficiency

### 5.2 Active Cooling

$$Q_{\text{cool,active}} = k_{\text{cool}}(T_{\text{batt}} - T_{\text{opt}}) \quad \text{if } T_{\text{batt}} > T_{\text{opt}}$$

**Parameters:**
- $T_{\text{opt}} = 40$ °C: Optimal battery temperature
- $k_{\text{cool}} = 0.8$: Active cooling rate

### 5.3 Passive Cooling

$$Q_{\text{cool,passive}} = k_{\text{passive}}(T_{\text{batt}} - T_{\text{ambient}}) \cdot \Delta t$$

**Parameters:**
- $k_{\text{passive}} = 0.05$: Passive cooling coefficient
- $T_{\text{batt}} \in [20, 60]$ °C: Safe operating range

---

## 6. Driver Control

### 6.1 Target Speed Calculation

$$v_{\text{target}} = v_{\max,\text{segment}} \cdot \alpha_{\text{skill}} \cdot \alpha_{\text{aggr}}$$

**Parameters:**
- $v_{\text{target}}$: Desired speed (m/s)
- $v_{\max,\text{segment}}$: Maximum safe speed for segment
- $\alpha_{\text{skill}} \in [0.95, 1.08]$: Driver skill factor
- $\alpha_{\text{aggr}} \in [0.60, 0.90]$: Aggression factor (risk tolerance)

### 6.2 Throttle Control

$$\theta = \begin{cases}
\min\left(\frac{e_v}{k_\theta}, 1\right) \cdot (0.7 + 0.3\alpha_{\text{aggr}}) & e_v > \epsilon \\
\theta_{\text{maintain}} & |e_v| \leq \epsilon \\
0 & e_v < -\epsilon
\end{cases}$$

$$e_v = v_{\text{target}} - v_{\text{current}}$$

**Parameters:**
- $e_v$: Speed error (m/s)
- $k_\theta = 15$: Throttle gain (straights)
- $\epsilon = 1$ m/s: Deadband threshold
- $\theta_{\text{maintain}} = 0.4$ (straight), $0.15$ (corner)

### 6.3 Brake Control

$$\beta = \begin{cases}
\min\left(\frac{|e_v|}{k_\beta}, 1\right) & e_v < -\epsilon
\end{cases}$$

$$k_\beta = \begin{cases}
8 & \text{corner (aggressive)} \\
15 & \text{straight (gentle)}
\end{cases}$$

**Parameters:**
- $k_\beta$: Brake gain (context-dependent)
- Corner braking is 2× more aggressive

### 6.4 Steering Control

$$\delta = \arctan\left(\frac{L_{\text{wb}}}{r}\right) \cdot s$$

$$s = \begin{cases}
-1 & \text{left turn} \\
+1 & \text{right turn} \\
0 & \text{straight}
\end{cases}$$

**Parameters:**
- $\delta$: Steering angle (rad)
- $s$: Turn direction sign
- $L_{\text{wb}} = 2.97$ m: Wheelbase

### 6.5 Attack Mode Decision

$$P(\text{activate AM}) = \begin{cases}
0.6 + 0.3\alpha_{\text{aggr}} & \text{if conditions met} \\
0 & \text{otherwise}
\end{cases}$$

**Conditions:**
- $\text{AM}_{\text{uses}} > 0$: Activations remaining
- $\Delta t_{\text{ahead}} < 2.0$ s: Close to car ahead
- $P > 1$: Not leading
- In attack mode zone

**Parameters:**
- Probability per timestep when all conditions true
- $\alpha_{\text{aggr}}$: Driver aggression affects activation likelihood

---

## 7. Stochastic Dynamics

### 7.1 Control Input Noise

$$\mathbf{u}_{\text{actual}} = \mathbf{u}_{\text{ideal}} + \boldsymbol{\varepsilon}_{\text{control}}$$

$$\boldsymbol{\varepsilon}_{\text{control}} \sim \mathcal{N}\left(0, (1-\alpha_{\text{cons}}) \cdot \boldsymbol{\Sigma}_{\text{control}}\right)$$

$$\boldsymbol{\Sigma}_{\text{control}} = \text{diag}(\sigma_\theta^2, \sigma_\beta^2, \sigma_\delta^2, 0)$$

**Parameters:**
- $\alpha_{\text{cons}} \in [0.80, 0.98]$: Driver consistency
- $\sigma_\theta = 0.02$: Throttle noise std dev
- $\sigma_\beta = 0.02$: Brake noise std dev
- $\sigma_\delta = 0.005$ rad: Steering noise std dev

### 7.2 Process Noise

$$\mathbf{x}(t+\Delta t) = \mathbf{x}^*(t+\Delta t) + \sqrt{\Delta t} \cdot \boldsymbol{\varepsilon}_{\text{process}}$$

$$\boldsymbol{\varepsilon}_{\text{process}} \sim \mathcal{N}(0, \boldsymbol{\Sigma}_{\text{process}})$$

**Parameters:**
- $\sqrt{\Delta t}$: Brownian motion scaling factor
- $\sigma_{v_x} = 0.15$ m/s: Velocity noise
- $\sigma_{v_y} = 0.075$ m/s: Lateral velocity noise
- $\sigma_p = 0.05$ m: Position noise
- $\sigma_a = 0.08$ m/s²: Acceleration noise
- $\sigma_{T,\text{tire}} = 0.5$ °C: Tire temperature noise
- $\sigma_{T,\text{batt}} = 0.3$ °C: Battery temperature noise

### 7.3 Tire Degradation Noise

$$\Delta\tau_{\text{actual}} = \Delta\tau_{\text{base}} + \mathcal{N}\left(0, 0.15\Delta\tau_{\text{base}} \cdot \left(1 + \frac{T_{\text{tire}}-70}{100}\right)\right)$$

**Parameters:**
- Temperature-dependent variance
- Hotter tires → more unpredictable wear
- 15% base noise magnitude

### 7.4 Energy Consumption Noise

$$E_{\text{consumed,actual}} = E_{\text{consumed,base}} + \mathcal{N}(0, \sigma_E^2 E_{\text{consumed,base}})$$

$$\sigma_E^2 = 0.02 + 0.001|T_{\text{batt}} - 40|$$

**Parameters:**
- Minimum 2% variance at optimal temperature
- Increases with temperature deviation from 40°C

---

## 8. Event Probabilities

### 8.1 Crash Probability (Sigmoid)

$$P(\text{crash}|\mathbf{x}, t) = p_{\text{base}} \cdot (1 + \kappa \cdot R(\mathbf{x}))$$

$$R(\mathbf{x}) = w_v\frac{v}{v_{\max}} + w_\tau\tau + w_\alpha\alpha_{\text{aggr}} + w_p\frac{N_{\text{nearby}}}{5} + w_E\left(1-\frac{E}{100}\right)$$

**Parameters:**
- $p_{\text{base}} = 10^{-7}$: Base crash probability per timestep
- $\kappa = 50$: Risk amplification factor
- $w_v = 0.30$: Speed risk weight
- $w_\tau = 0.25$: Tire degradation weight
- $w_\alpha = 0.20$: Aggression weight
- $w_p = 0.15$: Proximity risk weight
- $w_E = 0.10$: Energy stress weight
- $N_{\text{nearby}}$: Cars within 20m

### 8.2 Overtake Probability (Logistic)

$$P(\text{overtake}|\mathbf{x}_i, \mathbf{x}_j) = \frac{1}{1 + e^{-z}}$$

$$z = c_1\Delta v + c_2\Delta E + c_3\mathbb{I}_{\text{AM}_i} - c_4\mathbb{I}_{\text{AM}_j} + c_5\Delta\tau + k_{\text{track}}$$

**Parameters:**
- $c_1 = 0.5$: Speed differential coefficient
- $c_2 = 0.02$: Energy advantage coefficient
- $c_3 = 0.3$: Attack mode bonus (attacker)
- $c_4 = 0.2$: Attack mode penalty (defender)
- $c_5 = 0.4$: Tire condition advantage
- $k_{\text{track}}$: Track segment factor
  - Straight: $k = 0.8$
  - Corner: $k = 0.3$
  - Chicane: $k = 0.5$
- $\Delta v = v_i - v_j$: Speed differential (m/s)
- $\Delta E = E_i - E_j$: Energy differential (%)
- $\Delta\tau = \tau_j - \tau_i$: Tire advantage

### 8.3 Safety Car (Poisson Process)

$$P(\text{SC in lap } \ell) = 1 - e^{-\lambda(\ell)}$$

$$\lambda(\ell) = \lambda_0\left(1 + 0.5\sum_{k=\ell-2}^{\ell}N_{\text{crashes}}(k)\right)$$

**Parameters:**
- $\lambda_0 = 0.1$: Base rate (per lap)
- Recent crashes increase probability
- Guards: Not lap 1, not within 5 laps of previous SC

### 8.4 Mechanical Failure (Weibull)

$$h(t) = \frac{k}{\lambda}\left(\frac{t}{\lambda}\right)^{k-1}$$

$$F(t) = 1 - e^{-(t/\lambda)^k}$$

**Parameters:**
- $k = 2.5$: Shape parameter (increasing hazard rate)
- $\lambda = 5000$ s: Scale parameter (characteristic lifetime)
- $t$: Component age (seconds)
- Stress accelerates aging: $t_{\text{eff}} = t(1 + s)$ where $s$ is stress level

---

## 9. Performance Metrics

### 9.1 Performance Index

$$P_i(t) = \sum_{j=1}^{5} w_j \cdot c_j(t)$$

$$c_1 = \frac{v(t)}{v_{\max}}, \quad c_2 = \frac{a(t)}{a_{\max}}, \quad c_3 = \frac{E(t)}{E_{\max}}, \quad c_4 = 1-\tau(t), \quad c_5 = \psi(t)$$

$$\psi(t) = \frac{c_1 + c_3 + c_4}{3}$$

**Parameters:**
- $w_1 = 0.30$: Velocity weight
- $w_2 = 0.15$: Acceleration weight
- $w_3 = 0.25$: Energy weight
- $w_4 = 0.20$: Tire condition weight
- $w_5 = 0.10$: Strategy effectiveness weight
- $P_i \in [0, 1]$: Normalized performance score

### 9.2 Gap Calculations

$$\Delta t_{\text{leader}}^i = \frac{d_{\text{total}}^{\text{leader}} - d_{\text{total}}^i}{v^i}$$

$$\Delta t_{\text{ahead}}^i = \frac{d_{\text{total}}^{P-1} - d_{\text{total}}^i}{v^i}$$

**Parameters:**
- $\Delta t_{\text{leader}}$: Time gap to race leader (seconds)
- $\Delta t_{\text{ahead}}$: Time gap to car immediately ahead (seconds)
- $P$: Current position
- Approximation assumes constant average speed

### 9.3 Energy Efficiency

$$\eta_{\text{distance}} = \frac{d_{\text{total}}/1000}{E_{\text{consumed}}/3.6 \times 10^6} \quad [\text{km/kWh}]$$

**Parameters:**
- Distance in kilometers
- Energy in kilowatt-hours
- Higher is better (more efficient)

### 9.4 Lap Time Prediction

$$t_{\text{lap}} = \frac{L_{\text{track}}}{\bar{v}} \cdot \alpha_{\text{skill}} \cdot \left(1 + \mathcal{N}(0, (1-\alpha_{\text{cons}})^2)\right) \cdot f_{\text{fatigue}}$$

$$f_{\text{fatigue}} = 1 - 0.05\frac{L_{\text{current}}}{L_{\text{total}}}$$

**Parameters:**
- $L_{\text{track}}$: Track length (m)
- $\bar{v}$: Average speed (m/s)
- $f_{\text{fatigue}}$: Fatigue factor (up to 5% slower at race end)

---

## 10. GPU Vectorization

### 10.1 Batch State Update

$$\mathbf{X}(t+\Delta t) = \mathbf{F}(\mathbf{X}(t)) + \mathbf{G}\mathbf{U}(t) + \boldsymbol{\mathcal{E}}(t)$$

**Parameters:**
- $\mathbf{X} \in \mathbb{R}^{N \times 20}$: All car states
- $\mathbf{U} \in \mathbb{R}^{N \times 4}$: All control inputs
- $\mathbf{F}: \mathbb{R}^{N \times 20} \to \mathbb{R}^{N \times 20}$: Vectorized physics
- $\mathbf{G}$: Control gain matrix
- $\boldsymbol{\mathcal{E}} \sim \mathcal{N}(0, \mathbf{I}_N \otimes \boldsymbol{\Sigma})$: Batch noise

### 10.2 Vectorized Force Calculation

$$\mathbf{A} = \frac{1}{m}(\mathbf{F}_{\text{motor}} - \mathbf{F}_{\text{drag}} - \mathbf{F}_{\text{roll}} - \mathbf{F}_{\text{brake}})$$

**Element-wise operations on vectors of length $N$**

### 10.3 Speedup Factor

$$S(N) = \frac{T_{\text{CPU}}(N)}{T_{\text{GPU}}(N)}$$

**Empirical scaling:**
- $S(24) \approx 15\times$
- $S(50) \approx 40\times$
- $S(100) \approx 100\times$
- $S(500) \approx 160\times$

### 10.4 Memory Requirement

$$M_{\text{GPU}} = N \times (80 + 50) \text{ bytes} = 130N \text{ bytes}$$

**Parameters:**
- 80 bytes: State matrix (20 × 4 bytes float32)
- 50 bytes: Auxiliary arrays (controls, forces)
- 130 KB for 1000 cars

---

## 11. Constants Summary

### Physical Constants
- $g = 9.81$ m/s²: Gravity
- $\rho = 1.225$ kg/m³: Air density (sea level)

### Gen3 Car Specifications
- $m = 920$ kg: Total mass
- $L_{\text{wb}} = 2.97$ m: Wheelbase
- $P_{\max} = 350$ kW: Maximum power
- $P_{\text{regen,max}} = 600$ kW: Maximum regeneration
- $E_{\text{capacity}} = 51$ kWh = 183.6 MJ
- $v_{\max} = 322$ km/h = 89.44 m/s
- $C_d = 0.32$: Drag coefficient
- $C_l = 1.8$: Lift coefficient
- $A = 1.5$ m²: Frontal area

### Efficiency Values
- $\eta_{\text{motor}} = 0.97$ (97%)
- $\eta_{\text{regen}} = 0.40$ (40%)
- $\eta_{\text{battery}} = 0.95$ (95%)

### Tire Parameters
- $\mu_{\max} = 1.2$: New tire grip
- $\mu_{\min} = 0.9$: Worn tire grip
- $T_{\text{opt}} = 90$ °C: Optimal temperature

### Simulation Parameters
- $\Delta t = 0.01$ s: Timestep (100 Hz)
- $N \in [10, 500]$: Number of cars
- $L_{\text{track}} = 2370$ m: Plaksha circuit length

---

## 12. Notation Conventions

### Scalars
- Lowercase italics: $v, t, \tau, \mu$
- Greek letters: $\theta, \beta, \delta, \alpha, \epsilon$

### Vectors
- Bold lowercase: $\mathbf{x}, \mathbf{u}, \mathbf{v}$
- Subscript for component: $v_x, p_y$

### Matrices
- Bold uppercase: $\mathbf{X}, \mathbf{U}, \mathbf{F}$
- Dimensions: $\mathbf{X} \in \mathbb{R}^{N \times 20}$

### Functions
- Italics: $f(), P(), R()$
- Subscript for type: $F_{\text{drag}}, E_{\text{consumed}}$

### Probability
- $P(\cdot)$: Probability
- $\mathbb{E}[\cdot]$: Expected value
- $\mathcal{N}(\mu, \sigma^2)$: Normal distribution
- $\mathbb{I}_{\text{condition}}$: Indicator function (1 if true, 0 if false)

### Time Derivatives
- $\frac{dx}{dt}$: Continuous derivative
- $\Delta x = x(t+\Delta t) - x(t)$: Discrete change

---

**End of Mathematical Reference**

*Last updated: November 16, 2025*
*SimPulse Formula E Simulator - Mathematical Foundation*
