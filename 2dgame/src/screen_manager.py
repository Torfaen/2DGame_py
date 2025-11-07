from screen import MainMenu
from config_loader import load_config
import pygame
config=load_config("config.yaml")
config_ui=load_config("config_ui.yaml")
class ScreenManager:
    def __init__(self,window):
        self.window=window
        self.screens={
            
        }
        self.current_screen=None
        self.running=True
        self.clock=pygame.time.Clock()

    def add_screen(self,screen_name,screen):
        self.screens[screen_name]=screen

    def switch_screen(self,screen_name):
        if screen_name in self.screens:
            self.current_screen=self.screens[screen_name]

    def quit(self):
        self.running=False

    def run(self):
        fps=config['windows']['fps']
        while self.running:
            self.clock.tick(fps)
            events=pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()

            if self.current_screen:
                self.current_screen.handle_events(events,self)
                self.current_screen.draw(self.window)
                pygame.display.update()

        