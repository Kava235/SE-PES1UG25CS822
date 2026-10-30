import pygame

ICON_COLORS = {
    "ROCK": (200, 70, 70),
    "PAPER": (60, 130, 210),
    "SCISSORS": (220, 180, 50),
}
OUTLINE = (20, 22, 28)


def draw_icon(surface, choice, cx, cy, size, color=None, flip=False):
    """Draw a hand-gesture icon for ROCK / PAPER / SCISSORS using only pygame shapes.
    (cx, cy) is the centre, size is roughly the icon's width in pixels."""
    color = color or ICON_COLORS[choice]
    s = size
    dark = tuple(max(0, c - 70) for c in color)
    d = -1 if flip else 1  # mirror horizontally for the CPU's hand

    if choice == "ROCK":
        # fist: palm block + four knuckles + thumb
        body = pygame.Rect(0, 0, int(0.8 * s), int(0.55 * s))
        body.center = (cx, cy + int(0.12 * s))
        pygame.draw.rect(surface, color, body, border_radius=int(0.18 * s))
        for i in range(4):
            kx = cx + d * int((-0.3 + i * 0.2) * s)
            pygame.draw.circle(surface, color, (kx, cy - int(0.2 * s)), int(0.12 * s))
            pygame.draw.circle(surface, OUTLINE, (kx, cy - int(0.2 * s)), int(0.12 * s), 2)
        for i in range(1, 4):  # finger gaps
            lx = cx + d * int((-0.4 + i * 0.2) * s)
            pygame.draw.line(surface, dark, (lx, cy - int(0.12 * s)), (lx, cy + int(0.1 * s)), 3)
        thumb = pygame.Rect(0, 0, int(0.32 * s), int(0.2 * s))
        thumb.center = (cx + d * int(0.0 * s), cy + int(0.1 * s))
        pygame.draw.ellipse(surface, color, thumb)
        pygame.draw.ellipse(surface, OUTLINE, thumb, 2)
        pygame.draw.rect(surface, OUTLINE, body, 2, border_radius=int(0.18 * s))

    elif choice == "PAPER":
        # open hand: palm + four fingers of different heights + thumb
        palm = pygame.Rect(0, 0, int(0.7 * s), int(0.5 * s))
        palm.center = (cx, cy + int(0.2 * s))
        heights = [0.42, 0.52, 0.48, 0.36]
        for i, h in enumerate(heights):
            fw = int(0.15 * s)
            fx = cx + d * int((-0.3 + i * 0.2) * s) - fw // 2
            fh = int(h * s)
            f = pygame.Rect(fx, palm.top - fh + int(0.08 * s), fw, fh)
            pygame.draw.rect(surface, color, f, border_radius=fw // 2)
            pygame.draw.rect(surface, OUTLINE, f, 2, border_radius=fw // 2)
        pygame.draw.rect(surface, color, palm, border_radius=int(0.12 * s))
        pygame.draw.rect(surface, OUTLINE, palm, 2, border_radius=int(0.12 * s))
        thumb = [(cx - d * int(0.3 * s), cy + int(0.05 * s)),
                 (cx - d * int(0.62 * s), cy - int(0.12 * s)),
                 (cx - d * int(0.68 * s), cy + int(0.0 * s)),
                 (cx - d * int(0.4 * s), cy + int(0.32 * s))]
        pygame.draw.polygon(surface, color, thumb)
        pygame.draw.polygon(surface, OUTLINE, thumb, 2)

    elif choice == "SCISSORS":
        # two crossing blades + two ring handles + pivot
        pivot = (cx, cy + int(0.05 * s))
        for sign in (-1, 1):
            tip = (cx + sign * int(0.3 * s), cy - int(0.45 * s))
            hand = (cx - sign * int(0.25 * s), cy + int(0.38 * s))
            pygame.draw.line(surface, (225, 228, 235), pivot, tip, int(0.13 * s))
            pygame.draw.line(surface, OUTLINE, pivot, tip, 2)
            pygame.draw.line(surface, color, pivot, hand, int(0.08 * s))
            pygame.draw.circle(surface, color, hand, int(0.15 * s), int(0.06 * s))
            pygame.draw.circle(surface, OUTLINE, hand, int(0.15 * s), 2)
        pygame.draw.circle(surface, OUTLINE, pivot, int(0.07 * s))
