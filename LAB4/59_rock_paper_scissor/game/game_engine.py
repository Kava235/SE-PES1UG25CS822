import math
import random
from collections import Counter, deque
import pygame
from game.button import ChoiceButton
from game.icons import draw_icon, ICON_COLORS

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.choices = ["ROCK", "PAPER", "SCISSORS"]
        btn_w, btn_h = 130, 50
        gap = 20
        total_w = 3 * btn_w + 2 * gap
        start_x = (width - total_w) // 2
        btn_y = height - 85

        self.buttons = [
            ChoiceButton("ROCK", pygame.Rect(start_x, btn_y, btn_w, btn_h), (160, 50, 50), (200, 70, 70)),
            ChoiceButton("PAPER", pygame.Rect(start_x + btn_w + gap, btn_y, btn_w, btn_h), (40, 100, 170), (60, 130, 210)),
            ChoiceButton("SCISSORS", pygame.Rect(start_x + 2 * (btn_w + gap), btn_y, btn_w, btn_h), (180, 140, 30), (220, 180, 50)),
        ]

        self.player_choice = None
        self.cpu_choice = None
        self.result_text = "Make your move!"
        self.result_color = (220, 225, 235)

        self.player_score = 0
        self.cpu_score = 0

        self.round_resolved_time = 0
        self.display_duration = 1800
        self.showing_result = False

        # Task 2: first to TARGET_SCORE wins the match
        self.target_score = 3
        self.game_over = False
        self.match_winner = None

        # Task 3: adaptive AI - remember the player's last few throws
        self.player_history = deque(maxlen=6)
        self.counter_moves = {"ROCK": "PAPER", "PAPER": "SCISSORS", "SCISSORS": "ROCK"}
        self.adapt_chance = 0.7   # how often CPU uses its prediction

        # Task 4: countdown / shaking reveal before each result
        self.reveal_duration = 1200   # ms
        self.revealing = False
        self.reveal_start = 0
        self.pending_outcome = None

        self.font_title = pygame.font.SysFont(None, 36)
        self.font_hud = pygame.font.SysFont(None, 26)
        self.font_arena = pygame.font.SysFont(None, 32)

    def determine_winner(self, player, cpu):
        if player == cpu:
            return "TIE"
            
        # Key = (player, cpu); value = who wins that matchup
        rules = {
            ("ROCK", "SCISSORS"): "PLAYER",
            ("SCISSORS", "PAPER"): "PLAYER",
            ("PAPER", "ROCK"): "PLAYER",
            ("SCISSORS", "ROCK"): "CPU",
            ("PAPER", "SCISSORS"): "CPU",
            ("ROCK", "PAPER"): "CPU",
        }
        return rules.get((player, cpu), "TIE")

    def choose_cpu_move(self):
        """Counter the player's favourite move if they repeat it, else random."""
        if len(self.player_history) >= 3:
            favourite, count = Counter(self.player_history).most_common(1)[0]
            if count >= 2 and random.random() < self.adapt_chance:
                return self.counter_moves[favourite]
        return random.choice(self.choices)

    def play_round(self, choice):
        """Start a round: lock in both picks, then run the shaking countdown."""
        self.player_choice = choice
        self.cpu_choice = self.choose_cpu_move()
        self.player_history.append(choice)
        self.showing_result = False
        self.revealing = True
        self.reveal_start = pygame.time.get_ticks()
        self.result_text = "Get ready..."
        self.result_color = (190, 195, 205)

    def resolve_round(self):
        """Called when the countdown ends: reveal picks and score the round."""
        self.revealing = False
        outcome = self.determine_winner(self.player_choice, self.cpu_choice)
        if outcome == "PLAYER":
            self.player_score += 1
            self.result_text = f"You Win! {self.player_choice} beats {self.cpu_choice}."
            self.result_color = (80, 230, 120)
        elif outcome == "CPU":
            self.cpu_score += 1
            self.result_text = f"You Lose! {self.cpu_choice} beats {self.player_choice}."
            self.result_color = (240, 80, 80)
        else:
            self.result_text = f"It's a Draw! Both picked {self.player_choice}."
            self.result_color = (240, 210, 80)

        self.showing_result = True
        self.round_resolved_time = pygame.time.get_ticks()

        # Task 2: check match end
        if self.player_score >= self.target_score:
            self.game_over = True
            self.match_winner = "PLAYER"
        elif self.cpu_score >= self.target_score:
            self.game_over = True
            self.match_winner = "CPU"

    def reset_match(self):
        self.player_score = 0
        self.cpu_score = 0
        self.player_choice = None
        self.cpu_choice = None
        self.result_text = "Make your move!"
        self.result_color = (220, 225, 235)
        self.showing_result = False
        self.game_over = False
        self.match_winner = None
        self.player_history.clear()

    def handle_event(self, event):
        if self.revealing:
            return  # no clicks while the countdown plays
        if self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset_match()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn.contains(event.pos):
                    self.play_round(btn.choice_name)
                    break

    def update(self):
        if self.game_over:
            return  # keep the final picks on screen
        now = pygame.time.get_ticks()
        if self.revealing:
            if now - self.reveal_start >= self.reveal_duration:
                self.resolve_round()
            return
        if self.showing_result and (now - self.round_resolved_time >= self.display_duration):
            self.player_choice = None
            self.cpu_choice = None
            self.result_text = "Make your move!"
            self.result_color = (190, 195, 205)
            self.showing_result = False

    def render(self, screen):
        screen.fill((24, 28, 36))

        title_surf = self.font_title.render("Rock Paper Scissors", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 14))

        p_surf = self.font_hud.render(f"Player Score: {self.player_score}", True, (100, 180, 255))
        c_surf = self.font_hud.render(f"CPU Score: {self.cpu_score}", True, (255, 120, 120))
        screen.blit(p_surf, (35, 52))
        screen.blit(c_surf, (self.width - c_surf.get_width() - 35, 52))

        pygame.draw.line(screen, (45, 52, 66), (25, 82), (self.width - 25, 82), 2)

        self.render_arena(screen)

        res_surf = self.font_arena.render(self.result_text, True, self.result_color)
        screen.blit(res_surf, (self.width // 2 - res_surf.get_width() // 2, 238))

        for btn in self.buttons:
            btn.render(screen)

        if self.game_over:
            self.render_game_over(screen)

    def render_arena(self, screen):
        lx, rx, cy, size = int(self.width * 0.25), int(self.width * 0.75), 155, 90
        cx = self.width // 2
        you = self.font_hud.render("YOU", True, (100, 180, 255))
        cpu = self.font_hud.render("CPU", True, (255, 120, 120))
        screen.blit(you, (lx - you.get_width() // 2, 92))
        screen.blit(cpu, (rx - cpu.get_width() // 2, 92))

        if self.revealing:
            elapsed = pygame.time.get_ticks() - self.reveal_start
            bob = int(math.sin(elapsed / 55.0) * 16)          # fists pump up and down
            draw_icon(screen, "ROCK", lx, cy + bob, size, (170, 175, 185))
            draw_icon(screen, "ROCK", rx, cy - bob, size, (170, 175, 185), flip=True)
            step = min(3, int(elapsed / (self.reveal_duration / 4)))
            word = ["ROCK...", "PAPER...", "SCISSORS...", "SHOOT!"][step]
            t = pygame.font.SysFont(None, 40).render(word, True, (245, 220, 90))
            screen.blit(t, (cx - t.get_width() // 2, cy - t.get_height() // 2))
        elif self.player_choice and self.cpu_choice:
            draw_icon(screen, self.player_choice, lx, cy, size)
            draw_icon(screen, self.cpu_choice, rx, cy, size, flip=True)
            for name, x in ((self.player_choice, lx), (self.cpu_choice, rx)):
                n = self.font_hud.render(name, True, (225, 225, 230))
                screen.blit(n, (x - n.get_width() // 2, cy + 52))
            vs = self.font_arena.render("VS", True, (150, 155, 170))
            screen.blit(vs, (cx - vs.get_width() // 2, cy - vs.get_height() // 2))
        else:
            for x in (lx, rx):
                q = pygame.font.SysFont(None, 90).render("?", True, (70, 78, 95))
                screen.blit(q, (x - q.get_width() // 2, cy - q.get_height() // 2))

    def render_game_over(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 225))
        screen.blit(overlay, (0, 0))

        if self.match_winner == "PLAYER":
            text, color = "YOU WON THE MATCH!", (80, 230, 120)
        else:
            text, color = "CPU WON THE MATCH!", (240, 80, 80)
        banner = pygame.font.SysFont(None, 54).render(text, True, color)
        sub = self.font_arena.render(
            f"Final Score  {self.player_score} - {self.cpu_score}   (First to {self.target_score})",
            True, (235, 235, 240))
        hint = self.font_hud.render("Press R to play again", True, (200, 205, 215))
        cx = self.width // 2
        screen.blit(banner, (cx - banner.get_width() // 2, 120))
        screen.blit(sub, (cx - sub.get_width() // 2, 180))
        screen.blit(hint, (cx - hint.get_width() // 2, 220))
