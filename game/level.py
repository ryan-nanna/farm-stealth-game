# game/level.py
# Static farm map: geometry, cover zones, objective zones, and rendering.
# draw_ground() is called before entities; draw_canopies() is called after,
# so tree canopies appear in front of the tractor when it hides under them.

from __future__ import annotations

import math

import pygame

from game.settings import (
    COLOUR_BARN_FENCE,
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
    COLOUR_ROOF_SILVER,
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
    MAP_BARN_BODY_RECT,
    MAP_BARN_RECT,
    MAP_CHICKEN_COOP_RECT,
    MAP_COW_PASTURE_RECT,
    MAP_ENTRY_HEIGHT,
    MAP_ENTRY_Y,
    MAP_EXTRA_OAK_RECT,
    MAP_HAY_BALE_1_RECT,
    MAP_HAY_BALE_2_RECT,
    MAP_OAK_TREE_RECT,
    MAP_OLD_SHED_RECT,
    MAP_ORCHARD_TREE_1,
    MAP_ORCHARD_TREE_2,
    MAP_PATH_LEFT_RECT,
    MAP_PATH_RIGHT_RECT,
    MAP_PIG_PEN_RECT,
    MAP_POND_RECT,
    MAP_SCARECROW_RECT,
    MAP_SHEEP_PEN_RECT,
    MAP_SILO_RECT,
    MAP_WALL_CENTRE_RECT,
    MAP_WALL_LEFT_RECT,
    MAP_WALL_RIGHT_RECT,
    MAP_WELL_RECT,
    COLOUR_POND,
    COLOUR_SHEEP,
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
        # Collision walls — tractor cannot pass through these
        self.wall_rects: list[pygame.Rect] = [
            pygame.Rect(*MAP_WALL_LEFT_RECT),
            pygame.Rect(*MAP_WALL_CENTRE_RECT),
            pygame.Rect(*MAP_WALL_RIGHT_RECT),
            pygame.Rect(*MAP_BARN_BODY_RECT),   # solid barn building
        ]

        # Full cover zones
        self.full_cover_rects: list[pygame.Rect] = [
            pygame.Rect(*MAP_APPLE_TREE_RECT),
            pygame.Rect(*MAP_OAK_TREE_RECT),
            pygame.Rect(*MAP_EXTRA_OAK_RECT),
            pygame.Rect(*MAP_ORCHARD_TREE_1),
            pygame.Rect(*MAP_ORCHARD_TREE_2),
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
            pygame.Rect(*MAP_SHEEP_PEN_RECT),
            pygame.Rect(*MAP_POND_RECT),
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
        self._draw_flower_patches(surface)
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
        self._draw_sheep_pen(surface)
        self._draw_pond(surface)

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
        """
        Front-facing barn illustration (Stardew / Zelda convention).
        The barn "stands up" in the world — big silver peaked roof at top,
        red vertical-board walls below, two sets of white X-brace double
        doors, loft windows, cupola with rooster weathervane.
        Surrounded by a black board fence with a gate on the south side.
        """
        # ── Core geometry ─────────────────────────────────────────────
        BX      = 2060       # left wall of barn building
        BW      = 460        # barn width
        PEAK_X  = BX + BW // 2   # 2290 — horizontal centre
        PEAK_Y  = 10         # roof peak (top of world)
        EAVE_L  = BX - 34   # eave overhang left
        EAVE_R  = BX + BW + 34  # eave overhang right
        EAVE_Y  = 230        # where roof meets front wall
        WALL_BOT = 430       # bottom of front wall / foundation top

        # ── Fence yard (drawn first — acts as background) ─────────────
        YARD = pygame.Rect(*MAP_BARN_RECT)   # (1960, 10, 600, 560)

        # Yard grass — slightly brighter/warmer than open field
        pygame.draw.rect(surface, (118, 192, 68), YARD)

        # Worn dirt patch in front of the doors (where Gramps stands)
        dirt = pygame.Rect(PEAK_X - 130, WALL_BOT - 10, 260, 180)
        pygame.draw.ellipse(surface, (200, 165, 95), dirt)
        pygame.draw.ellipse(surface, (180, 148, 78), dirt, 2)

        # ── ROOF — dominant silver peaked gable ───────────────────────
        # Full roof triangle (base colour)
        roof_tri = [(PEAK_X, PEAK_Y), (EAVE_L, EAVE_Y), (EAVE_R, EAVE_Y)]
        pygame.draw.polygon(surface, COLOUR_ROOF_SILVER, roof_tri)

        # Left half slightly darker (shadow side)
        pygame.draw.polygon(surface, (172, 177, 192), [
            (PEAK_X, PEAK_Y), (EAVE_L, EAVE_Y), (PEAK_X, EAVE_Y),
        ])

        # Standing-seam panel lines radiating from peak to eave
        _SEAM = (158, 163, 178)
        for i in range(1, 11):
            t = i / 11.0
            # Left-side seams
            lx = int(PEAK_X + t * (EAVE_L - PEAK_X))
            pygame.draw.line(surface, _SEAM, (PEAK_X, PEAK_Y), (lx, EAVE_Y), 1)
            # Right-side seams
            rx = int(PEAK_X + t * (EAVE_R - PEAK_X))
            pygame.draw.line(surface, _SEAM, (PEAK_X, PEAK_Y), (rx, EAVE_Y), 1)

        # Ridge cap highlight (brightest strip at the very peak)
        pygame.draw.line(surface, (230, 234, 244),
                         (PEAK_X - 3, PEAK_Y), (PEAK_X + 3, PEAK_Y + 55), 5)

        # Roof outline
        pygame.draw.polygon(surface, (132, 136, 150), roof_tri, 3)

        # Eave shadow (dark underside of the roof overhang)
        pygame.draw.rect(surface, (80, 70, 58),
                         pygame.Rect(EAVE_L, EAVE_Y, EAVE_R - EAVE_L, 16))

        # Gable siding: triangular red strips between overhang and wall
        pygame.draw.polygon(surface, COLOUR_BARN_RED, [
            (EAVE_L, EAVE_Y), (BX, EAVE_Y), (BX, PEAK_Y),
        ])
        pygame.draw.polygon(surface, COLOUR_BARN_RED, [
            (EAVE_R, EAVE_Y), (BX + BW, EAVE_Y), (BX + BW, PEAK_Y),
        ])

        # ── FRONT WALL ────────────────────────────────────────────────
        wall = pygame.Rect(BX, EAVE_Y, BW, WALL_BOT - EAVE_Y)
        pygame.draw.rect(surface, COLOUR_BARN_RED, wall)

        # Vertical board siding lines
        for sx in range(BX + 14, BX + BW, 14):
            pygame.draw.line(surface, (190, 40, 40), (sx, EAVE_Y), (sx, WALL_BOT), 1)

        # White trim strip under eave
        pygame.draw.rect(surface, COLOUR_WHITE,
                         pygame.Rect(BX, EAVE_Y + 16, BW, 10))

        # ── LOFT WINDOWS ──────────────────────────────────────────────
        loft_y = EAVE_Y + 36
        for wx in (BX + BW // 4 - 36, BX + 3 * BW // 4 - 36):
            wr = pygame.Rect(wx, loft_y, 72, 50)
            pygame.draw.rect(surface, (190, 215, 235), wr)   # pale blue glass
            pygame.draw.rect(surface, COLOUR_WHITE, wr, 4)
            # Cross panes
            pygame.draw.line(surface, COLOUR_WHITE,
                             (wr.centerx, wr.y), (wr.centerx, wr.bottom), 3)
            pygame.draw.line(surface, COLOUR_WHITE,
                             (wr.x, wr.centery), (wr.right, wr.centery), 2)

        # ── X-BRACE DOUBLE DOORS (two sets) ──────────────────────────
        DOOR_TOP = EAVE_Y + 100
        DOOR_H   = WALL_BOT - DOOR_TOP - 2
        DOOR_W   = 120   # total width of each double-door set

        for door_cx in (BX + BW // 3, BX + 2 * BW // 3):
            dr = pygame.Rect(door_cx - DOOR_W // 2, DOOR_TOP, DOOR_W, DOOR_H)
            # White door panels
            pygame.draw.rect(surface, COLOUR_WHITE, dr)
            # Centre divider
            pygame.draw.line(surface, (160, 160, 160),
                             (dr.centerx, dr.top), (dr.centerx, dr.bottom), 4)
            # X-brace on left panel
            lp = pygame.Rect(dr.x, dr.y, dr.w // 2 - 2, dr.h)
            pygame.draw.line(surface, (150, 150, 150), lp.topleft,  lp.bottomright, 3)
            pygame.draw.line(surface, (150, 150, 150), lp.topright, lp.bottomleft,  3)
            # X-brace on right panel
            rp = pygame.Rect(dr.centerx + 2, dr.y, dr.w // 2 - 2, dr.h)
            pygame.draw.line(surface, (150, 150, 150), rp.topleft,  rp.bottomright, 3)
            pygame.draw.line(surface, (150, 150, 150), rp.topright, rp.bottomleft,  3)
            # Door outline
            pygame.draw.rect(surface, (78, 78, 78), dr, 3)

        # Wall outline
        pygame.draw.rect(surface, (175, 34, 34), wall, 2)

        # ── FOUNDATION ────────────────────────────────────────────────
        foundation = pygame.Rect(BX - 6, WALL_BOT - 10, BW + 12, 22)
        pygame.draw.rect(surface, (148, 138, 118), foundation)
        pygame.draw.rect(surface, (108, 98, 85), foundation, 2)

        # ── CUPOLA on roof peak ───────────────────────────────────────
        CW, CH = 66, 50
        cup = pygame.Rect(PEAK_X - CW // 2, PEAK_Y, CW, CH)
        pygame.draw.rect(surface, (75, 56, 40), cup, border_radius=4)
        # Louvered vents
        for vx in (cup.x + 5, cup.centerx + 3):
            vr = pygame.Rect(vx, cup.y + 10, CW // 2 - 8, CH - 20)
            pygame.draw.rect(surface, COLOUR_WHITE, vr)
            for vy in range(vr.y + 4, vr.bottom, 7):
                pygame.draw.line(surface, (175, 175, 175),
                                 (vr.x, vy), (vr.right, vy), 1)
        # Mini peaked roof on cupola
        cup_peak = (PEAK_X, PEAK_Y - 30)
        pygame.draw.polygon(surface, COLOUR_ROOF_SILVER, [
            (PEAK_X - CW // 2 - 10, PEAK_Y),
            cup_peak,
            (PEAK_X + CW // 2 + 10, PEAK_Y),
        ])
        pygame.draw.polygon(surface, (145, 150, 164), [
            (PEAK_X - CW // 2 - 10, PEAK_Y),
            cup_peak,
            (PEAK_X + CW // 2 + 10, PEAK_Y),
        ], 2)
        # Weathervane: pole + stylised rooster
        WVX, WVY = PEAK_X, PEAK_Y - 30
        pygame.draw.line(surface, (68, 122, 102), (WVX, WVY), (WVX, WVY - 40), 3)
        # Rooster silhouette (simple circles + beak)
        pygame.draw.circle(surface, (68, 122, 102), (WVX, WVY - 42), 7)   # body
        pygame.draw.circle(surface, (68, 122, 102), (WVX + 2, WVY - 52), 5)  # head
        pygame.draw.polygon(surface, (68, 122, 102), [                    # beak
            (WVX + 7, WVY - 54), (WVX + 14, WVY - 52), (WVX + 7, WVY - 49),
        ])
        pygame.draw.circle(surface, (212, 46, 46), (WVX + 4, WVY - 48), 3)   # wattle

        # ── BLACK BOARD FENCE around yard ────────────────────────────
        FC  = COLOUR_BARN_FENCE          # (32, 28, 25) near-black
        FHI = (55, 50, 44)               # highlight
        POST_W    = 14
        POST_SPACING = 90
        RAIL_H    = 7
        RAIL_GAP  = 28

        # ─ West fence (x=1960, y=10 → y=570) ─
        for py in range(YARD.y, YARD.bottom, POST_SPACING):
            pygame.draw.rect(surface, FC,
                             pygame.Rect(YARD.x - POST_W // 2, py, POST_W,
                                         min(POST_SPACING - 4, YARD.bottom - py)))
        for ry in (YARD.y + RAIL_GAP, YARD.y + RAIL_GAP * 2, YARD.bottom - RAIL_GAP):
            pygame.draw.rect(surface, FC,
                             pygame.Rect(YARD.x - POST_W // 2, ry, POST_W + 4, RAIL_H))

        # ─ South fence — left of gate (1960 → PEAK_X-110) ─
        gate_left  = PEAK_X - 110
        gate_right = PEAK_X + 110
        for fx in range(YARD.x, gate_left, POST_SPACING):
            pygame.draw.rect(surface, FC,
                             pygame.Rect(fx, YARD.bottom - POST_W, POST_SPACING - 4, POST_W))
        for ry_off in (RAIL_GAP, RAIL_GAP * 2):
            pygame.draw.rect(surface, FC,
                             pygame.Rect(YARD.x, YARD.bottom - ry_off - RAIL_H,
                                         gate_left - YARD.x, RAIL_H))

        # ─ South fence — right of gate (PEAK_X+110 → YARD.right) ─
        for fx in range(gate_right, YARD.right, POST_SPACING):
            pygame.draw.rect(surface, FC,
                             pygame.Rect(fx, YARD.bottom - POST_W, POST_SPACING - 4, POST_W))
        for ry_off in (RAIL_GAP, RAIL_GAP * 2):
            pygame.draw.rect(surface, FC,
                             pygame.Rect(gate_right, YARD.bottom - ry_off - RAIL_H,
                                         YARD.right - gate_right, RAIL_H))

        # Gate posts (taller, highlighted)
        for gx in (gate_left, gate_right):
            pygame.draw.rect(surface, FC,
                             pygame.Rect(gx - POST_W // 2, YARD.bottom - 70, POST_W, 70))
            pygame.draw.line(surface, FHI,
                             (gx - POST_W // 2 + 3, YARD.bottom - 64),
                             (gx - POST_W // 2 + 3, YARD.bottom - 6), 1)

        # ─ East fence (world right edge — from top to south fence line) ─
        for py in range(YARD.y, YARD.bottom - POST_W, POST_SPACING):
            pygame.draw.rect(surface, FC,
                             pygame.Rect(YARD.right - POST_W, py, POST_W,
                                         min(POST_SPACING - 4, YARD.bottom - POST_W - py)))
        for ry in (YARD.y + RAIL_GAP, YARD.y + RAIL_GAP * 2, YARD.bottom - RAIL_GAP - 30):
            pygame.draw.rect(surface, FC,
                             pygame.Rect(YARD.right - POST_W - 4, ry, POST_W + 4, RAIL_H))

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
        for rect_data in (MAP_APPLE_TREE_RECT, MAP_OAK_TREE_RECT, MAP_EXTRA_OAK_RECT,
                          MAP_ORCHARD_TREE_1, MAP_ORCHARD_TREE_2):
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
        for rect_data in (MAP_APPLE_TREE_RECT, MAP_OAK_TREE_RECT, MAP_EXTRA_OAK_RECT,
                          MAP_ORCHARD_TREE_1, MAP_ORCHARD_TREE_2):
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

    def _draw_flower_patches(self, surface: pygame.Surface) -> None:
        """Scattered flower dots across the grass — purely decorative."""
        # Fixed positions spread across the world, avoiding structure zones
        flowers = [
            # (x, y, colour)
            (420, 120, (242, 210, 58)),   # yellow
            (680, 200, (255, 255, 255)),   # white
            (900, 140, (242, 210, 58)),
            (1450, 180, (255, 255, 255)),
            (1680, 200, (242, 210, 58)),
            (300, 620, (255, 255, 255)),
            (1500, 620, (242, 210, 58)),
            (1900, 580, (255, 255, 255)),
            (450, 900, (242, 210, 58)),
            (820, 950, (255, 255, 255)),
            (1650, 900, (242, 210, 58)),
            (2000, 880, (255, 255, 255)),
            (350, 1260, (242, 210, 58)),
            (1100, 1250, (255, 255, 255)),
            (1750, 1260, (242, 210, 58)),
        ]
        for fx, fy, fc in flowers:
            # 3 petals as small circles around a centre
            for i in range(5):
                a = math.radians(i * 72)
                px = int(fx + 5 * math.cos(a))
                py = int(fy + 5 * math.sin(a))
                pygame.draw.circle(surface, fc, (px, py), 3)
            pygame.draw.circle(surface, (218, 185, 52), (fx, fy), 3)  # yellow centre

    def _draw_sheep_pen(self, surface: pygame.Surface) -> None:
        r = pygame.Rect(*MAP_SHEEP_PEN_RECT)   # (380, 430, 280, 220)
        # Bright grass inside
        pygame.draw.rect(surface, COLOUR_PASTURE, r, border_radius=5)
        # Sheep
        for sx, sy in ((r.x+60, r.y+70), (r.x+160, r.y+60), (r.x+100, r.y+150), (r.x+210, r.y+145)):
            self._draw_sheep(surface, sx, sy)
        # Fence
        self._draw_fence(surface, r)

    def _draw_sheep(self, surface: pygame.Surface, cx: int, cy: int) -> None:
        # Fluffy wool body — cluster of overlapping circles
        for ox, oy in ((-8,0),(8,0),(0,-7),(0,7),(-5,-5),(5,-5),(-5,5),(5,5)):
            pygame.draw.circle(surface, COLOUR_SHEEP, (cx+ox, cy+oy), 9)
        pygame.draw.ellipse(surface, COLOUR_SHEEP, pygame.Rect(cx-12, cy-8, 24, 16))
        # Face / head
        pygame.draw.circle(surface, (215, 200, 185), (cx+14, cy-2), 7)
        pygame.draw.circle(surface, (45, 38, 30), (cx+16, cy-4), 2)  # eye
        # Legs — tiny dark stubs below body
        for lx in (cx-6, cx, cx+6):
            pygame.draw.line(surface, (148, 130, 105), (lx, cy+8), (lx, cy+14), 2)
        # Outline
        pygame.draw.ellipse(surface, (195, 188, 178), pygame.Rect(cx-12, cy-8, 24, 16), 1)

    def _draw_pond(self, surface: pygame.Surface) -> None:
        r = pygame.Rect(*MAP_POND_RECT)   # (1380, 820, 200, 130)
        cx, cy = r.centerx, r.centery
        # Outer dark rim
        pygame.draw.ellipse(surface, (62, 118, 168), r.inflate(8, 6))
        # Main water body
        pygame.draw.ellipse(surface, COLOUR_POND, r)
        # Lighter water highlight — upper-left
        pygame.draw.ellipse(surface, (118, 188, 235),
                            pygame.Rect(cx - r.width//3, cy - r.height//3,
                                        r.width//2, r.height//2))
        # Lily pad suggestions
        for lx, ly in ((cx-30, cy+10), (cx+35, cy-15), (cx+10, cy+30)):
            pygame.draw.circle(surface, (68, 148, 58), (lx, ly), 10)
            pygame.draw.circle(surface, (88, 172, 72), (lx, ly), 10, 2)
            pygame.draw.line(surface, (88, 172, 72), (lx, ly), (lx+6, ly-8), 1)
        # Reeds at edge
        for rx, ry in ((r.x+12, cy), (r.x+22, cy-18), (r.right-12, cy+8)):
            pygame.draw.line(surface, (98, 138, 72), (rx, ry+18), (rx, ry-18), 2)
            pygame.draw.ellipse(surface, (88, 112, 52),
                                pygame.Rect(rx-3, ry-18, 6, 10))
        # Ripple rings
        pygame.draw.ellipse(surface, (78, 148, 205), r, 2)
        pygame.draw.ellipse(surface, (78, 148, 205), r.inflate(-20, -14), 1)

    def _draw_scarecrow(self, surface: pygame.Surface) -> None:
        """
        "Clunky" style: bucket-head scarecrow in a black jacket.
        Arms outstretched, white gloves, red bow tie, tall top hat,
        smiley face painted on the tin-can head. Straw wisps everywhere.
        """
        r  = pygame.Rect(*MAP_SCARECROW_RECT)
        cx = r.centerx

        # Palette
        _BLACK   = ( 28,  24,  20)
        _JACKET  = ( 38,  34,  32)   # dark charcoal suit
        _BUCKET  = (172, 175, 178)   # tin-can grey
        _BUCKET_D = (138, 140, 144)  # darker grey for bucket shading
        _STRAW   = (205, 172,  62)   # bright wheat straw
        _GLOVE   = (245, 242, 235)   # off-white gloves
        _BOWTIE  = (210,  35,  35)   # red bow tie
        _FACE_PL = (200, 198, 195)   # face paint (slightly lighter than bucket)
        _SMILE   = ( 48,  38,  28)   # painted-on features

        # ── Wooden stake / post ──────────────────────────────────────
        stake_top = r.y + 90
        pygame.draw.rect(surface, COLOUR_TREE_TRUNK,
                         pygame.Rect(cx - 5, stake_top, 10, r.bottom - stake_top),
                         border_radius=2)
        pygame.draw.line(surface, (88, 58, 28), (cx - 5, stake_top), (cx - 5, r.bottom), 1)

        # ── Straw wisps from body / sleeves ─────────────────────────
        for sx, sy, ex, ey in [
            (r.x + 10, r.y + 90, r.x + 2,  r.y + 82),
            (r.x + 18, r.y + 88, r.x + 8,  r.y + 78),
            (r.right - 10, r.y + 90, r.right - 2,  r.y + 82),
            (r.right - 18, r.y + 88, r.right - 8,  r.y + 78),
            (cx - 6,  r.y + 88, cx - 12, r.y + 96),
        ]:
            pygame.draw.line(surface, _STRAW, (sx, sy), (ex, ey), 2)

        # ── Jacket body ─────────────────────────────────────────────
        jacket = pygame.Rect(cx - 36, r.y + 72, 72, 54)
        pygame.draw.rect(surface, _JACKET, jacket, border_radius=4)
        # Lapels (two angled white triangles suggest collar/lapels)
        pygame.draw.polygon(surface, (220, 218, 212), [
            (cx,      jacket.y + 2),
            (cx - 14, jacket.y + 18),
            (cx,      jacket.y + 22),
        ])
        pygame.draw.polygon(surface, (220, 218, 212), [
            (cx,      jacket.y + 2),
            (cx + 14, jacket.y + 18),
            (cx,      jacket.y + 22),
        ])
        pygame.draw.rect(surface, _BLACK, jacket, 2, border_radius=4)

        # ── Arms (outstretched wide, in jacket sleeves) ─────────────
        arm_shoulder_y = r.y + 82
        arm_end_y      = r.y + 88
        for arm_x in (r.x + 4, r.right - 4):
            pygame.draw.line(surface, _JACKET,
                             (cx, arm_shoulder_y), (arm_x, arm_end_y), 16)
            pygame.draw.line(surface, _BLACK,
                             (cx, arm_shoulder_y), (arm_x, arm_end_y), 1)

        # ── White gloves at arm ends ─────────────────────────────────
        for gx in (r.x + 2, r.right - 2):
            pygame.draw.circle(surface, _GLOVE, (gx, arm_end_y), 10)
            pygame.draw.circle(surface, (200, 198, 192), (gx, arm_end_y), 10, 1)
            # Thumb suggestion
            pygame.draw.circle(surface, _GLOVE, (gx + (6 if gx > cx else -6), arm_end_y - 4), 5)

        # ── Red bow tie ──────────────────────────────────────────────
        bty = r.y + 72
        pygame.draw.polygon(surface, _BOWTIE, [
            (cx - 16, bty - 5), (cx,      bty),     (cx - 16, bty + 5),
        ])
        pygame.draw.polygon(surface, _BOWTIE, [
            (cx + 16, bty - 5), (cx,      bty),     (cx + 16, bty + 5),
        ])
        pygame.draw.circle(surface, (175, 28, 28), (cx, bty), 4)   # bow knot

        # ── Straw wisps from hat ─────────────────────────────────────
        for hsx, hsy, hex_, hey in [
            (cx - 8, r.y + 12, cx - 14, r.y + 2),
            (cx,     r.y + 10, cx,      r.y - 2),
            (cx + 8, r.y + 12, cx + 14, r.y + 2),
            (cx - 4, r.y + 12, cx - 6,  r.y),
            (cx + 4, r.y + 12, cx + 6,  r.y),
        ]:
            pygame.draw.line(surface, _STRAW, (hsx, hsy), (hex_, hey), 2)

        # ── Top hat ──────────────────────────────────────────────────
        # Brim (wide flat ring)
        brim = pygame.Rect(cx - 28, r.y + 38, 56, 8)
        pygame.draw.rect(surface, _BLACK, brim, border_radius=2)
        pygame.draw.rect(surface, (55, 50, 46), brim, 1, border_radius=2)
        # Crown (tall rectangle)
        crown = pygame.Rect(cx - 20, r.y + 10, 40, 30)
        pygame.draw.rect(surface, _BLACK, crown, border_radius=3)
        # Hat band
        pygame.draw.rect(surface, (55, 50, 45),
                         pygame.Rect(cx - 20, r.y + 36, 40, 4))
        pygame.draw.rect(surface, (65, 60, 54), crown, 1, border_radius=3)

        # ── Bucket / tin-can head ────────────────────────────────────
        head_top = r.y + 38
        head_h   = 36
        head_w   = 44
        head = pygame.Rect(cx - head_w // 2, head_top, head_w, head_h)
        pygame.draw.rect(surface, _BUCKET, head, border_radius=4)
        # Shading (right side slightly darker)
        shade = pygame.Rect(head.centerx, head.y + 2, head.w // 2 - 2, head.h - 4)
        pygame.draw.rect(surface, _BUCKET_D, shade, border_radius=3)
        # Rim line at top and bottom of bucket
        pygame.draw.rect(surface, _BUCKET_D,
                         pygame.Rect(head.x, head.y, head.w, 4), border_radius=2)
        pygame.draw.rect(surface, _BUCKET_D,
                         pygame.Rect(head.x, head.bottom - 4, head.w, 4), border_radius=2)
        # Bucket outline
        pygame.draw.rect(surface, (110, 112, 116), head, 2, border_radius=4)

        # ── Painted-on smiley face ───────────────────────────────────
        face_cx   = cx
        face_ey   = head_top + 13   # eye y
        face_ny   = head_top + 20   # nose y

        # Eyes — two simple dark dots with white glint
        for ex in (face_cx - 10, face_cx + 10):
            pygame.draw.circle(surface, _SMILE, (ex, face_ey), 5)
            pygame.draw.circle(surface, _FACE_PL, (ex - 1, face_ey - 1), 2)

        # Nose — small rivet/circle
        pygame.draw.circle(surface, _SMILE, (face_cx, face_ny), 4)
        pygame.draw.circle(surface, _FACE_PL, (face_cx - 1, face_ny - 1), 1)

        # Smile — wide painted-on grin
        pygame.draw.arc(surface, _SMILE,
                        pygame.Rect(face_cx - 14, face_ny - 2, 28, 16),
                        math.pi, 2 * math.pi, 3)

        # Rosy cheeks
        for chx in (face_cx - 13, face_cx + 13):
            chk = pygame.Surface((10, 6), pygame.SRCALPHA)
            pygame.draw.ellipse(chk, (220, 120, 100, 80), chk.get_rect())
            surface.blit(chk, (chx - 5, face_ey + 2))

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
