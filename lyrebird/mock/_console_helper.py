from colorama import Fore, Style

from . import context


def tag_green(msg):
    if not msg:
        return ''
    return f'{Fore.GREEN}[{msg}]{Style.RESET_ALL}'


def tag_yello(msg):
    if not msg:
        return ''
    return f'{Fore.YELLOW}[{msg}]{Style.RESET_ALL}'


def warning_msg(*msg, check_verbose=False):
    print(f'{Fore.YELLOW}lyrebird', *msg, Style.RESET_ALL)


def mock_msg(*msg, check_verbose=False):
    print(f'{Fore.GREEN}lyrebird{Style.RESET_ALL}', *msg)


def err_msg(*msg, check_verbose=False):
    print(f'{Fore.RED}lyrebird Error{Style.RESET_ALL}', *msg)


def url_color(line):
    return f'{Fore.BLUE}{line}{Style.RESET_ALL}'


def statistic_msg(*msg, check_verbose=False):
    print(f'{Fore.RED}[STATISTIC_MSG]{Style.RESET_ALL}', *msg)
