# game/level.py
# Static farm map: geometry, cover zones, objective zones, and rendering.
# draw_ground() is called before entities; draw_canopies() is called after,
# so tree canopies appear in front of the tractor when it hides under them.

from __future__ import annotations

import pygame

from game.settings import (
    COLOUR_BARN_RED,
    COLOUR_COOP,
    COLOUR_COVER_FULL,
    COLOUR_COVER_PARTIAL,
    COLOUR_DARK_GREY,
    COLOUR_DIRT,
    COLOUR_FENCE,
    COLOUR_GRASS_GREEN,
    COLOUR_PASTURE,
    COLOUR_PIG_PEN,
    COLOUR_SHED,
    COLOUR_STONE,
    COLOUR_TREE_CANOPY,
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
    MAP_OAK_TREE_RECT,
    MAP_OLD_SHED_RECT,
    MAP_PATH_LEFT_RECT,
    MAP_PATH_RIGHT_RECT,
    MAP_PIG_PEN_RECT,
    MAP_SCARECROW_RECT,
    MAP_WALL_CENTRE_RECT,
    MAP_WALL_LEFT_RECT,
    MAP_WALL_RIGHT_RECT,
    MAP_WELL_RECT,
    SCREEN_WIDTH,
)


class Level:
    """
    Holds all static map data: cover zones, wall rects, objective zones.
    Draws itself each frame as coloured shapes (no sprite art yet).

    wall_rects is the collision list queried by Tractor.update() each frame.
    full_cover_rects / partial_cover_rects are queried by the detection system (Session 5+).
    """

    def __init__(self) -> None:
        # Collision walls — tractor (and later dealers) cannot pass through these
        self.wall_rects: list[pygame.Rect] = [
            pygame.Rect(*MAP_WALL_LEFT_RECT),
            pygame.Rect(*MAP_WALL_CENTRE_RECT),
            pygame.Rect(*MAP_WALL_RIGHT_RECT),
        ]

        # Full cover: tractor invisible to vision cone when inside
        self.full_cover_rects: list[pygame.Rect] = [
            pygame.Rect(*MAP_APPLE_TREE_RECT),
            pygame.Rect(*MAP_OAK_TREE_RECT),
            pygame.Rect(*MAP_CHICKEN_COOP_RECT),
            pygame.Rect(*MAP_OLD_SHED_RECT),
            pygame.Rect(*MAP_PIG_PEN_RECT),
        ]

        # Partial cover: vision-cone range reduced 60% when tractor is inside
        self.partial_cover_rects: list[pygame.Rect] = [
            pygame.Rect(*MAP_WALL_LEFT_RECT),
            pygame.Rect(*MAP_WALL_CENTRE_RECT),
            pygame.Rect(*MAP_WALL_RIGHT_RECT),
            pygame.Rect(*MAP_WELL_RECT),
            pygame.Rect(*MAP_SCARECROW_RECT),
        ]

        # Key zone rects used by objective / win-condition logic (Sessions 6-7)
        self.barn_rect:        pygame.Rect = pygame.Rect(*MAP_BARN_RECT)
        self.cow_pasture_rect: pygame.Rect = pygame.Rect(*MAP_COW_PASTURE_RECT)
        self.scarecrow_rect:   pygame.Rect = pygame.Rect(*MAP_SCARECROW_RECT)
        self.pig_pen_rect:     pygame.Rect = pygame.Rect(*MAP_PIG_PEN_RECT)

    # ------------------------------------------------------------------
    # Draw — two-pass so entities sit between ground and canopy layers
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

    def _draw_background(self, surface: pygame.Surface) -> None:
        surface.fill(COLOUR_GRASS_GREEN)
        # Dirt trails through the two wall gaps — drawn before structures so
        # walls render on top, leaving the gap visible as a ground-level path.
        pygame.draw.rect(surface, COLOUR_DIRT, pygame.Rect(*MAP_PATH_LEFT_RECT))
        pygame.draw.rect(surface, COLOUR_DIRT, pygame.Rect(*MAP_PATH_RIGHT_RECT))
        # Entry road at the bottom edge where dealers arrive each round
        pygame.draw.rect(
            surface,
            COLOUR_DIRT,
            pygame.Rect(0, MAP_ENTRY_Y, SCREEN_WIDTH, MAP_ENTRY_HEIGHT),
        )

    def _draw_zones(self, surface: pygame.Surface) -> None:
        # Cow pasture — brighter grass with wooden fence border
        pasture = pygame.Rect(*MAP_COW_PASTURE_RECT)
        pygame.draw.rect(surface, COLOUR_PASTURE, pasture)
        pygame.draw.rect(surface, COLOUR_FENCE, pasture, 4)

        # Pig pen — muddy ground with fence
        pen = pygame.Rect(*MAP_PIG_PEN_RECT)
        pygame.draw.rect(surface, COLOUR_PIG_PEN, pen)
        pygame.draw.rect(surface, COLOUR_FENCE, pen, 4)

    def _draw_structures(self, surface: pygame.Surface) -> None:
        self._draw_stone_wall(surface)
        self._draw_coop(surface)
        self._draw_shed(surface)
        self._draw_well(surface)
        self._draw_barn(surface)

    def _draw_barn(self, surface: pygame.Surface) -> None:
        r = pygame.Rect(*MAP_BARN_RECT)
        pygame.draw.rect(surface, COLOUR_BARN_RED, r, border_radius=4)
        # Roof ridge — a white horizontal stripe across the centre
        ridge = pygame.Rect(r.x + 10, r.centery - 5, r.width - 20, 10)
        pygame.draw.rect(surface, COLOUR_WHITE, ridge)
        # Double barn doors on the south face
        door_w, door_h = 38, 30
        door = pygame.Rect(r.centerx - door_w // 2, r.bottom - door_h, door_w, door_h)
        pygame.draw.rect(surface, COLOUR_WOOD_DARK, door)
        pygame.draw.line(surface, COLOUR_DARK_GREY, door.midtop, door.midbottom, 2)
        # White trim
        pygame.draw.rect(surface, COLOUR_WHITE, r, 3, border_radius=4)

    def _draw_coop(self, surface: pygame.Surface) -> None:
        r = pygame.Rect(*MAP_CHICKEN_COOP_RECT)
        pygame.draw.rect(surface, COLOUR_COOP, r, border_radius=3)
        # Small entrance hole on the right face
        hole = pygame.Rect(r.right - 10, r.centery - 8, 10, 16)
        pygame.draw.rect(surface, COLOUR_DARK_GREY, hole)
        pygame.draw.rect(surface, COLOUR_FENCE, r, 3, border_radius=3)

    def _draw_shed(self, surface: pygame.Surface) -> None:
        r = pygame.Rect(*MAP_OLD_SHED_RECT)
        pygame.draw.rect(surface, COLOUR_SHED, r, border_radius=3)
        # Slightly darker roof strip along the top edge
        roof_colour = (
            max(0, COLOUR_SHED[0] - 25),
            max(0, COLOUR_SHED[1] - 25),
            max(0, COLOUR_SHED[2] - 25),
        )
        roof = pygame.Rect(r.x, r.y, r.width, 20)
        pygame.draw.rect(surface, roof_colour, roof, border_radius=3)
        # Door on the left face
        door = pygame.Rect(r.x + 8, r.bottom - 38, 24, 38)
        pygame.draw.rect(surface, COLOUR_WOOD_DARK, door)
        pygame.draw.rect(surface, COLOUR_FENCE, r, 3, border_radius=3)

    def _draw_well(self, surface: pygame.Surface) -> None:
        r = pygame.Rect(*MAP_WELL_RECT)
        pygame.draw.rect(surface, COLOUR_WELL, r, border_radius=6)
        # Small bucket suggestion at the top
        pygame.draw.circle(surface, COLOUR_DARK_GREY, r.midtop, 8)
        pygame.draw.rect(surface, COLOUR_DARK_GREY, r, 2, border_radius=6)

    def _draw_stone_wall(self, surface: pygame.Surface) -> None:
        for wall_data in (MAP_WALL_LEFT_RECT, MAP_WALL_CENTRE_RECT, MAP_WALL_RIGHT_RECT):
            r = pygame.Rect(*wall_data)
            pygame.draw.rect(surface, COLOUR_STONE, r)
            # Horizontal mortar line through the middle
            mid_y = r.y + r.height // 2
            pygame.draw.line(surface, COLOUR_DARK_GREY, (r.x, mid_y), (r.right, mid_y), 1)
            # Vertical stone-block divisions every 40 px
            for bx in range(r.x + 40, r.right, 40):
                pygame.draw.line(surface, COLOUR_DARK_GREY, (bx, r.y), (bx, r.bottom), 1)
            pygame.draw.rect(surface, COLOUR_DARK_GREY, r, 2)

    # ------------------------------------------------------------------
    # Vegetation — split into two passes (trunks before entities, canopies after)
    # ------------------------------------------------------------------

    def _draw_tree_trunks(self, surface: pygame.Surface) -> None:
        for rect_data in (MAP_APPLE_TREE_RECT, MAP_OAK_TREE_RECT):
            r = pygame.Rect(*rect_data)
            trunk_w = max(12, r.width // 5)
            trunk_h = max(18, r.height // 3)
            trunk = pygame.Rect(r.centerx - trunk_w // 2, r.bottom - trunk_h, trunk_w, trunk_h)
            pygame.draw.rect(surface, COLOUR_TREE_TRUNK, trunk, border_radius=2)

    def _draw_tree_canopies(self, surface: pygame.Surface) -> None:
        for rect_data in (MAP_APPLE_TREE_RECT, MAP_OAK_TREE_RECT):
            r = pygame.Rect(*rect_data)
            radius = min(r.width, r.height) // 2 - 4
            pygame.draw.circle(surface, COLOUR_TREE_CANOPY, r.center, radius)
            hl_colour = (
                min(255, COLOUR_TREE_CANOPY[0] + 30),
                min(255, COLOUR_TREE_CANOPY[1] + 30),
                min(255, COLOUR_TREE_CANOPY[2] + 10),
            )
            hl_pos = (r.centerx - radius // 4, r.centery - radius // 4)
            pygame.draw.circle(surface, hl_colour, hl_pos, max(4, radius // 3))

    def _draw_scarecrow(self, surface: pygame.Surface) -> None:
        r = pygame.Rect(*MAP_SCARECROW_RECT)
        post_w = 8
        # Vertical post
        pygame.draw.rect(surface, COLOUR_TREE_TRUNK, pygame.Rect(r.centerx - post_w // 2, r.y, post_w, r.height))
        # Horizontal crossbar (one-third from top)
        bar_y = r.y + r.height // 3
        pygame.draw.rect(surface, COLOUR_TREE_TRUNK, pygame.Rect(r.x, bar_y - post_w // 2, r.width, post_w))
        # Head
        head_r = 10
        pygame.draw.circle(surface, COLOUR_WHEAT, (r.centerx, r.y + head_r), head_r)
        pygame.draw.circle(surface, COLOUR_DARK_GREY, (r.centerx, r.y + head_r), head_r, 2)

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
        # Key objective / safe-zone outlines
        for rect in (self.barn_rect, self.cow_pasture_rect, self.scarecrow_rect, self.pig_pen_rect):
            pygame.draw.rect(surface, (0, 150, 255), rect, 2)
