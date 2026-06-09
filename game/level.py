# game/level.py
# Static farm map: geometry, cover zones, objective zones, and rendering.
# draw_ground() is called before entities; draw_canopies() is called after,
# so tree canopies appear in front of the tractor when it hides under them.

from __future__ import annotations

import math

import pygame

from game.settings import (
    COLOUR_BARN_RED,
    COLOUR_COVER_FULL,
    COLOUR_COVER_PARTIAL,
    COLOUR_DARK_GREY,
    COLOUR_DARK_GREEN,
    COLOUR_DIRT,
    COLOUR_FENCE,
    COLOUR_FENCE_POST,
    COLOUR_GRASS_GREEN,
    COLOUR_PASTURE,
    COLOUR_PIG_PEN,
    COLOUR_ROOF_DARK,
    COLOUR_SHED,
    COLOUR_STONE,
    COLOUR_STONE_MORTAR,
    COLOUR_TREE_CANOPY,
    COLOUR_TREE_HIGHLIGHT,
    COLOUR_TREE_SHADOW,
    COLOUR_TREE_TRUNK,
    COLOUR_WELL,
    COLOUR_WHEAT,
    COLOUR_WHITE,
    COLOUR_WOOD_DARK,
    DEBUG_COLOUR,
    DEBUG_DRAW_HITBOXES,
    MAP_APPLE_TREE_RECT,
    MAP_BARN_RECT,
    MAP_CHICKEN_COOP_RECT,
    MAP_COW_PASTURE_RECT,
    MAP_ENTRY_HEIGHT,
    MAP_ENTRY_Y,
    MAP_HAY_BALE_1_RECT,
    MAP_HAY_BALE_2_RECT,
    MAP_OAK_TREE_RECT,
    MAP_OLD_SHED_RECT,
    MAP_PATH_LEFT_RECT,
    MAP_PATH_RIGHT_RECT,
    MAP_PIG_PEN_RECT,
    MAP_SCARECROW_RECT,
    MAP_SILO_RECT,
    MAP_WALL_CENTRE_RECT,
    MAP_WALL_LEFT_RECT,
    MAP_WALL_RIGHT_RECT,
    MAP_WELL_RECT,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)


