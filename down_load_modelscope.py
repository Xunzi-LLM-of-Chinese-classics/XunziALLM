from modelscope.hub.snapshot_download import snapshot_download

model_dir = snapshot_download('Xunzillm4cc/Xunzi-Qwen-Chat', 
                              cache_dir='./Xunzi-Qwen-Chat', 
                              revision='master')