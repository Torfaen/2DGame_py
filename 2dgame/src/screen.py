from config_loader import load_config
import pygame
from path_utils import resolve_relative_path
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
        self.image_path=resolve_relative_path(path)
        self.image=pygame.image.load(self.image_path).convert_alpha()

    def draw(self,window):
        window.blit(self.image, self.rect)



class BlueWd(Screen):
    def __init__(self,window,cfg_ui):
        cfg_blue_wd=cfg_ui['ui']['blue_wd']
        width=cfg_blue_wd['width']
        height=cfg_blue_wd['height']
        path=resolve_relative_path(cfg_blue_wd['image_path'])
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
        path=resolve_relative_path(cfg_main_menu['image_path'])
        name=cfg_main_menu['name']
        super().__init__(window,name,width,height,path,x=0,y=0)
        self.button_font = pygame.font.Font(None, 36)
        self.mode_buttons = self._create_mode_buttons(cfg_ui['ui']['buttons'])

        #菜单背景
        self.bg_img=pygame.image.load(resolve_relative_path(cfg_main_menu['image_path'])).convert_alpha()
        self.bg_img=pygame.transform.scale(self.bg_img, (self.width, self.height))

    def _create_mode_buttons(self, buttons_cfg):
        buttons = {}
        for mode_name, mode_cfg in buttons_cfg.items():
            image = pygame.image.load(resolve_relative_path(mode_cfg['image_path'])).convert_alpha()
            rect = image.get_rect()
            rect.center = (mode_cfg['center_x'], mode_cfg['center_y'])
            buttons[mode_name] = {
                "image": image,
                "rect": rect,
                "label": mode_cfg['name'].upper(),
            }
        return buttons

    def handle_events(self,events,manager):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for mode_name, button in self.mode_buttons.items():
                    if button["rect"].collidepoint(event.pos):
                        manager.set_selected_mode(mode_name)
                        manager.quit()
                        break
    
    def draw(self,window):
        window.blit(self.bg_img, (0,0))
        for button in self.mode_buttons.values():
            window.blit(button["image"], button["rect"])
            text_surface = self.button_font.render(button["label"], True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button["rect"].center)
            window.blit(text_surface, text_rect)

