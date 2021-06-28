from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class BusinessIDValidator(RegexValidator):
    regex = r"^[0-9]{7}\-[0-9]{1}\Z"
    message = _("Enter a valid business ID.")
