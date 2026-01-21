from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """
    Allows access to superusers.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class IsAdmin(BasePermission):
    """
    Allows access to admin.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.groups.filter(name='admin').exists()


class IsEventOrganizer(BasePermission):
    """
    Allows access to studio manager.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.groups.filter(
            name='event_organizer').exists()


class IsAdminOrSuperUser(BasePermission):
    """
    Allows access to admin and superusers.
    """

    def has_permission(self, request, view):
        return (
                request.user and request.user.is_authenticated and (
                request.user.is_superuser or
                request.user.groups.filter(name='admin').exists()
        )
        )


class IsAdminOrEventOrganizerOrSuperUser(BasePermission):
    """
    Allows access to admin, studio managers, and superusers.
    """

    def has_permission(self, request, view):
        return (
                request.user and request.user.is_authenticated and (
                request.user.is_superuser or
                request.user.groups.filter(name='admin').exists() or
                request.user.groups.filter(name='event_organizer').exists()
        )
        )


class IsOwnerOrAdminOrSuperUser(BasePermission):
    """
    Allows access to the owner of the object, admin, and superusers.
    """

    def has_object_permission(self, request, view, obj):
        return (
                request.user and request.user.is_authenticated and (
                request.user.is_superuser or
                request.user.groups.filter(name='admin').exists() or
                obj == request.user
        )
        )