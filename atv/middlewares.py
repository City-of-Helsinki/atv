from services.models import Service


class ServiceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not hasattr(request, "service"):
            request.service = None

        # Only get the service for authenticated users
        user = request.user

        # TODO: Once we set up the Tunnistamo instance and helusers, we should check
        #  properly that the user is authenticated and authorised
        # The superuser is excluded from the check, since they should always get
        # full access to all resources.
        if user and user.is_authenticated and not user.is_superuser:
            # TODO: while we set up the proper authentication with Tunnistamo,
            #  we fetch the Service according to which group the user belongs to.
            group = user.groups.first()

            if group:
                service = Service.objects.filter(name=group.name).first()
                request.service = service

        return self.get_response(request)
