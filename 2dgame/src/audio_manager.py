import pygame
import os
from config_loader import load_config

config_audio = load_config("config_audio.yaml")
audio_config = config_audio['audio']  # 获取 audio 节点下的所有配置

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.load_sounds()
        

    def load_sounds(self):
        """
        预加载所有音效到内存
        作用：游戏开始时一次性加载所有音效文件，播放时直接调用，避免卡顿
        """
        try:
            # 遍历配置文件中的所有音效
            for sound_name, sound_path in audio_config['sounds'].items():  
                # 加载音效文件，存入字典（sound_name 是键，Sound对象是值）
                self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
        except Exception as e:
            print(f"Error loading sounds: {e}")

    #播放音效volume是音量大小0.0-1.0，1.0是最大音量
    def play(self, sound_name, volume=1.0):
        if sound_name in self.sounds:
            # 设置音量
            self.sounds[sound_name].set_volume(volume)
            # 播放音效（可以同时播放多个）
            self.sounds[sound_name].play()
        else:
            print(f"Sound {sound_name} not found")

#播放背景音乐loop是循环次数-1表示无限循环，0表示只播放一次，1表示播放2次
    @staticmethod
    def play_bgm(bgm_name, loop=-1):
        try:
            # 检查 BGM 是否存在
            if bgm_name in audio_config['bgm']:
                # 从配置中获取BGM的路径
                bgm_path = os.path.join(audio_config['bgm'][bgm_name])
                # 加载背景音乐文件
                pygame.mixer.music.load(bgm_path)
                # 播放背景音乐（loop=-1 表示无限循环）
                pygame.mixer.music.play(loop)
            else:
                print(f"BGM {bgm_name} not found")
        except Exception as e:
            print(f"Error playing BGM: {e}")