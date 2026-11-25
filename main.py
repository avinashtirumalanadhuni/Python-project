"""
VaultPass - Modern Dark-Mode Password Generator
Powered by Pygame for UI and Tkinter for clipboard operations.
Includes native Windows high-DPI scaling and procedural vector icons.
"""

import ctypes
import sys
import pygame
from clipboard_helper import copy_to_clipboard
from generator import evaluate_strength, generate_password
from sound import SoundEngine
from ui import (
    ACCENT_BLUE,
    ACCENT_GREEN,
    BORDER_COLOR,
    CARD_BG,
    CARD_SURFACE,
    TEXT_DARK,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    Button,
    FontManager,
    HistoryPanel,
    Slider,
    StrengthMeter,
    ToastNotification,
    ToggleSwitch,
    draw_lock_icon,
    draw_rounded_card,
)

BASE_WIDTH = 840
BASE_HEIGHT = 740
FPS = 60


def init_windows_dpi() -> float:
    """Enables Windows process DPI awareness and returns the monitor scale factor."""
    scale = 1.0
    if sys.platform == "win32":
        try:
            # Per-monitor DPI aware (Windows 8.1 / 10 / 11)
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

        try:
            hdc = ctypes.windll.user32.GetDC(0)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
            ctypes.windll.user32.ReleaseDC(0, hdc)
            scale = dpi / 96.0
        except Exception:
            scale = 1.0
    return max(1.0, scale)


