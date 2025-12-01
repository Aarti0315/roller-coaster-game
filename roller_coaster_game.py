import pygame
import sys
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)  # KE - more vibrant
BLUE = (50, 100, 220)  # PE - more vibrant
GREEN = (50, 180, 50)  # TE - more vibrant
GRAY = (200, 200, 200)
LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (100, 100, 100)
ORANGE = (255, 140, 0)
PURPLE = (148, 0, 211)

# Enhanced UI Colors
UI_PRIMARY = (64, 123, 255)
UI_SUCCESS = (76, 175, 80)
UI_WARNING = (255, 152, 0)
UI_ERROR = (244, 67, 54)
UI_SURFACE = (250, 250, 250)
UI_CARD = (255, 255, 255)
UI_SHADOW = (0, 0, 0, 30)
UI_TEXT_PRIMARY = (33, 37, 41)
UI_TEXT_SECONDARY = (108, 117, 125)
UI_ACCENT = (156, 39, 176)

g = 9.81  # more precise gravity value

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎢 Roller Coaster Physics Simulator - Interactive Learning Tool")
font = pygame.font.SysFont("Segoe UI", 18)
title_font = pygame.font.SysFont("Segoe UI", 28, bold=True)
small_font = pygame.font.SysFont("Segoe UI", 14)
large_font = pygame.font.SysFont("Segoe UI", 24, bold=True)

# Simulation variables
mass = 50.0
initial_velocity = 8.0
current_velocity = initial_velocity
paused = True
speed_factor = 0.03
show_vectors = False
show_grid = True


# Create a more interesting track with multiple hills and loops
def create_track():
    points = []
    for x in range(0, WIDTH - 100, 3):
        # Multiple sine waves for varied terrain
        y1 = 80 * math.sin(x / 150)
        y2 = 40 * math.sin(x / 80 + math.pi / 4)
        y3 = 20 * math.sin(x / 200 + math.pi)
        y = int(HEIGHT / 2 + y1 + y2 + y3)
        # Ensure track stays within bounds
        y = max(100, min(HEIGHT - 150, y))
        points.append((x + 50, y))
    return points


track_points = create_track()
cart_pos = 0.0


# Helper function to draw rounded rectangles
def draw_rounded_rect(surface, color, rect, radius=10, shadow=False):
    if shadow:
        shadow_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.width, rect.height)
        shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, UI_SHADOW, (0, 0, rect.width, rect.height), border_radius=radius)
        surface.blit(shadow_surf, shadow_rect)

    pygame.draw.rect(surface, color, rect, border_radius=radius)


# Input validation and formatting
def validate_float_input(text, min_val=0.1, max_val=1000):
    try:
        value = float(text)
        return max(min_val, min(max_val, value))
    except:
        return None


