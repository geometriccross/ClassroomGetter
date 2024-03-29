from functools import wraps
from pathlib import Path
from random import choice
from re import sub, match
from string import ascii_letters, digits
from typing import Any, Callable, Iterable, SupportsInt
from itertools import groupby


def higher_order(func):
    """
        与えられた関数をlambdaで包み、返す。このラムダ関数は可変長引数を受け取るが、それらは実際には使われずに捨てられるため注意すること。\n
        これはpipeなどの演算子と共に使う際に必要である。\n        
    """
    @wraps(func)
    def _wrapper(*args, **kwargs):
        def _inner(*_):
            return func(*args, **kwargs)
        return _inner
    return _wrapper
    
def text_filter(value: str) -> str:
    def __remove(value: str, patterns: list[str], pattern_count: int = 0) -> str:
        if pattern_count == len(patterns):
            return value
        
        removeed_value = sub(patterns[pattern_count], '', value)
        return __remove(removeed_value, patterns, pattern_count + 1)
        
    brackets_pattern = '[\(（].+?[\)）]' #括弧とその中のものが指定される
    year_pattern = '[A-Z一-龠]?.*[0-9一二三四五六七八九十]' #HogeHoge令和五年度HogeHogeでは、令和五のみ指定される
    nendo_pattern = '[年度]'
    space_pattern = '[\s　]' #半角全角スペースが指定される
    
    all_pattern = [brackets_pattern, year_pattern, nendo_pattern, space_pattern]
    
    if any([x in value for x in ['.pdf', '.mp3', '.mp4', '.jpg', '.png', '.mov']]):
        return value
    else:
        return __remove(value, all_pattern)

def identity(*x):
    if len(x) == 1:
        return x[0]
    else:
        return x
    
def left(x = None):
    def func(f = identity):
        f(x)
        return x
    return func

def is_none(default, fail_case):
    if default is None:
        if isinstance(fail_case, Callable):
            return is_none(fail_case(), None)
        else:
            return fail_case
    else:
        if isinstance(default, Callable):
            return is_none(default(), fail_case)
        else:
            return default

def splitparN(iterable, N=3):
    for _, item in groupby(enumerate(iterable), lambda x: x[0] // N):
        yield (x[1] for x in item)
                
def public_vars(x) -> dict[str, Any]:
    return dict([(k, v) for k, v in vars(x).items() if match('.*__', k) is None])

def randstr(length: SupportsInt) -> str:
    return ''.join(choice(ascii_letters + digits) for _ in range(length))

def get_geometory(widget) -> str:
    return f'{widget.winfo_width()}x{widget.winfo_height()}'

def size_to_geometory(width: int, height: int) -> str:
    return f'{width}x{height}'

class Infix:
    def __init__(self, function):
        self.function = function

    def __ror__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))

    def __or__(self, other):
        return self.function(other)

    def __call__(self, value1, value2):
        return self.function(value1, value2)
            
pipe = Infix(lambda x, func: func(x) if x is not None else func()) #関数の返値を次の関数の引数にするもの
arrow = Infix(lambda x, func: left(x)(func)) #最初に指定された対象を常にいじるもの