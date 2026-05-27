import streamlit as st
import numpy as np
import matplotlib
# 클라우드 서버 환경 환경 고정
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 1. 페이지 설정
st.set_page_config(page_title="Fourier Series Synthesis", layout="wide")

st.title('📊 푸리에 급수: 사인파로 펄스파 만들기')
st.markdown("""
이 앱은 여러 주파수의 사인파(하모닉스)를 쌓아가며 이상적인 **사각 펄스 파형(Square Wave)**에 가까워지는 과정을 시각화합니다.
""")

# 2. 사이드바 컨트롤러
st.sidebar.header('조절 패널')
n_harmonics_max = st.sidebar.slider(
    '합성에 사용할 최대 하모닉스 차수 (N)',
    min_value=1,
    max_value=99,
    value=1,
    step=2
)

f0 = st.sidebar.number_input('기본 주파수 (Hz)', value=1.0, min_value=0.1, step=0.1)
w0 = 2 * np.pi * f0

# 3. 데이터 계산
t = np.linspace(-0.5, 1.5, 1000)
ideal_pulse = 0.5 + 0.5 * np.sign(np.sin(w0 * t))

accumulated_wave = np.ones_like(t) * 0.5
current_harmonics_list = []

for n in range(1, n_harmonics_max + 1, 2):
    harmonic_component = (2 / (np.pi * n)) * np.sin(n * w0 * t)
    current_harmonics_list.append((n, harmonic_component))
    accumulated_wave += harmonic_component

# 4. 그래프 플로팅 (sharey=True 제거 및 개별 축 설정)
fig, axes = plt.subplots(1, 2, figsize=(15, 5)) # sharey=True 제거하여 독립된 Y축 사용
plt.subplots_adjust(wspace=0.2)

# --- [왼쪽 그래프] 개별 하모닉스성분 (영문 및 수식 처리로 폰트 깨짐 방지) ---
axes[0].set_title(f'Individual Harmonics Components ($n=1$ to $n={n_harmonics_max}$)', fontsize=12)
if n_harmonics_max > 7:
    indices_to_show = sorted(list(set([0, 1, 2, len(current_harmonics_list)//2, -1])))
else:
    indices_to_show = list(range(len(current_harmonics_list)))

for i in indices_to_show:
    if i < len(current_harmonics_list):
        n_val, comp = current_harmonics_list[i]
        linewidth = 2.5 if i == len(current_harmonics_list)-1 else 1.0
        alpha = 1.0 if i == len(current_harmonics_list)-1 else 0.5
        axes[0].plot(t, comp, label=f'$n={n_val}$', linewidth=linewidth, alpha=alpha)

axes[0].set_ylabel('Amplitude')
axes[0].set_xlabel('Time (seconds)')
axes[0].set_ylim(-0.7, 0.7) # n=1 성분(+-0.64)이 잘리지 않도록 안정한 범위 지정
axes[0].grid(True, linestyle=':', alpha=0.6)
if n_harmonics_max < 15:
    axes[0].legend(loc='upper right', fontsize='small')

# --- [오른쪽 그래프] 합성된 결과 파형 ---
axes[1].set_title(f'Accumulated Waveform (Sum up to $n={n_harmonics_max}$)', fontsize=12)
axes[1].plot(t, accumulated_wave, color='blue', linewidth=2.0, label='Synthesized Wave')
axes[1].plot(t, ideal_pulse, 'k--', alpha=0.4, label='Ideal Pulse (Ref)')
axes[1].set_xlabel('Time (seconds)')
axes[1].set_ylim(-0.3, 1.3) # 합성 파형용 스케일 유지
axes[1].grid(True, linestyle=':', alpha=0.6)
axes[1].legend(loc='upper right')

plt.tight_layout()

# Streamlit에 피겨 전달 및 메모리 관리
st.pyplot(fig, clear_figure=True)
plt.close(fig)

# 5. 하단 텍스트 설명 (웹 브라우저 렌더링 영역이므로 한글 깨짐 없음)
st.markdown("""
### 💡 어떻게 작동하나요?
* **하모닉스 누적**: 고주파 성분이 더해질수록 에지가 날카로워집니다.
* **깁스 현상**: 불연속점 근처의 오버슈트는 유한한 차수 합산에서 기인합니다.
""")