# Enhanced UI elements with modern design
class ModernInputBox:
    def __init__(self, x, y, w, h, label, initial_value, min_val=0.1, max_val=1000, unit=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.text = str(initial_value)
        self.active = False
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit
        self.hover = False
        self.focus_animation = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            was_active = self.active
            self.active = self.rect.collidepoint(event.pos)
            if self.active and not was_active:
                self.focus_animation = 0

        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                value = validate_float_input(self.text, self.min_val, self.max_val)
                if value is not None:
                    self.text = f"{value:.1f}"
                self.active = False
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.unicode.replace('.', '').replace('-', '').isdigit() or event.unicode == '.':
                    if len(self.text) < 8:
                        self.text += event.unicode
        return False

    def update(self):
        if self.active and self.focus_animation < 10:
            self.focus_animation += 1
        elif not self.active and self.focus_animation > 0:
            self.focus_animation -= 1

    def draw(self, surface):
        self.update()

        # Draw shadow
        draw_rounded_rect(surface, UI_CARD, self.rect, 8, shadow=True)

        # Draw main input box
        border_color = UI_PRIMARY if self.active else (LIGHT_GRAY if self.hover else GRAY)
        draw_rounded_rect(surface, UI_CARD, self.rect, 8)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)

        # Animated focus indicator
        if self.focus_animation > 0:
            focus_intensity = self.focus_animation / 10.0
            focus_color = (*UI_PRIMARY, int(50 * focus_intensity))
            focus_surf = pygame.Surface((self.rect.width + 4, self.rect.height + 4), pygame.SRCALPHA)
            pygame.draw.rect(focus_surf, focus_color, (0, 0, self.rect.width + 4, self.rect.height + 4),
                             border_radius=10)
            surface.blit(focus_surf, (self.rect.x - 2, self.rect.y - 2))

        # Draw label
        label_color = UI_PRIMARY if self.active else UI_TEXT_SECONDARY
        label_surf = small_font.render(self.label, True, label_color)
        surface.blit(label_surf, (self.rect.x, self.rect.y - 22))

        # Draw text with unit
        display_text = f"{self.text} {self.unit}".strip()
        text_color = UI_TEXT_PRIMARY if self.text else UI_TEXT_SECONDARY
        text_surf = font.render(display_text, True, text_color)
        text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.centery))
        surface.blit(text_surf, text_rect)

        # Draw cursor if active
        if self.active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = text_rect.right - len(self.unit) * 8 if self.unit else text_rect.right
            pygame.draw.line(surface, UI_PRIMARY,
                             (cursor_x + 2, self.rect.centery - 8),
                             (cursor_x + 2, self.rect.centery + 8), 2)

    def get_value(self):
        value = validate_float_input(self.text, self.min_val, self.max_val)
        return value if value is not None else float(self.text) if self.text else 0.1


