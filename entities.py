"""
entities.py —— 游戏实体类与底层检测

包含：
  - checkCollision()    AABB 碰撞检测
  - checkLimits()       环绕边界检测
  - Apple               食物类
  - Segment             蛇身段类
  - Snake               蛇类（移动 / 生长 / 方向 / 自碰 / 绘制）
"""

import pygame
from config import (
    SNAKE_SIZE, APPLE_SIZE, SEPARATION,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    SPEED, BASE_FPS, KEY,
    COLOR_GREEN, COLOR_YELLOW, COLOR_ORANGE,
    COLOR_BLACK,
)


# ============================================================
#  碰撞与边界
# ============================================================

def checkCollision(posA, sizeA, posB, sizeB):
    """AABB（轴对齐包围盒）碰撞检测。

    参数 posA / posB 可以是任何含 .x / .y 属性的对象；
    sizeA / sizeB 为对应的宽高（本游戏中二者相等）。
    """
    return (posA.x < posB.x + sizeB and
            posA.x + sizeA > posB.x and
            posA.y < posB.y + sizeB and
            posA.y + sizeA > posB.y)


def checkLimits(head):
    """环绕边界：蛇头越界后从对侧出现（无死亡墙）。

    参数 head 必须有 .x / .y 属性并被原地修改。
    """
    if head.x > SCREEN_WIDTH:
        head.x = SNAKE_SIZE
    if head.x < 0:
        head.x = SCREEN_WIDTH - SNAKE_SIZE
    if head.y > SCREEN_HEIGHT:
        head.y = SNAKE_SIZE
    if head.y < 0:
        head.y = SCREEN_HEIGHT - SNAKE_SIZE


# ============================================================
#  Apple —— 食物
# ============================================================

class Apple:
    """食物类：记录坐标与状态，绘制自身。"""

    __slots__ = ("x", "y", "state", "color")

    def __init__(self, x, y, state=1):
        self.x = x
        self.y = y
        self.state = state          # 1 = 活跃, 0 = 已被吃
        self.color = COLOR_ORANGE

    def draw(self, screen_surface):
        """绘制食物：橙色方块 + 黄色光晕描边。"""
        # 外光晕
        pygame.draw.rect(
            screen_surface, COLOR_YELLOW,
            (self.x - 1, self.y - 1, APPLE_SIZE + 2, APPLE_SIZE + 2), 1,
        )
        # 实体
        pygame.draw.rect(
            screen_surface, self.color,
            (self.x, self.y, APPLE_SIZE, APPLE_SIZE), 0,
        )


# ============================================================
#  Segment —— 蛇身段
# ============================================================

class Segment:
    """蛇的单个身体段：坐标、方向、颜色标记。"""

    __slots__ = ("x", "y", "direction", "color")

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = KEY["UP"]
        self.color = "white"


# ============================================================
#  Snake —— 蛇
# ============================================================

