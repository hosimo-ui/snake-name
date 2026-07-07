"""
ui.py —— 界面渲染

负责所有屏幕绘制逻辑：
  - HUD（得分、最高分、存活时间）
  - 开始菜单
  - 暂停覆盖层
  - 游戏结束结算画面

所有函数均接收 screen_surface 作为第一个参数，不依赖全局变量。
"""

import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SNAKE_SIZE,
    COLOR_BG, COLOR_BLACK, COLOR_WHITE,
    COLOR_GREEN, COLOR_YELLOW, COLOR_ORANGE,
    COLOR_RED, COLOR_DIM,
)

# ============================================================
#  字体资源（在 pygame.init() 之后导入本模块即可安全创建）
# ============================================================
TITLE_FONT = pygame.font.Font(None, 72)
SCORE_FONT = pygame.font.Font(None, 38)
SCORE_NUMB_FONT = pygame.font.Font(None, 28)
GAME_OVER_FONT = pygame.font.Font(None, 48)
INFO_FONT = pygame.font.Font(None, 24)


# ============================================================
#  HUD 元素
# ============================================================

def draw_score(screen, score):
    """右上角：当前得分。"""
    label = SCORE_FONT.render("Score:", 1, COLOR_GREEN)
    value = SCORE_NUMB_FONT.render(str(score), 1, COLOR_RED)
    screen.blit(label, (SCREEN_WIDTH - 120, 10))
    screen.blit(value, (SCREEN_WIDTH - 45, 14))


def draw_high_score(screen, high_score):
    """得分下方：历史最高分。"""
    label = INFO_FONT.render("Best:", 1, COLOR_ORANGE)
    value = INFO_FONT.render(str(high_score), 1, COLOR_WHITE)
    screen.blit(label, (30, 40))
    screen.blit(value, (75, 40))


def draw_game_time(screen, game_time_ms):
    """左上角：存活时间。"""
    label = SCORE_FONT.render("Time:", 1, COLOR_WHITE)
    value = SCORE_NUMB_FONT.render(f"{game_time_ms / 1000:.1f}s", 1, COLOR_WHITE)
    screen.blit(label, (30, 10))
    screen.blit(value, (105, 14))


# ============================================================
#  全屏界面
# ============================================================

def draw_start_screen(screen, high_score):
    """主菜单：标题 + 操作说明 + 最高分。

    参数 high_score 由外部加载后传入，避免每帧读磁盘。
    """
    screen.fill(COLOR_BG)

    # 标题
    title = TITLE_FONT.render("SNAKE GAME", 1, COLOR_GREEN)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 120))

    # 副标题
    sub = SCORE_FONT.render("Classic Arcade  ·  Pygame Edition", 1, COLOR_DIM)
    screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 180))

    # 操作说明
    hints = [
        ("↑ ↓ ← →", "Move the snake"),
        ("P", "Pause / Resume"),
        ("ESC", "Quit game"),
        ("Y / N", "Play again / Exit  (on Game Over screen)"),
    ]
    y = 260
    for key_text, desc in hints:
        k = INFO_FONT.render(f"  {key_text}", 1, COLOR_YELLOW)
        d = INFO_FONT.render(f"  —  {desc}", 1, COLOR_WHITE)
        screen.blit(k, (200, y))
        screen.blit(d, (420, y))
        y += 35

    # 开始提示
    start = GAME_OVER_FONT.render("Press ANY KEY to Start", 1, COLOR_GREEN)
    screen.blit(start, (SCREEN_WIDTH // 2 - start.get_width() // 2, 440))

    # 历史最高分
    if high_score > 0:
        hs = SCORE_FONT.render(f"High Score: {high_score}", 1, COLOR_ORANGE)
        screen.blit(hs, (SCREEN_WIDTH // 2 - hs.get_width() // 2, 490))

    pygame.display.flip()


def draw_pause_screen(screen):
    """暂停覆盖层：半透明遮罩 + 提示文字。"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(150)
    overlay.fill(COLOR_BLACK)
    screen.blit(overlay, (0, 0))

    pause = GAME_OVER_FONT.render("PAUSED", 1, COLOR_YELLOW)
    hint = SCORE_FONT.render("Press P to Resume", 1, COLOR_WHITE)
    screen.blit(pause, (SCREEN_WIDTH // 2 - pause.get_width() // 2, 250))
    screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 300))
    pygame.display.flip()


def draw_game_over_screen(screen, score, high_score):
    """游戏结束结算画面：得分 + 是否破纪录 + 重玩提示。"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(COLOR_BLACK)
    screen.blit(overlay, (0, 0))

    over = GAME_OVER_FONT.render("GAME OVER", 1, COLOR_RED)
    screen.blit(over, (SCREEN_WIDTH // 2 - over.get_width() // 2, 200))

    sc = SCORE_FONT.render(f"Score: {score}", 1, COLOR_WHITE)
    screen.blit(sc, (SCREEN_WIDTH // 2 - sc.get_width() // 2, 260))

    # 新纪录提示
    if score >= high_score and score > 0:
        nb = SCORE_FONT.render("★ NEW HIGH SCORE! ★", 1, COLOR_YELLOW)
        screen.blit(nb, (SCREEN_WIDTH // 2 - nb.get_width() // 2, 300))

    pa = SCORE_FONT.render("Play Again?  (Y / N)", 1, COLOR_GREEN)
    screen.blit(pa, (SCREEN_WIDTH // 2 - pa.get_width() // 2, 360))

    pygame.display.flip()
