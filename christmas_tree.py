import argparse
import os
import time
import copy

import numpy as np
from pyparsing import *


class bcolors:
    # \033 = \x1b
    CEND = '\033[0m'
    
    CBLACK  = '\33[30m'
    CRED    = '\33[31m'
    CGREEN  = '\33[32m'
    CYELLOW = '\33[33m'
    CBLUE   = '\33[34m'
    CVIOLET = '\33[35m'
    CBEIGE  = '\33[36m'
    CWHITE  = '\33[37m'
    
    CGREY    = '\33[90m'
    CRED2    = '\33[91m'
    CGREEN2  = '\33[92m'
    CYELLOW2 = '\33[93m'
    CBLUE2   = '\33[94m'
    CVIOLET2 = '\33[95m'
    CBEIGE2  = '\33[96m'
    CWHITE2  = '\33[97m'

    RGB = '\33[{r};{g};{b}m'


parser = argparse.ArgumentParser(description='ASCII Christmas tree',
                    formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-h1', '--tree-height', type=int, default=15,
                    help='The height of the tree\'s leaves.')
parser.add_argument('-h2', '--trunk-height', type=int, default=3,
                    help='The height of the tree\'s trunk.')
parser.add_argument('-w', '--trunk-width', type=int, default=7,
                    help='The width of the tree\'s trunk.')
parser.add_argument('-c', '--caption', type=str, default='Christmas!', dest='subcaption',
                    help='The caption below the tree. This will be appended after "Merry".\n'
                    f'The color is fixed to {bcolors.CGREEN}green{bcolors.CEND}. So it is recommended to edit it directly in the code.')
parser.add_argument('-i', '--interval', type=float, default=.7,
                    help='The interval in seconds in-between loops.')
args = parser.parse_args()


console_width = os.get_terminal_size().columns - 1
center = console_width // 2
caption = f'{bcolors.CRED}Merry{bcolors.CEND} {bcolors.CGREEN}{args.subcaption}{bcolors.CEND}'

ESC = Literal('\x1b')
integer = Word(nums)
escapeSeq = Combine(ESC + '[' + Optional(delimitedList(integer,';')) + oneOf(list(alphas)))
nonAnsiString = lambda s: Suppress(escapeSeq).transformString(s)
C = lambda r, g, b: bcolors.RGB.format(r=r, g=g, b=b)

sky_height = 2

leaf_elems = ['*', '^', 'o', 'O', '~', ',', '.']
leaf_weights = np.array([7, 5, 4, 3, 1, 2, 1], dtype=np.float32)
leaf_weights /= leaf_weights.sum()
leaf_colors = [bcolors.CGREEN2, bcolors.CGREEN]
leaf_color_weights = np.array([8, 5], dtype=np.float32)
leaf_color_weights /= leaf_color_weights.sum()
deco_colors = [bcolors.CRED, bcolors.CYELLOW, bcolors.CBLUE, bcolors.CVIOLET, bcolors.CBEIGE]
leaf = lambda elem, color=bcolors.CGREEN2: f'{color}{elem}{bcolors.CEND}'
trunk_cell = f'{bcolors.CYELLOW}@{bcolors.CEND}'

snow_offset = 3
snow_height = 2

figure_width = 2 * (args.tree_height + snow_offset) + 1
figure_height = sky_height + args.tree_height + args.trunk_height + snow_height
figure_center = figure_width // 2
figure_offset = (console_width - figure_width) // 2


def get_initial_figure():
    figure = []
    for i in range(sky_height):
        row = [' '] * figure_width
        figure.append(row)
    for i in range(args.tree_height):
        leaves = np.random.choice(leaf_elems, 2*i+1, p=leaf_weights).tolist()
        blank = [' '] * (figure_center - i)
        row = blank + leaves + blank
        figure.append(row)
    for i in range(args.trunk_height):
        trunk = [trunk_cell] * args.trunk_width
        blank = [' '] * (figure_center - args.trunk_width//2)
        row = blank + trunk + blank
        figure.append(row)
    for i in range(snow_height):
        row = ['*'] * figure_width
        figure.append(row)
    figure[sky_height][figure_center] = '★'
    return figure


def colorize_leaves(figure):
    for i in range(sky_height, sky_height+args.tree_height):
        for j in range(figure_center-i, figure_center+i+1):
            elem = figure[i][j]
            if elem in ['o', 'O']:
                color, = np.random.choice(deco_colors, 1)
            else:
                color, = np.random.choice(leaf_colors, 1, p=leaf_color_weights)
            figure[i][j] = f'{color}{elem}{bcolors.CEND}'


def generate_snows(snows):
    snow_gen_rate = .1
    if len(snows) == figure_height - snow_height:
        snows.pop(0)
    snows += [
        np.where(
            np.random.choice(2, figure_width, p=[1-snow_gen_rate, snow_gen_rate])
        )[0]
    ]


def draw_snows(figure, snows):
    for row_fig, snow_idxs in zip(figure, snows[::-1]):
        for snow_idx in snow_idxs:
            row_fig[snow_idx] = '*'


def display_figure(figure):
    for row in figure:
        print(' ' * figure_offset + ''.join(row))


def display_caption(caption):
    print(' '*(center-len(nonAnsiString(caption))//2), end='')
    print(caption)


init_figure = get_initial_figure()
snows = []
while True:
    figure = copy.deepcopy(init_figure)
    colorize_leaves(figure)
    generate_snows(snows)
    draw_snows(figure, snows)
    os.system('cls') if os.name=='nt' else os.system('clear')
    display_figure(figure)
    print('\n\n')
    display_caption(caption)
    time.sleep(args.interval)
