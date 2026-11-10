import curses
import time
import random

SHIP = "▲"
ENEMY = "ψ"
BULLET = "|"
STAR = "✦"
LIVES = 3
ROUNDS = 10

# i need to fix this later but whatever
temp_debug = 0
# TODO: fix the enemy spawn its too hard after round 4

def setup_colors():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)

def draw_ship(stdscr, ship_x, height, has_wingmen):
    if has_wingmen and ship_x - 2 > 0:
        stdscr.addstr(height - 2, ship_x - 2, SHIP, curses.color_pair(5))
    stdscr.addstr(height - 2, ship_x, SHIP, curses.color_pair(1))
    if has_wingmen and ship_x + 2 < curses.COLS - 1:
        stdscr.addstr(height - 2, ship_x + 2, SHIP, curses.color_pair(5))

def draw_enemies(stdscr, enemies):
    for (y, x) in enemies:
        stdscr.addstr(y, x, ENEMY, curses.color_pair(2))

def draw_bullets(stdscr, bullets):
    for (y, x) in bullets:
        stdscr.addstr(y, x, BULLET, curses.color_pair(3))

def draw_star(stdscr, star):
    if star:
        stdscr.addstr(star[0], star[1], STAR, curses.color_pair(5))

def draw_hud(stdscr, score, lives, width, round_num, has_wingmen):
    if has_wingmen:
        hud = f" SCORE: {score}    LIVES: {'♥ ' * lives}   ROUND: {round_num}/{ROUNDS}  WINGMEN ACTIVE"
    else:
        hud = f" SCORE: {score}    LIVES: {'♥ ' * lives}   ROUND: {round_num}/{ROUNDS}"
    stdscr.addstr(0, 0, hud[:width - 1], curses.color_pair(2))
    # used to have a border here but it looked bad

def draw_round_banner(stdscr, height, width, round_num):
    stdscr.clear()
    msg = f"ROUND {round_num}"
    # idk why 5 works but it does
    stdscr.addstr(height // 2 - 1, width // 2 - len(msg) // 2, msg, curses.color_pair(5) | curses.A_BOLD)
    stdscr.addstr(height // 2 + 1, width // 2 - 5, "GET READY", curses.color_pair(1))
    stdscr.refresh()
    time.sleep(2)

def draw_game_over(stdscr, height, width, score):
    stdscr.clear()
    stdscr.addstr(height // 2 - 1, width // 2 - 4, "GAME OVER", curses.color_pair(4) | curses.A_BOLD)
    stdscr.addstr(height // 2 + 1, width // 2 - 6, f"SCORE: {score}", curses.color_pair(4) | curses.A_BOLD)
    stdscr.addstr(height // 2 + 3, width // 2 - 5, "PRESS Q", curses.color_pair(1))
    stdscr.refresh()
    while True:
        if stdscr.getch() == ord('q'):
            break

def draw_you_win(stdscr, height, width, score):
    stdscr.clear()
    stdscr.addstr(height // 2 - 1, width // 2 - 3, "YOU WIN", curses.color_pair(5) | curses.A_BOLD)
    stdscr.addstr(height // 2 + 1, width // 2 - 6, f"SCORE: {score}", curses.color_pair(5) | curses.A_BOLD)
    stdscr.addstr(height // 2 + 3, width // 2 - 5, "PRESS Q", curses.color_pair(1))
    stdscr.refresh()
    while True:
        if stdscr.getch() == ord('q'):
            break

def enemies_for_round(round_num):
    # this gets intense at level 10
    return 3 * (2 ** (round_num - 1))

def spawn_round_enemies(height, width, count):
    enemies = []
    for i in range(count):
        x = random.randint(1, width - 2)
        y = random.randint(1, height // 4)
        enemies.append([y, x])
    return enemies

def spawn_star(height, width):
    x = random.randint(2, width - 3)
    return [1, x]

def move_enemies(enemies, height):
    for e in enemies:
        e[0] += 1
    enemies[:] = [e for e in enemies if e[0] < height - 2]

def move_bullets(bullets):
    for b in bullets:
        b[0] -= 1
    bullets[:] = [b for b in bullets if b[0] > 1]

def move_star(star):
    if star:
        star[0] += 1
    return star

def check_collisions(bullets, enemies):
    score = 0
    for b in bullets[:]:
        for e in enemies[:]:
            if b[0] == e[0] and b[1] == e[1]:
                bullets.remove(b)
                enemies.remove(e)
                score += 10
                break
    return score

# used youtube should be good for the collision
def check_star_caught(star, ship_x, height):
    if star and star[0] >= height - 3 and abs(star[1] - ship_x) <= 1:
        return True
    return False

# i think this works? tested it a bit
def check_enemy_hit_player(enemies, ship_x, height, has_wingmen):
    for e in enemies[:]:
        if e[0] >= height - 2:
            enemies.remove(e)
            return True
        if e[0] == height - 2 and e[1] == ship_x:
            enemies.remove(e)
            return True
        if has_wingmen:
            if e[0] == height - 2 and e[1] == ship_x - 2:
                enemies.remove(e)
                return True
            if e[0] == height - 2 and e[1] == ship_x + 2:
                enemies.remove(e)
                return True
    return False

def shoot(bullets, ship_x, height, has_wingmen):
    bullets.append([height - 3, ship_x])
    if has_wingmen:
        if ship_x - 2 > 0:
            bullets.append([height - 3, ship_x - 2])
        if ship_x + 2 < curses.COLS - 1:
            bullets.append([height - 3, ship_x + 2])

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    setup_colors()

    height, width = stdscr.getmaxyx()
    ship_x = width // 2
    score = 0
    lives = LIVES
    round_num = 1
    has_wingmen = False
    
    # testing value - remove later
    # enemies = 5

    while round_num <= ROUNDS:
        draw_round_banner(stdscr, height, width, round_num)

        enemies = spawn_round_enemies(height, width, enemies_for_round(round_num))
        bullets = []
        star = None
        tick = 0

        while enemies or star:
            stdscr.clear()

            if star is None and tick % 50 == 0:
                star = spawn_star(height, width)

            if tick % 10 == 0:
                star = move_star(star)
                if star and star[0] >= height - 2:
                    star = None

            if has_wingmen == False and check_star_caught(star, ship_x, height):
                has_wingmen = True
                star = None

            if tick % 20 == 0:
                move_enemies(enemies, height)

            move_bullets(bullets)
            score = score + check_collisions(bullets, enemies)

            if check_enemy_hit_player(enemies, ship_x, height, has_wingmen):
                lives = lives - 1
                if lives <= 0:
                    draw_game_over(stdscr, height, width, score)
                    return

            draw_ship(stdscr, ship_x, height, has_wingmen)
            draw_enemies(stdscr, enemies)
            draw_bullets(stdscr, bullets)
            draw_star(stdscr, star)
            draw_hud(stdscr, score, lives, width, round_num, has_wingmen)

            stdscr.refresh()

            key = stdscr.getch()

            if key == ord('q'):
                return
            elif key == ord(' '):
                shoot(bullets, ship_x, height, has_wingmen)
            elif key == ord('a') and ship_x > 2:
                ship_x = ship_x - 1
            elif key == ord('d') and ship_x < width - 3:
                ship_x = ship_x + 1

            tick = tick + 1
            time.sleep(0.05)

        round_num = round_num + 1

    draw_you_win(stdscr, height, width, score)

curses.wrapper(main)
#im going to sleep Mr southwood too tired