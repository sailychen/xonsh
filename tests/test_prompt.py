from unittest.mock import Mock

import pytest

from xonsh.environ import Env
from xonsh.prompt.base import PromptFormatter


@pytest.fixture
def formatter(xonsh_builtins):
    return PromptFormatter()


@pytest.mark.parametrize('formatter_dict', [{
    'a_string': 'cat',
    'none': (lambda: None),
    'f': (lambda: 'wakka'),
}])
@pytest.mark.parametrize('inp, exp', [
    ('my {a_string}', 'my cat'),
    ('my {none}{a_string}', 'my cat'),
    ('{f} jawaka', 'wakka jawaka'),
])
def test_format_prompt(inp, exp, formatter_dict, formatter, xonsh_builtins):
    obs = formatter(template=inp, formatter_dict=formatter_dict)
    assert exp == obs


@pytest.mark.parametrize('formatter_dict', [{
    'a_string': 'cats',
    'a_number': 7,
    'empty': '',
    'current_job': (lambda: 'sleep'),
    'none': (lambda: None),
}])
@pytest.mark.parametrize('inp, exp', [
    ('{a_number:{0:^3}}cats', ' 7 cats'),
    ('{current_job:{} | }xonsh', 'sleep | xonsh'),
    ('{none:{} | }{a_string}{empty:!}', 'cats!'),
    ('{none:{}}', ''),
    ('{{{a_string:{{{}}}}}}', '{{cats}}'),
    ('{{{none:{{{}}}}}}', '{}'),
])
def test_format_prompt_with_format_spec(inp, exp, formatter_dict,
                                        formatter, xonsh_builtins):
    obs = formatter(template=inp, formatter_dict=formatter_dict)
    assert exp == obs


def test_format_prompt_with_broken_template(formatter, xonsh_builtins):
    for p in ('{user', '{user}{hostname'):
        assert formatter(p) == p

    # '{{user' will be parsed to '{user'
    for p in ('{{user}', '{{user'):
        assert 'user' in formatter(p)


@pytest.mark.parametrize('inp', [
    '{user',
    '{{user',
    '{{user}',
    '{user}{hostname',
    ])
def test_format_prompt_with_broken_template_in_func(inp, formatter, xonsh_builtins):
    # '{{user' will be parsed to '{user'
    assert '{user' in formatter(lambda: inp)


def test_format_prompt_with_invalid_func(formatter, xonsh_builtins):
    xonsh_builtins.__xonsh_env__ = Env()

    def p():
        foo = bar  # raises exception # noqa
        return '{user}'

    assert isinstance(formatter(p), str)


def test_format_prompt_with_func_that_raises(formatter, capsys, xonsh_builtins):
    xonsh_builtins.__xonsh_env__ = Env()
    template = 'tt {zerodiv} tt'
    exp = 'tt (ERROR:zerodiv) tt'
    formatter_dict = {'zerodiv': lambda: 1/0}
    obs = formatter(template, formatter_dict)
    assert exp == obs
    out, err = capsys.readouterr()
    assert 'prompt: error' in err


def test_promptformatter_cache(formatter):
    spam = Mock()
    spam.return_value = 'eggs'
    template = '{spam} and {spam}'
    formatter_dict = {'spam': spam}

    formatter(template, formatter_dict)

    assert spam.call_count == 1


def test_promptformmater_clears_cache(formatter):
    spam = Mock()
    spam.return_value = 'eggs'
    template = '{spam} and {spam}'
    formatter_dict = {'spam': spam}

    formatter(template, formatter_dict)
    formatter(template, formatter_dict)

    assert spam.call_count == 2
