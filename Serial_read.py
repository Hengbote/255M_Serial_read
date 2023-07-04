import serial
import re
from datetime import datetime

def read_serial_data(serial_port, baud_rate=115200, timeout=0.2):
    # 配置串口
    ser = serial.Serial(
        port=serial_port,               # 串口名称
        baudrate=baud_rate,             # 串口通信速度
        bytesize=serial.EIGHTBITS,      # 数据位数，也是默认值
        parity=serial.PARITY_NONE,      # 校验位
        stopbits=serial.STOPBITS_ONE,   # 停止位
        timeout=timeout                 # 读取操作的超时时间（单位：秒）
    )

    # 初始化状态变量
    expected_num = None
    total_packets = 0
    lost_packets = 0
    lost_packet_streak = False  # 标记当前是否在丢包状态中
    lost_packet_times = 0       # 丢包次数

    while True:
        # 读取一行数据
        data = ser.readline().decode('utf-8').strip()
        #data = ser.readline().hex()

        # 如果数据为空，则跳过这次循环
        if not data:
            continue

        # 检查数据格式
        matches = re.findall(r'(\D+\d+)', data)
        for match in matches:
            total_packets += 1

            prefix, num = re.match(r'(\D+)(\d+)', match).groups()  # 提取前缀和数字
            num = int(num)

            # 检查数字是否是预期的数字
            if expected_num is None:
                expected_num = (num % 20) + 1
            elif num != expected_num:
                # 如果数字不是预期的数字，我们认为丢失了一些数据包
                lost_packets += (num - expected_num) % 20
                expected_num = (num % 20) + 1

                # 如果不在丢包状态中，则丢包次数加一，并开始丢包状态
                if not lost_packet_streak:  
                    lost_packet_streak = True
                    lost_packet_times += 1
            else:
                expected_num = (expected_num % 20) + 1
                lost_packet_streak = False
                
            # 如果总包数为0，则丢失率为0；否则，进行正常的丢失率计算
            loss_rate = 0 if total_packets == 0 else (lost_packets / total_packets * 100)

            # 获取当前时间并格式化
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")   

            print(f'{current_time}-->{prefix}{num}\t(总包数: {total_packets}, 丢失包数: {lost_packets}, 丢失率: {loss_rate}%, 丢包次数: {lost_packet_times})')

# 使用默认的串口（如：'COM1'，'COM2'，'/dev/ttyACM0'，'/dev/ttyUSB0'等）
# 你需要根据你的设备来更改
serial_port = 'COM8'  

# 开始读取串口数据
read_serial_data(serial_port)
