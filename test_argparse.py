import argparse as ap

def make_parser():
    # Parse arguments
    parser = ap.ArgumentParser(description='Hexo Web Builder!')

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('-s', '--server', action='store_true', default = False, help='open local server')
    group1.add_argument('-p', '--push', action='store_true', default = False, help='push to GitHub')

    parser.add_argument('-c', '--chatgpt', type=str, metavar='keyword', nargs='+', help='open chatgpt mode')
    parser.add_argument('-d', '--debug', action='store_true', default = False, help='open debug mode')
    parser.add_argument('-r', '--rebuild', action='store_true', default = False,help='re-build project')
    # Choose the setting file from ./customize/input_settings/
    parser.add_argument('-n', '--new', action='store_true', default = False, help='Create a new project according to setting file.')
    # Choose the setting file from ./saved_set/
    parser.add_argument('saved_set_file', type=str, help='use saved setting file which been created before.')
    return parser

if __name__ == '__main__':
    p = make_parser()
    a = p.parse_args()
    for ele in a.chatgpt:
        print(ele.encode('utf-8').decode('utf-8'))
        with open('ta.txt', '+w', encoding='utf-8') as f:
            f.write(ele)