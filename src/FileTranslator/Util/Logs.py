class _FontColor:
    _ESC = "\033"
    RESET = f"{_ESC}[0m"
    BOLD = f"{_ESC}[1m"
    BLACK = f"{_ESC}[30m"
    RED = f"{_ESC}[31m"
    GREEN = f"{_ESC}[32m"
    YELLOW = f"{_ESC}[33m"
    BLUE = f"{_ESC}[34m"
    MAGENTA = f"{_ESC}[35m"
    CYAN = f"{_ESC}[36m"
    GREY = f"{_ESC}[37m"


# Elements can be concatenated: {BLACK}{BOLD} - black bold font


_logs_file: None
_is_release: bool


def init(logs_path: str, is_release: bool):
    global _logs_file, _is_release
    _logs_file = open(logs_path, "w")
    _is_release = is_release


def user(msg: str, flush: bool = False):
    if len(msg) == 0:
        msg = "USER_LOG WITH EMPTY MESSAGE"
    splitted = msg.split("\n")

    # log
    if _logs_file is not None:
        _logs_file.write(f"[log] {splitted[0]}\n")
        for line in splitted[1:]:
            _logs_file.write(f"      {line}\n")

    # console
    fmt1 = lambda ln: f"[log] {ln}"
    fmt2 = lambda ln: f"      {ln}"
    print(fmt1(splitted[0]), flush=flush)
    for line in splitted[1:]:
        print(fmt2(line), flush=flush)


def dev(msg: str, flush: bool = True):
    if len(msg) == 0:
        msg = "DEV_LOG WITH EMPTY MESSAGE"
    splitted = msg.split("\n")

    # log
    if _logs_file is not None:
        _logs_file.write(f"[dev] {splitted[0]}\n")
        for line in splitted[1:]:
            _logs_file.write(f"      {line}\n")

    # console
    if not _is_release:
        fmt1 = lambda ln: f"{_FontColor.MAGENTA}[dev]{_FontColor.RESET} {ln}"
        fmt2 = lambda ln: f"      {ln}"
        print(fmt1(splitted[0]), flush=flush)
        for line in splitted[1:]:
            print(fmt2(line), flush=flush)


def warning(msg: str, flush: bool = True):
    if len(msg) == 0:
        msg = "WARNING WITH EMPTY MESSAGE"
    splitted = msg.split("\n")

    # log
    if _logs_file is not None:
        _logs_file.write(f"[warning] {splitted[0]}\n")
        for line in splitted[1:]:
            _logs_file.write(f"          {line}\n")

    # console
    fmt1 = lambda ln: f"{_FontColor.YELLOW}[warning]{_FontColor.RESET} {ln}"
    fmt2 = lambda ln: f"          {ln}"
    print(fmt1(splitted[0]), flush=flush)
    for line in splitted[1:]:
        print(fmt2(line), flush=flush)


def error(msg: str, flush: bool = True):
    text = f"{_FontColor.RED}{msg}{_FontColor.RESET}"
    if _logs_file is not None:
        _logs_file.write(text)
    print(text, flush=flush)
