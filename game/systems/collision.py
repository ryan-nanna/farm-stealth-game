# game/systems/collision.py
# Cover-zone overlap detection.
# Wall-collision resolution lives in Tractor.update() (per-axis, per entity)
# because each entity type may need slightly different behaviour.

from __future__ import annotations

import pygame


def check_cover(
    entity_rect: pygame.Rect,
    full_cover_rects: list[pygame.Rect],
    partial_cover_rects: list[pygame.Rect],
) -> tuple[bool, bool]:
    """
    Return (is_fully_hidden, is_in_partial_cover) for the given rect.
    Full cover is checked first; if matched, partial is reported False
    because full cover already implies the stronger protection.
    """
    for rect in full_cover_rects:
        if entity_rect.colliderect(rect):
            return True, False
    for rect in partial_cover_rects:
        if entity_rect.colliderect(rect):
            return False, True
    return False, False
