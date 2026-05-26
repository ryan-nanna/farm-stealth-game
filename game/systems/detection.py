# game/systems/detection.py
# Vision-cone and noise-radius detection used by enemy NPCs.
# Pure functions — no game state, no settings imports — so they can be called
# with any entity's parameters and are trivial to unit-test.

from __future__ import annotations

import math

import pygame


def tractor_in_cone(
    dealer_center:      tuple[int, int],
    facing_angle_deg:   float,
    cone_range:         float,
    half_angle_deg:     float,
    tractor_rect:       pygame.Rect,
    full_cover_rects:   list[pygame.Rect],
    partial_cover_rects: list[pygame.Rect],
    partial_range_mult: float,
) -> bool:
    """
    Return True if the tractor is visible inside the dealer's vision cone.

    Full cover makes the tractor completely invisible.
    Partial cover reduces the effective range by partial_range_mult.
    """
    # Full cover → invisible to vision cone (noise still active)
    for rect in full_cover_rects:
        if tractor_rect.colliderect(rect):
            return False

    # Effective range — reduced in partial cover
    effective_range = cone_range
    for rect in partial_cover_rects:
        if tractor_rect.colliderect(rect):
            effective_range *= partial_range_mult
            break

    tx, ty = tractor_rect.center
    dx     = tx - dealer_center[0]
    dy     = ty - dealer_center[1]
    dist   = math.hypot(dx, dy)

    if dist > effective_range:
        return False

    # Angle between dealer's facing direction and the vector to the tractor
    target_angle_deg = math.degrees(math.atan2(dy, dx))
    delta = (target_angle_deg - facing_angle_deg + 180.0) % 360.0 - 180.0
    return abs(delta) <= half_angle_deg


def dealer_hears_noise(
    dealer_center:  tuple[int, int],
    tractor_center: tuple[int, int],
    noise_radius:   float,
) -> bool:
    """
    Return True if the dealer is within the tractor's noise radius.
    A noise_radius of 0 means the tractor is silent.
    Note: noise penetrates full cover — only vision is blocked by cover.
    """
    if noise_radius <= 0.0:
        return False
    return math.hypot(
        tractor_center[0] - dealer_center[0],
        tractor_center[1] - dealer_center[1],
    ) <= noise_radius
