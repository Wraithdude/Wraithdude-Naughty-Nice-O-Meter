import pygame
import sys
import math
import random

pygame.init()
pygame.mixer.init()

# Base resolution
BASE_WIDTH, BASE_HEIGHT = 1440, 3120
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h
scale = screen_height / BASE_HEIGHT

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Naughty or Nice Scanner")

# Load and scale images
def load_scaled(path):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))

layer1 = load_scaled("scanner-layer1.png")
layer2 = load_scaled("scanner-layer2.png")
layer3 = load_scaled("scanner-layer3.png")
layer4 = load_scaled("scanner-layer4.png")
start_btn = load_scaled("button-start.png")
reset_btn = load_scaled("button-reset.png")
scanning_img = load_scaled("result-scanning.png")
title_img = load_scaled("title.png")

result_images = {
    "naughty": load_scaled("result-naughty.png"),
    "naughtyish": load_scaled("result-naughtyish.png"),
    "ontheline": load_scaled("result-ontheline.png"),
    "nice": load_scaled("result-nice.png"),
    "wow": load_scaled("result-wow.png")
}

# Load sounds
click_sound = pygame.mixer.Sound("click.wav")
scan_sound = pygame.mixer.Sound("scan.wav")
naughty_sound = pygame.mixer.Sound("naughty.wav")
ontheline_sound = pygame.mixer.Sound("ontheline.wav")
nice_sound = pygame.mixer.Sound("nice-bell.wav")
def show_title_sequence():
    fade_duration = 500
    hold_duration = 5000
    crossfade_duration = 500

    black = pygame.Surface((screen_width, screen_height))
    black.fill((0, 0, 0))

    # Fade in
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < fade_duration:
        elapsed = pygame.time.get_ticks() - start_time
        alpha = int(255 * elapsed / fade_duration)
        title_img.set_alpha(alpha)
        screen.blit(black, (0, 0))
        screen.blit(title_img, ((screen_width - title_img.get_width()) // 2, 0))
        pygame.display.update()
        pygame.time.delay(16)

    # Hold
    title_img.set_alpha(255)
    screen.blit(title_img, ((screen_width - title_img.get_width()) // 2, 0))
    pygame.display.update()
    pygame.time.delay(hold_duration)

    # Fade out
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < fade_duration:
        elapsed = pygame.time.get_ticks() - start_time
        alpha = 255 - int(255 * elapsed / fade_duration)
        title_img.set_alpha(alpha)
        screen.blit(black, (0, 0))
        screen.blit(title_img, ((screen_width - title_img.get_width()) // 2, 0))
        pygame.display.update()
        pygame.time.delay(16)

    # Crossfade to app
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < crossfade_duration:
        elapsed = pygame.time.get_ticks() - start_time
        alpha = int(255 * elapsed / crossfade_duration)
        app_frame = pygame.Surface((screen_width, screen_height))
        app_frame.fill((0, 0, 0))  # Placeholder for app background
        app_frame.set_alpha(alpha)
        screen.blit(black, (0, 0))
        screen.blit(app_frame, (0, 0))
        pygame.display.update()
        pygame.time.delay(16)
# Positioning
center_x = int(screen_width / 2)
gauge_center = (center_x, int(566 * scale))
reset_center = (center_x, int(1791 * scale))
start_center = (center_x, int(2295 * scale))

gauge_rect = layer2.get_rect(center=gauge_center)
reset_rect = reset_btn.get_rect(center=reset_center)
start_rect = start_btn.get_rect(center=start_center)
result_rect = reset_rect.copy()

needle_pivot = (1277, 376)

# Animation variables
angle = 0
target_angle = 0
animating = False
animation_start_time = 0
scan_trigger_time = 0
chaos_duration = 6500
windup_duration = 500
settle_duration = 2417
chaos_interval = 600
chaos_phase_start = 0
chaos_start_angle = 0
chaos_target_angle = 0

windup_angle = 0
windup_complete = False
settle_start_time = 0

# Transition flags
result_ready = False
holding_result = False
resetting = False
reset_start_time = 0
reset_duration = 700

# Scanning overlay
scanning_fade_start_time = 0
scanning_fade_duration = 550
scan_total_duration = 10417
input_locked = False
scanning_alpha = 0

# Crossfade logic
crossfade_active = False
crossfade_start_time = 0
crossfade_duration = 500

# Result mapping
result_angles = {
    "naughty": -70,
    "naughtyish": -20,
    "ontheline": 0,
    "nice": 20,
    "wow": 70
}

fade_in_result = False
result_sound_played = False
result = None
title_shown = False

clock = pygame.time.Clock()
running = True

# 🎬 Show title sequence once
if not title_shown:
    show_title_sequence()
    title_shown = True
while running:
    dt = clock.tick(60)
    current_time = pygame.time.get_ticks()

    if input_locked and current_time - scan_trigger_time > scan_total_duration:
        input_locked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and not input_locked:
            if start_rect.collidepoint(event.pos) and result and not animating and not result_ready:
                click_sound.play()
                scan_sound.play()
                scan_trigger_time = current_time
                animation_start_time = current_time + 1250
                chaos_phase_start = animation_start_time
                chaos_start_angle = angle
                chaos_target_angle = random.uniform(-70, 70)
                animating = True
                result_ready = False
                windup_complete = False
                input_locked = True
                scanning_fade_start_time = current_time
                scanning_alpha = 0
                result_sound_played = False
                crossfade_active = False

            elif reset_rect.collidepoint(event.pos) and not result_ready:
                click_sound.play()
                zone_width = reset_rect.width // 5
                local_x = event.pos[0] - reset_rect.left
                zone_index = local_x // zone_width
                result_keys = list(result_angles.keys())
                if 0 <= zone_index < len(result_keys):
                    result = result_keys[zone_index]
                    target_angle = result_angles[result]
                    angle = 0
                    animating = False
                    result_ready = False
                    print(f"Secretly selected: {result}")

            elif result_ready and holding_result:
                resetting = True
                reset_start_time = current_time
                holding_result = False
    # Animate needle
    if animating and current_time >= animation_start_time:
        elapsed = current_time - animation_start_time
        if elapsed < chaos_duration:
            chaos_elapsed = current_time - chaos_phase_start
            chaos_progress = min(chaos_elapsed / chaos_interval, 1)
            eased = math.sin(chaos_progress * math.pi / 2)
            angle = chaos_start_angle * (1 - eased) + chaos_target_angle * eased

            if chaos_elapsed >= chaos_interval:
                chaos_phase_start = current_time
                chaos_start_angle = angle
                chaos_target_angle = random.uniform(-70, 70)

        elif not windup_complete:
            windup_elapsed = elapsed - chaos_duration
            progress = min(windup_elapsed / windup_duration, 1)
            eased = math.sin(progress * math.pi / 2)

            if windup_elapsed == 0:
                windup_angle = -target_angle if target_angle != 0 else random.choice([-70, 70])

            angle = angle * (1 - eased) + windup_angle * eased

            if progress >= 1:
                windup_complete = True
                settle_start_time = current_time

        elif elapsed < chaos_duration + windup_duration + settle_duration:
            settle_elapsed = current_time - settle_start_time
            progress = min(settle_elapsed / settle_duration, 1)
            eased = 1 - (1 - progress) ** 2
            angle = angle * (1 - eased) + target_angle * eased

            if not result_sound_played:
                if result in ["naughty", "naughtyish"]:
                    naughty_sound.play()
                elif result == "ontheline":
                    ontheline_sound.play()
                elif result in ["nice", "wow"]:
                    nice_sound.play()
                result_sound_played = True

        else:
            angle = target_angle
            animating = False
            result_ready = True
            crossfade_active = True
            crossfade_start_time = current_time
            windup_complete = False

    # Draw layers
    rotated_needle = pygame.transform.rotate(layer3, -angle)
    needle_rect = rotated_needle.get_rect(center=needle_pivot)

    screen.blit(layer1, ((screen_width - layer1.get_width()) // 2, 0))
    screen.blit(layer2, gauge_rect)
    screen.blit(rotated_needle, needle_rect)
    screen.blit(layer4, ((screen_width - layer4.get_width()) // 2, 0))
    screen.blit(start_btn, start_rect)
    # Scanning overlay fade-in
    if input_locked and scanning_fade_start_time and not crossfade_active and not fade_in_result:
        elapsed = current_time - scanning_fade_start_time
        fade_progress = min(elapsed / scanning_fade_duration, 1)
        scanning_alpha = int(255 * fade_progress)
        reset_btn.set_alpha(int(255 * (1 - fade_progress)))
        temp_scan = scanning_img.copy()
        temp_scan.set_alpha(scanning_alpha)
        screen.blit(reset_btn, reset_rect)
        screen.blit(temp_scan, result_rect)

    # Crossfade scanning → result
    elif crossfade_active and result in result_images:
        elapsed = current_time - crossfade_start_time
        progress = min(elapsed / crossfade_duration, 1)
        scan_alpha = int(255 * (1 - progress))
        result_alpha = int(255 * progress)

        temp_scan = scanning_img.copy()
        temp_scan.set_alpha(scan_alpha)
        temp_result = result_images[result].copy()
        temp_result.set_alpha(result_alpha)

        screen.blit(temp_scan, result_rect)
        screen.blit(temp_result, result_rect)

        if progress >= 1:
            crossfade_active = False
            holding_result = True
            hold_start_time = current_time

    # Hold result image
    elif holding_result and result in result_images:
        result_images[result].set_alpha(255)
        screen.blit(result_images[result], result_rect)
        if current_time - hold_start_time > 15000:
            resetting = True
            reset_start_time = current_time
            holding_result = False

    # Reset fade-out result → fade-in reset button
    elif resetting:
        elapsed = current_time - reset_start_time
        fade_progress = min(elapsed / reset_duration, 1)
        result_images[result].set_alpha(int(255 * (1 - fade_progress)))
        reset_btn.set_alpha(int(255 * fade_progress))
        screen.blit(result_images[result], result_rect)
        screen.blit(reset_btn, reset_rect)

        if fade_progress >= 1:
            result = None
            result_ready = False
            resetting = False
            angle = 0

    # Default reset button display
    else:
        screen.blit(reset_btn, reset_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
