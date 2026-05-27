import numpy as np
import matplotlib.pyplot as plt

# 1. 시간축 및 기본 파라미터 설정
t = np.linspace(-0.5, 1.5, 1000)
f0 = 1                      # 기본 주파수 (1 Hz)
w0 = 2 * np.pi * f0         # 각주파수

# 2. 비교 대상인 이상적인 펄스 파형 (Square wave, 0 to 1)
ideal_pulse = 0.5 + 0.5 * np.sign(np.sin(w0 * t))

# 3. 누적할 하모닉스 차수 설정 (홀수 차수만 기여함)
harmonics_counts = [1, 3, 7, 19, 49]

# 4. 시각화를 위한 서브플롯 생성
fig, axes = plt.subplots(len(harmonics_counts), 1, figsize=(10, 12), sharex=True)

for i, N in enumerate(harmonics_counts):
    # DC 성분 (1/2)으로 시작
    f_t = np.ones_like(t) * 0.5
    
    # 1부터 N까지의 홀수 하모닉스를 누적 합산
    for n in range(1, N + 1, 2):
        f_t += (2 / (np.pi * n)) * np.sin(n * w0 * t)
    
    # 이상적인 펄스 파형을 점선으로 표시
    axes[i].plot(t, ideal_pulse, 'k--', alpha=0.5, label='Ideal Pulse Wave')
    
    # 푸리에 급수로 합성된 파형 표시
    axes[i].plot(t, f_t, color='blue', linewidth=2, label=f'Sum of harmonics up to n={N}')
    
    # 그래프 스타일링
    axes[i].set_ylabel('Amplitude')
    axes[i].grid(True, linestyle=':', alpha=0.6)
    axes[i].legend(loc='upper right')
    axes[i].set_ylim(-0.3, 1.3)
    axes[i].set_title(f'Fourier Series Synthesis: N = {N} (Up to {N}th Harmonic)', fontsize=10)

# 최하단 그래프에 X축 레이블 추가
axes[-1].set_xlabel('Time (seconds)')
plt.tight_layout()

# 이미지 파일로 저장
plt.savefig('fourier_pulse_synthesis.png', dpi=300)
