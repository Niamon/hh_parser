import argparse
import sys
import os

# папка где main.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from main import main as main_function


def run():
    parser = argparse.ArgumentParser(
        description="Скрипт запуска программы без ручного ввода."
    )

    parser.add_argument(
        "--query",
        type=str,
        required=False,
        help="Поисковый запрос для получения вакансий"
    )

    args = parser.parse_args()

    if args.query:

        def fake_input(prompt=""):
            return args.query

        __builtins__.input = fake_input


    main_function()


if __name__ == "__main__":
    run()