class PasswordApp:
    def __init__(self):
        self.scale = init_windows_dpi()
        pygame.init()
        pygame.display.set_caption("VaultPass - Password Generator")

        self.width = self.S(BASE_WIDTH)
        self.height = self.S(BASE_HEIGHT)
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = True

        self.font_mgr = FontManager.get(scale=self.scale)
        self.sound = SoundEngine()
        self.toast = ToastNotification(self.width, scale=self.scale)

        # Generator settings
        self.length = 16
        self.use_upper = True
        self.use_lower = True
        self.use_digits = True
        self.use_symbols = True
        self.exclude_ambiguous = False

        self.current_password = ""
        self.strength_score = 0
        self.strength_label = ""
        self.strength_color = (100, 100, 110)

        # Build UI
        self._init_ui()

        # Generate initial password
        self.do_generate(record_history=False)

    def S(self, val: int) -> int:
        """Scales a layout pixel value by the monitor DPI scale."""
        return int(round(val * self.scale))

    def _init_ui(self):
        # 1. Top bar mute button
        self.btn_mute = Button(
            rect=pygame.Rect(self.width - self.S(145), self.S(18), self.S(125), self.S(34)),
            text="Sound: On",
            icon="sound_on",
            on_click=self.on_mute_clicked,
            bg_color=CARD_BG,
            hover_color=CARD_SURFACE,
            text_color=TEXT_SECONDARY,
            font=self.font_mgr.font_small_bold,
            border_radius=self.S(8),
            scale=self.scale,
        )

        # 2. Main Password Card Action Buttons
        pwd_box_y = self.S(70)
        pwd_box_h = self.S(138)
        self.pwd_card_rect = pygame.Rect(self.S(20), pwd_box_y, self.width - self.S(40), pwd_box_h)

        btn_h = self.S(42)
        btn_y = pwd_box_y + self.S(16)
        btn_gen_w = self.S(130)
        btn_copy_w = self.S(110)

        self.btn_generate = Button(
            rect=pygame.Rect(self.pwd_card_rect.right - btn_gen_w - self.S(16), btn_y, btn_gen_w, btn_h),
            text="Generate",
            icon="refresh",
            on_click=self.on_generate_clicked,
            bg_color=ACCENT_BLUE,
            text_color=TEXT_DARK,
            border_radius=self.S(8),
            scale=self.scale,
        )

        self.btn_copy = Button(
            rect=pygame.Rect(self.btn_generate.rect.left - btn_copy_w - self.S(12), btn_y, btn_copy_w, btn_h),
            text="Copy",
            icon="copy",
            on_click=self.on_copy_clicked,
            bg_color=ACCENT_GREEN,
            text_color=TEXT_DARK,
            border_radius=self.S(8),
            scale=self.scale,
        )

        # 3. Password Strength Bar (inside password card)
        meter_y = pwd_box_y + self.S(76)
        self.strength_meter = StrengthMeter(
            rect=pygame.Rect(self.pwd_card_rect.x + self.S(20), meter_y, self.pwd_card_rect.width - self.S(40), self.S(36)),
            scale=self.scale,
        )

        # 4. Settings Card
        settings_y = pwd_box_y + pwd_box_h + self.S(16)
        settings_h = self.S(246)
        self.settings_rect = pygame.Rect(self.S(20), settings_y, self.width - self.S(40), settings_h)

        # Length Slider
        self.slider_length = Slider(
            rect=pygame.Rect(self.settings_rect.x + self.S(8), self.settings_rect.y + self.S(12), self.settings_rect.width - self.S(16), self.S(52)),
            min_val=6,
            max_val=64,
            value=self.length,
            label="Password Length",
            on_change=self.on_length_changed,
            scale=self.scale,
        )

        # Character toggles grid (2 columns)
        toggle_w = (self.settings_rect.width - self.S(48)) // 2
        toggle_h = self.S(44)
        col1_x = self.settings_rect.x + self.S(16)
        col2_x = col1_x + toggle_w + self.S(16)

        row1_y = self.settings_rect.y + self.S(80)
        row2_y = row1_y + toggle_h + self.S(6)
        row3_y = row2_y + toggle_h + self.S(6)

        self.toggle_upper = ToggleSwitch(
            col1_x, row1_y, toggle_w, toggle_h,
            label="Uppercase Letters", hint="A - Z",
            checked=self.use_upper,
            on_toggle=lambda val: self.on_toggle_option("upper", val),
            scale=self.scale,
        )
        self.toggle_lower = ToggleSwitch(
            col2_x, row1_y, toggle_w, toggle_h,
            label="Lowercase Letters", hint="a - z",
            checked=self.use_lower,
            on_toggle=lambda val: self.on_toggle_option("lower", val),
            scale=self.scale,
        )

        self.toggle_digits = ToggleSwitch(
            col1_x, row2_y, toggle_w, toggle_h,
            label="Numbers", hint="0 - 9",
            checked=self.use_digits,
            on_toggle=lambda val: self.on_toggle_option("digits", val),
            scale=self.scale,
        )
        self.toggle_symbols = ToggleSwitch(
            col2_x, row2_y, toggle_w, toggle_h,
            label="Special Symbols", hint="!@#$%^&*()_+-=",
            checked=self.use_symbols,
            on_toggle=lambda val: self.on_toggle_option("symbols", val),
            scale=self.scale,
        )

        self.toggle_ambiguous = ToggleSwitch(
            col1_x, row3_y, self.settings_rect.width - self.S(32), toggle_h,
            label="Exclude Ambiguous Characters",
            hint="Avoid confusing glyphs like 0, O, 1, l, I, |",
            checked=self.exclude_ambiguous,
            on_toggle=lambda val: self.on_toggle_option("ambiguous", val),
            scale=self.scale,
        )

        # 5. History Panel
        hist_y = settings_y + settings_h + self.S(16)
        hist_h = self.height - hist_y - self.S(34)
        self.history_panel = HistoryPanel(
            rect=pygame.Rect(self.S(20), hist_y, self.width - self.S(40), hist_h),
            on_copy_item=self.on_copy_history_item,
            scale=self.scale,
        )

    # ---------------- UI Callbacks ----------------
    def on_mute_clicked(self):
        is_muted = self.sound.toggle_mute()
        self.btn_mute.text = "Sound: Off" if is_muted else "Sound: On"
        self.btn_mute.icon = "sound_off" if is_muted else "sound_on"
        if not is_muted:
            self.sound.play_click()

    def on_length_changed(self, new_val: int):
        self.length = new_val
        self.sound.play_click()
        self.do_generate(record_history=False)

    def on_toggle_option(self, option_name: str, value: bool):
        if option_name == "upper":
            self.use_upper = value
        elif option_name == "lower":
            self.use_lower = value
        elif option_name == "digits":
            self.use_digits = value
        elif option_name == "symbols":
            self.use_symbols = value
        elif option_name == "ambiguous":
            self.exclude_ambiguous = value

        # Keep at least one character class enabled
        if not any([self.use_upper, self.use_lower, self.use_digits, self.use_symbols]):
            if option_name == "lower":
                self.use_upper = True
                self.toggle_upper.checked = True
            else:
                self.use_lower = True
                self.toggle_lower.checked = True

        self.sound.play_toggle()
        self.do_generate(record_history=False)

    def on_generate_clicked(self):
        self.sound.play_generate()
        self.do_generate(record_history=True)

    def on_copy_clicked(self):
        if not self.current_password:
            return
        success = copy_to_clipboard(self.current_password)
        if success:
            self.sound.play_chime()
            self.toast.show("Password copied to clipboard!")
        else:
            self.toast.show("Failed to copy password")

    def on_copy_history_item(self, password: str):
        success = copy_to_clipboard(password)
        if success:
            self.sound.play_chime()
            self.toast.show("Copied from history to clipboard!")

    def do_generate(self, record_history: bool = True):
        if record_history and self.current_password:
            self.history_panel.add_password(self.current_password)

        self.current_password = generate_password(
            length=self.length,
            use_upper=self.use_upper,
            use_lower=self.use_lower,
            use_digits=self.use_digits,
            use_symbols=self.use_symbols,
            exclude_ambiguous=self.exclude_ambiguous,
        )

        score, label, color = evaluate_strength(self.current_password)
        self.strength_score = score
        self.strength_label = label
        self.strength_color = color
        self.strength_meter.set_strength(score, label, color, immediate=(not record_history))

    # ---------------- Application Loop ----------------
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.on_generate_clicked()
                    elif event.key == pygame.K_c and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        self.on_copy_clicked()
                    elif event.key == pygame.K_m:
                        self.on_mute_clicked()

                # Dispatch events
                self.btn_mute.handle_event(event)
                self.btn_generate.handle_event(event)
                self.btn_copy.handle_event(event)
                self.slider_length.handle_event(event)
                self.toggle_upper.handle_event(event)
                self.toggle_lower.handle_event(event)
                self.toggle_digits.handle_event(event)
                self.toggle_symbols.handle_event(event)
                self.toggle_ambiguous.handle_event(event)
                self.history_panel.handle_event(event)

            # Update animated components
            self.toggle_upper.update(dt)
            self.toggle_lower.update(dt)
            self.toggle_digits.update(dt)
            self.toggle_symbols.update(dt)
            self.toggle_ambiguous.update(dt)
            self.strength_meter.update(dt)
            self.toast.update(dt)

            self.draw()

        pygame.quit()
        sys.exit(0)

    def draw(self):
        from ui import BG_COLOR
        self.screen.fill(BG_COLOR)

        # Header with vector padlock icon
        lock_size = self.S(22)
        lock_cx = self.S(34)
        lock_cy = self.S(30)
        draw_lock_icon(self.screen, lock_cx, lock_cy, lock_size, ACCENT_BLUE, bg_color=BG_COLOR)

        title_surf = self.font_mgr.font_title.render("VaultPass", True, TEXT_PRIMARY)
        self.screen.blit(title_surf, (lock_cx + lock_size // 2 + self.S(10), self.S(16)))

        sub_surf = self.font_mgr.font_subtitle.render("Pygame & Tkinter Password Generator", True, TEXT_MUTED)
        self.screen.blit(sub_surf, (lock_cx + lock_size // 2 + self.S(10), self.S(44)))

        # Top Right Mute Button
        self.btn_mute.draw(self.screen)

        # 1. Password Display Card
        draw_rounded_card(self.screen, self.pwd_card_rect, bg_color=CARD_BG, border_color=BORDER_COLOR, radius=self.S(12))

        # Password Box
        avail_w = self.btn_copy.rect.left - (self.pwd_card_rect.x + self.S(20)) - self.S(12)
        pwd_box_rect = pygame.Rect(self.pwd_card_rect.x + self.S(16), self.pwd_card_rect.y + self.S(16), avail_w, self.S(44))
        pygame.draw.rect(self.screen, CARD_SURFACE, pwd_box_rect, border_radius=self.S(8))
        pygame.draw.rect(self.screen, BORDER_COLOR, pwd_box_rect, width=1, border_radius=self.S(8))

        # Render Password text with dynamic font sizing
        pwd_font = self.font_mgr.font_mono if len(self.current_password) <= 30 else self.font_mgr.font_mono_small
        rendered_pwd = pwd_font.render(self.current_password, True, TEXT_PRIMARY)
        self.screen.blit(rendered_pwd, (pwd_box_rect.x + self.S(12), pwd_box_rect.centery - rendered_pwd.get_height() // 2))

        # Action Buttons
        self.btn_copy.draw(self.screen)
        self.btn_generate.draw(self.screen)

        # Strength Meter
        self.strength_meter.draw(self.screen)

        # 2. Settings Card
        draw_rounded_card(self.screen, self.settings_rect, bg_color=CARD_BG, border_color=BORDER_COLOR, radius=self.S(12))
        self.slider_length.draw(self.screen)
        self.toggle_upper.draw(self.screen)
        self.toggle_lower.draw(self.screen)
        self.toggle_digits.draw(self.screen)
        self.toggle_symbols.draw(self.screen)
        self.toggle_ambiguous.draw(self.screen)

        # 3. History Panel
        self.history_panel.draw(self.screen)

        # 4. Keyboard Shortcuts Footer
        shortcuts_text = "Hotkeys:  [Space / Enter] Generate   |   [Ctrl+C] Copy   |   [M] Mute"
        shortcuts_surf = self.font_mgr.font_small.render(shortcuts_text, True, TEXT_MUTED)
        shortcuts_x = (self.width - shortcuts_surf.get_width()) // 2
        self.screen.blit(shortcuts_surf, (shortcuts_x, self.height - self.S(22)))

        # 5. Toast Notification
        self.toast.draw(self.screen)

        pygame.display.flip()


if __name__ == "__main__":
    app = PasswordApp()
    app.run()
