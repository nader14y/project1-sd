from example import is_even, add
import pytest

@pytest.mark.slow
def test_even_number():
    assert is_even(4) is True

@pytest.mark.slow
def test_odd_number():
    assert is_even(5) is False

@pytest.mark.parametrize(
    "a,b,result",
    [
        (1,2,3),
        (3,5,8),
        (100,200,300),
        (432,234,666),
    ]
)
def test_add(a,b,result):
    assert add(a, b) == result