#!/usr/bin/env python
"""
Simple ncurses based game-of-life implementation
(https://en.wikipedia.org/wiki/Conway's_Game_of_Life)

Keys:
'q' quits the program
'p' pauses the loop
'+' speeds up the animation
'-' slows it down
Enter or Space at any time stops the current grid and restarts with a new one

It wraps borders both horizontally and vertically, and detects true
equilibrium as well as 'constant change' (oscillators) and offers to
re-seed the grid accordingly.

You can give a percentage of cells that should be marked as alive initially
as an argument to this program.
For example:

./gol.py 10

On your average 16:9 monitor, I find a 10% seed yields the most visually
satisfying result.

Author: Erik Ljungstrom, 2015
"""

import curses
import random
import sys

# Percent of cells that we should randomise as being alive (alive_c).
# Note that the same cell may be randomised twice, so even if you
# give 100 as a value here, all cells may not be marked as alive.
seed_percentage = 10

# Number of ms to sleep between iterations.
sleep_interval = 10

dead_c = '-'
alive_c = 'x'

x_padding = 1
y_padding = 7

stdscr = None


class ResizeError(Exception):
    """ Raised when we encounter an error due to the window/grid being
    resized mid-flight
    """
    def __init__(self, msg):
        super(ResizeError, self).__init__(msg)
        self.msg = msg


def draw(grid):
    """ Iterates through our grid and draws the values on the screen """

    # Start at 1 to keep our borders intact
    y_cnt = 1
    x_cnt = 1
    for row in grid:
        for value in row:
            color = 2 if value is alive_c else 1
            try:
                stdscr.addstr(y_cnt, x_cnt, value, curses.color_pair(color))
            except curses.error:
                raise ResizeError
            x_cnt += 1
        x_cnt = 1
        y_cnt += 1
    stdscr.refresh()


def wrap_border(x, y, grid):
    """ Detects border collision and adjusts
        x and/or y to wrap to the other side
    """

    rows = len(grid)
    cols = len(grid[0])

    if x >= cols:
        x = x - cols
    elif x < 0:
        x = cols + x

    if y >= rows:
        y = y - rows
    elif y < 0:
        y = rows + y

    return (x, y)


def get_coordinate_value(x, y, grid):
    """ Returns the value (dead or alive) of a cell at any given coordinate """
    x, y = wrap_border(x, y, grid)

    if grid[y][x] == alive_c:
        return True

    return False


def sum_adjecent_fields(x, y, grid):
    """ Returns the number of cells adjecent to x, y that are alive """

    sum_fields = 0

    if get_coordinate_value(x - 1, y, grid):
        sum_fields += 1
    if get_coordinate_value(x - 1, y - 1, grid):
        sum_fields += 1
    if get_coordinate_value(x - 1, y + 1, grid):
        sum_fields += 1

    if get_coordinate_value(x + 1, y, grid):
        sum_fields += 1
    if get_coordinate_value(x + 1, y - 1, grid):
        sum_fields += 1
    if get_coordinate_value(x + 1, y + 1, grid):
        sum_fields += 1

    if get_coordinate_value(x, y - 1, grid):
        sum_fields += 1
    if get_coordinate_value(x, y + 1, grid):
        sum_fields += 1

    return sum_fields


def decide_fate(x, y, sum_fields, grid):
    """ Considers the adjecent fields and the state of the cell itself
    to determine whether the cell at x, y will live or die
    """
    is_alive = get_coordinate_value(x, y, grid)
    if is_alive:
        sum_fields += 1

    if sum_fields == 3:
        return alive_c
    if sum_fields == 4:
        return alive_c if is_alive else dead_c

    return dead_c


def set_up_grid(seed_grid=True):
    """ Sets up a two dimensional list which holds our grid. The dimensions are
    determined by our window size.
    Optionally the grid can be seeded with alive cells
    """
    cols, rows = get_grid_dimensions()
    seeds = int((seed_percentage / 100.0) * (rows * cols))

    grid = []
    for _ in xrange(0, rows + 1):
        grid.append([dead_c for x in xrange(0, cols + 1)])

    if seed_grid:
        for _ in xrange(0, seeds):
            y = random.randint(0, rows - 1)
            x = random.randint(0, cols - 1)
            grid[y][x] = alive_c

    """ Uncomment for a glider example.. You will also want to
    comment out the regular seed above
    """
    """
    if seed_grid:
        grid[rows/2-4][2] = alive_c
        grid[rows/2-3][2] = alive_c
        grid[rows/2-2][2] = alive_c
        grid[rows/2-4][1] = alive_c
        grid[rows/2-2][0] = alive_c
    """

    """ Uncomment for a toad oscillator """
    """
    if seed_grid:
        grid[rows/2+1][cols/2+1] = alive_c
        grid[rows/2+1][cols/2+2] = alive_c
        grid[rows/2+1][cols/2+3] = alive_c
        grid[rows/2][cols/2+2] = alive_c
        grid[rows/2][cols/2+3] = alive_c
        grid[rows/2][cols/2+4] = alive_c
        grid[rows/2][cols/2+1] = alive_c  # Uncomment for a neat flower
    """
    """ Border wrapping test x-wise"""
    """
    if seed_grid:
        grid[0][0] = alive_c
        grid[0][1] = alive_c
        grid[0][2] = alive_c
    """

    """ Border wrapping test y-wise"""
    """
    if seed_grid:
        grid[rows-13][0] = alive_c
        grid[rows-12][0] = alive_c
        grid[rows-11][0] = alive_c
    """

    return grid


