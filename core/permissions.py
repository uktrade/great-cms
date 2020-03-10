from rest_framework import permissions


class HasNoCompany(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.company is None


class HasCompany(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.company is not None
