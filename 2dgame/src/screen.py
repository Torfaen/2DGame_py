from config_loader import load_config
import pygame
config=load_config("config.yaml")
config_ui=load_config("config_ui.yaml")

class Screen(pygame.sprite.Sprite):
    #一个screen对象对应一个界面
    def __init__(self,window,screen_name,width,height,path,x,y):
        super().__init__()
        self.screen_name = screen_name
        self.width=width
        self.height=height
        self.rect=pygame.Rect(0, 0, self.width, self.height)
        self.image_path=path
        self.image=pygame.image.load(self.image_path).convert_alpha()

    def draw(self,window):
        window.blit(self.image, self.rect)



class BlueWd(Screen):
    def __init__(self,window,cfg_ui):
        cfg_blue_wd=cfg_ui['ui']['blue_wd']
        width=cfg_blue_wd['width']
        height=cfg_blue_wd['height']
        path=cfg_blue_wd['image_path']
        name=cfg_blue_wd['name']
        super().__init__(window,name,width,height,path,x=0,y=0)
        self.image=pygame.image.load(path).convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.topleft=(0,0)

    def draw(self,window):
        window.blit(self.image, self.rect)

#暂时硬编码
class MainMenu(Screen):
    def __init__(self,window,cfg_ui):
        cfg_main_menu=cfg_ui['ui']['screens']['main_menu']
        width=cfg_main_menu['width']
        height=cfg_main_menu['height']
        path=cfg_main_menu['image_path']
        name=cfg_main_menu['name']
        super().__init__(window,name,width,height,path,x=0,y=0)
        self.buttons_start_img=pygame.image.load(cfg_ui['ui']['buttons']['play']['image_path']).convert_alpha()
        self.bt_start_rect=self.buttons_start_img.get_rect()
        #按钮坐标
        self.bt_start_rect.x= 750
        self.bt_start_rect.y= 400
        self.bt_start_rect.center=(self.bt_start_rect.x, self.bt_start_rect.y)

        #菜单背景
        self.bg_img=pygame.image.load(cfg_main_menu['image_path']).convert_alpha()
        self.bg_img=pygame.transform.scale(self.bg_img, (self.width, self.height))

    def handle_events(self,events,manager):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                #如果点击了开始按钮，则切换到游戏界面
                if self.bt_start_rect.collidepoint(event.pos):
                    manager.switch_screen("gameplay")
                    #临时使用，直接退出当前界面，之后再封装游戏界面进gameplayScreen类，继承screen
                    manager.quit()
    
    def draw(self,window):
        window.blit(self.bg_img, (0,0))
        window.blit(self.buttons_start_img, self.bt_start_rect)

