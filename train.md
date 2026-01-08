## 直接命令行启动：
# yolo pose train data=Triangle_215.yaml model=yolov8n-pose.pt pretrained=True project=Triangle_215 name=n_pretrain epochs=50 batch=16 device=0

## yaml文件换成你自己的路径
## 这里v8换成v11，每一个都训一下，（m，n,l,x）。
## 如果不换cfg,训练结果应该在runs中

##