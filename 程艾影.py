import pyaudio
import numpy as np
import wave
import matplotlib.pyplot as plt

# 设置音频文件路径
audio_path = "你的音频文件路径.wav"

# 打开音频文件
wf = wave.open(audio_path, 'rb')

# 获取音频文件的基本信息
sample_rate = wf.getframerate()
num_channels = wf.getnchannels()
frame_size = wf.getsampwidth()
num_frames = wf.getnframes()

# PyAudio 设置
FORMAT = pyaudio.paInt16  # 音频格式：16位整型
CHANNELS = num_channels   # 音频通道数
RATE = sample_rate        # 采样率
CHUNK = 1024              # 每次读取的帧数

# 创建 PyAudio 实例
p = pyaudio.PyAudio()

# 打开流，用于播放音频
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)

# 用于绘制频谱的图形
plt.ion()
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(0, CHUNK)
line, = ax.plot(x, np.random.rand(CHUNK))

def update_plot(data):
    # 计算频谱（使用FFT计算快速傅里叶变换）
    spectrum = np.abs(np.fft.fft(data))
    spectrum = spectrum[:CHUNK//2]  # 只取一半，频谱是对称的

    # 更新图形
    line.set_ydata(spectrum)
    ax.draw_artist(ax.patch)
    ax.draw_artist(line)
    fig.canvas.flush_events()

try:
    while True:
        # 从音频文件读取数据
        data = wf.readframes(CHUNK)
        
        if len(data) == 0:  # 文件读取完毕
            break
        
        # 将音频数据转为 numpy 数组
        audio_data = np.frombuffer(data, dtype=np.int16)

        # 播放音频数据
        stream.write(data)

        # 更新频谱图
        update_plot(audio_data)

except KeyboardInterrupt:
    print("停止播放")

# 关闭流、PyAudio和文件
stream.stop_stream()
stream.close()
p.terminate()
wf.close()
