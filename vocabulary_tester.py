import click
from operator import itemgetter
from pathlib import Path
from typing import List
import numpy as np
import pandas as pd
import random


def loop(words, langs, max_count, random_language: bool = True):
    words = np.array(words)
    mistakes = set()
    for i, k in enumerate(np.random.choice(len(words), size=max_count, replace=False)):
        idx = random.randint(0, 1) if random_language else 0
        other_idx = abs(idx - 1)
        word = words[k, idx]

        while True:
            answer = input(f'({i+1:3d}/{max_count}). [{langs[k][idx]}] {word} => [{langs[k][other_idx]}] ')
            if len(answer) == 0:
                print(f'\tYou must enter something...')
            else:
                break
        expected = words[k, other_idx]
        
        answer = answer.strip()
        if answer != expected:
            if answer.lower() == expected.lower():
                print(f'\tWatch out for capitalisation. Correct was "{expected}"')
            elif answer.replace(' ', '') == expected.replace(' ', ''):
                print(f'\tWatch out for extra spaces in the answer')
            else:
                mistakes.add((word, answer, expected, idx, other_idx))
                print(f'\tWrong! Correct was "{expected}"')

    return mistakes


def process_words(words: str):
    words = words.strip()
    for k, v in  {'’': "'",}.items():
        words = words.replace(k, v)
    return words

def read_words_file(file_name):
    words = []
    with file_name.open('r') as fr:
        for line in fr:
            words.append(tuple(map(process_words, line.replace('\n', '').split(';'))))
    return words


@click.command()
@click.argument('who', type=str)
def run(who):
    base_dir = Path(__file__).parent / who
    words = read_words_file(base_dir / 'words.txt')
    mistakes_file = base_dir / 'mistakes.txt'
    extra_words = []
    try:
        # Add previous mistakes one more time
        extra_words = read_words_file(Path(mistakes_file))
    except FileNotFoundError as e:
        pass

    for w in extra_words:
        if w in words:
            words.append(w)
        else:
            print(f'Words from mistakes not found in the list: {w}')

    for i, w in enumerate(words):
        if len(w) != 2:
            raise ValueError(f'Error on line {i}: {w}')

    langs = ('Fr', 'De')
    max_count = len(words)
    if max_count > 100:
        if input(f'There are {len(words)} words. Would you like to test all? [y/n] ').lower() != 'y':
            max_count = 100

    mistakes = loop(words, [langs] * len(words), max_count)

    print("\n\n")
    if len(mistakes) == 0:
        print(f"Congratulations!!! You got everything right. Keep it up.")
        return

    perc = int((1. - float(len(mistakes)) / max_count) * 100)
    print(f"You got {perc}% right from {max_count} words with {len(mistakes)} mistakes.")
    print(f"Let's test only the words you got wrong?\n")
    idxs = select_tuple(mistakes, 3, 4)
    langs = [(langs[l[0]], langs[l[1]]) for l in idxs]
    new_mistakes = loop(select_tuple(mistakes, 0, 2), langs, len(mistakes), random_language=False)
    wrong_count = len(new_mistakes)
    print('')
    if wrong_count == 0:
        print(f'Very cool! Now you got them all right.')
    elif wrong_count < len(mistakes):
        print(f'This time you got only {wrong_count} wrong. Keep at it')
    else:
        print(f'Still {wrong_count} mistakes. Here is a summary of all that you got wrong:')
        print(pd.DataFrame(select_tuple(mistakes, 0, 1, 2), columns=['Word', 'Answer', 'Correct']))

    with Path(mistakes_file).open('w') as fw:
        for m in mistakes:
            list_ = [''] * 2
            list_[m[3]] = m[0]
            list_[m[4]] = m[2]
            fw.write(';'.join(list_))
            fw.write('\n')

def select_tuple(input_: List[tuple], *args):
    return [tuple(itemgetter(*args)(i)) for i in input_]


if __name__ == '__main__':
    run()