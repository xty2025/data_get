"""
步骤1: 划分训练集和验证集
将json标注文件和对应的图片按比例分配到新的目录结构中
"""
import os 
import shutil
import random
from tqdm import tqdm
import seedir
# ==================== 配置参数（修改这里）====================
DATA_ROOT = "./buff_hit"          # 数据集根目录
JSON_DIR = "D:\\狼牙-梯队任务（暑假 ）\\camera_ camera calibration\\dataset"          # 原始json和图片所在文件夹名（相对于DATA_ROOT）
OUTPUT_DIR = "imgs"               # 输出文件目录名（将创建在DATA_ROOT下）
                                  # 最终结构: DATA_ROOT/imgs/{image,label}/{train,val}
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp']  # 支持的图片格式
TEST_FRAC = 0.2                   # 验证集比例
RANDOM_SEED = 123                 # 随机种子，保证可复现
# ===========================================================

def create_dir_if_not_exists(path):
    """创建目录（如果不存在）"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"创建目录: {path}")

def find_image_file(json_folder, json_filename):
    """
    根据json文件名查找对应的图片文件
    """
    base_name = os.path.splitext(json_filename)[0]
    for ext in IMAGE_EXTENSIONS:
        img_file = base_name + ext
        img_path = os.path.join(json_folder, img_file)
        if os.path.exists(img_path):
            return img_file
    return None

def main():
    print("=" * 60)
    print("步骤1: 划分训练集和验证集（构建目录结构）")
    print("=" * 60)
    
    # 设置随机种子
    random.seed(RANDOM_SEED)
    
    # 获取json文件路径
    json_folder = os.path.join(DATA_ROOT, JSON_DIR)
    if not os.path.exists(json_folder):
        print(f"错误: 找不到源文件夹 {json_folder}")
        return
    
    # 获取所有json文件
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
    
    if len(json_files) == 0:
        print(f"错误: {json_folder} 中没有找到json文件")
        return
    
    print(f"\n找到 {len(json_files)} 个json标注文件")

    # 随机打乱
    random.shuffle(json_files)
    
    # 划分训练集和验证集
    val_number = int(len(json_files) * TEST_FRAC)
    train_files = json_files[val_number:]
    val_files = json_files[:val_number]
    
    print(f"训练集文件个数: {len(train_files)}")
    print(f"验证集文件个数: {len(val_files)}")
    
    # 构建输出目录结构
    # imgs/image/train, imgs/image/val
    # imgs/jsons/train, imgs/jsons/val (用于存放json，方便下一步生成label)
    output_root = os.path.join(DATA_ROOT, OUTPUT_DIR)
    
    train_img_dir = os.path.join(output_root, 'image', 'train')
    val_img_dir = os.path.join(output_root, 'image', 'val')
    train_json_dir = os.path.join(output_root, 'jsons', 'train')
    val_json_dir = os.path.join(output_root, 'jsons', 'val')
    
    # 创建目录
    for d in [train_img_dir, val_img_dir, train_json_dir, val_json_dir]:
        create_dir_if_not_exists(d)
    
    # 处理训练集
    print(f"\n复制训练集文件...")
    missing_images_train = []
    for json_file in tqdm(train_files, desc="训练集"):
        # 复制json文件
        src_json = os.path.join(json_folder, json_file)
        dst_json = os.path.join(train_json_dir, json_file)
        shutil.copy2(src_json, dst_json)
        
        # 查找并复制对应的图片
        img_file = find_image_file(json_folder, json_file)
        if img_file:
            src_img = os.path.join(json_folder, img_file)
            dst_img = os.path.join(train_img_dir, img_file)
            shutil.copy2(src_img, dst_img)
        else:
            missing_images_train.append(json_file)
    
    # 处理验证集
    print(f"复制验证集文件...")
    missing_images_val = []
    for json_file in tqdm(val_files, desc="验证集"):
        # 复制json文件
        src_json = os.path.join(json_folder, json_file)
        dst_json = os.path.join(val_json_dir, json_file)
        shutil.copy2(src_json, dst_json)
        
        # 查找并复制对应的图片
        img_file = find_image_file(json_folder, json_file)
        if img_file:
            src_img = os.path.join(json_folder, img_file)
            dst_img = os.path.join(val_img_dir, img_file)
            shutil.copy2(src_img, dst_img)
        else:
            missing_images_val.append(json_file)
    
    print("\n" + "=" * 60)
    print("✓ 数据集划分完成！")
    print(f"输出目录: {output_root}")
    print(f"训练集图片: {train_img_dir}")
    print(f"验证集图片: {val_img_dir}")
    
    if missing_images_train or missing_images_val:
        print("\n⚠ 警告: 以下json文件找不到对应的图片:")
        for f in missing_images_train:
            print(f"  [训练集] {f}")
        for f in missing_images_val:
            print(f"  [验证集] {f}")
    print("=" * 60)

if __name__ == '__main__':
    main()


