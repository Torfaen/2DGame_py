import os
from typing import List, Optional

path=os.path.join("..", "assets", "sprites", "raw")
#重命名文件夹内所有文件，n个为一组

def batch_rename(
    directory: str,
    group_size: int,
    prefix: str,
    labels: Optional[List[str]] = None,
    ext_keep: bool = True,
):
    # 读取并按文件名排序，过滤出常见图片格式
    valid_exts={".png",".jpg",".jpeg",".webp",".bmp"}
    files=[f for f in os.listdir(directory) if os.path.splitext(f)[1].lower() in valid_exts]
    files.sort()
    if not files:
        print("目录内没有待处理图片")
        return

    total=len(files)
    if group_size<=0:
        raise ValueError("group_size 必须 > 0")

    # 计算分组
    groups=[files[i:i+group_size] for i in range(0,total,group_size)]

    # 组标签
    if labels:
        if len(labels)!=len(groups):
            raise ValueError(f"labels 数量({len(labels)})必须等于分组数({len(groups)})")
        group_names=labels
    else:
        # 自动使用四向标签
        if len(groups)==4:
            group_names=["down","left","right","up"]
        else:
            group_names=[f"g{i}" for i in range(len(groups))]

    # 为避免覆盖，先生成新名映射
    renames=[]
    for gi,group in enumerate(groups):
        gname=group_names[gi]
        for fi,old in enumerate(group):
            old_path=os.path.join(directory,old)
            ext=os.path.splitext(old)[1] if ext_keep else ".png"
            if prefix:
                new=f"{prefix}_{gname}_{fi}{ext}"
            else:
                new=f"{gname}_{fi}{ext}"
            new_path=os.path.join(directory,new)
            renames.append((old_path,new_path))

    # 冲突处理：若新名已存在，先加中间扩展名 .tmp 防止覆盖
    tmp_paths=[]
    for old_path,new_path in renames:
        tmp_path=new_path+".tmp"
        os.replace(old_path,tmp_path)
        tmp_paths.append((tmp_path,new_path))

    for tmp_path,new_path in tmp_paths:
        os.replace(tmp_path,new_path)

    print(f"已重命名 {total} 个文件 → {len(groups)} 组，每组 {group_size} 个")


if __name__=="__main__":
    # 直接在这里设置参数并运行，无需命令行：
    directory = path  # 目标目录
    group_size = 3    # 每组文件数
    prefix = ""       # 空字符串表示不加前缀
    labels = ["down","left","right","up"]  # 或者 None 使用自动/默认标签
    force_png = False # True 则统一输出为 .png

    batch_rename(
        directory=directory,
        group_size=group_size,
        prefix=prefix,
        labels=labels,
        ext_keep=not force_png,
    )
