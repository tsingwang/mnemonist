import argparse

from .app import MnemonistApp
from .profile import profile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", dest="user", help="Use the user account.")
    args = parser.parse_args()

    if args.user:
        profile.current_user = args.user
    else:
        MnemonistApp().run()


if __name__ == '__main__':
    main()
