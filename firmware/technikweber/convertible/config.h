// Copyright 2026 TechnikWeber
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

// Hintergrundbeleuchtung auf GP21 (Gate des AO3400A).
// RP2040 bildet GPIO n auf Slice (n / 2) % 8 ab, Kanal A bei geradem, B bei
// ungeradem Pin: GP21 -> 21/2 = 10, 10 % 8 = 2 -> PWMD2, Kanal B.
#define BACKLIGHT_PWM_DRIVER PWMD2
#define BACKLIGHT_PWM_CHANNEL RP2040_PWM_CHANNEL_B
