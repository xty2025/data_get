import os
import cv2
import gxipy as gx
from gxipy.Exception import InvalidAccess
from PIL import Image
import datetime

# 用户可修改的参数
WIDTH_SET = 1280
HEIGHT_SET = 1024
FRAMERATE_SET = 5
NUM_FRAMES = 4000
EXPOSURE_TIME=4000
GAIN_VALUE = 8
SAVE_IMAGES = True
SAVE_DIR = r"./images/buff_red"
#D:\狼牙-梯队任务（暑假 ）\camera_ camera calibration\gxipy

def main():
    Width_set = WIDTH_SET  # 设置分辨率宽   360
    Height_set = HEIGHT_SET  # 设置分辨率高  480
    framerate_set = FRAMERATE_SET  # 设置帧率      #r=400r
    framerate_get = 0
    num = NUM_FRAMES  # 采集帧率次数（为调试用，可把后边的图像采集设置成while循环，进行无限制循环采集）

    # 创建设备
    device_manager = gx.DeviceManager()  # 创建设备对象

    dev_num, dev_info_list = device_manager.update_device_list()  # 枚举设备，即枚举所有可用的设备
    if dev_num == 0:
        print("Number of enumerated devices is 0")
        return
    else:
        # print("")
        # print("**********************************************************")
        print("创建设备成功，设备号为:%d" % dev_num)

    # 通过设备序列号打开一个设备，若失败（设备已被打开），尝试以只读方式回退
    try:
        cam = device_manager.open_device_by_sn(dev_info_list[0].get("sn"))
    except InvalidAccess as e:
        print("设备可能已被其他进程或句柄打开，尝试以只读方式打开。错误：%s" % e)
        try:
            cam = device_manager.open_device_by_sn(dev_info_list[0].get("sn"), access_mode=gx.GxAccessMode.READONLY)
            print("以只读模式打开设备成功。")
        except Exception as e2:
            print("以只读方式打开设备失败：%s" % e2)
            return

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

    # 尝试设置曝光（若不可写则回退到自动曝光或调整增益）
    try:
        if hasattr(cam, 'ExposureTime') and cam.ExposureTime.is_writable():
            try:
                cam.ExposureTime.set(EXPOSURE_TIME)
                print(f"设置手动曝光: {EXPOSURE_TIME}")
            except Exception as e:
                print(f"设置手动曝光失败: {e}")
        else:
            # 如果支持硬件自动曝光，启用之
            if hasattr(cam, 'ExposureAuto') and cam.ExposureAuto.is_implemented() and cam.ExposureAuto.is_writable():
                try:
                    cam.ExposureAuto.set(gx.GxAutoEntry.CONTINUOUS)
                    print("相机不允许写入曝光时间，已启用硬件自动曝光（CONTINUOUS）。")
                except Exception as e:
                    print(f"启用自动曝光失败: {e}")
            else:
                print("相机不允许写入曝光时间，且不支持自动曝光。将尝试设置增益作为退路。")
    except Exception as _:
        print("检查曝光控制属性时发生异常，跳过曝光设置。")

    # 尝试设置增益
    try:
        if hasattr(cam, 'Gain') and cam.Gain.is_writable():
            try:
                cam.Gain.set(GAIN_VALUE)
                print(f"设置增益: {GAIN_VALUE}")
            except Exception as e:
                print(f"设置增益失败: {e}")
        else:
            print("相机不允许写入增益值。")
    except Exception:
        print("检查增益属性时发生异常，跳过增益设置。")
    # 设置连续采集
    # cam.TriggerMode.set(gx.GxSwitchEntry.OFF) # 设置触发模式
    cam.AcquisitionFrameRateMode.set(gx.GxSwitchEntry.ON)

    # 设置帧率
    cam.AcquisitionFrameRate.set(framerate_set)
    # 启用自动白平衡
    try:
        if hasattr(cam, 'BalanceWhiteAuto') and cam.BalanceWhiteAuto.is_writable():
            cam.BalanceWhiteAuto.set(gx.GxAutoEntry.CONTINUOUS)
    except Exception:
        pass
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

    # 创建保存目录并找到已有的最大序号
    if SAVE_IMAGES:
        os.makedirs(SAVE_DIR, exist_ok=True)
        # 扫描目录中已有的图片，找到最大序号
        existing_files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.jpg') and f[:-4].isdigit()]
        if existing_files:
            max_num = max([int(f[:-4]) for f in existing_files])
            save_counter = max_num + 1
            print(f"检测到已有图片，从序号 {save_counter} 开始保存")
        else:
            save_counter = 1
    else:
        save_counter = 1

    # 采集图像
    for i in range(num):
        try:
            raw_image = cam.data_stream[0].get_image()  # 打开第0通道数据流
        except Exception as e:
            print(f"获取图像时发生异常: {e}")
            continue
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
        key = cv2.waitKey(1)  # 等待1ms
        # 按 q 键可以退出
        if key & 0xFF == ord('q'):
            print("检测到退出按键，结束采集。")
            break

        # 保存图片（按序号命名：1.jpg,2.jpg...）
        if SAVE_IMAGES:
            try:
                filename = os.path.join(SAVE_DIR, f"{save_counter}.jpg")
                # numpy_image_bgr 已经是 BGR 格式，直接使用 cv2.imwrite 保存
                cv2.imwrite(filename, numpy_image_bgr)
                print(f"已保存: {filename}")
                save_counter += 1
            except Exception as e:
                print(f"保存图片失败: {e}")

        print("Frame ID: %d   Height: %d   Width: %d   framerate_set:%dfps   framerate_get:%dfps"
              % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width(), framerate_set,
                 framerate_get))  # 打印采集的图像的高度、宽度、帧ID、用户设置的帧率、当前采集到的帧率
    cam.stream_off()
    print("系统提示您：设备已经关闭！")
    cam.close_device()


if __name__ == "__main__":
    main()

