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
def draw(windows, background, bg_image, player):
    for tile in background:
        windows.blit(bg_image, tile)
    player.draw(windows)
    pygame.display.update()
def handle_move(player):
    keys=pygame.key.get_pressed()
    #速度置0，防止无线移动
    player.x_vel=0
    if keys[pygame.K_LEFT]:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT]:
        player.move_right(PLAYER_VEL)

def main(windows):
    clock=pygame.time.Clock()
    background,bg_image=get_background("Gray.png")
    player=Player(100,100,50,50)
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
        handle_move(player)
        #处理一帧画面
        draw(windows, background, bg_image, player)

    #释放资源，关闭进程
    pygame.quit()
    quit()
if __name__=="__main__":
    main(window)