def check_for_extinction(grid):
    for row in grid:
        for col in row:
            if col == alive_c:
                return False
    return True


def pause():
    stdscr.nodelay(0)
    c = stdscr.getch()
    if c == ord('q'):
        graceful_exit()
    stdscr.nodelay(1)


def put_msg(screen, msg, offset_y, offset_x=1):
    """ Puts a message in the given window. Offset is a number of lines from
    the last line of the window.
    """
    max_y, _ = screen.getmaxyx()

    try:
        screen.addstr(max_y - offset_y, offset_x+1, msg)
    except curses.error as ex:
        if "addstr" in ex:
            raise ResizeError
    screen.refresh()


def get_grid_dimensions():
    """ Returns number of rows and cols the grid should have in order
    to fit the window
    """
    max_y, max_x = stdscr.getmaxyx()
    grid_x = max_x - x_padding - 2
    grid_y = max_y - y_padding - 3
    return (grid_x, grid_y)


def check_input():
    """ Checks for key-presses during the main loop.
        Returns True if user wants to re-seed, which leads
        main() returning.
    """
    global sleep_interval

    q = stdscr.getch()
    if q == ord('q'):
        graceful_exit()
    if q == ord('p'):
        pause()
    if q == ord('-'):
        sleep_interval += 50
    if q == ord('+'):
        sleep_interval = sleep_interval - 50 \
            if sleep_interval - 50 >= 0 else 0
    if q == curses.KEY_RESIZE:
        return True
    elif q in [10, 32]:
        return True


def add_help(pad):
    """ Places the help in the messages pad down """
    put_msg(pad,
            "Press 'q' at any time to quit, 'p' to pause",
            y_padding - 1)
    put_msg(pad,
            "      '+' to speed up and '-' to slow down",
            y_padding - 2)
    put_msg(pad,
            "      Enter or space to re-seed the grid",
            y_padding - 3)


def main():
    """ Main loop """
    max_y, max_x = stdscr.getmaxyx()
    # Some padding

    messages = stdscr.subpad(y_padding, max_x-x_padding-1,
                             max_y-y_padding-1, x_padding)
    messages.clear()
    messages.refresh()
    add_help(messages)

    messages.border()

    grid = set_up_grid()
    draw(grid)

    grandfather_grid = []
    iterations = 0

    iter_counter_active = True
    changed = False

    try:
        while True:
            y = 0
            x = 0
            next_grid = set_up_grid(seed_grid=False)
            for row in grid:
                for _ in row:

                    try:
                        sum_fields = sum_adjecent_fields(x, y, grid)
                        new_value = decide_fate(x, y, sum_fields, grid)
                        if new_value != grid[y][x]:
                            changed = True
                        next_grid[y][x] = new_value
                    except IndexError:
                        # This happens when we're resized while in the loop
                        return

                    x += 1

                x = 0
                y += 1

            if iterations % 2 == 0:
                grandfather_grid = grid

            grid = next_grid
            draw(grid)

            put_msg(messages, "Iterations: %d" % iterations, y_padding-4)

            if check_input():
                return

            if not changed:
                if check_for_extinction(grid):
                    msg = ("All cells are dead. Try increasing the"
                           "seed percentage!")
                else:
                    msg = "True equilibrium achieved! "
                put_msg(messages, msg, y_padding - 5)
                pause()
                return

            if next_grid == grandfather_grid:
                msg = ("Grid is as stable as it will ever be."
                       " Press Enter to seed a new grid.")
                put_msg(messages, msg, y_padding - 5)
                iter_counter_active = False

            if iter_counter_active:
                iterations += 1

            changed = False
            curses.napms(sleep_interval)
    except ResizeError:
        return


def graceful_exit(msg=None):
    reset_term()
    if msg:
        print msg
    exit(0)


def reset_term():
    try:
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        curses.curs_set(1)
        stdscr.keypad(0)
    except curses.error:
        print ("Unable to initialise ncurses. Are you using a terminal from"
               " the 60's?")
        print ex
        exit(1)
    except NameError:
        pass


def init_curses():
    global stdscr
    stdscr = curses.initscr()

    y, x = stdscr.getmaxyx()
    if y < 24 or x < 80:
        graceful_exit("Your terminal is too small to run this program in a"
                      " decent manner. It must be at least 24x80. Yours"
                      " is %dx%d" % (y, x))
    stdscr.nodelay(1)
    stdscr.leaveok(1)
    stdscr.border()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(1)
    return stdscr


if __name__ == '__main__':
    try:
        if sys.argv[1]:
            seed_percentage = int(sys.argv[1])
    except (IndexError, ValueError):
        pass

    try:
        while True:
            stdscr = init_curses()
            main()
            reset_term()

    except KeyboardInterrupt:
        reset_term()
    except Exception as ex:
        reset_term()
        import traceback
        traceback.print_exc()
        raise ex
