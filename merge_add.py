import os
import shutil
from tqdm import tqdm

# ==================== 配置参数 ====================
# 源数据路径 (包含 img 和 txt 子文件夹)
SOURCE_ROOT = r"D:\\狼牙-梯队任务（暑假 ）\\camera_ camera calibration\\blue_val\\VV"
SOURCE_IMG_DIR = os.path.join(SOURCE_ROOT, "img")
SOURCE_LABEL_DIR = os.path.join(SOURCE_ROOT, "txt")

# 目标数据路径 (train集)
DEST_ROOT = r"D:\\狼牙-梯队任务（暑假 ）\\camera_ camera calibration\\buff_hit\\imgs"
DEST_IMG_DIR = os.path.join(DEST_ROOT, "image", "train")
DEST_LABEL_DIR = os.path.join(DEST_ROOT, "label", "train")

# 支持的图片扩展名
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp']
# ================================================

def get_max_file_number(directory):
    """获取目录下最大的数字编号"""
    max_num = 0
    if not os.path.exists(directory):
        return 0
        
    for filename in os.listdir(directory):
        # 获取文件名（不含扩展名）
        name, _ = os.path.splitext(filename)
        # 尝试转换为数字
        if name.isdigit():
            num = int(name)
            if num > max_num:
                max_num = num
    return max_num

def main():
    print("=" * 60)
    print("开始合并数据集...")
    print(f"源目录: {SOURCE_ROOT}")
    print(f"目标目录: {DEST_IMG_DIR}")
    print("=" * 60)

    # 检查源目录是否存在
    if not os.path.exists(SOURCE_IMG_DIR) or not os.path.exists(SOURCE_LABEL_DIR):
        print(f"错误: 源目录下的 img 或 txt 文件夹不存在")
        print(f"检查: {SOURCE_IMG_DIR}")
        print(f"检查: {SOURCE_LABEL_DIR}")
        return

    # 检查目标目录是否需要创建
    if not os.path.exists(DEST_IMG_DIR):
        os.makedirs(DEST_IMG_DIR)
    if not os.path.exists(DEST_LABEL_DIR):
        os.makedirs(DEST_LABEL_DIR)

    # 获取目标目录当前最大编号
    # 同时检查image和label目录，取最大值以防万一
    max_img_num = get_max_file_number(DEST_IMG_DIR)
    max_label_num = get_max_file_number(DEST_LABEL_DIR)
    current_num = max(max_img_num, max_label_num)
    
    print(f"当前最大编号: {current_num}")
    print(f"新文件将从 {current_num + 1} 开始编号")

    # 获取源图片列表
    source_images = [f for f in os.listdir(SOURCE_IMG_DIR) 
                    if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS]
    
    if not source_images:
        print("源目录中没有找到图片文件")
        return

    print(f"找到 {len(source_images)} 张待合并图片")
    
    success_count = 0
    skip_count = 0 
    
    # 开始复制并重命名
    for img_file in tqdm(source_images, desc="合并中"):
        base_name = os.path.splitext(img_file)[0]
        ext = os.path.splitext(img_file)[1]
        
        # 查找对应的txt文件
        # 有可能是同名的 .txt
        label_file = base_name + ".txt"
        src_label_path = os.path.join(SOURCE_LABEL_DIR, label_file)
        
        if not os.path.exists(src_label_path):
            # 尝试查找不同扩展名的图片对应的txt (虽然通常是一样的base_name)
            # 这里简单起见只找同名txt
            # print(f"警告: 找不到对应的标签文件 {src_label_path}，跳过该图片")
            skip_count += 1
            continue
            
        # 生成新编号
        current_num += 1
        new_base_name = str(current_num)
        
        # 目标路径
        dst_img_path = os.path.join(DEST_IMG_DIR, new_base_name + ext)
        dst_label_path = os.path.join(DEST_LABEL_DIR, new_base_name + ".txt")
        
        # 复制文件
        src_img_path = os.path.join(SOURCE_IMG_DIR, img_file)
        
        try:
            shutil.copy2(src_img_path, dst_img_path)
            shutil.copy2(src_label_path, dst_label_path)
            success_count += 1
        except Exception as e:
            print(f"复制失败 {img_file}: {e}")
            skip_count += 1
            current_num -= 1 # 回退编号

    print("\n" + "=" * 60)
    print("✓ 合并完成！")
    print(f"成功合并: {success_count} 对文件")
    print(f"跳过(无标签): {skip_count} 张图片")
    print(f"新的最大编号: {current_num}")
    print("=" * 60)

if __name__ == '__main__':
    main()