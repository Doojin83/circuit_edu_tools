import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# 초기 변수 설정
initial_alpha = 1.0
initial_omega = 5.0
t = np.linspace(0, 10, 1000)

# 신호 및 극점 계산 함수
def calc_signal(alpha, omega, t):
    return np.exp(-alpha * t) * np.sin(omega * t)

def calc_poles(alpha, omega):
    return [-alpha + 1j*omega, -alpha - 1j*omega]

# 그래프 Figure 및 Axes 설정
fig, (ax_time, ax_splane) = plt.subplots(1, 2, figsize=(12, 5))
plt.subplots_adjust(bottom=0.25) # 슬라이더를 위한 공간 확보

# 1. 시간 영역 (Time Domain) 플롯 초기화
v_t = calc_signal(initial_alpha, initial_omega, t)
line_time, = ax_time.plot(t, v_t, lw=2, color='#1f77b4')
ax_time.set_title('Time Domain: $v(t) = e^{-\\alpha t}\\sin(\\omega t)$')
ax_time.set_xlabel('Time (t)')
ax_time.set_ylabel('Amplitude')
ax_time.set_xlim(0, 10)
ax_time.set_ylim(-1.2, 1.2)
ax_time.grid(True)

# 2. 주파수 영역 (s-plane) 플롯 초기화
poles = calc_poles(initial_alpha, initial_omega)
# 복소수의 실수부(Real)와 허수부(Imag)를 나누어 산점도로 표시
scatter_poles = ax_splane.scatter([p.real for p in poles], [p.imag for p in poles], 
                                  marker='x', color='red', s=100, linewidths=2)
ax_splane.set_title('s-plane: Poles of $V(s)$')
ax_splane.set_xlabel('Real ($\\sigma$)')
ax_splane.set_ylabel('Imaginary ($j\\omega$)')
ax_splane.set_xlim(-5.5, 0.5)
ax_splane.set_ylim(-11, 11)
ax_splane.axhline(0, color='black', lw=1)
ax_splane.axvline(0, color='black', lw=1)
ax_splane.grid(True)

# 3. 슬라이더 UI 구성
axcolor = 'lightgoldenrodyellow'
ax_alpha = plt.axes([0.15, 0.1, 0.65, 0.03], facecolor=axcolor)
ax_omega = plt.axes([0.15, 0.05, 0.65, 0.03], facecolor=axcolor)

s_alpha = Slider(ax_alpha, 'Alpha ($\\alpha$)', 0.0, 5.0, valinit=initial_alpha)
s_omega = Slider(ax_omega, 'Omega ($\\omega$)', 1.0, 10.0, valinit=initial_omega)

# 4. 슬라이더 업데이트 이벤트 처리 함수
def update(val):
    alpha = s_alpha.val
    omega = s_omega.val
    
    # 시간 영역 업데이트
    line_time.set_ydata(calc_signal(alpha, omega, t))
    
    # 극점 업데이트
    new_poles = calc_poles(alpha, omega)
    scatter_poles.set_offsets(np.c_[[p.real for p in new_poles], [p.imag for p in new_poles]])
    
    fig.canvas.draw_idle()

# 슬라이더에 이벤트 함수 연결
s_alpha.on_changed(update)
s_omega.on_changed(update)

plt.show()