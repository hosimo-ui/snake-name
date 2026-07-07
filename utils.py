"""
utils.py —— 工具函数

包含：
  - 食物生成（spawn_apple / spawn_apples）
  - 最高分读写（load_high_score / save_high_score）
  - 键盘输入处理（get_key）
"""

import random
import sys
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SNAKE_SIZE,
    HIGH_SCORE_FILE, KEY,
)
from entities import Apple


# ============================================================
#  食物生成
# ============================================================

def spawn_apple(snake, apples, index):
    """在随机位置生成一个食物，自动避开蛇的全部身体段。

    参数:
        snake  -- Snake 实例（用于获取占位集合）
        apples -- 食物列表
        index  -- 替换 apples[index] 处的食物
    """
    occupied = snake.getOccupiedPositions()
    margin = 40
    while True:
        x = random.randint(margin, SCREEN_WIDTH - margin)
        y = random.randint(margin, SCREEN_HEIGHT - margin)
        # 对齐到网格
        x = (x // SNAKE_SIZE) * SNAKE_SIZE
        y = (y // SNAKE_SIZE) * SNAKE_SIZE
        # 确保不在蛇身上
        if (x, y) not in occupied:
            break
    apples[index] = Apple(x, y, 1)


def spawn_apples(snake, apples, quantity):
    """批量生成指定数量的食物，均避开蛇身。"""
    occupied = snake.getOccupiedPositions()
    apples.clear()
    margin = 40
    for _ in range(quantity):
        while True:
            x = random.randint(margin, SCREEN_WIDTH - margin)
            y = random.randint(margin, SCREEN_HEIGHT - margin)
            x = (x // SNAKE_SIZE) * SNAKE_SIZE
            y = (y // SNAKE_SIZE) * SNAKE_SIZE
            if (x, y) not in occupied:
                break
        apples.append(Apple(x, y, 1))
        occupied.add((x, y))          # 避免多个食物重叠


# ============================================================
#  最高分持久化
# ============================================================

def load_high_score():
    """从文件读取最高分；文件不存在或损坏时返回 0。"""
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(score):
    """将最高分写入文件持久化；写入失败静默忽略。"""
    try:
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(score))
    except OSError:
        pass


# ============================================================
#  键盘输入
# ============================================================

def get_key():
    """从事件队列取一个按键，返回方向值或特殊操作字符串。

    返回值:
        KEY["UP"] / KEY["DOWN"] / KEY["LEFT"] / KEY["RIGHT"]  方向
        "pause"      P 键
        "exit"       ESC 键
        "yes"        Y 键
        "no"         N 键
        "any"        其他任意键（用于菜单）
        None         本帧无按键
    """
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                return KEY["UP"]
            elif event.key == pygame.K_DOWN:
                return KEY["DOWN"]
            elif event.key == pygame.K_LEFT:
                return KEY["LEFT"]
            elif event.key == pygame.K_RIGHT:
                return KEY["RIGHT"]
            elif event.key == pygame.K_ESCAPE:
                return "exit"
            elif event.key == pygame.K_y:
                return "yes"
            elif event.key == pygame.K_n:
                return "no"
            elif event.key == pygame.K_p:
                return "pause"
            else:
                return "any"
        if event.type == pygame.QUIT:
            sys.exit(0)
    return None