class Level:
    """
    Holds all static map data: cover zones, wall rects, objective zones.
    Draws itself each frame as procedural shapes inspired by the Little Grey
    Fergie art style — bright saturated greens, warm wood, bold outlines.

    wall_rects          — collision list queried by Tractor.update() each frame.
    full_cover_rects    — tractor invisible to vision cones when inside.
    partial_cover_rects — vision cone range reduced 60% when tractor inside.
    """

    def __init__(self) -> None:
        # Collision walls
        self.wall_rects: list[pygame.Rect] = [
            pygame.Rect(*MAP_WALL_LEFT_RECT),
            pygame.Rect(*MAP_WALL_CENTRE_RECT),
            pygame.Rect(*MAP_WALL_RIGHT_RECT),
        ]

        # Full cover zones
        self.full_cover_rects: list[pygame.Rect] = [
            pygame.Rect(*MAP_APPLE_TREE_RECT),
            pygame.Rect(*MAP_OAK_TREE_RECT),
            pygame.Rect(*MAP_CHICKEN_COOP_RECT),
            pygame.Rect(*MAP_OLD_SHED_RECT),
            pygame.Rect(*MAP_PIG_PEN_RECT),
            pygame.Rect(*MAP_HAY_BALE_1_RECT),
            pygame.Rect(*MAP_HAY_BALE_2_RECT),
            pygame.Rect(*MAP_SILO_RECT),
        ]

        # Partial cover zones
        self.partial_cover_rects: list[pygame.Rect] = [
            pygame.Rect(*MAP_WALL_LEFT_RECT),
            pygame.Rect(*MAP_WALL_CENTRE_RECT),
            pygame.Rect(*MAP_WALL_RIGHT_RECT),
            pygame.Rect(*MAP_WELL_RECT),
            pygame.Rect(*MAP_SCARECROW_RECT),
        ]

        # Objective / win-condition rects
        self.barn_rect:        pygame.Rect = pygame.Rect(*MAP_BARN_RECT)
        self.cow_pasture_rect: pygame.Rect = pygame.Rect(*MAP_COW_PASTURE_RECT)
        self.scarecrow_rect:   pygame.Rect = pygame.Rect(*MAP_SCARECROW_RECT)
        self.pig_pen_rect:     pygame.Rect = pygame.Rect(*MAP_PIG_PEN_RECT)

        # Precompute stone block layout — consistent across frames
        self._stone_layout: list[tuple[pygame.Rect, list[tuple[pygame.Rect, int]]]] = []
        self._precompute_stones()

    def _precompute_stones(self) -> None:
        """Build deterministic stone block positions for each wall segment."""
        for wall_data in (MAP_WALL_LEFT_RECT, MAP_WALL_CENTRE_RECT, MAP_WALL_RIGHT_RECT):
            r = pygame.Rect(*wall_data)
            stones: list[tuple[pygame.Rect, int]] = []
            row_h = max(8, (r.height - 4) // 2)
            for row in range(2):
                sy = r.y + 2 + row * (row_h + 2)
                x  = r.x - (18 if row % 2 else 0)   # stagger alternate rows
                col = 0
                while x < r.right:
                    sw = 28 + (col % 4) * 7           # 28, 35, 42, 49 cycling
                    sx_start = max(r.x, x) + 1
                    sx_end   = min(r.right, x + sw) - 1
                    if sx_end - sx_start > 5:
                        sr    = pygame.Rect(sx_start, sy, sx_end - sx_start, row_h - 2)
                        shade = col % 3               # 0=light, 1=mid, 2=dark
                        stones.append((sr, shade))
                    x   += sw
                    col += 1
            self._stone_layout.append((r, stones))

    # ------------------------------------------------------------------
    # Public draw interface
    # ------------------------------------------------------------------

    def draw_ground(self, surface: pygame.Surface) -> None:
        """Everything drawn before entities: terrain, structures, tree trunks."""
        self._draw_background(surface)
        self._draw_zones(surface)
        self._draw_structures(surface)
        self._draw_tree_trunks(surface)
        self._draw_scarecrow(surface)

    def draw_canopies(self, surface: pygame.Surface) -> None:
        """Tree canopies drawn after entities, plus debug overlays on top."""
        self._draw_tree_canopies(surface)
        if DEBUG_DRAW_HITBOXES:
            self._draw_debug_covers(surface)

    # ------------------------------------------------------------------
    # Background / terrain
    # ------------------------------------------------------------------

    def _draw_background(self, surface: pygame.Surface) -> None:
        # Warm yellow-green grass base
        surface.fill(COLOUR_GRASS_GREEN)

        # Dirt path through left wall gap — wide and prominent
        lp = pygame.Rect(*MAP_PATH_LEFT_RECT)
        pygame.draw.rect(surface, COLOUR_DIRT, lp.inflate(16, 0), border_radius=18)
        # Path edge worn darker strip
        pygame.draw.rect(surface, (185, 148, 82),
                         lp.inflate(16, 0), 3, border_radius=18)

        # Dirt path through right wall gap — wide and prominent
        rp = pygame.Rect(*MAP_PATH_RIGHT_RECT)
        pygame.draw.rect(surface, COLOUR_DIRT, rp.inflate(16, 0), border_radius=18)
        pygame.draw.rect(surface, (185, 148, 82),
                         rp.inflate(16, 0), 3, border_radius=18)

        # Entry road at bottom
        road = pygame.Rect(0, MAP_ENTRY_Y - 16, WORLD_WIDTH, MAP_ENTRY_HEIGHT + 16)
        pygame.draw.rect(surface, COLOUR_DIRT, road)
        pygame.draw.line(surface, (178, 140, 78),
                         (0, MAP_ENTRY_Y - 16), (WORLD_WIDTH, MAP_ENTRY_Y - 16), 3)

        # Dark grass border at very bottom
        pygame.draw.rect(surface, COLOUR_DARK_GREEN,
                         pygame.Rect(0, WORLD_HEIGHT - 10, WORLD_WIDTH, 10))

    # ------------------------------------------------------------------
    # Zones — cow pasture and pig pen
    # ------------------------------------------------------------------

    def _draw_zones(self, surface: pygame.Surface) -> None:
        self._draw_cow_pasture(surface)
        self._draw_pig_pen(surface)

    def _draw_cow_pasture(self, surface: pygame.Surface) -> None:
        r = pygame.Rect(*MAP_COW_PASTURE_RECT)
        # Vivid grass inside fence
        pygame.draw.rect(surface, COLOUR_PASTURE, r, border_radius=5)
        # Cows — white with black spots
        for cx, cy in ((r.x+65, r.y+60), (r.x+175, r.y+110)):
            self._draw_cow(surface, cx, cy)
        # Fence
        self._draw_fence(surface, r)

    def _draw_cow(self, surface: pygame.Surface, cx: int, cy: int) -> None:
        # Body — large white oval
        pygame.draw.ellipse(surface, (245, 242, 235), pygame.Rect(cx-20, cy-11, 40, 22))
        pygame.draw.ellipse(surface, COLOUR_DARK_GREY, pygame.Rect(cx-20, cy-11, 40, 22), 1)
        # Black spots
        pygame.draw.ellipse(surface, (38, 32, 28), pygame.Rect(cx-8, cy-8, 14, 10))
        pygame.draw.ellipse(surface, (38, 32, 28), pygame.Rect(cx+6, cy, 10, 8))
        # Head
        pygame.draw.circle(surface, (245, 242, 235), (cx+20, cy-2), 10)
        pygame.draw.circle(surface, COLOUR_DARK_GREY, (cx+20, cy-2), 10, 1)
        # Nose
        pygame.draw.ellipse(surface, (215, 175, 155), pygame.Rect(cx+25, cy-4, 9, 7))
        # Eye
        pygame.draw.circle(surface, (38, 32, 28), (cx+18, cy-6), 2)
        # Ear
        pygame.draw.ellipse(surface, (225, 205, 190), pygame.Rect(cx+14, cy-12, 8, 6))

    def _draw_pig_pen(self, surface: pygame.Surface) -> None:
        r = pygame.Rect(*MAP_PIG_PEN_RECT)
        # Muddy ground
        pygame.draw.rect(surface, COLOUR_PIG_PEN, r, border_radius=5)
        # Mud puddle shapes
        mud = (
            max(0, COLOUR_PIG_PEN[0] - 20),
            max(0, COLOUR_PIG_PEN[1] - 20),
            max(0, COLOUR_PIG_PEN[2] - 24),
        )
        for ox, oy, rr in ((32, 42, 20), (95, 85, 16), (58, 138, 14)):
            pygame.draw.ellipse(surface, mud,
                                pygame.Rect(r.x + ox - rr, r.y + oy - rr // 2, rr * 2, rr))
        # Feeding trough
        trough = pygame.Rect(r.x + 18, r.y + 18, 58, 18)
        pygame.draw.rect(surface, COLOUR_WOOD_DARK, trough, border_radius=4)
        pygame.draw.rect(surface, (50, 40, 22), trough, 2, border_radius=4)
        # Pigs — pink ovals with snouts
        for px, py in ((r.x+55, r.y+65), (r.x+120, r.y+100), (r.x+80, r.y+145)):
            self._draw_pig(surface, px, py)
        # Fence
        self._draw_fence(surface, r)

    def _draw_pig(self, surface: pygame.Surface, cx: int, cy: int) -> None:
        # Body
        pygame.draw.ellipse(surface, (240, 168, 168), pygame.Rect(cx-14, cy-9, 28, 18))
        pygame.draw.ellipse(surface, (210, 130, 130), pygame.Rect(cx-14, cy-9, 28, 18), 1)
        # Head
        pygame.draw.circle(surface, (240, 168, 168), (cx+12, cy-2), 9)
        pygame.draw.circle(surface, (210, 130, 130), (cx+12, cy-2), 9, 1)
        # Snout
        pygame.draw.ellipse(surface, (225, 148, 148), pygame.Rect(cx+16, cy-4, 10, 8))
        pygame.draw.circle(surface, (170, 100, 100), (cx+18, cy-1), 2)
        pygame.draw.circle(surface, (170, 100, 100), (cx+22, cy-1), 2)
        # Ear
        pygame.draw.ellipse(surface, (220, 148, 148), pygame.Rect(cx+8, cy-10, 7, 6))
        # Curly tail
        pygame.draw.arc(surface, (210, 130, 130),
                        pygame.Rect(cx-18, cy-8, 8, 8), 0, math.pi, 2)

    def _draw_fence(self, surface: pygame.Surface, r: pygame.Rect) -> None:
        """Wooden post-and-rail fence around rect r."""
        post_w       = 8
        post_spacing = 40
        post_y       = r.y - 5
        post_h       = r.height + 10
        rail_hi      = (
            min(255, COLOUR_FENCE[0] + 26),
            min(255, COLOUR_FENCE[1] + 18),
            min(255, COLOUR_FENCE[2] + 10),
        )
        post_hi = (
            min(255, COLOUR_FENCE_POST[0] + 32),
            min(255, COLOUR_FENCE_POST[1] + 22),
            min(255, COLOUR_FENCE_POST[2] + 14),
        )

        # Horizontal rails (behind posts)
        for ry in (r.y + 14, r.bottom - 14):
            pygame.draw.line(surface, COLOUR_FENCE, (r.x, ry), (r.right, ry), 5)
            pygame.draw.line(surface, rail_hi,      (r.x, ry - 1), (r.right, ry - 1), 1)

        # Vertical posts
        px = r.x
        while px <= r.right:
            pygame.draw.rect(surface, COLOUR_FENCE_POST,
                             pygame.Rect(px - post_w // 2, post_y, post_w, post_h),
                             border_radius=3)
            pygame.draw.line(surface, post_hi,
                             (px - post_w // 2 + 2, post_y + 5),
                             (px - post_w // 2 + 2, post_y + post_h - 5), 1)
            px += post_spacing

    # ------------------------------------------------------------------
    # Structures
    # ------------------------------------------------------------------

    def _draw_structures(self, surface: pygame.Surface) -> None:
        self._draw_stone_wall(surface)
        self._draw_hay_bales(surface)
        self._draw_coop(surface)
        self._draw_shed(surface)
        self._draw_well(surface)
        self._draw_silo(surface)
        self._draw_barn(surface)

    def _draw_hay_bales(self, surface: pygame.Surface) -> None:
        """Two clusters of round hay bales — full cover, warm golden colour."""
        for rect_data in (MAP_HAY_BALE_1_RECT, MAP_HAY_BALE_2_RECT):
            r = pygame.Rect(*rect_data)
            # Ground shadow under the cluster
            pygame.draw.ellipse(surface, (165, 132, 70),
                                pygame.Rect(r.x + 4, r.y + 4, r.width, r.height))
            # 3 bales arranged in a rough triangle
            bale_positions = [
                (r.x + r.width // 4,      r.y + r.height // 2),   # left
                (r.x + r.width * 3 // 4,  r.y + r.height // 2),   # right
                (r.centerx,               r.y + r.height // 4),    # back-centre
            ]
            for bx, by in bale_positions:
                br = min(r.width, r.height) // 4
                # Bale body — warm golden-yellow
                pygame.draw.circle(surface, (218, 175, 68), (bx, by), br)
                # Bale wrap rings (darker bands)
                pygame.draw.circle(surface, (185, 145, 50), (bx, by), br, 3)
                pygame.draw.circle(surface, (185, 145, 50), (bx, by), br // 2, 2)
                # Highlight
                pygame.draw.circle(surface, (238, 202, 98),
                                   (bx - br // 4, by - br // 4), br // 3)
                # Outline
                pygame.draw.circle(surface, (148, 112, 38), (bx, by), br, 2)

    def _draw_silo(self, surface: pygame.Surface) -> None:
        """Tall stone/concrete silo — full cover near the barn."""
        r = pygame.Rect(*MAP_SILO_RECT)   # (1940, 30, 100, 130)
        cx = r.centerx

        # Silo body — grey concrete cylinder (from top-down: a circle)
        body_r = r.width // 2 - 4
        body_cy = r.centery + 10

        # Shadow
        pygame.draw.circle(surface, (115, 112, 108), (cx + 5, body_cy + 5), body_r)

        # Concrete body
        pygame.draw.circle(surface, (168, 162, 152), (cx, body_cy), body_r)

        # Vertical seam lines (looking down the cylinder)
        for i in range(6):
            angle = math.radians(i * 60)
            sx = int(cx + (body_r - 2) * math.cos(angle))
            sy = int(body_cy + (body_r - 2) * math.sin(angle))
            pygame.draw.line(surface, (140, 135, 128), (cx, body_cy), (sx, sy), 1)

        # Outer ring
        pygame.draw.circle(surface, (128, 122, 114), (cx, body_cy), body_r, 3)

        # Roof cone suggestion — red peaked top visible from above
        roof_r = body_r - 4
        pygame.draw.circle(surface, COLOUR_BARN_RED, (cx, body_cy), roof_r)
        # Roof highlight
        pygame.draw.circle(surface, (228, 72, 72), (cx - roof_r // 4, body_cy - roof_r // 4), roof_r // 3)
        # Roof centre point
        pygame.draw.circle(surface, (170, 35, 35), (cx, body_cy), 5)
        # Roof outline
        pygame.draw.circle(surface, (148, 28, 28), (cx, body_cy), roof_r, 2)

        # Ladder on the side — small dark rungs
        lx = cx + body_r - 4
        for ly in range(body_cy - body_r + 8, body_cy + body_r - 4, 8):
            pygame.draw.line(surface, COLOUR_DARK_GREY, (lx - 3, ly), (lx + 3, ly), 1)
        pygame.draw.line(surface, COLOUR_DARK_GREY,
                         (lx - 3, body_cy - body_r + 8),
                         (lx - 3, body_cy + body_r - 4), 1)
        pygame.draw.line(surface, COLOUR_DARK_GREY,
                         (lx + 3, body_cy - body_r + 8),
                         (lx + 3, body_cy + body_r - 4), 1)

    def _draw_barn(self, surface: pygame.Surface) -> None:
        r = pygame.Rect(*MAP_BARN_RECT)   # (1060, 15, 205, 150)

        # ── Top-down peaked roof ──────────────────────────────────────
        # Visible from above: two sloping faces meet at a central ridge.
        # Left slope (slightly darker — in shadow), right slope (lit),
        # ridge line down the centre.
        ridge_x = r.centerx

        # Left roof face (slightly darker)
        left_pts = [
            (r.x,      r.y),
            (r.x,      r.bottom),
            (ridge_x,  r.bottom - 10),
            (ridge_x,  r.y + 10),
        ]
        pygame.draw.polygon(surface, (102, 82, 58), left_pts)

        # Right roof face (lit side)
        right_pts = [
            (ridge_x,  r.y + 10),
            (ridge_x,  r.bottom - 10),
            (r.right,  r.bottom),
            (r.right,  r.y),
        ]
        pygame.draw.polygon(surface, (122, 100, 72), right_pts)

        # Ridge line — lighter highlight
        pygame.draw.line(surface, (165, 140, 108),
                         (ridge_x, r.y + 10), (ridge_x, r.bottom - 10), 4)

        # Eave outlines (edges of the roof)
        pygame.draw.polygon(surface, COLOUR_DARK_GREY, left_pts,  2)
        pygame.draw.polygon(surface, COLOUR_DARK_GREY, right_pts, 2)

        # ── Red barn walls visible below eave on south face ──────────
        # Show just the south-facing wall strip (where the doors are)
        wall_h = 38
        wall = pygame.Rect(r.x + 4, r.bottom - wall_h, r.width - 8, wall_h)
        pygame.draw.rect(surface, COLOUR_BARN_RED, wall)

        # Vertical siding lines
        for bx in range(wall.x + 24, wall.right, 24):
            pygame.draw.line(surface, (178, 38, 38), (bx, wall.y), (bx, wall.bottom), 1)

        # White trim
        pygame.draw.rect(surface, COLOUR_WHITE, wall, 2)

        # Double barn doors
        door_w, door_h = 58, 34
        door = pygame.Rect(r.centerx - door_w // 2, wall.bottom - door_h, door_w, door_h)
        pygame.draw.rect(surface, COLOUR_WOOD_DARK, door)
        pygame.draw.line(surface, COLOUR_DARK_GREY,
                         (door.centerx, door.top), (door.centerx, door.bottom), 2)
        for dx, dw in ((door.x, door_w // 2 - 1), (door.centerx + 1, door_w // 2 - 1)):
            dr = pygame.Rect(dx, door.top, dw, door_h)
            pygame.draw.line(surface, (80, 50, 24), dr.topleft,  dr.bottomright, 1)
            pygame.draw.line(surface, (80, 50, 24), dr.topright, dr.bottomleft,  1)
        pygame.draw.rect(surface, COLOUR_FENCE_POST, door, 2)

        # Overall outline
        pygame.draw.rect(surface, COLOUR_DARK_GREY, r, 3, border_radius=2)

    def _draw_coop(self, surface: pygame.Surface) -> None:
        r = pygame.Rect(*MAP_CHICKEN_COOP_RECT)   # (35, 525, 165, 120)

        # Straw / dirt ground
        pygame.draw.rect(surface, (200, 172, 118), r, border_radius=4)
        for sy in range(r.y + 10, r.bottom - 8, 15):
            pygame.draw.line(surface, (185, 155, 100),
                             (r.x + 6, sy), (r.right - 6, sy), 1)

        # Small henhouse — top-left corner of the pen
        hh_w, hh_h = 62, 58
        hh = pygame.Rect(r.x + 8, r.y + 8, hh_w, hh_h)
        pygame.draw.rect(surface, (185, 130, 72), hh, border_radius=2)
        # Peaked roof polygon
        roof_pts = [
            (hh.x - 5,    hh.y),
            (hh.centerx,  hh.y - 20),
            (hh.right + 5, hh.y),
        ]
        pygame.draw.polygon(surface, (148, 78, 42), roof_pts)
        pygame.draw.polygon(surface, COLOUR_DARK_GREY, roof_pts, 2)
        # Entrance hole
        hole = pygame.Rect(hh.centerx - 9, hh.bottom - 24, 18, 24)
        pygame.draw.rect(surface, COLOUR_DARK_GREY, hole, border_radius=3)
        pygame.draw.rect(surface, COLOUR_WOOD_DARK, hh, 2, border_radius=2)

        # Chickens — small white blobs with orange beaks
        for cx, cy in ((r.x + 108, r.y + 32), (r.x + 130, r.y + 78), (r.x + 90, r.y + 95)):
            pygame.draw.circle(surface, (242, 240, 232), (cx, cy), 8)
            pygame.draw.circle(surface, COLOUR_DARK_GREY, (cx, cy), 8, 1)
            pygame.draw.polygon(surface, (222, 168, 48),
                                [(cx + 8, cy - 1), (cx + 12, cy), (cx + 8, cy + 2)])

        # Fence around the whole pen
        self._draw_fence(surface, r)

    def _draw_shed(self, surface: pygame.Surface) -> None:
        r = pygame.Rect(*MAP_OLD_SHED_RECT)   # (535, 515, 185, 140)

        # Dark roof strip at top
        roof_h = 32
        roof_r = pygame.Rect(r.x, r.y, r.width, roof_h)
        pygame.draw.rect(surface, COLOUR_ROOF_DARK, roof_r, border_radius=4)
        pygame.draw.line(surface, (110, 88, 64),
                         (r.x + 4, r.y + 3), (r.right - 4, r.y + 3), 1)

        # Weathered wood body
        body = pygame.Rect(r.x, r.y + roof_h, r.width, r.height - roof_h)
        pygame.draw.rect(surface, COLOUR_SHED, body)

        # Horizontal grain lines
        grain = (
            max(0, COLOUR_SHED[0] - 16),
            max(0, COLOUR_SHED[1] - 13),
            max(0, COLOUR_SHED[2] - 9),
        )
        for sy in range(body.y + 12, body.bottom - 4, 14):
            pygame.draw.line(surface, grain, (body.x + 4, sy), (body.right - 4, sy), 1)

        # Window — left side
        win = pygame.Rect(r.x + 14, body.y + 14, 30, 22)
        pygame.draw.rect(surface, (158, 202, 228), win, border_radius=2)
        pygame.draw.line(surface, COLOUR_DARK_GREY, win.midleft,  win.midright, 1)
        pygame.draw.line(surface, COLOUR_DARK_GREY, win.midtop,   win.midbottom, 1)
        pygame.draw.rect(surface, COLOUR_WHITE, win, 2, border_radius=2)

        # Door — right side
        door_w, door_h = 38, 55
        door = pygame.Rect(r.right - door_w - 10, body.bottom - door_h, door_w, door_h)
        pygame.draw.rect(surface, COLOUR_WOOD_DARK, door, border_radius=2)
        pygame.draw.line(surface, (80, 50, 24), door.topleft,  door.bottomright, 1)
        pygame.draw.line(surface, (80, 50, 24),
                         (door.x, door.centery), door.bottomright, 1)
        pygame.draw.rect(surface, COLOUR_DARK_GREY, door, 2, border_radius=2)

        # Outline
        pygame.draw.rect(surface, COLOUR_DARK_GREY, r, 3, border_radius=4)

    def _draw_well(self, surface: pygame.Surface) -> None:
        r  = pygame.Rect(*MAP_WELL_RECT)   # (775, 530, 90, 65)
        cx = r.centerx

        # Stone base
        base = pygame.Rect(r.x + 10, r.y + 22, r.width - 20, r.height - 22)
        pygame.draw.rect(surface, COLOUR_STONE, base, border_radius=8)
        # Stone mortar lines
        pygame.draw.line(surface, COLOUR_STONE_MORTAR,
                         (base.x, base.centery), (base.right, base.centery), 2)
        for bx in range(base.x + 24, base.right, 24):
            pygame.draw.line(surface, COLOUR_STONE_MORTAR,
                             (bx, base.y), (bx, base.bottom), 2)
        pygame.draw.rect(surface, COLOUR_DARK_GREY, base, 2, border_radius=8)

        # Wooden frame posts
        for px in (r.x + 14, r.right - 14):
            pygame.draw.rect(surface, COLOUR_TREE_TRUNK,
                             pygame.Rect(px - 4, r.y, 8, r.height - 12), border_radius=2)

        # Crossbeam
        pygame.draw.line(surface, COLOUR_TREE_TRUNK,
                         (r.x + 14, r.y + 7), (r.right - 14, r.y + 7), 7)

        # Rope and bucket
        pygame.draw.line(surface, COLOUR_DARK_GREY, (cx, r.y + 7), (cx, r.y + 24), 2)
        bucket = pygame.Rect(cx - 9, r.y + 22, 18, 14)
        pygame.draw.rect(surface, COLOUR_WELL, bucket, border_radius=2)
        pygame.draw.rect(surface, COLOUR_DARK_GREY, bucket, 1, border_radius=2)

    def _draw_stone_wall(self, surface: pygame.Surface) -> None:
        stone_cols = [
            (162, 156, 146),   # shade 0 — light
            (150, 144, 134),   # shade 1 — mid
            (140, 134, 124),   # shade 2 — dark
        ]
        for r, stones in self._stone_layout:
            # Mortar base
            pygame.draw.rect(surface, COLOUR_STONE_MORTAR, r)
            # Individual stones
            for sr, shade in stones:
                c = stone_cols[shade]
                pygame.draw.rect(surface, c, sr, border_radius=2)
                # Top highlight
                pygame.draw.line(surface,
                                 (min(255, c[0] + 20), min(255, c[1] + 16), min(255, c[2] + 12)),
                                 sr.topleft, sr.topright, 1)
            # Wall outline
            pygame.draw.rect(surface, COLOUR_DARK_GREY, r, 2)

    # ------------------------------------------------------------------
    # Vegetation — two-pass (trunks before entities, canopies after)
    # ------------------------------------------------------------------

    def _draw_tree_trunks(self, surface: pygame.Surface) -> None:
        for rect_data in (MAP_APPLE_TREE_RECT, MAP_OAK_TREE_RECT):
            r = pygame.Rect(*rect_data)
            trunk_w = max(16, r.width // 5)
            trunk_h = max(26, r.height // 3)
            trunk   = pygame.Rect(r.centerx - trunk_w // 2,
                                  r.bottom - trunk_h, trunk_w, trunk_h)
            pygame.draw.rect(surface, COLOUR_TREE_TRUNK, trunk, border_radius=3)
            # Bark highlight
            pygame.draw.line(surface, (148, 108, 68),
                             (trunk.x + 3, trunk.y + 4),
                             (trunk.x + 3, trunk.bottom - 4), 2)
            pygame.draw.rect(surface, COLOUR_DARK_GREY, trunk, 1, border_radius=3)

    def _draw_tree_canopies(self, surface: pygame.Surface) -> None:
        for rect_data in (MAP_APPLE_TREE_RECT, MAP_OAK_TREE_RECT):
            r      = pygame.Rect(*rect_data)
            cx, cy = r.centerx, r.centery - 8
            radius = min(r.width, r.height) // 2

            # Drop shadow
            pygame.draw.circle(surface, COLOUR_TREE_SHADOW, (cx + 6, cy + 6), radius - 2)

            # Main canopy
            pygame.draw.circle(surface, COLOUR_TREE_CANOPY, (cx, cy), radius)

            # Secondary blobs for organic silhouette
            for bx, by, br in (
                (-radius // 3, -radius // 4, radius - 6),
                ( radius // 3, -radius // 3, radius - 8),
                ( radius // 2,  radius // 5, radius - 10),
                (-radius // 2,  radius // 6, radius - 9),
            ):
                pygame.draw.circle(surface, COLOUR_TREE_CANOPY, (cx + bx, cy + by), br)

            # Sunlit highlight — upper-left
            hl_r   = max(10, radius // 2 - 2)
            hl_pos = (cx - radius // 3, cy - radius // 3)
            pygame.draw.circle(surface, COLOUR_TREE_HIGHLIGHT, hl_pos, hl_r)

            # Outline
            pygame.draw.circle(surface, (34, 104, 20), (cx, cy), radius, 2)

    def _draw_scarecrow(self, surface: pygame.Surface) -> None:
        r  = pygame.Rect(*MAP_SCARECROW_RECT)   # (600, 255, 55, 80)
        cx = r.centerx

        # Main post
        post_w = 8
        pygame.draw.rect(surface, COLOUR_TREE_TRUNK,
                         pygame.Rect(cx - post_w // 2, r.y + 24, post_w, r.height - 24),
                         border_radius=2)

        # Crossbar / arms
        bar_y = r.y + r.height // 3
        pygame.draw.rect(surface, COLOUR_TREE_TRUNK,
                         pygame.Rect(r.x, bar_y - 4, r.width, 8), border_radius=3)

        # Shirt on the arms
        pygame.draw.rect(surface, (108, 82, 148),
                         pygame.Rect(r.x + 4, bar_y - 3, r.width - 8, 10), border_radius=2)

        # Head (straw-stuffed)
        head_r  = 12
        head_cy = r.y + 13
        pygame.draw.circle(surface, COLOUR_WHEAT, (cx, head_cy), head_r)
        # Straw texture lines
        for sa in range(-3, 4, 2):
            pygame.draw.line(surface, (195, 160, 68),
                             (cx + sa * 3, head_cy - head_r + 3),
                             (cx + sa * 3, head_cy + head_r - 3), 1)
        pygame.draw.circle(surface, COLOUR_DARK_GREY, (cx, head_cy), head_r, 2)

        # Hat
        brim  = pygame.Rect(cx - 14, head_cy - head_r - 2, 28, 5)
        crown = pygame.Rect(cx - 10, head_cy - head_r - 12, 20, 12)
        pygame.draw.rect(surface, COLOUR_WOOD_DARK, crown, border_radius=2)
        pygame.draw.rect(surface, COLOUR_WOOD_DARK, brim)

        # X-eyes and smile
        for ex in (cx - 5, cx + 3):
            pygame.draw.line(surface, COLOUR_DARK_GREY, (ex, head_cy - 4), (ex + 2, head_cy - 2), 1)
            pygame.draw.line(surface, COLOUR_DARK_GREY, (ex + 2, head_cy - 4), (ex, head_cy - 2), 1)
        pygame.draw.arc(surface, COLOUR_DARK_GREY,
                        pygame.Rect(cx - 4, head_cy + 1, 8, 5),
                        math.pi, 2 * math.pi, 1)

    # ------------------------------------------------------------------
    # Debug overlays
    # ------------------------------------------------------------------

    def _draw_debug_covers(self, surface: pygame.Surface) -> None:
        for rect in self.full_cover_rects:
            pygame.draw.rect(surface, COLOUR_COVER_FULL, rect, 2)
        for rect in self.partial_cover_rects:
            pygame.draw.rect(surface, COLOUR_COVER_PARTIAL, rect, 2)
        for rect in self.wall_rects:
            pygame.draw.rect(surface, DEBUG_COLOUR, rect, 2)
        for rect in (self.barn_rect, self.cow_pasture_rect,
                     self.scarecrow_rect, self.pig_pen_rect):
            pygame.draw.rect(surface, (0, 150, 255), rect, 2)
