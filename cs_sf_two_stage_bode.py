import streamlit as st
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

# Streamlit 레이아웃 설정
st.set_page_config(layout="wide", page_title="Circuit Bode Plot Interactive Lab")

# wide 레이아웃에서 메인 콘텐츠 영역이 너무 퍼지지 않도록 가로 폭 분할 구조 배치
col_main, _ = st.columns([3, 1])

with col_main:
    # 컬럼을 나누어 제목과 회로 이미지를 나란히 배치 (비율 4:1)
    col_title, col_img = st.columns([4, 1])

    with col_title:
        st.title("Bode Plot Analyzer: CS + SF")
        st.markdown("""
        ### Cascade of CS Stage and Source Follower with Capacitor Coupling
        Adjust the sliders to observe the real-time impact of circuit parameters on the Magnitude and Phase Bode Plots.
        """)

    with col_img:
        # GitHub의 원본 이미지(raw) 전용 주소
        raw_img_url = "https://raw.githubusercontent.com/Doojin83/circuit_edu_tools/main/circuit_diagram.png"
        st.image(raw_img_url, width=250, caption="Circuit Layout")

    # 사이드바에 슬라이더 배치
    st.sidebar.header("Circuit Parameters Setup")

    gm1_ma = st.sidebar.slider(r"M1 Transconductance: $g_{m1}$ (mA/V)", min_value=0.1, max_value=20.0, value=2.0, step=0.1)
    gm2_ma = st.sidebar.slider(r"M2 Transconductance: $g_{m2}$ (mA/V)", min_value=0.1, max_value=20.0, value=5.0, step=0.1)
    RD_k = st.sidebar.slider(r"Drain Resistor: $R_{D}$ (kΩ)", min_value=1.0, max_value=50.0, value=10.0, step=1.0)
    Ri_k = st.sidebar.slider(r"Bias Resistor: $R_{i}$ (kΩ)", min_value=10.0, max_value=500.0, value=100.0, step=10.0)
    Ci_pf = st.sidebar.slider(r"Coupling Capacitor: $C_{i}$ (pF)", min_value=1.0, max_value=100.0, value=10.0, step=1.0)
    CL_pf = st.sidebar.slider(r"Load Capacitor: $C_L$ (pF)", min_value=0.1, max_value=50.0, value=5.0, step=0.1)

    # 사이드바 최하단 크레딧 배치
    st.sidebar.markdown("---")
    st.sidebar.caption("Designed by Doojin Jang © 2026 ORBIT LAB. All Rights Reserved.")

    # SI 단위계로 변환
    gm1 = gm1_ma * 1e-3
    gm2 = gm2_ma * 1e-3
    R_D = RD_k * 1e3
    R_i = Ri_k * 1e3
    C_i = Ci_pf * 1e-12
    C_L = CL_pf * 1e-12

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

    # 이론적 주요 지점 계산
    midband_gain_db = 20 * np.log10(gm2 * R_D)
    fp1_hz = 1 / (2 * np.pi * R_i * C_i)
    fp2_hz = gm1 / (2 * np.pi * C_L)

    # 화면에 현재 주요 지점의 이론적 스펙 수치 표시
    col1, col2, col3 = st.columns(3)
    col1.metric("Midband Gain (approx.)", f"{midband_gain_db:.2f} dB")
    col2.metric("Low-Freq Pole (fp1)", f"{fp1_hz/1e3:.1f} kHz")
    col3.metric("High-Freq Pole (fp2)", f"{fp2_hz/1e6:.1f} MHz")

    # 🛠️ [수정 구간] 2행 1열 구조의 서브플롯 생성 및 주파수축(X축) 공유 설정
    fig, (ax_mag, ax_phase) = plt.subplots(2, 1, figsize=(8, 5.5), sharex=True)

    # 1. 상단: 크기(Magnitude) 플롯
    ax_mag.semilogx(f_hz, mag, 'g-', lw=2.5, label="Stage Cascade Approach")
    ax_mag.axvline(fp1_hz, color='orange', linestyle=':', alpha=0.8, label=f'fp1 ({fp1_hz/1e3:.1f}kHz)')
    ax_mag.axvline(fp2_hz, color='red', linestyle=':', alpha=0.8, label=f'fp2 ({fp2_hz/1e6:.1f}MHz)')
    
    ax_mag.set_title("Bode Plot from Cascaded Slide Equations", fontsize=14, pad=12)
    ax_mag.set_ylabel("Magnitude (dB)", fontsize=12)
    ax_mag.set_ylim(midband_gain_db - 40, midband_gain_db + 10)
    ax_mag.grid(True, which='both', linestyle='--', alpha=0.5)
    ax_mag.legend(loc="lower left")

    # 2. 하단: 위상(Phase) 플롯 추가
    ax_phase.semilogx(f_hz, phase, 'b-', lw=2.5) # 위상은 전통적인 청색 라인으로 명시
    ax_phase.axvline(fp1_hz, color='orange', linestyle=':', alpha=0.8)
    ax_phase.axvline(fp2_hz, color='red', linestyle=':', alpha=0.8)
    
    ax_phase.set_xlabel("Frequency (Hz)", fontsize=12)
    ax_phase.set_ylabel("Phase (deg)", fontsize=12)
    ax_phase.grid(True, which='both', linestyle='--', alpha=0.5)

    # 각 플롯 레이블 및 타이틀 간격 최적화 정돈
    plt.tight_layout()

    # 컴팩트 크기가 화면 너비에 맞춰 강제로 늘어나는 현상 방지
    st.pyplot(fig, use_container_width=False)