class ModernSlider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, label, format_string="{:.3f}"):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.dragging = False
        self.hover = False
        self.format_string = format_string

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_value(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
            if self.dragging:
                self.update_value(event.pos[0])

    def update_value(self, mouse_x):
        relative_x = mouse_x - self.rect.x
        relative_x = max(0, min(self.rect.width, relative_x))
        self.val = self.min_val + (relative_x / self.rect.width) * (self.max_val - self.min_val)

    def draw(self, surface):
        # Draw label with value
        label_text = f"{self.label}: {self.format_string.format(self.val)}"
        label_surf = small_font.render(label_text, True, UI_TEXT_PRIMARY)
        surface.blit(label_surf, (self.rect.x, self.rect.y - 22))

        # Draw track shadow
        track_shadow = pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.width, self.rect.height)
        draw_rounded_rect(surface, UI_SHADOW, track_shadow, self.rect.height // 2)

        # Draw slider track
        draw_rounded_rect(surface, LIGHT_GRAY, self.rect, self.rect.height // 2)

        # Draw active track (filled portion)
        filled_width = int((self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        if filled_width > 0:
            filled_rect = pygame.Rect(self.rect.x, self.rect.y, filled_width, self.rect.height)
            draw_rounded_rect(surface, UI_PRIMARY, filled_rect, self.rect.height // 2)

        # Draw slider handle
        handle_x = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        handle_size = 20 if self.hover or self.dragging else 16
        handle_rect = pygame.Rect(handle_x - handle_size // 2, self.rect.centery - handle_size // 2, handle_size,
                                  handle_size)

        # Handle shadow
        shadow_rect = pygame.Rect(handle_rect.x + 2, handle_rect.y + 2, handle_rect.width, handle_rect.height)
        draw_rounded_rect(surface, UI_SHADOW, shadow_rect, handle_size // 2)

        # Handle
        draw_rounded_rect(surface, WHITE, handle_rect, handle_size // 2)
        pygame.draw.rect(surface, UI_PRIMARY, handle_rect, 2, border_radius=handle_size // 2)


class ModernButton:
    def __init__(self, x, y, w, h, text, style="primary", icon=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.icon = icon
        self.hover = False
        self.pressed = False
        self.style = style
        self.hover_scale = 1.0

        # Style colors
        self.colors = {
            "primary": {"bg": UI_PRIMARY, "text": WHITE, "hover": (44, 103, 235)},
            "success": {"bg": UI_SUCCESS, "text": WHITE, "hover": (56, 155, 60)},
            "warning": {"bg": UI_WARNING, "text": WHITE, "hover": (235, 132, 0)},
            "danger": {"bg": UI_ERROR, "text": WHITE, "hover": (224, 47, 34)},
            "secondary": {"bg": LIGHT_GRAY, "text": UI_TEXT_PRIMARY, "hover": GRAY},
            "accent": {"bg": UI_ACCENT, "text": WHITE, "hover": (136, 19, 156)}
        }

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                return True
            self.pressed = False
        elif event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        return False

    def update(self):
        target_scale = 1.05 if self.hover else 1.0
        self.hover_scale += (target_scale - self.hover_scale) * 0.2

    def draw(self, surface):
        self.update()

        # Calculate scaled rect
        scale_offset = int((self.rect.width * (self.hover_scale - 1)) / 2)
        scaled_rect = pygame.Rect(
            self.rect.x - scale_offset,
            self.rect.y - scale_offset,
            self.rect.width + scale_offset * 2,
            self.rect.height + scale_offset * 2
        )

        # Draw shadow
        draw_rounded_rect(surface, UI_CARD, scaled_rect, 8, shadow=True)

        # Choose colors based on state and style
        color_set = self.colors.get(self.style, self.colors["primary"])
        bg_color = color_set["hover"] if self.hover else color_set["bg"]
        text_color = color_set["text"]

        # Draw button
        draw_rounded_rect(surface, bg_color, scaled_rect, 8)

        # Draw text with icon
        display_text = f"{self.icon} {self.text}".strip()
        text_surf = font.render(display_text, True, text_color)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# Create modern UI elements
mass_input = ModernInputBox(920, 80, 140, 40, "Mass", mass, 1, 200, "kg")
velocity_input = ModernInputBox(920, 150, 140, 40, "Initial Velocity", initial_velocity, 0.1, 20, "m/s")
speed_slider = ModernSlider(50, 550, 350, 20, 0.005, 0.1, speed_factor, "Animation Speed")

# Create modern buttons
start_btn = ModernButton(750, 580, 80, 45, "Start", "success", "▶")
pause_btn = ModernButton(840, 580, 80, 45, "Pause", "warning", "⏸")
reset_btn = ModernButton(930, 580, 80, 45, "Reset", "danger", "🔄")
menu_btn = ModernButton(1020, 580, 100, 45, "Menu", "secondary", "📋")
vectors_btn = ModernButton(920, 240, 140, 35, "Vectors", "secondary", "🎯")
grid_btn = ModernButton(920, 285, 140, 35, "Grid", "secondary", "⚏")

# Menu buttons
menu_start_btn = ModernButton(WIDTH // 2 - 150, 250, 300, 60, "Start Simulation", "success", "🎢")
menu_explain_btn = ModernButton(WIDTH // 2 - 150, 330, 300, 60, "Physics Guide", "primary", "📚")
menu_exit_btn = ModernButton(WIDTH // 2 - 150, 410, 300, 60, "Exit", "danger", "❌")


# Energy calculation and tracking
def calculate_energies(cart_x, cart_y, velocity):
    height = HEIGHT - cart_y
    PE = mass * g * (height / 50)  # Scale factor for reasonable values
    KE = 0.5 * mass * velocity * velocity
    return KE, PE, KE + PE


def reset_simulation():
    global cart_pos, current_velocity, paused, graph_data_KE, graph_data_PE, graph_data_TE, E_total
    cart_pos = 0.0
    current_velocity = velocity_input.get_value()
    paused = True

    # Calculate initial total energy
    x0, y0 = track_points[0]
    _, PE0, _ = calculate_energies(x0, y0, current_velocity)
    KE0 = 0.5 * mass * current_velocity * current_velocity
    E_total = KE0 + PE0

    # Clear graph data
    graph_data_KE.clear()
    graph_data_PE.clear()
    graph_data_TE.clear()


# Graph data storage
graph_data_KE = []
graph_data_PE = []
graph_data_TE = []
max_graph_points = 300
E_total = 0

# States
current_state = "menu"  # "menu", "simulation", "explanation"


def draw_grid():
    if not show_grid:
        return

    # Softer grid lines
    for x in range(0, WIDTH, 50):
        pygame.draw.line(screen, (240, 240, 240), (x, 0), (x, HEIGHT), 1)

    for y in range(0, HEIGHT, 50):
        pygame.draw.line(screen, (240, 240, 240), (0, y), (WIDTH, y), 1)


def draw_text(text, x, y, color=UI_TEXT_PRIMARY, font_obj=font, center=False):
    surface = font_obj.render(text, True, color)
    if center:
        rect = surface.get_rect(center=(x, y))
        screen.blit(surface, rect)
    else:
        screen.blit(surface, (x, y))


def show_menu():
    # Gradient background
    for y in range(HEIGHT):
        color_factor = y / HEIGHT
        r = int(245 + color_factor * 10)
        g = int(245 + color_factor * 10)
        b = int(250 + color_factor * 5)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    # Main title card
    title_card = pygame.Rect(WIDTH // 2 - 300, 80, 600, 120)
    draw_rounded_rect(screen, UI_CARD, title_card, 15, shadow=True)

    # Title
    draw_text("🎢 Roller Coaster Physics", WIDTH // 2, 130, UI_PRIMARY, large_font, True)
    draw_text("Interactive Energy Conservation Simulator", WIDTH // 2, 160, UI_TEXT_SECONDARY, font, True)

    # Menu buttons
    menu_start_btn.draw(screen)
    menu_explain_btn.draw(screen)
    menu_exit_btn.draw(screen)

    # Feature highlights
    features = [
        "🔴 Real-time Kinetic Energy tracking",
        "🔵 Potential Energy visualization",
        "📊 Interactive energy graphs",
        "🎯 Physics vector display"
    ]

    feature_y = 520
    for i, feature in enumerate(features):
        x_pos = WIDTH // 2 - 200 + (i % 2) * 200
        y_pos = feature_y + (i // 2) * 25
        draw_text(feature, x_pos, y_pos, UI_TEXT_SECONDARY, small_font)


def show_explanation():
    # Gradient background
    for y in range(HEIGHT):
        color_factor = y / HEIGHT
        r = int(250 + color_factor * 5)
        g = int(250 + color_factor * 5)
        b = int(255)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    # Main content card
    content_card = pygame.Rect(50, 50, WIDTH - 100, HEIGHT - 120)
    draw_rounded_rect(screen, UI_CARD, content_card, 15, shadow=True)

    draw_text("📚 Physics Concepts Guide", WIDTH // 2, 80, UI_PRIMARY, title_font, True)

    # Organized sections
    sections = [
        {
            "title": "🔴 Kinetic Energy (KE)",
            "formula": "KE = ½mv²",
            "points": ["Energy of motion", "Increases with speed", "Higher when going downhill"]
        },
        {
            "title": "🔵 Potential Energy (PE)",
            "formula": "PE = mgh",
            "points": ["Energy of position", "Increases with height", "Higher at peaks"]
        },
        {
            "title": "🟢 Energy Conservation",
            "formula": "Total Energy = KE + PE",
            "points": ["Total energy stays constant", "Energy transforms between KE and PE",
                       "No energy is lost or gained"]
        }
    ]

    y_pos = 130
    for section in sections:
        # Section header
        draw_text(section["title"], 80, y_pos, UI_TEXT_PRIMARY, font)
        draw_text(section["formula"], 350, y_pos, UI_ACCENT, font)
        y_pos += 30

        # Section points
        for point in section["points"]:
            draw_text(f"• {point}", 100, y_pos, UI_TEXT_SECONDARY, small_font)
            y_pos += 20
        y_pos += 15

    # Interactive tip
    tip_rect = pygame.Rect(80, HEIGHT - 100, WIDTH - 160, 40)
    draw_rounded_rect(screen, (230, 247, 255), tip_rect, 8)
    draw_text("💡 Tip: Watch the real-time graph to see energy transformation!",
              WIDTH // 2, tip_rect.centery, UI_PRIMARY, font, True)

    # Return instruction
    draw_text("Click anywhere to return to menu", WIDTH // 2, HEIGHT - 30, UI_TEXT_SECONDARY, small_font, True)


def draw_energy_graph():
    # Modern card design
    graph_card = pygame.Rect(30, 30, 340, 170)
    draw_rounded_rect(screen, UI_CARD, graph_card, 12, shadow=True)

    # Header
    draw_text("📊 Energy Analysis", 50, 40, UI_TEXT_PRIMARY, font)

    graph_rect = pygame.Rect(50, 70, 300, 130)
    pygame.draw.rect(screen, UI_SURFACE, graph_rect, border_radius=8)

    if len(graph_data_KE) < 2:
        draw_text("Simulation data will appear here", graph_rect.centerx, graph_rect.centery,
                  UI_TEXT_SECONDARY, small_font, True)
        return

    # Find max value for scaling
    all_data = graph_data_KE + graph_data_PE + graph_data_TE
    if not all_data:
        return

    max_val = max(all_data)
    if max_val <= 0:
        return

    scale_y = 120 / max_val
    scale_x = 290 / max_graph_points

    # Draw graph lines with smoother appearance
    for i in range(1, len(graph_data_KE)):
        # KE line (red)
        pygame.draw.line(screen, RED,
                         (55 + (i - 1) * scale_x, graph_rect.bottom - 10 - graph_data_KE[i - 1] * scale_y),
                         (55 + i * scale_x, graph_rect.bottom - 10 - graph_data_KE[i] * scale_y), 3)

        # PE line (blue)
        pygame.draw.line(screen, BLUE,
                         (55 + (i - 1) * scale_x, graph_rect.bottom - 10 - graph_data_PE[i - 1] * scale_y),
                         (55 + i * scale_x, graph_rect.bottom - 10 - graph_data_PE[i] * scale_y), 3)

        # TE line (green)
        pygame.draw.line(screen, GREEN,
                         (55 + (i - 1) * scale_x, graph_rect.bottom - 10 - graph_data_TE[i - 1] * scale_y),
                         (55 + i * scale_x, graph_rect.bottom - 10 - graph_data_TE[i] * scale_y), 3)

    # Modern legend with colored boxes
    legend_items = [("KE", RED), ("PE", BLUE), ("TE", GREEN)]
    legend_x = 55
    for label, color in legend_items:
        pygame.draw.rect(screen, color, (legend_x, 10, 12, 12), border_radius=2)
        draw_text(label, legend_x + 18, 6, UI_TEXT_PRIMARY, small_font)
        legend_x += 50


def draw_velocity_vectors(cart_x, cart_y, velocity):
    if not show_vectors or velocity <= 0:
        return

    # Calculate direction based on track slope
    idx = max(0, min(int(cart_pos), len(track_points) - 2))
    if idx < len(track_points) - 1:
        dx = track_points[idx + 1][0] - track_points[idx][0]
        dy = track_points[idx + 1][1] - track_points[idx][1]
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx, dy = dx / length, dy / length

        # Scale vector by velocity
        vector_length = velocity * 12
        end_x = cart_x + dx * vector_length
        end_y = cart_y + dy * vector_length

        # Enhanced vector with gradient
        pygame.draw.line(screen, ORANGE, (cart_x, cart_y), (end_x, end_y), 4)
        pygame.draw.circle(screen, (255, 200, 0), (int(end_x), int(end_y)), 6)
        pygame.draw.circle(screen, ORANGE, (int(end_x), int(end_y)), 6, 2)


def show_simulation():
    global cart_pos, current_velocity, paused, mass, E_total

    # Modern gradient background
    for y in range(HEIGHT):
        color_factor = y / HEIGHT
        r = int(248 + color_factor * 7)
        g = int(250 + color_factor * 5)
        b = int(252 + color_factor * 3)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    draw_grid()

    # Update mass from input
    mass = mass_input.get_value()
    speed_factor = speed_slider.val

    # Enhanced track drawing
    if len(track_points) > 1:
        # Track shadow
        shadow_points = [(x + 3, y + 3) for x, y in track_points]
        pygame.draw.lines(screen, (180, 180, 180), False, shadow_points, 10)
        # Main track
        pygame.draw.lines(screen, (60, 60, 60), False, track_points, 8)
        # Track highlights
        pygame.draw.lines(screen, (120, 120, 120), False, track_points, 4)

    # Get cart position and draw enhanced cart
    if track_points:
        idx = max(0, min(int(cart_pos), len(track_points) - 1))
        cart_x, cart_y = track_points[idx]

        # Calculate energies
        KE, PE, TE = calculate_energies(cart_x, cart_y, current_velocity)

        # Enhanced cart with modern styling
        cart_size = 22
        # Cart shadow
        pygame.draw.ellipse(screen, (100, 100, 100, 100),
                            (cart_x - cart_size // 2 + 3, cart_y - cart_size // 2 + 3, cart_size, cart_size))
        # Main cart
        pygame.draw.ellipse(screen, UI_ERROR, (cart_x - cart_size // 2, cart_y - cart_size // 2, cart_size, cart_size))
        # Cart highlight
        pygame.draw.ellipse(screen, (255, 200, 200),
                            (cart_x - cart_size // 2 + 2, cart_y - cart_size // 2 + 2, cart_size // 2, cart_size // 3))
        # Cart outline
        pygame.draw.ellipse(screen, BLACK, (cart_x - cart_size // 2, cart_y - cart_size // 2, cart_size, cart_size), 2)

        # Draw velocity vectors
        draw_velocity_vectors(cart_x, cart_y, current_velocity)

        # Modern energy display panel
        panel_rect = pygame.Rect(400, 20, 480, 140)
        draw_rounded_rect(screen, UI_CARD, panel_rect, 12, shadow=True)

        # Panel header
        draw_text("📊 Real-Time Energy Analysis", 420, 40, UI_PRIMARY, font)

        # Create a grid layout for data
        draw_text(f"Mass: {mass:.1f} kg", 420, 70, UI_TEXT_PRIMARY, font)
        draw_text(f"Velocity: {current_velocity:.2f} m/s", 420, 95, UI_TEXT_PRIMARY, font)

        # Energy values with color coding
        draw_text(f"🔴 Kinetic Energy: {KE:.1f} J", 620, 70, RED, font)
        draw_text(f"🔵 Potential Energy: {PE:.1f} J", 620, 95, BLUE, font)
        draw_text(f"🟢 Total Energy: {TE:.1f} J", 420, 120, GREEN, font)
        conservation_pct = (TE / E_total * 100) if E_total > 0 else 100
        conservation_color = UI_SUCCESS if conservation_pct > 98 else UI_WARNING
        draw_text(f"⚖️ Conservation: {conservation_pct:.1f}%", 620, 120, conservation_color, font)

    # Right panel for controls
    control_panel = pygame.Rect(900, 10, 280, 270)
    draw_rounded_rect(screen, UI_CARD, control_panel, 12, shadow=True)

    # Panel header
    draw_text("🎛️ Simulation Controls", 920, 30, UI_PRIMARY, font)

    # UI Elements with better spacing
    mass_input.draw(screen)
    velocity_input.draw(screen)
    # vectors_btn.draw(screen)
    # grid_btn.draw(screen)

    # Status indicator with modern design
    status_card = pygame.Rect(920, 210, 140, 60)
    status_color = UI_SUCCESS if not paused else UI_WARNING
    draw_rounded_rect(screen, status_color, status_card, 8)

    status_icon = "🟢" if not paused else "🟡"
    status_text = "RUNNING" if not paused else "PAUSED"
    draw_text(status_icon, status_card.centerx, status_card.centery - 8, WHITE, font, True)
    draw_text(status_text, status_card.centerx, status_card.centery + 8, WHITE, small_font, True)

    # Bottom control bar
    control_bar = pygame.Rect(0, HEIGHT - 70, WIDTH, 70)
    draw_rounded_rect(screen, UI_CARD, control_bar, 0, shadow=True)

    # Control buttons
    start_btn.draw(screen)
    pause_btn.draw(screen)
    reset_btn.draw(screen)
    menu_btn.draw(screen)

    # Speed slider
    speed_slider.draw(screen)

    # Graph
    draw_energy_graph()

    # Update simulation
    if not paused and track_points and not any([mass_input.active, velocity_input.active]):
        old_pos = cart_pos
        cart_pos += current_velocity * speed_factor

        if cart_pos >= len(track_points) - 1:
            cart_pos = 0.0

        # Physics calculation with energy conservation
        idx = max(0, min(int(cart_pos), len(track_points) - 1))
        cart_x, cart_y = track_points[idx]
        KE, PE, TE = calculate_energies(cart_x, cart_y, current_velocity)

        # Update velocity based on energy conservation
        available_KE = max(0.01, E_total - PE)  # Minimum KE to prevent stopping
        current_velocity = math.sqrt(2 * available_KE / mass)

        # Store data for graph
        if int(old_pos) != int(cart_pos):  # Only store when position changes significantly
            graph_data_KE.append(KE)
            graph_data_PE.append(PE)
            graph_data_TE.append(TE)

            if len(graph_data_KE) > max_graph_points:
                graph_data_KE.pop(0)
                graph_data_PE.pop(0)
                graph_data_TE.pop(0)


# Initialize simulation
reset_simulation()

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle UI events
        if current_state == "simulation":
            mass_input.handle_event(event)
            velocity_input.handle_event(event)
            speed_slider.handle_event(event)

            # Handle button events
            if start_btn.handle_event(event):
                paused = False
            elif pause_btn.handle_event(event):
                paused = True
            elif reset_btn.handle_event(event):
                reset_simulation()
            elif menu_btn.handle_event(event):
                current_state = "menu"
            elif vectors_btn.handle_event(event):
                show_vectors = not show_vectors
                vectors_btn.text = "Hide Vectors" if show_vectors else "Show Vectors"
            elif grid_btn.handle_event(event):
                show_grid = not show_grid
                grid_btn.text = "Hide Grid" if show_grid else "Show Grid"

        elif current_state == "menu":
            if menu_start_btn.handle_event(event):
                current_state = "simulation"
                reset_simulation()
            elif menu_explain_btn.handle_event(event):
                current_state = "explanation"
            elif menu_exit_btn.handle_event(event):
                running = False

        elif current_state == "explanation":
            if event.type == pygame.MOUSEBUTTONDOWN:
                current_state = "menu"

    # Render current state
    if current_state == "menu":
        show_menu()
    elif current_state == "simulation":
        show_simulation()
    elif current_state == "explanation":
        show_explanation()

    pygame.display.flip()
    clock.tick(60)  # 60 FPS for smooth animation

pygame.quit()
sys.exit()
