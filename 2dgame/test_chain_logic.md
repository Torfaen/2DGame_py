#!/usr/bin/env python3
"""
测试连锁爆炸逻辑
"""
print("=== 连锁爆炸逻辑测试 ===")
print("1. 炸弹A爆炸")
print("2. 检查爆炸范围内的其他炸弹")
print("3. 触发范围内的炸弹B连锁爆炸")
print("4. 炸弹B爆炸后继续检查连锁")
print("5. 重复直到没有更多连锁")
print()
print("关键代码逻辑:")
print("- Bomb.trigger_chain_explosion(): 立即引爆炸弹")
print("- Explosion.update(): 检查爆炸范围内的炸弹并触发连锁")
print("- 爆炸区域计算: 十字形，考虑障碍物阻挡")
print()
print("测试场景:")
print("炸弹A(100,100) -> 炸弹B(132,100) -> 炸弹C(164,100)")
print("炸弹A爆炸时应该连锁引爆B和C")

