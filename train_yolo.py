from ultralytics import YOLO

# 加载预训练模型
model = YOLO('yolov11n-pose.pt')

# 开始训练
results = model.train(
    data='train_buff.yaml',
    epochs=50,
    batch=16,
    device=0,
    project='buff_training',
    name='n_pretrain',
    pretrained=True
)
# 训练完成后，结果将保存在 'buff_training/n_pretrain' 目录下