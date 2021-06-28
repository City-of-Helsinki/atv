import pytest
from django.core.exceptions import ValidationError

from documents.validators import BusinessIDValidator


@pytest.mark.parametrize(
    "business_id,passes",
    [
        ("1234567-8", True),
        ("12345678", False),
        ("abcdefg-h", False),
        ("AbbaAcDc", False),
    ],
)
def test_business_id_validator(business_id, passes):
    validator = BusinessIDValidator()

    if passes:
        validator(business_id)
    else:
        with pytest.raises(ValidationError):
            validator(business_id)
