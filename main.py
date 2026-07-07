"""
main.py —— 贪吃蛇游戏入口

项目结构：
  config.py     全局常量与颜色定义
  entities.py   游戏实体（Apple, Segment, Snake）+ 碰撞/边界检测
  utils.py      工具函数（食物生成、最高分读写、键盘输入）
  ui.py         界面渲染（HUD、菜单、暂停、结束画面）

运行方式：
  pip install pygame
  python main.py
"""

import pygame
import sys

# pygame 必须在导入 ui（创建字体）之前初始化
pygame.init()
pygame.display.set_caption("Snake Game")
pygame.font.init()

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SNAKE_SIZE, APPLE_SIZE,
    BASE_FPS, MAX_FPS, FPS_INCREMENT,
    SCORE_PER_FOOD, SPEED_UP_EVERY,
    KEY, MENU, PLAYING, PAUSED, GAME_OVER,
    COLOR_BG,
)
from entities import Snake, checkCollision, checkLimits
from utils import spawn_apple, spawn_apples, load_high_score, save_high_score, get_key
from ui import (
    draw_score, draw_high_score, draw_game_time,
    draw_start_screen, draw_pause_screen, draw_game_over_screen,
)

# ============================================================
#  全局资源
# ============================================================
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE)
game_clock = pygame.time.Clock()


# ============================================================
#  主游戏循环
# ============================================================

def main():
    """游戏入口：状态机驱动的贪吃蛇游戏。"""
    game_state = MENU
    score = 0
    high_score = load_high_score()

    snake = None
    apples = []
    max_apples = 1
    eaten_apple = False
    start_time = 0
    current_fps = BASE_FPS

    # ======================== 主循环 ========================
    while True:

        # ---- 菜单 ----
        if game_state == MENU:
            game_clock.tick(BASE_FPS)               # 避免 CPU 空转
            draw_start_screen(screen, high_score)   # 传入已加载的最高分，不反复读磁盘
            key = get_key()
            if key == "exit":
                break                               # 菜单中 ESC 直接退出
            elif key is not None:
                # 任意键 → 初始化一局新游戏
                score = 0
                current_fps = BASE_FPS
                snake = Snake(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                snake.setDirection(KEY["UP"])
                snake.move()
                for _ in range(3):                  # 初始 3 节身体
                    snake.grow()
                    snake.move()
                apples.clear()
                spawn_apples(snake, apples, max_apples)
                eaten_apple = False
                start_time = pygame.time.get_ticks()
                game_state = PLAYING

        # ---- 游戏进行中 ----
        elif game_state == PLAYING:
            game_clock.tick(current_fps)

            key = get_key()
            if key == "exit":
                game_state = GAME_OVER
                continue
            elif key == "pause":
                game_state = PAUSED
                continue

            # 更新蛇方向
            if key in (KEY["UP"], KEY["DOWN"], KEY["LEFT"], KEY["RIGHT"]):
                snake.setDirection(key)

            # 移动
            snake.move()

            # 环绕边界（传入蛇头）
            checkLimits(snake.getHead())

            # 自碰 → 游戏结束
            if snake.checkCrashing():
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                game_state = GAME_OVER
                continue

            # 食物碰撞检测
            for apple in apples:
                if apple.state != 1:
                    continue
                if checkCollision(snake.getHead(), SNAKE_SIZE, apple, APPLE_SIZE):
                    snake.grow()
                    apple.state = 0
                    score += SCORE_PER_FOOD
                    eaten_apple = True
                    # 难度递增
                    if score % SPEED_UP_EVERY == 0 and current_fps < MAX_FPS:
                        current_fps += FPS_INCREMENT

            # 重新生成食物
            if eaten_apple:
                eaten_apple = False
                spawn_apple(snake, apples, 0)

            # ---- 绘制 ----
            screen.fill(COLOR_BG)

            for apple in apples:
                if apple.state == 1:
                    apple.draw(screen)

            snake.draw(screen)

            game_time = pygame.time.get_ticks() - start_time
            draw_score(screen, score)
            draw_high_score(screen, high_score)
            draw_game_time(screen, game_time)

            pygame.display.flip()

        # ---- 暂停 ----
        elif game_state == PAUSED:
            draw_pause_screen(screen)
            key = get_key()
            if key == "pause":
                game_state = PLAYING
            elif key == "exit":
                game_state = GAME_OVER

        # ---- 游戏结束 ----
        elif game_state == GAME_OVER:
            draw_game_over_screen(screen, score, high_score)
            key = get_key()
            if key == "yes":
                game_state = MENU
            elif key in ("no", "exit"):
                break

    # 安全退出
    pygame.quit()
    sys.exit(0)


# ============================================================
#  入口
# ============================================================
if __name__ == "__main__":
    main()
