import cv2
import gxipy as gx
from PIL import Image
import datetime
def main():
    Width_set = 1280  # 设置分辨率宽   360
    Height_set = 1024  # 设置分辨率高  480
    framerate_set = 5# 设置帧率     #r=400r
    framerate_get=0
    num = 4000  # 采集帧率次数（为调试用，可把后边的图像采集设置成while循环，进行无限制循环采集）

    # 创建设备
    device_manager = gx.DeviceManager()  # 创建设备对象

    dev_num, dev_info_list = device_manager.update_device_list()  # 枚举设备，即枚举所有可用的设备
    if dev_num is 0:
        print("Number of enumerated devices is 0")
        return
    else:
        # print("")
        # print("**********************************************************")
        print("创建设备成功，设备号为:%d" % dev_num)

    # 通过设备序列号打开一个设备
    cam = device_manager.open_device_by_sn(dev_info_list[0].get("sn"))

    # 如果是黑白相机
    if cam.PixelColorFilter.is_implemented() is False:  # is_implemented判断枚举型属性参数是否已实现
        print("该示例不支持黑白相机.")
        cam.close_device()
        return
    else:
        print("")
        print("**********************************************************")
        print("打开彩色摄像机成功，SN号为：%s" % dev_info_list[0].get("sn"))

    # 设置宽和高
    cam.Width.set(Width_set)
    cam.Height.set(Height_set)
    cam.ExposureTime.set(12000.0)
    cam.Gain.set(12)
    # 设置连续采集
    # cam.TriggerMode.set(gx.GxSwitchEntry.OFF) # 设置触发模式
    cam.AcquisitionFrameRateMode.set(gx.GxSwitchEntry.ON)

    # 设置帧率
    cam.AcquisitionFrameRate.set(framerate_set)
    # 启用自动白平衡
    cam.BalanceWhiteAuto.set(gx.GxAutoEntry.CONTINUOUS)
    print("")
    # print("**********************************************************")
    # print("用户设置的帧率为:%d fps" % framerate_set)
    framerate_get = cam.CurrentAcquisitionFrameRate.get()  # 获取当前采集的帧率
    print("当前采集的帧率为:%d fps" % framerate_get)
    # 开始数据采集
    # print("")
    # print("**********************************************************")
    # print("开始数据采集......")
    # print("")
    cam.stream_on()

    # 采集图像
    for i in range(num):
        raw_image = cam.data_stream[0].get_image()  # 打开第0通道数据流
        if raw_image is None:
            print("获取彩色原始图像失败.")
            continue

        rgb_image = raw_image.convert("RGB")  # 从彩色原始图像获取RGB图像
        if rgb_image is None:
            continue

        # rgb_image.image_improvement(color_correction_param, contrast_lut, gamma_lut)  # 实现图像增强

        numpy_image = rgb_image.get_numpy_array()  # 从RGB图像数据创建numpy数组
        if numpy_image is None:
            continue
        # 转换通道顺序
        numpy_image_bgr = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
        img = Image.fromarray(numpy_image_bgr, 'RGB')  # 展示获取的图像
        mtime = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')


        # 展示图像
        cv2.imshow("RGB Image", numpy_image_bgr)
        cv2.waitKey(1)  # 等待1ms
        #img.save(r"./images/2/" + str(i) + str("-") + mtime + ".jpg")  # 保存图片到本地

        print("Frame ID: %d   Height: %d   Width: %d   framerate_set:%dfps   framerate_get:%dfps"
              % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width(), framerate_set,
                 framerate_get))  # 打印采集的图像的高度、宽度、帧ID、用户设置的帧率、当前采集到的帧率
    cam.stream_off()
    print("系统提示您：设备已经关闭！")
    cam.close_device()


if __name__ == "__main__":
    main()

