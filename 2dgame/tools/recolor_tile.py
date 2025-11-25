import os
import pygame
import colorsys

def extract_main_color(surface, prefer_deep=True):
    """从pygame surface提取主要颜色"""
    width, height = surface.get_map_size()
    pixels = []
    
    for y in range(height):
        for x in range(width):
            color = surface.get_at((x, y))
            r, g, b, a = color
            
            # 过滤：排除透明和太暗/太亮的像素
            if a > 128 and r > 30 and g > 30 and b > 30 and (r + g + b) < 700:
                pixels.append((r, g, b))
    
    if len(pixels) == 0:
        # 如果没有有效像素，使用所有不透明像素
        for y in range(height):
            for x in range(width):
                color = surface.get_at((x, y))
                if color[3] > 0:
                    pixels.append((color[0], color[1], color[2]))
    
    if len(pixels) == 0:
        return (128, 128, 128)
    
    if prefer_deep:
        # 提取更深的颜色：选择饱和度较高且不太亮的颜色
        # 计算每个像素的饱和度，选择饱和度较高的
        best_pixel = pixels[0]
        best_score = 0
        
        for r, g, b in pixels:
            h, s, v = rgb_to_hsv(r, g, b)
            # 评分：饱和度越高越好，亮度中等（不要太亮也不要太暗）
            score = s * (1 - abs(v - 0.6))  # 偏好饱和度高的中等亮度
            
            if score > best_score:
                best_score = score
                best_pixel = (r, g, b)
        
        return best_pixel
    else:
        # 计算平均颜色
        avg_r = sum(p[0] for p in pixels) // len(pixels)
        avg_g = sum(p[1] for p in pixels) // len(pixels)
        avg_b = sum(p[2] for p in pixels) // len(pixels)
        return (avg_r, avg_g, avg_b)

def rgb_to_hsv(r, g, b):
    """RGB转HSV"""
    return colorsys.rgb_to_hsv(r/255, g/255, b/255)

def hsv_to_rgb(h, s, v):
    """HSV转RGB"""
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r*255), int(g*255), int(b*255))

def recolor_image(base_path, reference_path, output_path):
    """
    将基底图片的颜色替换为参考图片的颜色
    保持原图的形状和明暗变化，只改变色调
    """
    # 初始化pygame（用于图片处理）
    pygame.init()
    # 设置一个虚拟显示模式（用于加载图片）
    pygame.display.set_mode((1, 1))
    
    # 加载图片
    base_img = pygame.image.load(base_path).convert_alpha()
    ref_img = pygame.image.load(reference_path).convert_alpha()
    
    # 提取参考图片的主要颜色（偏好更深的颜色）
    ref_color = extract_main_color(ref_img, prefer_deep=True)
    ref_name = os.path.basename(reference_path).replace(".png", "")
    print(f"参考颜色（{ref_name}）: RGB{ref_color}")
    
    # 提取基底图片的主要颜色
    base_color = extract_main_color(base_img, prefer_deep=False)
    base_name = os.path.basename(base_path).replace(".png", "")
    print(f"基底颜色（{base_name}）: RGB{base_color}")
    
    # 转换为HSV
    base_hsv = rgb_to_hsv(base_color[0], base_color[1], base_color[2])
    ref_hsv = rgb_to_hsv(ref_color[0], ref_color[1], ref_color[2])
    
    # 计算色相偏移
    hue_shift = ref_hsv[0] - base_hsv[0]
    
    # 创建输出surface
    width, height = base_img.get_size()
    output_img = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # 遍历每个像素
    for y in range(height):
        for x in range(width):
            pixel = base_img.get_at((x, y))
            r, g, b, a = pixel
            
            # 跳过透明像素
            if a == 0:
                output_img.set_at((x, y), (r, g, b, 0))
                continue
            
            # 转换为HSV
            pixel_hsv = rgb_to_hsv(r, g, b)
            
            # 计算与基底颜色的相似度（色相）
            hue_diff = abs(pixel_hsv[0] - base_hsv[0])
            if hue_diff > 0.5:
                hue_diff = 1 - hue_diff  # 处理色相环的循环
            
            # 如果像素颜色接近基底颜色，则应用色相偏移
            if hue_diff < 0.25:  # 色相相似度阈值（可调整，值越大替换范围越大）
                # 应用色相偏移，保持饱和度和亮度（完全匹配参考颜色）
                new_hue = (pixel_hsv[0] + hue_shift) % 1.0
                new_s = pixel_hsv[1]  # 保持原图的饱和度
                new_v = pixel_hsv[2]  # 保持原图的亮度
                
                # 转换回RGB
                new_r, new_g, new_b = hsv_to_rgb(new_hue, new_s, new_v)
                output_img.set_at((x, y), (new_r, new_g, new_b, a))
            else:
                # 保持原色（阴影、高光等细节）
                output_img.set_at((x, y), pixel)
    
    # 保存结果
    pygame.image.save(output_img, output_path)
    print(f"已保存新图片: {output_path}")

def main():
    # 路径配置
    base_dir = os.path.join("..", "assets", "sprites", "background", "map_base")
    base_path = os.path.join(base_dir, "house_yellow.png")
    reference_path = os.path.join(base_dir, "house_blue.png")
    output_path = os.path.join(base_dir, "house_blue_new.png")
    
    if not os.path.exists(base_path):
        print(f"错误：找不到基底文件 {base_path}")
        return
    
    if not os.path.exists(reference_path):
        print(f"错误：找不到参考文件 {reference_path}")
        return
    
    print("开始处理图片...")
    print(f"基底: {base_path}")
    print(f"参考: {reference_path}")
    print(f"输出: {output_path}\n")
    
    recolor_image(base_path, reference_path, output_path)
    print("\n完成！")

if __name__ == "__main__":
    main()

