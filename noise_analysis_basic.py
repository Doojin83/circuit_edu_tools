import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Page 레이아웃 설정
st.set_page_config(page_title="Noise Analysis Simulator", layout="wide")

st.title("💡 Noise Analysis & Verification Interactive Tool")
st.markdown("본 앱은 **IC 설계 및 검증** 강의의 Noise 개념 이해를 돕기 위한 교육용 시뮬레이터입니다.")

# ----------------------------------------------------------------
# 사이드바: 글로벌 파라미터 및 탭 선택
# ----------------------------------------------------------------
st.sidebar.header("📊 Simulation Parameters")
tab_select = st.sidebar.radio(
    "확인할 강의 장표를 선택하세요:",
    ["1. Stochastic & PDF (4장)", "2. PSD & kT/C Noise (5-8장)", "3. Correlated Sources (9장)"]
)

# ----------------------------------------------------------------
# Tab 1: Stochastic Process & PDF (정규분포와 시그마 경계선)
# ----------------------------------------------------------------
if tab_select == "1. Stochastic & PDF (4장)":
    st.header("1. Time Domain Stochastic Process & PDF")
    st.markdown("💡 **핵심 개념:** 노이즈는 미래의 값을 예측할 수 없지만, 오랜 시간 샘플링하면 통계적 한계선($4\\sigma$) 내에 존재함을 예측할 수 있습니다.")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader("설정 파라미터")
        num_samples = st.slider("샘플 개수 (Time Samples)", 500, 10000, 2000, step=500)
        sigma = st.slider("노이즈 표준편차 (Sigma, Root-Mean-Square)", 0.1, 2.0, 0.5, step=0.1)
        
    # 데이터 생성
    np.random.seed(42)
    noise_time = np.random.normal(0, sigma, num_samples)
    time = np.arange(num_samples)
    
    with col1:
        # Time Domain Plot
        fig, ax = plt.subplots(2, 1, figsize=(10, 6))
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
        # Gaussian Fit
        xmin, xmax = ax[1].get_xlim()
        x_axis = np.linspace(xmin, xmax, 100)
        ax[1].plot(x_axis, norm.pdf(x_axis, 0, sigma), color='darkblue', linewidth=2, label='Gaussian Fit')
        
        # 1, 2, 3 Sigma 영역 표시
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
# Tab 2: PSD & kT/C Noise (RC 필터 적분 및 R 무관성 증명)
# ----------------------------------------------------------------
elif tab_select == "2. PSD & kT/C Noise (5-8장)":
    st.header("2. Power Spectral Density & $kT/C$ Noise Paradox")
    st.markdown("💡 **핵심 개념:** RC Low-Pass Filter에서 저항 $R$의 백색 잡음 밀도는 $4kTR$이지만, 필터의 대역폭(BW)은 $1/(4RC)$입니다. 따라서 총 출력 노이즈 전력은 $R$과 무관하게 오직 **$kT/C$**로만 결정됩니다.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("회로 및 환경 변수")
        T_celsius = st.slider("온도 (Temperature, °C)", -40, 125, 25, step=5)
        R_kohm = st.slider("저항 값 ($R$, kΩ)", 1.0, 100.0, 10.0, step=5.0)
        C_pf = st.slider("커패시터 값 ($C$, pF)", 1.0, 50.0, 5.0, step=1.0)
        
        # 물리 상수 정의
        k_B = 1.38e-23  # Boltzmann Constant
        T_kelvin = T_celsius + 273.15
        R = R_kohm * 1e3
        C = C_pf * 1e-12
        
        # 계산 값
        S_in = 4 * k_B * T_kelvin * R  # V^2/Hz (Single-sided)
        fc = 1 / (2 * np.pi * R * C)  # Cut-off frequency
        kt_c_theoretical = (k_B * T_kelvin) / C
        rms_noise_theoretical = np.sqrt(kt_c_theoretical)
        
        # 메트릭 출력
        st.info(f"**White Noise PSD ($S_{{in}}$):** \n{S_in:.2e} $V^2/Hz$")
        st.success(f"**필터 차단 주파수 ($f_c$):** \n{fc/1e6:.2f} MHz")
        st.metric(label="이론적 Total RMS Noise (√kT/C)", value=f"{rms_noise_theoretical*1e6:.2f} μV")
        
    with col2:
        # 주파수 축 생성 (Log scale)
        freq = np.logspace(3, 10, 500)  # 1kHz ~ 10GHz
        
        # Transfer Function |H(f)|^2
        H_squared = 1 / (1 + (freq / fc)**2)
        S_out = S_in * H_squared
        
        fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
        
        # 입력 백색 소음 및 필터 특성
        ax[0].loglog(freq, np.full_like(freq, S_in), 'r--', label="Input Noise $S_{in}(f) = 4kTR$")
        ax[0].loglog(freq, H_squared, 'b-', label=r"Filter Response $|H(f)|^2$")
        ax[0].axvline(fc, color='k', linestyle=':', label=f'Cut-off $f_c$ ({fc/1e6:.1f}MHz)')
        ax[0].set_ylabel("Magnitude / PSD")
        ax[0].set_title("Filter Transfer Function & Input White Noise")
        ax[0].legend(loc="lower left")
        ax[0].grid(True, which="both", alpha=0.3)
        
        # 출력 노이즈 스펙트럼 밀도 (PSD)
        ax[1].loglog(freq, S_out, color='purple', label="Output Noise $S_{out}(f)$")
        ax[1].fill_between(freq, S_out, color='purple', alpha=0.15, label="Total Noise Power (Area = $kT/C$)")
        ax[1].axvline(fc, color='k', linestyle=':')
        ax[1].set_xlabel("Frequency [Hz]")
        ax[1].set_ylabel("Output PSD [$V^2/Hz$]")
        ax[1].set_title("Output Power Spectral Density ($S_{out}$)")
        ax[1].legend(loc="lower left")
        ax[1].grid(True, which="both", alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        st.caption("💡 **교수님 가이드 팁:** 저항($R$)을 극단적으로 키워보세요. 입력 노이즈 바닥($S_{in}$)은 올라가지만, 대역폭($f_c$)이 좁아지면서 보라색 면적($kT/C$)은 신기하게도 완벽히 일정하게 유지되는 대역폭 트레이드오프 관계를 시각적으로 보여줄 수 있습니다.")

# ----------------------------------------------------------------
# Tab 3: Correlated vs Uncorrelated Sources (중첩의 원리 위배 시각화)
# ----------------------------------------------------------------
elif tab_select == "3. Correlated Sources (9장)":
    st.header("3. Correlated vs. Uncorrelated Noise Sources")
    st.markdown("💡 **핵심 개념:** 노이즈는 전압이 아닌 **제곱(Power)** 단위로 더해지기 때문에 단순 중첩의 원리(Superposition)가 통하지 않습니다. 두 노이즈 간 상관관계($3^{rd}\\text{ term}$)에 따라 합산 전력이 어떻게 변하는지 확인합니다.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("상관관계 계수 설정")
        rho = st.slider("상관 계수 (Correlation Coefficient, ρ)", -1.0, 1.0, 0.0, step=0.1)
        st.markdown("""
        * **ρ = 0**: Uncorrelated (독립 노이즈 소스, $3^{rd}\\text{ term} = 0$)
        * **ρ = 1**: Fully Correlated (동일 노이즈 소스)
        * **ρ = -1**: Anti-Correlated (차동 입력 등 상쇄 관계)
        """)
        
    # 독립된 노이즈 생성
    np.random.seed(100)
    samples = 1000
    x1 = np.random.normal(0, 1, samples)
    w = np.random.normal(0, 1, samples)
    
    # 상관관계가 적용된 x2 생성: x2 = rho*x1 + sqrt(1-rho^2)*w
    x2 = rho * x1 + np.sqrt(1 - rho**2) * w
    
    # 각각의 Power 및 합산 Power 계산
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
        ax.set_title(f"Noise Power Summation (Current ρ = {rho})")
        
        # 값 텍스트 표시
        for i, v in enumerate(powers):
            ax.text(i, v + 0.05, f"{v:.2f}", ha='center', fontweight='bold')
            
        st.pyplot(fig)
        
        # 교안 공식 매핑 텍스트
        st.markdown(f"""
        ### 📝 수식 검증 결과 (장표 9페이지 수식 매핑)
        $$P_{{av}} = P_{{av1}} + P_{{av2}} + \\lim_{{T\\to\\infty}}\\frac{{1}}{{T}}\\int_{{-T/2}}^{{+T/2}} 2x_1(t)x_2(t)dt$$
        * **$P_{{av1}} + P_{{av2}}$ (단순 합):** `{p1+p2:.4f}`
        * **$3^{{rd}}$ Term (제3의 항 교차 전력):** `{p3rd_term:.4f}`
        * **최종 합산 전력 ($P_{{tot}}$):** `{ptot_real:.4f}`  
        
        _결론: `ρ = 0`일 때는 제3의 항이 0에 수렴하여 두 소스의 전력이 단순히 더해지지만, 상관관계가 생기면 단순 중첩 결과와 큰 오차가 발생합니다._
        """)
