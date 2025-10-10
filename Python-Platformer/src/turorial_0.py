import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join

pygame.init()
pygame.display.set_caption("Platformer")
#BG_COLOR=(255,255,255)
WIDTH, HEIGHT = 1000, 800
FPS=60
PLAYER_VEL=5
window= pygame.display.set_mode((WIDTH,HEIGHT))
# 再导入 Player 类
from player import Player
from object import Block
#获取背景 图片
def get_background(name):
    #image= pygame.image.load("assets/Background/gray.png")
    #本部分上在mac上开发的，使用join来兼容其他使用windows的同学
    image = pygame.image.load(join( "assets", "Background", name))
    #_ 忽略不需要的 x 和 y 坐标值
    _,_,width,heigh = image.get_rect()
    tiles=[]
    for i in range(WIDTH//width+1):
        for j in range(HEIGHT//heigh+1):
            #需要绘制tile的坐标为i行j列
            pos=(i*width,j*heigh)
            tiles.append(pos)
    return tiles,image
#draw函数，处理一帧画面
def draw(windows, background, bg_image, player,objects):
    for tile in background:
        #仅是作为背景，所以可以直接用blit方法
        windows.blit(bg_image, tile)
    for obj in objects:
        #作为碰撞，用封装好的方法绘制，包含图片与碰撞
        obj.draw(windows)
    player.draw(windows)
    pygame.display.update()
def handle_vertical_collision(player, objects, dy):
    collided_objects=[]
    for obj in objects:
        #检测碰撞
        if pygame.sprite.collide_mask(player, obj):
        #向上跳，即y向速度大于0，把玩家放到地板上面，视为跳上台阶
            if dy>0:
                player.rect.bottom=obj.rect.top
                player.landed()
            if dy<0:
                player.rect.top=obj.rect.bottom
                player.hit_head()
        collided_objects.append(obj)
    #返回碰撞的物体，以便于知道是碰壁还是碰火
    return collided_objects
def handle_move(player,objects):
    keys=pygame.key.get_pressed()
    #速度置0，防止无线移动
    player.x_vel=0
    if keys[pygame.K_LEFT]:
        player.move_left(PLAYER_VEL)#作为碰撞，用封装好的方法绘制，包含图片与碰撞
    if keys[pygame.K_RIGHT]:
        player.move_right(PLAYER_VEL)
    #碰撞处理
    handle_vertical_collision(player, objects, player.y_vel)

def main(windows):
    clock=pygame.time.Clock()
    background,bg_image=get_background("Gray.png")
    player=Player(100,500,50,50)
    #创建一组blocks与玩家碰撞,再传给draw函数画出来
    block_size=96
    blocks=[Block(0,HEIGHT-block_size,block_size)]
    #创建地板
    floor=[Block(i*block_size,HEIGHT-block_size,block_size)for i in range(-WIDTH//block_size,(WIDTH*2)//block_size)]
    run=True
    while run:
        clock.tick(FPS)

        '''
        当用户点击窗口关闭按钮时，将 run 设为 False，退出主循环
        这是Pygame游戏的标准结构，用于维持游戏运行并处理退出事件。
        '''
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run=False
                break
        #按帧刷新速度与位移
        player.loop(FPS)
        handle_move(player,floor)
        #处理一帧画面
        draw(windows, background, bg_image, player,floor)

    #释放资源，关闭进程
    pygame.quit()
    quit()
if __name__=="__main__":
    main(window)