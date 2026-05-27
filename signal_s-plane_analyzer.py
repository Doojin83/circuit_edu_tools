import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 웹 페이지 기본 설정
st.set_page_config(page_title="Circuit Signal Analyzer", layout="wide")
st.title("Signal in Time Domain & Pole Location in s-plane")

# 1. 왼쪽 사이드바에 UI(슬라이더) 배치
st.sidebar.header("Adjustment of Parameters")
# 과감쇠를 쉽게 관찰할 수 있도록 alpha의 범위를 넓혔습니다.
alpha = st.sidebar.slider('Attenuation Factor ($\\alpha$)', min_value=0.0, max_value=10.0, value=2.0, step=0.1)
omega_0 = st.sidebar.slider('Natural Frequency ($\\omega_0$)', min_value=0.1, max_value=10.0, value=5.0, step=0.1)

st.sidebar.markdown("---")
st.sidebar.caption("Designed by Doojin Jang © 2026 ORBIT LAB. All Rights Reserved.")

# 2. 데이터 계산 및 시스템 상태 판별
t = np.linspace(0, 20, 2000)

if alpha < omega_0:
    # 2.1 감쇠 미달 (Underdamped): 복소 극점 쌍, 댐핑 진동
    omega_d = np.sqrt(omega_0**2 - alpha**2)
    v_t = (1 / omega_d) * np.exp(-alpha * t) * np.sin(omega_d * t)
    poles = [-alpha + 1j*omega_d, -alpha - 1j*omega_d]
    status_str = "Underdamped"
    title_time = f'Time Domain ({status_str}): $v(t) = \\frac{{1}}{{\\omega_d}} e^{{{-alpha}t}} \\sin({omega_d:.2f}t)$'

elif alpha > omega_0:
    # 2.2 과감쇠 (Overdamped): 서로 다른 두 실근 극점, 진동 없음
    beta = np.sqrt(alpha**2 - omega_0**2)
    v_t = (1 / beta) * np.exp(-alpha * t) * np.sinh(beta * t)
    poles = [complex(-alpha + beta, 0), complex(-alpha - beta, 0)]
    status_str = "Overdamped"
    title_time = f'Time Domain ({status_str}): $v(t) = \\frac{{1}}{{\\beta}} e^{{{-alpha}t}} \\sinh({beta:.2f}t)$'

else:
    # 2.3 임계 감쇠 (Critically Damped): 중근 극점
    v_t = t * np.exp(-alpha * t)
    poles = [complex(-alpha, 0), complex(-alpha, 0)]
    status_str = "Critically Damped"
    title_time = f'Time Domain ({status_str}): $v(t) = t \\cdot e^{{{-alpha}t}}$'

# 3. 그래프 그리기
fig, (ax_time, ax_splane) = plt.subplots(1, 2, figsize=(14, 5))

# 시간 영역 플롯
ax_time.plot(t, v_t, lw=2, color='#1f77b4')
ax_time.set_title(title_time, fontsize=12)
ax_time.set_xlabel('Time (t)')
ax_time.set_ylabel('Amplitude')
ax_time.set_xlim(0, 20)
# 파형이 변할 때 축이 깨지지 않도록 동적 y축 설정
max_v = max(np.max(v_t), 0.1)
min_v = min(np.min(v_t), -0.1)
ax_time.set_ylim(min_v * 1.2, max_v * 1.2)
ax_time.grid(True)

# s-평면 플롯
ax_splane.scatter([p.real for p in poles], [p.imag for p in poles], 
                  marker='x', color='red', s=100, linewidths=2, zorder=3)
ax_splane.set_title(f's-plane: Poles ({status_str})', fontsize=14)
ax_splane.set_xlabel('Real ($\\sigma$)')
ax_splane.set_ylabel('Imaginary ($j\\omega$)')
ax_splane.set_xlim(-11, 1.0)
ax_splane.set_ylim(-11, 11)
ax_splane.axhline(0, color='black', lw=1)
ax_splane.axvline(0, color='black', lw=1)
ax_splane.grid(True)

# 4. Streamlit 화면에 그래프 출력
st.pyplot(fig)
