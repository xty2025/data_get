import cv2
import gxipy as gx
from PIL import Image
import datetime
import numpy as np

def main():
    Width_set = 1280  # 设置分辨率宽
    Height_set = 1024  # 设置分辨率高
    framerate_set = 5  # 设置帧率
    num = 4000  # 采集帧率次数（为调试用，可把后边的图像采集设置成 while 循环，进行无限制循环采集）

    # 创建设备
    device_manager = gx.DeviceManager()  # 创建设备对象

    dev_num, dev_info_list = device_manager.update_device_list()  # 枚举设备，即枚举所有可用的设备
    if dev_num is 0:
        print("Number of enumerated devices is 0")
        return
    else:
        print("创建设备成功，设备号为:%d" % dev_num)

    # 通过设备序列号打开一个设备
    cam = device_manager.open_device_by_sn(dev_info_list[0].get("sn"))

    # 如果是黑白相机
    if cam.PixelColorFilter.is_implemented() is False:  # is_implemented 判断枚举型属性参数是否已实现
        print("该示例不支持黑白相机.")
        cam.close_device()
        return
    else:
        print("打开彩色摄像机成功，SN 号为：%s" % dev_info_list[0].get("sn"))

    # 设置宽和高
    cam.Width.set(Width_set)
    cam.Height.set(Height_set)

    # 调整曝光时间和增益以优化图像
    cam.ExposureTime.set(5000.0)
    cam.Gain.set(10)

    # 设置连续采集
    # cam.TriggerMode.set(gx.GxSwitchEntry.OFF) # 设置触发模式
    cam.AcquisitionFrameRateMode.set(gx.GxSwitchEntry.ON)

    # 设置帧率
    cam.AcquisitionFrameRate.set(framerate_set)
    # 启用自动白平衡
    cam.BalanceWhiteAuto.set(gx.GxAutoEntry.CONTINUOUS)

    framerate_get = cam.CurrentAcquisitionFrameRate.get()  # 获取当前采集的帧率
    print("当前采集的帧率为:%d fps" % framerate_get)

    # 开始数据采集
    cam.stream_on()

    # 采集图像
    for i in range(num):
        raw_image = cam.data_stream[0].get_image()  # 打开第 0 通道数据流
        if raw_image is None:
            print("获取彩色原始图像失败.")
            continue

        rgb_image = raw_image.convert("RGB")  # 从彩色原始图像获取 RGB 图像
        if rgb_image is None:
            continue

        numpy_image = rgb_image.get_numpy_array()  # 从 RGB 图像数据创建 numpy 数组
        if numpy_image is None:
            continue

        # 转换通道顺序
        numpy_image_bgr = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

        # 转换到 HSV 颜色空间
        hsv = cv2.cvtColor(numpy_image_bgr, cv2.COLOR_BGR2HSV)

        # 定义红色在 HSV 空间中的范围
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])

        # 创建红色掩码
        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)

        # 应用掩码到原始图像
        result = cv2.bitwise_and(numpy_image_bgr, numpy_image_bgr, mask=mask_red)

        img = Image.fromarray(result, 'RGB')  # 展示获取的图像
        mtime = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')

        # 展示图像
        cv2.imshow("Red Filtered Image", result)
        cv2.waitKey(1)  # 等待 1ms
        img.save(r"./images/1/" + str(i) + str("-") + mtime + ".jpg")  # 保存图片到本地

        print("Frame ID: %d   Height: %d   Width: %d   framerate_set:%dfps   framerate_get:%dfps"
              % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width(), framerate_set,
                 framerate_get))  # 打印采集的图像的高度、宽度、帧 ID、用户设置的帧率、当前采集到的帧率

    cam.stream_off()
    print("系统提示您：设备已经关闭！")
    cam.close_device()


if __name__ == "__main__":
    main()