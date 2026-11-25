"""
Pygame UI components for Modern Dark-Mode Password Generator.
Features high-DPI scaling, smooth animations, and custom procedural vector icons.
"""

import math
from typing import Callable, List, Optional, Tuple
import pygame

# ----------------- Theme Color Palette (Catppuccin Mocha Inspired) -----------------
BG_COLOR = (24, 24, 37)          # Base background
CARD_BG = (30, 30, 46)           # Surface 0
CARD_SURFACE = (40, 41, 60)      # Surface 1
BORDER_COLOR = (49, 50, 68)      # Surface 2
BORDER_HIGHLIGHT = (88, 91, 112) # Overlay 0

TEXT_PRIMARY = (205, 214, 244)   # Crisp white/slate
TEXT_SECONDARY = (166, 173, 200) # Soft lavender-gray
TEXT_MUTED = (130, 135, 155)     # Dim label text
TEXT_DARK = (17, 17, 27)         # Deep dark text for bright buttons

ACCENT_BLUE = (137, 180, 250)    # Sapphire
ACCENT_BLUE_HOVER = (175, 205, 255)
ACCENT_GREEN = (166, 227, 161)   # Green / Copied
ACCENT_GREEN_HOVER = (195, 240, 190)
ACCENT_RED = (243, 139, 168)     # Red
ACCENT_PEACH = (250, 179, 135)   # Peach
ACCENT_YELLOW = (249, 226, 175)  # Yellow
ACCENT_TEAL = (148, 226, 213)    # Teal


class FontManager:
    """Manages system fonts with DPI-scaled point sizes and fallbacks."""
    _instance = None

    def __init__(self, scale: float = 1.0):
        pygame.font.init()
        self.scale = scale

        preferred_fonts = ["Segoe UI", "Inter", "San Francisco", "Roboto", "Helvetica Neue", "Arial"]
        found_font = None
        available = [f.lower() for f in pygame.font.get_fonts()]
        for fn in preferred_fonts:
            if fn.lower() in available:
                found_font = fn
                break

        def S(size: int) -> int:
            return max(10, int(round(size * self.scale)))

        self.font_title = pygame.font.SysFont(found_font, S(24), bold=True)
        self.font_subtitle = pygame.font.SysFont(found_font, S(13))
        self.font_body = pygame.font.SysFont(found_font, S(14))
        self.font_body_bold = pygame.font.SysFont(found_font, S(14), bold=True)
        self.font_small = pygame.font.SysFont(found_font, S(11))
        self.font_small_bold = pygame.font.SysFont(found_font, S(11), bold=True)

        mono_fonts = ["Consolas", "Cascadia Code", "Courier New", "Lucida Console"]
        found_mono = None
        for mf in mono_fonts:
            if mf.lower() in available:
                found_mono = mf
                break
        self.font_mono = pygame.font.SysFont(found_mono, S(18), bold=True)
        self.font_mono_small = pygame.font.SysFont(found_mono, S(13), bold=True)

    @classmethod
    def get(cls, scale: float = 1.0):
        if cls._instance is None:
            cls._instance = FontManager(scale)
        return cls._instance


# ----------------- Procedural Vector Icon Rendering -----------------

def draw_lock_icon(surface: pygame.Surface, cx: int, cy: int, size: int, color: Tuple[int, int, int], bg_color: Tuple[int, int, int] = CARD_BG):
    """Draws a modern vector padlock."""
    body_w = int(size * 0.85)
    body_h = int(size * 0.65)
    body_x = cx - body_w // 2
    body_y = cy - body_h // 2 + int(size * 0.14)
    r = max(2, int(size * 0.15))
    pygame.draw.rect(surface, color, (body_x, body_y, body_w, body_h), border_radius=r)

    # Shackle
    shackle_w = int(size * 0.5)
    shackle_h = int(size * 0.45)
    shackle_x = cx - shackle_w // 2
    shackle_y = body_y - shackle_h + 2
    shackle_rect = pygame.Rect(shackle_x, shackle_y, shackle_w, shackle_h * 2)
    line_w = max(2, int(size * 0.13))
    pygame.draw.arc(surface, color, shackle_rect, 0, math.pi, line_w)
    pygame.draw.line(surface, color, (shackle_x, shackle_y + shackle_h), (shackle_x, body_y + 2), line_w)
    pygame.draw.line(surface, color, (shackle_x + shackle_w - 1, shackle_y + shackle_h), (shackle_x + shackle_w - 1, body_y + 2), line_w)

    # Keyhole
    key_r = max(1, int(size * 0.09))
    pygame.draw.circle(surface, bg_color, (cx, body_y + int(body_h * 0.42)), key_r)
    pygame.draw.line(surface, bg_color, (cx, body_y + int(body_h * 0.42)), (cx, body_y + int(body_h * 0.72)), max(2, int(size * 0.08)))


