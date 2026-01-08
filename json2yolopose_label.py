"""
步骤2: 将labelme的json标注转换为YOLO pose格式的txt标注
格式: class_id center_x center_y width height kp1_x kp1_y v1 ... kp6_x kp6_y v6
其中：
- 矩形框(rectangle, label='buff')转换为边界框
- 多边形(polygon, label='poly')的6个顶点转换为6个关键点
"""
import os
import json
import shutil
from tqdm import tqdm


# ==================== 配置参数（修改这里）====================
DATASET_ROOT = "./buff_hit"              # 数据集根目录
INPUT_DIR = "imgs"                       # 输入输出目录名（包含image, label, jsons子目录）
BBOX_CLASS = {'buff': 0}                 # 目标框类别映射（buff对应类别0）
NUM_KEYPOINTS = 6                        # 关键点数量（多边形顶点数）
POLYGON_LABELS = ['poly', 'ploy']        # 多边形标签名称（支持poly和ploy）
# ===========================================================


def create_dir_if_not_exists(path):
    """创建目录（如果不存在）"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"创建目录: {path}")

def find_polygon_for_bbox(bbox, polygons, img_width, img_height):
    """
    为给定的边界框找到对应的多边形（关键点）
    通过计算多边形中心点是否在边界框内来匹配
    """
    bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max = bbox
    bbox_center_x = (bbox_x_min + bbox_x_max) / 2
    bbox_center_y = (bbox_y_min + bbox_y_max) / 2
    
    best_polygon = None
    min_distance = float('inf')
    
    for poly in polygons:
        # 计算多边形的中心点
        points = poly['points']
        if len(points) != NUM_KEYPOINTS:
            continue
            
        poly_center_x = sum(p[0] for p in points) / len(points)
        poly_center_y = sum(p[1] for p in points) / len(points)
        
        # 检查多边形中心是否在边界框内
        if (bbox_x_min <= poly_center_x <= bbox_x_max and 
            bbox_y_min <= poly_center_y <= bbox_y_max):
            # 计算距离，选择最近的
            distance = abs(poly_center_x - bbox_center_x) + abs(poly_center_y - bbox_center_y)
            if distance < min_distance:
                min_distance = distance
                best_polygon = poly
    
    return best_polygon

def process_single_json(labelme_path, save_folder):
    """
    处理单个labelme json文件，转换为YOLO格式
    """
    try:
        with open(labelme_path, 'r', encoding='utf-8') as f:
            labelme = json.load(f)
    except Exception as e:
        print(f"读取json文件失败: {labelme_path}, 错误: {e}")
        return False

    img_width = labelme['imageWidth']   # 图像宽度
    img_height = labelme['imageHeight'] # 图像高度

    # 生成 YOLO 格式的 txt 文件名
    json_filename = os.path.basename(labelme_path)
    txt_filename = json_filename.replace('.json', '.txt')
    yolo_txt_path = os.path.join(save_folder, txt_filename)

    # 分离矩形框和多边形
    rectangles = []
    polygons = []
    
    for shape in labelme['shapes']:
        if shape['shape_type'] == 'rectangle' and shape['label'] in BBOX_CLASS:
            rectangles.append(shape)
        elif shape['shape_type'] == 'polygon' and shape['label'] in POLYGON_LABELS:
            polygons.append(shape)
    
    if len(rectangles) == 0:
        print(f"警告: {json_filename} 中没有找到矩形框标注")
        # 创建空文件
        with open(yolo_txt_path, 'w', encoding='utf-8') as f:
            pass
        return True

    with open(yolo_txt_path, 'w', encoding='utf-8') as f:
        for rect in rectangles:  # 遍历每个矩形框
            yolo_str = ''

            # 1. 处理边界框信息
            bbox_class_id = BBOX_CLASS[rect['label']]
            yolo_str += '{} '.format(bbox_class_id)
            
            # 获取矩形框坐标
            bbox_x_min = min(rect['points'][0][0], rect['points'][1][0])
            bbox_x_max = max(rect['points'][0][0], rect['points'][1][0])
            bbox_y_min = min(rect['points'][0][1], rect['points'][1][1])
            bbox_y_max = max(rect['points'][0][1], rect['points'][1][1])
            
            # 计算中心点和宽高
            bbox_center_x = (bbox_x_min + bbox_x_max) / 2
            bbox_center_y = (bbox_y_min + bbox_y_max) / 2
            bbox_width = bbox_x_max - bbox_x_min
            bbox_height = bbox_y_max - bbox_y_min
            
            # 归一化坐标
            bbox_center_x_norm = bbox_center_x / img_width
            bbox_center_y_norm = bbox_center_y / img_height
            bbox_width_norm = bbox_width / img_width
            bbox_height_norm = bbox_height / img_height

            yolo_str += '{:.5f} {:.5f} {:.5f} {:.5f} '.format(
                bbox_center_x_norm, bbox_center_y_norm, 
                bbox_width_norm, bbox_height_norm
            )

            # 2. 找到对应的多边形（关键点）
            bbox_coords = (bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max)
            matched_polygon = find_polygon_for_bbox(bbox_coords, polygons, img_width, img_height)
            
            if matched_polygon and len(matched_polygon['points']) == NUM_KEYPOINTS:
                # 使用多边形的6个顶点作为关键点
                for point in matched_polygon['points']:
                    kp_x_norm = point[0] / img_width
                    kp_y_norm = point[1] / img_height
                    # 可见性设为2（可见且未遮挡）
                    yolo_str += '{:.5f} {:.5f} {} '.format(kp_x_norm, kp_y_norm, 2)
            else:
                # 如果没有匹配的多边形，填充0（不可见）
                print(f"警告: {json_filename} 中的框 {rect['label']} 没有匹配的多边形")
                for _ in range(NUM_KEYPOINTS):
                    yolo_str += '0 0 0 '
            
            # 写入txt文件
            f.write(yolo_str.strip() + '\n')
    
    return True

def process_dataset(split='train'):
    """
    处理训练集或验证集
    
    参数:
        split: 'train' 或 'val'
    """
    print(f"\n{'='*60}")
    print(f"处理 {split.upper()} 数据集")
    print(f"{'='*60}")
    
    # 输入输出路径
    # 读取路径: imgs/jsons/{split}
    # 输出路径: imgs/label/{split}
    input_root = os.path.join(DATASET_ROOT, INPUT_DIR)
    json_folder = os.path.join(input_root, 'jsons', split)
    save_folder = os.path.join(input_root, 'label', split)
    
    if not os.path.exists(json_folder):
        print(f"错误: 找不到文件夹 {json_folder}")
        return
    
    # 创建输出目录
    create_dir_if_not_exists(save_folder)
    
    # 获取所有json文件
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
    
    if len(json_files) == 0:
        print(f"警告: {json_folder} 中没有找到json文件")
        return
    
    print(f"找到 {len(json_files)} 个json文件")
    
    # 逐个处理
    success_count = 0
    error_count = 0
    
    for json_file in tqdm(json_files, desc=f"转换{split}"):
        json_path = os.path.join(json_folder, json_file)
        if process_single_json(json_path, save_folder):
            success_count += 1
        else:
            error_count += 1
            print(f"处理失败: {json_file}")
    
    print(f"\n✓ {split.upper()} 数据集转换完成!")
    print(f"  成功: {success_count} 个文件")
    print(f"  失败: {error_count} 个文件")
    print(f"  输出目录: {save_folder}")

def main():
    print("=" * 60)
    print("步骤2: JSON标注转YOLO Pose格式")
    print("=" * 60)
    print(f"\n数据集根目录: {DATASET_ROOT}")
    print(f"输入目录: {INPUT_DIR}")
    print(f"目标框类别: {BBOX_CLASS}")
    
    # 创建labels根目录
    label_root = os.path.join(DATASET_ROOT, INPUT_DIR, 'label')
    create_dir_if_not_exists(label_root)
    
    # 处理训练集
    process_dataset('train')
    
    # 处理验证集
    process_dataset('val')
    
    print("\n" + "=" * 60)
    print("✓ 所有数据集转换完成！")
    print("=" * 60)
    
    # 显示目录结构
    try:
        data_dir = os.path.join(DATASET_ROOT, INPUT_DIR)
        print("\n生成的目录结构:")
        print(f"{data_dir}/")
        
        for subdir in ['image', 'label', 'jsons']:
            sub_path = os.path.join(data_dir, subdir)
            if os.path.exists(sub_path):
                print(f"├── {subdir}/")
                for split in ['train', 'val']:
                    split_path = os.path.join(sub_path, split)
                    if os.path.exists(split_path):
                        count = len(os.listdir(split_path))
                        print(f"│   ├── {split}/  ({count} files)")
                    else:
                        print(f"│   ├── {split}/  (missing)")
            else:
                print(f"├── {subdir}/  (missing)")
                
    except Exception as e:
        print(f"\n无法显示目录结构: {e}")

if __name__ == '__main__':
    main()
