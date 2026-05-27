import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Page Configuration
st.set_page_config(page_title="Noise Analysis Simulator", layout="wide")

st.title("💡 Noise Analysis & Verification Interactive Tool")
st.markdown("This app is an interactive educational simulator designed for IC Design and Verification courses.")

# ----------------------------------------------------------------
# Sidebar: Navigation
# ----------------------------------------------------------------
st.sidebar.header("📊 Navigation")
tab_select = st.sidebar.radio(
    "Select a Lecture Topic:",
    ["1. Stochastic & PDF", "2. PSD & kT/C Noise", "3. Correlated Sources"]
)

# ----------------------------------------------------------------
# Tab 1: Stochastic Process & PDF
# ----------------------------------------------------------------
if tab_select == "1. Stochastic & PDF":
    st.header("1. Time Domain Stochastic Process & PDF")
    
    # Key Checkpoints Box
    st.info("""
    ### 🔍 Key Verification Checkpoints
    * **Temporal Randomness:** The exact amplitude at any specific time instance $t_1$ is completely unpredictable[cite: 21, 81].
    * **Statistical Bound:** Although individual values are random, the overall amplitude bounds are highly predictable and rarely exceed $\pm4\\sigma$ ($99.99\%$)[cite: 76, 81].
    * **Dynamic Scaling:** Adjusting the **Sigma (𝛔)** slider alters the absolute fluctuation wave, but the relative percentage within the $\pm1\\sigma$, $\pm2\\sigma$, and $\pm3\\sigma$ boundaries remains perfectly constant[cite: 66, 67].
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader("Simulation Control")
        num_samples = st.slider("Number of Time Samples", 500, 10000, 2000, step=500)
        sigma = st.slider("Noise Standard Deviation (Sigma, RMS)", 0.1, 2.0, 0.5, step=0.1)
        
    # Data Generation
    np.random.seed(42)
    noise_time = np.random.normal(0, sigma, num_samples)
    time = np.arange(num_samples)
    
    with col1:
        fig, ax = plt.subplots(2, 1, figsize=(10, 6))
        
        # Time Domain Plot
        ax[0].plot(time, noise_time, color='#2ca02c', alpha=0.7, linewidth=0.5)
        ax[0].axhline(3*sigma, color='r', linestyle='--', label=r'$\pm3\sigma$ Boundary')
        ax[0].axhline(-3*sigma, color='r', linestyle='--')
        ax[0].set_title("Time Domain Waveform $x(t)$")
        ax[0].set_xlabel("Time (sample)")
        ax[0].set_ylabel("Amplitude [V]")
        ax[0].legend(loc="upper right")
        ax[0].grid(True, alpha=0.3)
        
        # PDF Histogram Plot
        count, bins, ignored = ax[1].hist(noise_time, bins=50, density=True, color='skyblue', edgecolor='black', alpha=0.7)
        xmin, xmax = ax[1].get_xlim()
        x_axis = np.linspace(xmin, xmax, 100)
        ax[1].plot(x_axis, norm.pdf(x_axis, 0, sigma), color='darkblue', linewidth=2, label='Gaussian Fit')
        
        ax[1].axvline(sigma, color='orange', linestyle=':', label=r'$\pm1\sigma$ (68.26%)')
        ax[1].axvline(-sigma, color='orange', linestyle=':')
        ax[1].axvline(2*sigma, color='magenta', linestyle=':', label=r'$\pm2\sigma$ (95.44%)')
        ax[1].axvline(-2*sigma, color='magenta', linestyle=':')
        
        ax[1].set_title("Probability Density Function (PDF)")
        ax[1].set_xlabel("Amplitude [V]")
        ax[1].set_ylabel("Density")
        ax[1].legend(loc="upper right")
        ax[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)

# ----------------------------------------------------------------
# Tab 2: PSD & kT/C Noise
# ----------------------------------------------------------------
elif tab_select == "2. PSD & kT/C Noise":
    st.header("2. Power Spectral Density & $kT/C$ Noise Paradox")
    
    # Key Checkpoints Box
    st.info("""
    ### 🔍 Key Verification Checkpoints
    * **R-Independence Proof:** Total integrated output RMS noise depends strictly on $\\sqrt{kT/C}$ and is completely independent of the resistor value $R$[cite: 210].
    * **Bandwidth Trade-off:** Increasing $R$ drives up the white noise floor ($4kTR$)[cite: 206]. However, it simultaneously narrows the filter bandwidth ($f_c = 1/(2\\pi RC)$)[cite: 207, 210].
    * **Constant Area:** Observe the lower chart; sweeping $R$ changes the shape of the spectrum, but the total integrated area (purple shading) stays invariant[cite: 209, 210].
    """)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Circuit & Environment Parameters")
        T_celsius = st.slider("Temperature (°C)", -40, 125, 25, step=5)
        R_kohm = st.slider("Resistor Value ($R$, kΩ)", 1.0, 100.0, 10.0, step=5.0)
        C_pf = st.slider("Capacitor Value ($C$, pF)", 1.0, 50.0, 5.0, step=1.0)
        
        # Constants & Equations
        k_B = 1.38e-23  
        T_kelvin = T_celsius + 273.15
        R = R_kohm * 1e3
        C = C_pf * 1e-12
        
        S_in = 4 * k_B * T_kelvin * R  
        fc = 1 / (2 * np.pi * R * C)  
        kt_c_theoretical = (k_B * T_kelvin) / C
        rms_noise_theoretical = np.sqrt(kt_c_theoretical)
        
        st.metric(label="Input Noise PSD ($S_{in}$)", value=f"{S_in:.2e} V²/Hz")
        st.metric(label="Filter Cut-off Frequency ($f_c$)", value=f"{fc/1e6:.2f} MHz")
        st.success(f"**Total Integrated RMS Noise:** \n{rms_noise_theoretical*1e6:.2f} μV")
        
    with col2:
        freq = np.logspace(3, 10, 500)  
        H_squared = 1 / (1 + (freq / fc)**2)
        S_out = S_in * H_squared
        
        fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
        
        # Filter Response Plot
        ax[0].loglog(freq, np.full_like(freq, S_in), 'r--', label="Input Noise $S_{in}(f) = 4kTR$")
        ax[0].loglog(freq, H_squared, 'b-', label=r"Filter Response $|H(f)|^2$")
        ax[0].axvline(fc, color='k', linestyle=':', label=f'Cut-off $f_c$ ({fc/1e6:.1f}MHz)')
        ax[0].set_ylabel("Magnitude / PSD")
        ax[0].set_title("Filter Transfer Function & Input White Noise")
        ax[0].legend(loc="lower left")
        ax[0].grid(True, which="both", alpha=0.3)
        
        # Output PSD Plot
        ax[1].loglog(freq, S_out, color='purple', label="Output Noise $S_{out}(f)$")
        ax[1].fill_between(freq, S_out, color='purple', alpha=0.15, label="Total Power Area ($kT/C$)")
        ax[1].axvline(fc, color='k', linestyle=':')
        ax[1].set_xlabel("Frequency [Hz]")
        ax[1].set_ylabel("Output PSD [$V^2/Hz$]")
        ax[1].set_title("Output Power Spectral Density ($S_{out}$)")
        ax[1].legend(loc="lower left")
        ax[1].grid(True, which="both", alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)

# ----------------------------------------------------------------
# Tab 3: Correlated vs Uncorrelated Sources
# ----------------------------------------------------------------
elif tab_select == "3. Correlated Sources":
    st.header("3. Correlated vs. Uncorrelated Noise Sources")
    
    # Key Checkpoints Box
    st.info("""
    ### 🔍 Key Verification Checkpoints
    * **Superposition Violation:** Noise sources cannot be added linearly like raw voltage or current because noise is calculated using mean squared power[cite: 219, 235].
    * **Uncorrelated Case (𝛒 = 0):** The 3rd cross-term cancels out entirely during long-term integration, making the actual total power equal to the simple arithmetic sum ($P_{av1} + P_{av2}$)[cite: 222, 237].
    * **Correlated Case (𝛒 ≠ 0):** The 3rd term becomes significant[cite: 221, 237]. Fully correlated sources ($\\rho = 1$) cause constructive addition, while anti-correlated sources ($\\rho = -1$) provide total cancellation.
    """)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Correlation Control")
        rho = st.slider("Correlation Coefficient (ρ)", -1.0, 1.0, 0.0, step=0.1)
        
    # Statistical Data Generation
    np.random.seed(100)
    samples = 1000
    x1 = np.random.normal(0, 1, samples)
    w = np.random.normal(0, 1, samples)
    
    # Creating correlation: x2 = rho*x1 + sqrt(1-rho^2)*w
    x2 = rho * x1 + np.sqrt(1 - rho**2) * w
    
    p1 = np.mean(x1**2)
    p2 = np.mean(x2**2)
    ptot_real = np.mean((x1 + x2)**2)
    p3rd_term = np.mean(2 * x1 * x2)
    
    with col2:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        bars = ['Source 1 Power', 'Source 2 Power', 'Simple Sum (P1+P2)', 'Actual Total Power']
        powers = [p1, p2, p1 + p2, ptot_real]
        colors = ['#1f77b4', '#aec7e8', '#ffbb78', '#ff7f0e']
        
        ax.bar(bars, powers, color=colors, edgecolor='black', alpha=0.8)
        ax.set_ylabel("Normalized Average Power [$V^2$]")
        ax.set_title(f"Noise Power Summation Behavior (Current ρ = {rho})")
        
        for i, v in enumerate(powers):
            ax.text(i, v + 0.05, f"{v:.2f}", ha='center', fontweight='bold')
            
        st.pyplot(fig)
        
        # Quantitative Summary
        st.markdown(f"""
        ### 📝 Mathematical Verification
        $$P_{{av}} = P_{{av1}} + P_{{av2}} + \\lim_{{T\\to\\infty}}\\frac{{1}}{{T}}\\int_{{-T/2}}^{{+T/2}} 2x_1(t)x_2(t)dt$$
        * **Simple Arithmetic Sum ($P_{{av1}} + P_{{av2}}$):** `{p1+p2:.4f}`
        * **3rd Cross-Term Value:** `{p3rd_term:.4f}`
        * **Actual Integrated Total Power ($P_{{tot}}$):** `{ptot_real:.4f}`
        """)
