import pytest
import tyko.utils

good_test_data = [
    ("1993", 1),
    ("11-1950", 2),
    ("11-26-1993", 3),
    ("11-06-1993", 3),
    ("01-06-1993", 3),
]
@pytest.mark.parametrize("date, expected", good_test_data)
def test_date_identify_precision(date, expected):
    assert tyko.utils.identify_precision(date) == expected

bad_test_data = [
    "11-46-1993",
    "31-6-1993"
]

@pytest.mark.parametrize("date", bad_test_data)
def test_date_identify_bad_precision(date):
    with pytest.raises(AttributeError):
        assert tyko.utils.identify_precision(date)