def draw_copy_icon(surface: pygame.Surface, cx: int, cy: int, size: int, color: Tuple[int, int, int], bg_color: Tuple[int, int, int]):
    """Draws a clean modern dual-sheet copy vector icon."""
    w = int(size * 0.62)
    h = int(size * 0.76)
    offset = max(3, int(size * 0.18))
    lw = max(2, int(size * 0.1))

    # Back sheet
    back_r = pygame.Rect(cx - w // 2 - offset // 2, cy - h // 2 - offset // 2, w, h)
    pygame.draw.rect(surface, color, back_r, width=lw, border_radius=3)

    # Front sheet (filled background + stroke)
    front_r = pygame.Rect(cx - w // 2 + offset // 2, cy - h // 2 + offset // 2, w, h)
    pygame.draw.rect(surface, bg_color, front_r, border_radius=3)
    pygame.draw.rect(surface, color, front_r, width=lw, border_radius=3)


def draw_refresh_icon(surface: pygame.Surface, cx: int, cy: int, size: int, color: Tuple[int, int, int]):
    """Draws a circular refresh / regenerate arrow."""
    r = int(size * 0.38)
    rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
    lw = max(2, int(size * 0.12))
    # Draw arc ~290 degrees
    pygame.draw.arc(surface, color, rect, 0.4, 5.6, lw)

    # Arrowhead at end of arc
    ax = cx + int(r * math.cos(0.4))
    ay = cy - int(r * math.sin(0.4))
    arr_s = int(size * 0.22)
    points = [
        (ax, ay - arr_s // 2),
        (ax + arr_s, ay + arr_s // 3),
        (ax - arr_s // 3, ay + arr_s // 2),
    ]
    pygame.draw.polygon(surface, color, points)


def draw_speaker_icon(surface: pygame.Surface, cx: int, cy: int, size: int, color: Tuple[int, int, int], muted: bool = False):
    """Draws a speaker horn with sound waves or a mute slash."""
    body_w = int(size * 0.2)
    body_h = int(size * 0.35)
    body_x = cx - int(size * 0.32)
    body_y = cy - body_h // 2
    pygame.draw.rect(surface, color, (body_x, body_y, body_w, body_h), border_radius=1)

    pts = [
        (body_x + body_w, body_y),
        (cx + int(size * 0.05), cy - int(size * 0.35)),
        (cx + int(size * 0.05), cy + int(size * 0.35)),
        (body_x + body_w, body_y + body_h),
    ]
    pygame.draw.polygon(surface, color, pts)

    if not muted:
        lw = max(2, int(size * 0.1))
        arc1_r = int(size * 0.22)
        pygame.draw.arc(surface, color, pygame.Rect(cx - int(size * 0.05), cy - arc1_r, arc1_r * 2, arc1_r * 2), -math.pi * 0.3, math.pi * 0.3, lw)
        arc2_r = int(size * 0.36)
        pygame.draw.arc(surface, color, pygame.Rect(cx - int(size * 0.1), cy - arc2_r, arc2_r * 2, arc2_r * 2), -math.pi * 0.35, math.pi * 0.35, lw)
    else:
        lw = max(2, int(size * 0.12))
        slash_start = (cx + int(size * 0.12), cy - int(size * 0.25))
        slash_end = (cx + int(size * 0.36), cy + int(size * 0.25))
        pygame.draw.line(surface, color, slash_start, slash_end, lw)
        pygame.draw.line(surface, color, (cx + int(size * 0.36), cy - int(size * 0.25)), (cx + int(size * 0.12), cy + int(size * 0.25)), lw)


def draw_check_icon(surface: pygame.Surface, cx: int, cy: int, size: int, color: Tuple[int, int, int]):
    """Draws a crisp checkmark."""
    lw = max(2, int(size * 0.15))
    p1 = (cx - int(size * 0.35), cy)
    p2 = (cx - int(size * 0.08), cy + int(size * 0.28))
    p3 = (cx + int(size * 0.38), cy - int(size * 0.28))
    pygame.draw.line(surface, color, p1, p2, lw)
    pygame.draw.line(surface, color, p2, p3, lw)


def draw_rounded_card(surface: pygame.Surface, rect: pygame.Rect, bg_color=CARD_BG, border_color=BORDER_COLOR, radius=12, border_width=1):
    """Draws a card background with smooth rounded borders."""
    pygame.draw.rect(surface, bg_color, rect, border_radius=radius)
    if border_width > 0 and border_color:
        pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=radius)


# ----------------- UI Components -----------------

class Button:
    """Interactive button with hover states and procedural vector icon rendering."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        on_click: Optional[Callable[[], None]] = None,
        bg_color: Tuple[int, int, int] = ACCENT_BLUE,
        hover_color: Tuple[int, int, int] = ACCENT_BLUE_HOVER,
        text_color: Tuple[int, int, int] = TEXT_DARK,
        border_radius: int = 10,
        font: Optional[pygame.font.Font] = None,
        icon: Optional[str] = None,
        scale: float = 1.0,
    ):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.on_click = on_click
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.font = font or FontManager.get().font_body_bold
        self.icon = icon
        self.scale = scale
        self.is_hovered = False
        self.is_pressed = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.is_pressed
            self.is_pressed = False
            if was_pressed and self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surface: pygame.Surface):
        color = self.hover_color if self.is_hovered else self.bg_color
        if self.is_pressed:
            color = tuple(max(0, c - 25) for c in color)

        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)

        rendered_text = self.font.render(self.text, True, self.text_color)
        text_w = rendered_text.get_width()
        text_h = rendered_text.get_height()

        if self.icon:
            icon_size = max(14, int(text_h * 1.1))
            spacing = int(8 * self.scale)
            total_w = icon_size + spacing + text_w
            start_x = self.rect.centerx - total_w // 2
            icon_cx = start_x + icon_size // 2
            icon_cy = self.rect.centery

            if self.icon == "copy":
                draw_copy_icon(surface, icon_cx, icon_cy, icon_size, self.text_color, bg_color=color)
            elif self.icon == "refresh":
                draw_refresh_icon(surface, icon_cx, icon_cy, icon_size, self.text_color)
            elif self.icon == "sound_on":
                draw_speaker_icon(surface, icon_cx, icon_cy, icon_size, self.text_color, muted=False)
            elif self.icon == "sound_off":
                draw_speaker_icon(surface, icon_cx, icon_cy, icon_size, self.text_color, muted=True)

            text_pos = (start_x + icon_size + spacing, self.rect.centery - text_h // 2)
            surface.blit(rendered_text, text_pos)
        else:
            text_rect = rendered_text.get_rect(center=self.rect.center)
            surface.blit(rendered_text, text_rect)


class ToggleSwitch:
    """Pill toggle switch with smooth animated sliding knob."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        label: str,
        hint: str = "",
        checked: bool = True,
        on_toggle: Optional[Callable[[bool], None]] = None,
        scale: float = 1.0,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.hint = hint
        self.checked = checked
        self.on_toggle = on_toggle
        self.scale = scale

        # Switch pill dimensions
        self.pill_w = int(48 * scale)
        self.pill_h = int(24 * scale)
        pad = int(14 * scale)
        self.pill_rect = pygame.Rect(self.rect.right - self.pill_w - pad, self.rect.centery - self.pill_h // 2, self.pill_w, self.pill_h)

        self.anim_val = 1.0 if checked else 0.0
        self.is_hovered = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.on_toggle:
                    self.on_toggle(self.checked)
                return True
        return False

    def update(self, dt: float):
        target = 1.0 if self.checked else 0.0
        speed = 12.0 * dt
        if self.anim_val < target:
            self.anim_val = min(target, self.anim_val + speed)
        elif self.anim_val > target:
            self.anim_val = max(target, self.anim_val - speed)

    def draw(self, surface: pygame.Surface):
        fm = FontManager.get()

        if self.is_hovered:
            pygame.draw.rect(surface, CARD_SURFACE, self.rect, border_radius=int(8 * self.scale))

        # Label
        lbl_surf = fm.font_body.render(self.label, True, TEXT_PRIMARY)
        offset_y = int(18 * self.scale) if self.hint else int(8 * self.scale)
        surface.blit(lbl_surf, (self.rect.x + int(12 * self.scale), self.rect.centery - offset_y))

        # Hint
        if self.hint:
            hint_surf = fm.font_small.render(self.hint, True, TEXT_MUTED)
            surface.blit(hint_surf, (self.rect.x + int(12 * self.scale), self.rect.centery + int(2 * self.scale)))

        # Pill background interpolation
        c_off = BORDER_COLOR
        c_on = ACCENT_BLUE
        bg_col = (
            int(c_off[0] + (c_on[0] - c_off[0]) * self.anim_val),
            int(c_off[1] + (c_on[1] - c_off[1]) * self.anim_val),
            int(c_off[2] + (c_on[2] - c_off[2]) * self.anim_val),
        )
        pygame.draw.rect(surface, bg_col, self.pill_rect, border_radius=self.pill_h // 2)

        # Sliding Knob
        knob_radius = (self.pill_h - int(6 * self.scale)) // 2
        start_x = self.pill_rect.x + int(3 * self.scale) + knob_radius
        end_x = self.pill_rect.right - int(3 * self.scale) - knob_radius
        cur_x = int(start_x + (end_x - start_x) * self.anim_val)
        cur_y = self.pill_rect.centery

        knob_col = (255, 255, 255) if self.anim_val > 0.5 else (210, 215, 230)
        pygame.draw.circle(surface, knob_col, (cur_x, cur_y), knob_radius)


class Slider:
    """Horizontal slider with draggable knob, live badge, and high DPI scaling."""

    def __init__(
        self,
        rect: pygame.Rect,
        min_val: int = 6,
        max_val: int = 64,
        value: int = 16,
        label: str = "Password Length",
        on_change: Optional[Callable[[int], None]] = None,
        scale: float = 1.0,
    ):
        self.rect = pygame.Rect(rect)
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.label = label
        self.on_change = on_change
        self.scale = scale

        self.is_dragging = False
        self.is_hovered = False

        self.track_x = self.rect.x + int(16 * scale)
        self.track_y = self.rect.y + int(38 * scale)
        self.track_w = self.rect.width - int(32 * scale)
        self.track_h = max(4, int(6 * scale))

        self.knob_r = max(8, int(10 * scale))

    def _val_to_x(self) -> int:
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.track_x + ratio * self.track_w)

    def _x_to_val(self, x: int) -> int:
        clamped_x = max(self.track_x, min(x, self.track_x + self.track_w))
        ratio = (clamped_x - self.track_x) / self.track_w
        val = round(self.min_val + ratio * (self.max_val - self.min_val))
        return int(val)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            knob_pos = (self._val_to_x(), self.track_y)
            dist = math.hypot(event.pos[0] - knob_pos[0], event.pos[1] - knob_pos[1])
            self.is_hovered = dist <= self.knob_r + 6 or self.rect.collidepoint(event.pos)

            if self.is_dragging:
                new_val = self._x_to_val(event.pos[0])
                if new_val != self.value:
                    self.value = new_val
                    if self.on_change:
                        self.on_change(self.value)
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            knob_pos = (self._val_to_x(), self.track_y)
            dist = math.hypot(event.pos[0] - knob_pos[0], event.pos[1] - knob_pos[1])
            track_area = pygame.Rect(self.track_x - 12, self.track_y - 14, self.track_w + 24, 28)

            if dist <= self.knob_r + 8 or track_area.collidepoint(event.pos):
                self.is_dragging = True
                new_val = self._x_to_val(event.pos[0])
                if new_val != self.value:
                    self.value = new_val
                    if self.on_change:
                        self.on_change(self.value)
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                return True

        return False

    def draw(self, surface: pygame.Surface):
        fm = FontManager.get()

        # Label
        lbl_surf = fm.font_body.render(self.label, True, TEXT_PRIMARY)
        surface.blit(lbl_surf, (self.rect.x + int(16 * self.scale), self.rect.y + int(8 * self.scale)))

        # Value Badge Pill
        val_str = f"{self.value} characters"
        badge_surf = fm.font_small_bold.render(val_str, True, ACCENT_BLUE)
        badge_w = badge_surf.get_width() + int(16 * self.scale)
        badge_h = int(22 * self.scale)
        badge_rect = pygame.Rect(self.rect.right - badge_w - int(16 * self.scale), self.rect.y + int(6 * self.scale), badge_w, badge_h)
        pygame.draw.rect(surface, CARD_SURFACE, badge_rect, border_radius=badge_h // 2)
        surface.blit(badge_surf, (badge_rect.x + int(8 * self.scale), badge_rect.centery - badge_surf.get_height() // 2))

        # Unfilled track
        track_rect = pygame.Rect(self.track_x, self.track_y - self.track_h // 2, self.track_w, self.track_h)
        pygame.draw.rect(surface, BORDER_COLOR, track_rect, border_radius=self.track_h // 2)

        # Filled track
        knob_x = self._val_to_x()
        fill_w = max(0, knob_x - self.track_x)
        fill_rect = pygame.Rect(self.track_x, self.track_y - self.track_h // 2, fill_w, self.track_h)
        pygame.draw.rect(surface, ACCENT_BLUE, fill_rect, border_radius=self.track_h // 2)

        # Draggable Knob
        knob_col = (255, 255, 255) if (self.is_dragging or self.is_hovered) else (230, 235, 245)
        pygame.draw.circle(surface, ACCENT_BLUE, (knob_x, self.track_y), self.knob_r + 2)
        pygame.draw.circle(surface, knob_col, (knob_x, self.track_y), self.knob_r)


class StrengthMeter:
    """Visual multi-segment gauge displaying password entropy and score."""

    def __init__(self, rect: pygame.Rect, scale: float = 1.0):
        self.rect = pygame.Rect(rect)
        self.scale = scale
        self.score: int = 0
        self.label: str = "None"
        self.color: Tuple[int, int, int] = (100, 100, 110)
        self.anim_score: float = 0.0

    def set_strength(self, score: int, label: str, color: Tuple[int, int, int], immediate: bool = False):
        self.score = score
        self.label = label
        self.color = color
        if immediate:
            self.anim_score = float(score)

    def update(self, dt: float):
        speed = 150.0 * dt
        if self.anim_score < self.score:
            self.anim_score = min(float(self.score), self.anim_score + speed)
        elif self.anim_score > self.score:
            self.anim_score = max(float(self.score), self.anim_score - speed)

    def draw(self, surface: pygame.Surface):
        fm = FontManager.get()

        lbl_surf = fm.font_small_bold.render("PASSWORD STRENGTH", True, TEXT_MUTED)
        surface.blit(lbl_surf, (self.rect.x, self.rect.y))

        status_text = f"{self.label} ({int(self.anim_score)}%)"
        status_surf = fm.font_small_bold.render(status_text, True, self.color)
        surface.blit(status_surf, (self.rect.right - status_surf.get_width(), self.rect.y))

        bar_y = self.rect.y + int(20 * self.scale)
        total_segments = 4
        spacing = int(6 * self.scale)
        seg_w = (self.rect.width - (total_segments - 1) * spacing) // total_segments
        seg_h = max(5, int(7 * self.scale))

        active_segments = 0
        if self.anim_score >= 10:
            active_segments = 1
        if self.anim_score >= 35:
            active_segments = 2
        if self.anim_score >= 65:
            active_segments = 3
        if self.anim_score >= 85:
            active_segments = 4

        for i in range(total_segments):
            x = self.rect.x + i * (seg_w + spacing)
            seg_rect = pygame.Rect(x, bar_y, seg_w, seg_h)
            seg_color = self.color if i < active_segments else CARD_SURFACE
            pygame.draw.rect(surface, seg_color, seg_rect, border_radius=3)


class ToastNotification:
    """Floating banner for brief user confirmations with vector checkmark."""

    def __init__(self, screen_w: int, scale: float = 1.0):
        self.screen_w = screen_w
        self.scale = scale
        self.message = ""
        self.timer = 0.0
        self.duration = 2.2
        self.alpha = 0

    def show(self, message: str):
        self.message = message
        self.timer = self.duration

    def update(self, dt: float):
        if self.timer > 0:
            self.timer -= dt
            if self.timer > self.duration - 0.2:
                self.alpha = min(255, int(255 * (self.duration - self.timer) / 0.2))
            elif self.timer < 0.4:
                self.alpha = max(0, int(255 * (self.timer / 0.4)))
            else:
                self.alpha = 255
        else:
            self.alpha = 0

    def draw(self, surface: pygame.Surface):
        if self.alpha <= 0 or not self.message:
            return

        fm = FontManager.get()
        text_surf = fm.font_body_bold.render(self.message, True, TEXT_DARK)

        pad_x = int(22 * self.scale)
        pad_y = int(10 * self.scale)
        icon_size = int(16 * self.scale)
        spacing = int(10 * self.scale)

        toast_w = icon_size + spacing + text_surf.get_width() + pad_x * 2
        toast_h = max(icon_size, text_surf.get_height()) + pad_y * 2
        toast_x = (self.screen_w - toast_w) // 2
        toast_y = int(20 * self.scale)

        toast_surf = pygame.Surface((toast_w, toast_h), pygame.SRCALPHA)
        bg_col = (*ACCENT_GREEN, self.alpha)
        pygame.draw.rect(toast_surf, bg_col, (0, 0, toast_w, toast_h), border_radius=toast_h // 2)

        # Draw checkmark
        check_cx = pad_x + icon_size // 2
        check_cy = toast_h // 2
        draw_check_icon(toast_surf, check_cx, check_cy, icon_size, TEXT_DARK)

        text_surf.set_alpha(self.alpha)
        toast_surf.blit(text_surf, (pad_x + icon_size + spacing, toast_h // 2 - text_surf.get_height() // 2))

        surface.blit(toast_surf, (toast_x, toast_y))


class HistoryPanel:
    """Panel showing recent passwords with one-click copy buttons and vector icons."""

    def __init__(self, rect: pygame.Rect, on_copy_item: Callable[[str], None], scale: float = 1.0):
        self.rect = pygame.Rect(rect)
        self.history: List[str] = []
        self.max_items = 4
        self.on_copy_item = on_copy_item
        self.scale = scale
        self.hovered_idx = -1

    def add_password(self, password: str):
        if not password:
            return
        if self.history and self.history[0] == password:
            return
        self.history.insert(0, password)
        if len(self.history) > self.max_items:
            self.history.pop()

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.history:
            return False

        item_h = int(32 * self.scale)
        start_y = self.rect.y + int(42 * self.scale)
        pad = int(12 * self.scale)

        if event.type == pygame.MOUSEMOTION:
            self.hovered_idx = -1
            for i in range(len(self.history)):
                item_rect = pygame.Rect(self.rect.x + pad, start_y + i * (item_h + int(6 * self.scale)), self.rect.width - pad * 2, item_h)
                if item_rect.collidepoint(event.pos):
                    self.hovered_idx = i
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, pwd in enumerate(self.history):
                item_rect = pygame.Rect(self.rect.x + pad, start_y + i * (item_h + int(6 * self.scale)), self.rect.width - pad * 2, item_h)
                if item_rect.collidepoint(event.pos):
                    self.on_copy_item(pwd)
                    return True
        return False

    def draw(self, surface: pygame.Surface):
        fm = FontManager.get()

        draw_rounded_card(surface, self.rect, bg_color=CARD_BG, border_color=BORDER_COLOR, radius=int(12 * self.scale))

        # Title
        title_surf = fm.font_body_bold.render("Recent Passwords", True, TEXT_PRIMARY)
        surface.blit(title_surf, (self.rect.x + int(16 * self.scale), self.rect.y + int(14 * self.scale)))

        if not self.history:
            empty_surf = fm.font_small.render("Generated passwords will appear here for quick access.", True, TEXT_MUTED)
            surface.blit(empty_surf, (self.rect.x + int(16 * self.scale), self.rect.y + int(48 * self.scale)))
            return

        item_h = int(32 * self.scale)
        start_y = self.rect.y + int(42 * self.scale)
        pad = int(12 * self.scale)

        for i, pwd in enumerate(self.history):
            item_rect = pygame.Rect(self.rect.x + pad, start_y + i * (item_h + int(6 * self.scale)), self.rect.width - pad * 2, item_h)

            row_bg = CARD_SURFACE if i == self.hovered_idx else CARD_BG
            pygame.draw.rect(surface, row_bg, item_rect, border_radius=int(6 * self.scale))
            pygame.draw.rect(surface, BORDER_COLOR, item_rect, width=1, border_radius=int(6 * self.scale))

            display_pwd = pwd if len(pwd) <= 26 else pwd[:24] + "..."
            pwd_surf = fm.font_mono_small.render(display_pwd, True, TEXT_SECONDARY)
            surface.blit(pwd_surf, (item_rect.x + int(10 * self.scale), item_rect.centery - pwd_surf.get_height() // 2))

            # Right side: copy button & text
            copy_text = "Click to copy" if i == self.hovered_idx else "Copy"
            copy_col = ACCENT_BLUE if i == self.hovered_idx else TEXT_MUTED
            copy_surf = fm.font_small.render(copy_text, True, copy_col)

            # Draw small vector copy icon
            icon_s = int(12 * self.scale)
            icon_cx = item_rect.right - copy_surf.get_width() - icon_s - int(14 * self.scale)
            icon_cy = item_rect.centery
            draw_copy_icon(surface, icon_cx, icon_cy, icon_s, copy_col, bg_color=row_bg)

            surface.blit(copy_surf, (item_rect.right - copy_surf.get_width() - int(10 * self.scale), item_rect.centery - copy_surf.get_height() // 2))
