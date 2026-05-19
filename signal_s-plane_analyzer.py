import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 웹 페이지 기본 설정
st.set_page_config(page_title="회로 신호 분석기", layout="wide")
st.title("시간 영역 신호와 s-평면 극점(Pole) 분석기")

# 1. 왼쪽 사이드바에 UI(슬라이더) 배치
st.sidebar.header("파라미터 조절")
alpha = st.sidebar.slider('감쇠 상수 ($\\alpha$)', min_value=0.0, max_value=5.0, value=1.0, step=0.1)
omega = st.sidebar.slider('각주파수 ($\\omega$)', min_value=1.0, max_value=10.0, value=5.0, step=0.1)

# 2. 데이터 계산
t = np.linspace(0, 10, 1000)
v_t = np.exp(-alpha * t) * np.sin(omega * t)
poles = [-alpha + 1j*omega, -alpha - 1j*omega]

# 3. 그래프 그리기
fig, (ax_time, ax_splane) = plt.subplots(1, 2, figsize=(14, 5))

# 시간 영역 플롯
ax_time.plot(t, v_t, lw=2, color='#1f77b4')
ax_time.set_title(f'Time Domain: $v(t) = e^{{{-alpha}t}} \\sin({omega}t)$', fontsize=14)
ax_time.set_xlabel('Time (t)')
ax_time.set_ylabel('Amplitude')
ax_time.set_xlim(0, 10)
ax_time.set_ylim(-1.2, 1.2)
ax_time.grid(True)

# s-평면 플롯
ax_splane.scatter([p.real for p in poles], [p.imag for p in poles], 
                  marker='x', color='red', s=100, linewidths=2)
ax_splane.set_title('s-plane: Poles of $V(s)$', fontsize=14)
ax_splane.set_xlabel('Real ($\\sigma$)')
ax_splane.set_ylabel('Imaginary ($j\\omega$)')
ax_splane.set_xlim(-5.5, 0.5)
ax_splane.set_ylim(-11, 11)
ax_splane.axhline(0, color='black', lw=1)
ax_splane.axvline(0, color='black', lw=1)
ax_splane.grid(True)

# 4. Streamlit 화면에 그래프 출력
st.pyplot(fig)
