# 强化学习与 PVE 接入说明

## 本轮改动概览

这轮修改主要完成了两件事：

1. 把游戏入口从单一 PVP 启动方式，改成了同一个入口下由主菜单选择 `PVP` 或 `PVE`
2. 为后续强化学习接入补齐了可编程动作接口、无头运行选项和环境封装

当前项目已经支持：

- 从 `2dgame/src/main2.py` 统一启动
- 在主菜单选择 `PVP` 或 `PVE`
- `PVE` 模式下由 1P 人类对战 2P AI
- 使用 `BombermanEnv` 进行无头环境重置和步进

## 本轮新增或修改的核心能力

### 1. 单入口模式选择

当前主入口仍然是：

- `2dgame/src/main2.py`

启动后会先进入主菜单，由菜单返回模式，再由 `GameManager` 根据模式配置游戏逻辑。

目前支持：

- `pvp`: 1P 和 2P 都由玩家控制
- `pve`: 1P 由玩家控制，2P 由 AI 控制

相关文件：

- `2dgame/src/main2.py`
- `2dgame/src/screen.py`
- `2dgame/src/screen_manager.py`
- `2dgame/config/config_ui.yaml`

### 2. 主菜单按钮扩展

原来主菜单只有一个开始按钮，现在改成两个模式按钮：

- `PVP`
- `PVE`

当前两个按钮暂时复用同一张按钮图，并在按钮中央叠加文本区分模式。

按钮配置在：

- `2dgame/config/config_ui.yaml`

如果后续有正式的美术资源，可以直接替换这里的按钮图片路径和坐标。

### 3. 放炸弹输入抽象

为了兼容玩家操作和 AI 控制，放炸弹逻辑从直接读取 `pygame.key.get_pressed()` 改成了“按钮按住状态”抽象。

现在每个玩家对象都有：

- `bomb_button_held`

人类玩家：

- 通过 `KEYDOWN` / `KEYUP` 维护这个状态

AI 或训练环境：

- 通过 `apply_action()` 或 `set_bomb_button()` 直接设置这个状态

这样仍然保留了“按住放弹，冷却结束就持续放到上限”的原作效果，同时也让 AI 可以复用同一套规则。

相关文件：

- `2dgame/src/player.py`
- `2dgame/src/game_manager.py`

### 4. 程序化动作接口

为支持 AI 和 RL，`Player` 新增了程序化控制接口：

- `set_direction_state(direction)`
- `set_bomb_button(is_held)`
- `apply_action(action)`

`GameManager` 新增了：

- `set_player_action(player_id, action)`
- `clear_player_action(player_id)`

这样后续不需要依赖真实键盘输入，也可以控制角色移动和放弹。

### 5. PVE 模式下的 AI 控制器

新增了基础 AI 控制器模块：

- `2dgame/src/ai_controller.py`

当前默认实现是：

- `RandomAIController`

它会随机选择移动或放弹动作，用于打通完整的 PVE 流程。

这不是最终 AI，只是第一版占位实现，后续可以替换为：

- 规则 AI
- 强化学习模型
- 外部推理服务

### 6. 无头模式与训练选项

`GameManager` 现在支持通过 `options` 控制运行模式：

- `headless`
- `skip_menu`
- `render`
- `enable_audio`
- `human_controlled_ids`
- `match_mode`

这让同一套游戏逻辑同时支持：

- 可视化玩家对战
- 人类 vs AI
- 无头训练环境

说明：

- `headless=True` 表示不按正常可视化方式运行
- `skip_menu=True` 表示跳过主菜单
- `render=False` 表示不渲染
- `enable_audio=False` 表示不初始化音频

### 7. RL 环境封装

新增了：

- `2dgame/src/rl_env.py`

提供 `BombermanEnv`，支持：

- `reset()`
- `step(action)`
- `get_observation()`
- `compute_reward(done)`
- `is_done()`
- `get_info()`

当前动作空间为离散 6 动作：

- `idle`
- `up`
- `down`
- `left`
- `right`
- `bomb`

也支持直接传入字典动作：

```python
{"move": "left", "bomb": False}
{"move": None, "bomb": True}
```

### 8. 结构化状态导出

为了便于 AI 和训练，游戏现在可以导出结构化状态快照。

新增接口：

- `GameManager.get_state_snapshot()`
- `Map.export_layers()`

快照中包含：

- 当前游戏状态
- 胜者
- 存活人数
- 地图层数据
- 玩家状态
- 炸弹状态
- 爆炸区域
- 道具列表

当前 `BombermanEnv.get_observation()` 直接复用这套快照。

### 9. 音频可选初始化

为了避免无头训练时因为音频设备或混音器初始化失败导致无法运行，`AudioManager` 现在支持：

- `AudioManager(enabled=True/False)`

无头或训练模式下可以禁用音频。

## 当前奖励设计

当前强化学习首版奖励采用最简单的终局奖励，基于 `ONE_LIFE` 模式：

- AI 获胜：`+1`
- AI 失败：`-1`
- 平局：`0`
- 对局未结束：`0`

这版奖励的优点是简单、稳定、便于先打通训练流程。

后续可扩展的 shaping reward 包括：

- 吃到道具奖励
- 炸到对手奖励
- 自己被炸惩罚
- 靠近危险区惩罚
- 生存步数奖励或拖延惩罚

## 当前运行方式

### 正常启动游戏

在项目根目录、并激活虚拟环境后运行：

```powershell
python .\2dgame\src\main2.py
```

启动后可在主菜单选择：

- `PVP`
- `PVE`

### 在代码中使用 RL 环境

示例：

```python
from rl_env import BombermanEnv

env = BombermanEnv()
obs = env.reset()
obs, reward, done, info = env.step(0)
```

## 本轮安装的依赖

在项目 `.venv` 中安装了：

- `pygame`
- `PyYAML`

## 当前限制

### 1. AI 仍然是占位实现

当前 `PVE` 使用的是随机 AI，只能证明控制链路打通，不能提供高质量对战体验。

### 2. 训练速度仍受主循环帧率语义影响

当前游戏内部很多计时逻辑仍按“帧数”推进，比如：

- 炸弹引爆时间
- 爆炸持续时间
- 放弹冷却

所以如果后续要显著提升训练速度，需要进一步区分：

- 玩家模式
- 训练模式

并决定是否保留当前“按步数模拟时间”的语义。

### 3. 菜单按钮美术还是临时方案

当前 `PVP` / `PVE` 复用了同一张按钮图，只通过文字区分。

## 推荐的下一步

建议优先做这几项中的一项或两项：

1. 把 `RandomAIController` 升级为基础规则 AI
2. 为菜单按钮换成独立的正式资源
3. 为训练模式增加“不限帧的高速 step”
4. 扩展奖励函数，加入中间奖励
5. 给 `BombermanEnv` 补一个更标准的训练接口封装
