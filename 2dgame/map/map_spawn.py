import json

# 读取原始文件
with open('floor_map.json', 'r') as f:
    data = json.load(f)

# 创建50x50的地图
new_map1 = []
for i in range(32):
    row = ["grass"] * 32
    new_map1.append(row)

# 更新map1数据
data["map1"] = new_map1

# 写入文件
with open('floor_map.json', 'w') as f:
    json.dump(data, f, indent=2)