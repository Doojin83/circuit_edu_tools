import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 웹 페이지 기본 설정
st.set_page_config(page_title="Circuit Signal Analyzer", layout="wide")
st.title("RLC Step Response & Pole Location in s-plane")

# 1. 왼쪽 사이드바에 UI(슬라이더) 배치
st.sidebar.header("Adjustment of Parameters")
alpha = st.sidebar.slider('Attenuation Factor ($\\alpha$)', min_value=0.0, max_value=10.0, value=2.0, step=0.1)
omega_0 = st.sidebar.slider('Natural Frequency ($\\omega_0$)', min_value=0.0, max_value=10.0, value=5.0, step=0.1)

st.sidebar.markdown("---")
st.sidebar.caption("Designed by Doojin Jang © 2026 ORBIT LAB. All Rights Reserved.")

# 2. 데이터 계산 및 시스템 상태 판별 (20초 고정)
t = np.linspace(0, 20, 2000)

if alpha < omega_0:
    # 2.1 감쇠 미달 (Underdamped): 1V로 수렴하며 오버슈트/진동 발생
    omega_d = np.sqrt(omega_0**2 - alpha**2)
    v_t = 1 - np.exp(-alpha * t) * (np.cos(omega_d * t) + (alpha / omega_d) * np.sin(omega_d * t))
    poles = [-alpha + 1j*omega_d, -alpha - 1j*omega_d]
    status_str = "Underdamped"
    title_time = f'Step Response ({status_str}): $v(t) = 1 - e^{{{-alpha}t}} \\left[ \\cos({omega_d:.2f}t) + \\frac{{{alpha}}}{{{omega_d:.2f}}} \\sin({omega_d:.2f}t) \\right]$'

elif alpha > omega_0:
    # 2.2 과감쇠 (Overdamped): 진동 없이 느리게 1V로 수렴
    beta = np.sqrt(alpha**2 - omega_0**2)
    v_t = 1 - np.exp(-alpha * t) * (np.cosh(beta * t) + (alpha / beta) * np.sinh(beta * t))
    poles = [complex(-alpha + beta, 0), complex(-alpha - beta, 0)]
    status_str = "Overdamped"
    title_time = f'Step Response ({status_str}): $v(t) = 1 - e^{{{-alpha}t}} \\left[ \\cosh({beta:.2f}t) + \\frac{{{alpha}}}{{{beta:.2f}}} \\sinh({beta:.2f}t) \\right]$'

else:
    # 2.3 임계 감쇠 (Critically Damped): 진동 없이 가장 빠르게 1V로 수렴
    v_t = 1 - np.exp(-alpha * t) * (1 + alpha * t)
    poles = [complex(-alpha, 0), complex(-alpha, 0)]
    status_str = "Critically Damped"
    title_time = f'Step Response ({status_str}): $v(t) = 1 - e^{{{-alpha}t}} (1 + {alpha}t)$'

# 3. 그래프 그리기
fig, (ax_time, ax_splane) = plt.subplots(1, 2, figsize=(14, 5))

# 시간 영역 플롯 (Step Response)
ax_time.plot(t, v_t, lw=2, color='#1f77b4')
ax_time.axhline(1.0, color='green', linestyle='--', lw=1.5, label='Steady-state (1V)') # 최종 수렴선 추가
ax_time.set_title(title_time, fontsize=11)
ax_time.set_xlabel('Time (t)')
ax_time.set_ylabel('Amplitude (V)')
ax_time.set_xlim(0, 20)
# 스텝 응답 관찰을 위해 y축 스케일 고정
ax_time.set_ylim(-0.2, 2.2)
ax_time.grid(True)
ax_time.legend(loc='upper right')

# s-평면 플롯 (회로 고정 극점)
ax_splane.scatter([p.real for p in poles], [p.imag for p in poles], 
                  marker='x', color='red', s=100, linewidths=2, zorder=3)
ax_splane.set_title(f's-plane: System Poles ({status_str})', fontsize=14)
ax_splane.set_xlabel('Real ($\\sigma$)')
ax_splane.set_ylabel('Imaginary ($j\\omega$)')
ax_splane.set_xlim(-11, 1.0)
ax_splane.set_ylim(-11, 11)
ax_splane.axhline(0, color='black', lw=1)
ax_splane.axvline(0, color='black', lw=1)
ax_splane.grid(True)

# 4. Streamlit 화면에 그래프 출력
st.pyplot(fig)