class Snake:
    """蛇类。

    stack 列表： [0] = 蛇头（即 Snake 实例自身），
                [1..n-2] = 可见蛇身段，
                [n-1] = 尾部哨兵（color="NULL"，不可见，用于生长间隙）。

    哨兵机制：每次 grow() 在末尾追加一个新段 + 一个新哨兵；
    旧哨兵在后续移动中逐渐远离尾部，形成自然间隙。
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = KEY["UP"]
        self.stack = []

        # 蛇头：Snake 自身作为 stack[0]
        self.stack.append(self)

        # 尾部哨兵：不可见占位段
        sentinel = Segment(self.x, self.y + SEPARATION)
        sentinel.direction = KEY["UP"]
        sentinel.color = "NULL"
        self.stack.append(sentinel)

    # ============================================================
    #  移动
    # ============================================================

    def move(self):
        """将蛇整体向前移动一个单位格。

        算法：
          1. 从尾到头，每段复制前一段的坐标与方向
          2. 将蛇头（stack[0]）弹出
          3. 按当前方向推进蛇头
          4. 将蛇头插回栈顶
        """
        last = len(self.stack) - 1
        while last != 0:
            self.stack[last].direction = self.stack[last - 1].direction
            self.stack[last].x = self.stack[last - 1].x
            self.stack[last].y = self.stack[last - 1].y
            last -= 1

        # 弹出蛇头（Snake 实例自身）
        if len(self.stack) < 2:
            head = self
        else:
            head = self.stack.pop(0)

        # 按方向推进
        head.direction = self.stack[0].direction
        step = int(SPEED * BASE_FPS)                # = SNAKE_SIZE
        if self.stack[0].direction == KEY["UP"]:
            head.y = self.stack[0].y - step
        elif self.stack[0].direction == KEY["DOWN"]:
            head.y = self.stack[0].y + step
        elif self.stack[0].direction == KEY["LEFT"]:
            head.x = self.stack[0].x - step
        elif self.stack[0].direction == KEY["RIGHT"]:
            head.x = self.stack[0].x + step

        self.stack.insert(0, head)

    # ============================================================
    #  头部
    # ============================================================

    def getHead(self):
        """返回蛇头段（即 Snake 实例自身）。"""
        return self.stack[0]

    # ============================================================
    #  生长
    # ============================================================

    def grow(self):
        """在尾部追加一个可见段和一个哨兵段。

        新段方向与当前尾部哨兵相同，置于哨兵外侧。
        """
        tail = self.stack[-1]               # 当前最后一个元素 = 哨兵

        if tail.direction == KEY["UP"]:
            new_seg = Segment(tail.x, tail.y - SNAKE_SIZE)
            sentinel = Segment(new_seg.x, new_seg.y - SEPARATION)
        elif tail.direction == KEY["DOWN"]:
            new_seg = Segment(tail.x, tail.y + SNAKE_SIZE)
            sentinel = Segment(new_seg.x, new_seg.y + SEPARATION)
        elif tail.direction == KEY["LEFT"]:
            new_seg = Segment(tail.x - SNAKE_SIZE, tail.y)
            sentinel = Segment(new_seg.x - SEPARATION, new_seg.y)
        elif tail.direction == KEY["RIGHT"]:
            new_seg = Segment(tail.x + SNAKE_SIZE, tail.y)
            sentinel = Segment(new_seg.x + SEPARATION, new_seg.y)
        else:
            return

        sentinel.color = "NULL"
        self.stack.append(new_seg)
        self.stack.append(sentinel)

    # ============================================================
    #  方向
    # ============================================================

    def setDirection(self, direction):
        """设置方向，阻止 180° 掉头。"""
        opposite = {
            KEY["UP"]: KEY["DOWN"],
            KEY["DOWN"]: KEY["UP"],
            KEY["LEFT"]: KEY["RIGHT"],
            KEY["RIGHT"]: KEY["LEFT"],
        }
        if direction != opposite.get(self.direction):
            self.direction = direction

    # ============================================================
    #  自碰检测
    # ============================================================

    def checkCrashing(self):
        """检测蛇头是否撞到自身（跳过哨兵段）。"""
        head = self.stack[0]
        # 遍历除蛇头外的所有段，通过 NULL 标记跳过哨兵
        for seg in self.stack[1:]:
            if seg.color == "NULL":
                continue
            if checkCollision(head, SNAKE_SIZE, seg, SNAKE_SIZE):
                return True
        return False

    # ============================================================
    #  获取占位（用于食物生成避让）
    # ============================================================

    def getOccupiedPositions(self):
        """返回当前蛇占据的所有网格坐标集合（不含哨兵段）。

        食物生成时用于排除这些位置，避免食物出现在蛇身上。
        """
        positions = set()
        for seg in self.stack:
            if seg.color == "NULL":
                continue
            positions.add((seg.x, seg.y))
        return positions

    # ============================================================
    #  绘制
    # ============================================================

    def draw(self, screen_surface):
        """绘制蛇：绿色蛇头（含眼睛）+ 黄色渐变蛇身。"""

        # ---- 蛇头 ----
        head = self.stack[0]
        pygame.draw.rect(
            screen_surface, COLOR_GREEN,
            (head.x, head.y, SNAKE_SIZE, SNAKE_SIZE), 0,
        )

        # 眼睛（位置随方向变化）
        eye_r = 2
        if head.direction == KEY["RIGHT"]:
            e1 = (head.x + SNAKE_SIZE - 3, head.y + 2)
            e2 = (head.x + SNAKE_SIZE - 3, head.y + SNAKE_SIZE - 4)
        elif head.direction == KEY["LEFT"]:
            e1 = (head.x + 3, head.y + 2)
            e2 = (head.x + 3, head.y + SNAKE_SIZE - 4)
        elif head.direction == KEY["UP"]:
            e1 = (head.x + 2, head.y + 3)
            e2 = (head.x + SNAKE_SIZE - 4, head.y + 3)
        else:   # DOWN
            e1 = (head.x + 2, head.y + SNAKE_SIZE - 3)
            e2 = (head.x + SNAKE_SIZE - 4, head.y + SNAKE_SIZE - 3)
        pygame.draw.circle(screen_surface, COLOR_BLACK, e1, eye_r)
        pygame.draw.circle(screen_surface, COLOR_BLACK, e2, eye_r)

        # ---- 蛇身渐变色 ----
        visible_segments = [s for s in self.stack[1:] if s.color != "NULL"]
        total = len(visible_segments)
        for idx, seg in enumerate(visible_segments):
            ratio = 1.0 - (idx / max(total, 1)) * 0.6        # 越靠尾越暗
            r = max(int(255 * ratio), 40)
            g = max(int(215 * ratio), 20)
            color = pygame.Color(r, g, 0)
            pygame.draw.rect(
                screen_surface, color,
                (seg.x, seg.y, SNAKE_SIZE, SNAKE_SIZE), 0,
            )
