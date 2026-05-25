import streamlit as st
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

# Streamlit 레이아웃 설정
st.set_page_config(layout="wide", page_title="Circuit Bode Plot Interactive Lab")

st.title("Bode Plot Analyzer: Common-Source + Source Follower")
st.markdown("""
### Cascade of CS Stage and Source Follower with Capacitor Coupling
Adjust the sliders to observe the real-time impact of circuit parameters on the Magnitude Bode Plot.
""")

# 사이드바에 슬라이더 배치 (실무 단위를 사용하여 학생들의 직관성 향상)
st.sidebar.header("Circuit Parameters Setup")

gm1_ma = st.sidebar.slider("M1 Transconductance: gm1 (mA/V)", min_value=0.1, max_value=20.0, value=2.0, step=0.1)
gm2_ma = st.sidebar.slider("M2 Transconductance: gm2 (mA/V)", min_value=0.1, max_value=20.0, value=5.0, step=0.1)
RD_k = st.sidebar.slider("Drain Resistor: R_D (kΩ)", min_value=1.0, max_value=50.0, value=10.0, step=1.0)
Ri_k = st.sidebar.slider("Bias Resistor: R_i (kΩ)", min_value=10.0, max_value=500.0, value=100.0, step=10.0)
Ci_pf = st.sidebar.slider("Coupling Capacitor: C_i (pF)", min_value=1.0, max_value=100.0, value=10.0, step=1.0)
CL_pf = st.sidebar.slider("Load Capacitor: C_L (pF)", min_value=0.1, max_value=50.0, value=5.0, step=0.1)

# SI 단위계로 변환
gm1 = gm1_ma * 1e-3
gm2 = gm2_ma * 1e-3
R_D = RD_k * 1e3
R_i = Ri_k * 1e3
C_i = Ci_pf * 1e-12
C_L = CL_pf * 1e-12

# 슬라이드 기반 각 Stage별 전달함수 정의
# Stage 1: CS Gain
num1 = np.array([-gm2 * R_D])
den1 = np.array([1])

# Stage 2: Coupling Network
num2 = np.array([1, 0])
den2 = np.array([1, 1 / (R_i * C_i)])

# Stage 3: Source Follower
p2 = gm1 / C_L
num3 = np.array([p2])
den3 = np.array([1, p2])

# 다항식 곱셈(convolve)으로 시스템 결합
num = np.convolve(num1, num2)
num = np.convolve(num, num3)

den = np.convolve(den1, den2)
den = np.convolve(den, den3)

sys = signal.TransferFunction(num, den)

# 주파수 축 계산 (10 kHz ~ 10 GHz 대역)
w = np.logspace(4, 11, 1000)
w, mag, phase = signal.bode(sys, w)
f_hz = w / (2 * np.pi)

# 이론적 주요 지점 계산 (실시간 갱신용 레이블 데이터)
midband_gain_db = 20 * np.log10(gm2 * R_D)
fp1_hz = 1 / (2 * np.pi * R_i * C_i)
fp2_hz = gm1 / (2 * np.pi * C_L)

# 화면에 현재 주요 지점의 이론적 스펙 수치 표시
col1, col2, col3 = st.columns(3)
col1.metric("Midband Gain (approx.)", f"{midband_gain_db:.2f} dB")
col2.metric("Low-Freq Pole (fp1)", f"{fp1_hz/1e3:.1f} kHz")
col3.metric("High-Freq Pole (fp2)", f"{fp2_hz/1e6:.1f} MHz")

# Matplotlib을 이용한 그래프 렌더링
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.semilogx(f_hz, mag, 'g-', lw=2.5, label="Stage Cascade Approach")

# 폴(Pole) 위치 시각적 가이드 라인 추가
ax.axvline(fp1_hz, color='orange', linestyle=':', alpha=0.8, label=f'fp1 ({fp1_hz/1e3:.1f}kHz)')
ax.axvline(fp2_hz, color='red', linestyle=':', alpha=0.8, label=f'fp2 ({fp2_hz/1e6:.1f}MHz)')

ax.set_title("Bode Plot from Cascaded Slide Equations", fontsize=14, pad=15)
ax.set_xlabel("Frequency (Hz)", fontsize=12)
ax.set_ylabel("Magnitude (dB)", fontsize=12)
ax.set_ylim(midband_gain_db - 40, midband_gain_db + 10) # 이득 변화에 맞춰 y축 자동 스케일 조절
ax.grid(True, which='both', linestyle='--', alpha=0.5)
ax.legend(loc="lower left")

# Streamlit 화면에 플롯 출력
st.pyplot(fig)
