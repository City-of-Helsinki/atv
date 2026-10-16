from helusers.user_utils import oidc_to_user_data

PII_FIELDS = ("first_name", "last_name", "email")


def store_user_details(response, user=None, new_association=False, *args, **kwargs):
    """Save PII that User.clean() stripped before the social auth link existed."""
    if not user or not new_association:
        return

    data = oidc_to_user_data(response)
    for field in PII_FIELDS:
        if field in data:
            setattr(user, field, data[field])
    user.save(update_fields=PII_FIELDS)
