import os
import csv
import xml.etree.ElementTree as ET
import json
tile_set_path =os.path.join("..", "paopaotang", "小区_多图片集合.tsx")
nmap_barrier_path = os.path.join("..", "paopaotang", "csv", "小区_barrier.csv")
nmap_unbroken_path = os.path.join("..", "paopaotang","csv", "小区_unbroken.csv")
nmap_floor_path = os.path.join("..", "paopaotang","csv", "小区_floor.csv")

tree = ET.parse(tile_set_path)
root = tree.getroot()

#先建立ID-名字字典，用于转换tmj文件
#遍历tile信息
def create_tile_dict(root):
    tile_dict={}
    tile_dict[-1]="empty"
    for tile in root.findall('tile'):
        tile_id = int(tile.get('id'))
        tile_image_path = tile.find('image').get('source')
        # 提取贴图名字（不含扩展名）
        tile_image_name = os.path.splitext(os.path.basename(tile_image_path))[0]
        tile_dict[tile_id] = tile_image_name
    return tile_dict
    #{'0': 'empty', 21: 'block_orange', 39: 'block_red', 23: 'box_wooden', 
    # 24: 'box_wooden2', 25: 'floor_iron', 26: 'grass_green', 27: 'ground_00', 
    # 28: 'house_blue', 41: 'house_blue', 29: 'house_yellow', 30: 'ironbox_blue'}
#获取csv地图数据
def get_map_data(map_path):
    map_data=[]
    with open(map_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            map_data.append(row)
        return map_data

#合并障碍物地图
def merge_barrier_map(map_barrier_data, map_unbroken_data):
    map_barrier_data = get_map_data(nmap_barrier_path)
    map_unbroken_data = get_map_data(nmap_unbroken_path)
    #检查地图长度是否一致，不一致则返回
    if len(map_barrier_data) != len(map_unbroken_data) or len(map_barrier_data[0]) != len(map_unbroken_data[0]):
        print("barrier地图和unbroken地图尺寸不一致")
        print(f"barrier地图长度: {len(map_barrier_data)}")
        print(f"unbroken地图长度: {len(map_unbroken_data)}")
        print(f"barrier地图宽度: {len(map_barrier_data[0])}")
        print(f"unbroken地图宽度: {len(map_unbroken_data[0])}")
        return
    #通过检测，开始合并
    for i in range(len(map_barrier_data)):
        for j in range(len(map_barrier_data[i])):
            if map_unbroken_data[i][j] != "-1":
                map_barrier_data[i][j] = map_unbroken_data[i][j]
    return map_barrier_data


def create_collision_map(barrier_map_data,unbroken_map_data):
    #0:空地，1:可摧毁障碍物，2:不可摧毁障碍物
    collision_map_data=[]
    for i in range(len(barrier_map_data)):
        row = []
        for j in range(len(barrier_map_data[i])):
            #barriermap此时只有-1和其他情况，不为-1则说明有障碍，进一步判断障碍可否摧毁
            if barrier_map_data[i][j] != "-1" or unbroken_map_data[i][j] != "-1":
                #如果unbrokenmap此处为-1，则此处为可摧毁障碍物
                if unbroken_map_data[i][j] == "-1":
                    #可摧毁障碍物
                    row.append(1)
                else:
                    #不可摧毁障碍物
                    row.append(2)
            else:
                #空地
                row.append(0)
        collision_map_data.append(row)
    #外圈全部变为2
    for i in range(len(collision_map_data[0])):
        collision_map_data[0][i]=2
        collision_map_data[-1][i]=2
    for i in range(len(collision_map_data)):
        collision_map_data[i][0]=2
        collision_map_data[i][-1]=2

    return collision_map_data


#添加新的地图数据到json文件
def add_new_map(map_data, map_name,json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        #json_data 是一个字典，格式类似: {"map1": [...], "map2": [...]}
        json_data = json.load(f)
    json_data[map_name] = map_data
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)


#--------------------------------------------------------------------------------------------------
def main():
    tile_dict = create_tile_dict(root)
    print(tile_dict)
#---------此处配置新地图名字和当前地图json文件路径-----------------------------------------------------------------------------------------
    nmap_name="map1"
     #设置json文件路径
    barrier_json_path = os.path.join("..", "map", "barrier_map.json")
    floor_json_path = os.path.join("..", "map", "floor_map.json")
    collision_json_path = os.path.join("..", "map", "collision_map.json")
#--------------------------------------------------------------------------------------------------
    nmap_barrier_data = get_map_data(nmap_barrier_path)
    nmap_unbroken_data = get_map_data(nmap_unbroken_path)
    nmap_floor_data = get_map_data(nmap_floor_path)

    #创建碰撞地图
    nmap_collision_data = create_collision_map(nmap_barrier_data, nmap_unbroken_data)


    #合并障碍物地图
    nmap_merged_data = merge_barrier_map(nmap_barrier_data, nmap_unbroken_data)
    #翻译障碍物地图
    for i in range(len(nmap_merged_data)):
        for j in range(len(nmap_merged_data[i])):
            nmap_merged_data[i][j] = tile_dict[int(nmap_merged_data[i][j])]
    #翻译地板地图
    for i in range(len(nmap_floor_data)):
        for j in range(len(nmap_floor_data[i])):
            nmap_floor_data[i][j] = tile_dict[int(nmap_floor_data[i][j])]

    #添加新的地图数据到json文件 
    add_new_map(nmap_merged_data, nmap_name, barrier_json_path)
    add_new_map(nmap_floor_data, nmap_name, floor_json_path)
    add_new_map(nmap_collision_data, nmap_name, collision_json_path)

if __name__ == "__main__":
    main()
