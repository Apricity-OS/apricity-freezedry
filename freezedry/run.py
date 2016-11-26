import argparse

from freezedry.load_config import load_config


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--load', dest='fnm', type=str,
                        help='file name to load')
    parser.add_argument('--user', action='store_true')
    parser.add_argument('--root', action='store_true')
    parser.add_argument('--livecd', action='store_true')
    parser.add_argument('--disable', action='append', default=[])
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    if args.fnm:
        mode = []
        if args.user:
            mode.append('user')
        if args.root:
            mode.append('root')
        if len(mode) == 0:
            mode = ['user', 'root']
        load_config(args.fnm, mode,
                    livecd=args.livecd,
                    disable=args.disable)
    else:
        raise Exception('Please enter a valid mode')


if __name__ == '__main__':
    main()
