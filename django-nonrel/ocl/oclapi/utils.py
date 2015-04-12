from boto.s3.connection import S3Connection
from django.conf import settings
from django.core.urlresolvers import NoReverseMatch
from rest_framework.reverse import reverse

__author__ = 'misternando'


class S3ConnectionFactory:
    s3_connection = None

    @classmethod
    def get_s3_connection(cls):
        if not cls.s3_connection:
            cls.s3_connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        return cls.s3_connection

    @classmethod
    def get_export_bucket(cls):
        conn = cls.get_s3_connection()
        return conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)


def reverse_resource(resource, viewname, args=None, kwargs=None, request=None, format=None, **extra):
    """
    Generate the URL for the view specified as viewname of the object specified as resource.
    """
    kwargs = kwargs or {}
    parent = resource
    while parent is not None:
        if not hasattr(parent, 'get_url_kwarg'):
            return NoReverseMatch('Cannot get URL kwarg for %s' % resource)
        kwargs.update({parent.get_url_kwarg(): parent.mnemonic})
        parent = parent.parent if hasattr(parent, 'parent') else None
    return reverse(viewname, args, kwargs, request, format, **extra)


def reverse_resource_version(resource, viewname, args=None, kwargs=None, request=None, format=None, **extra):
    """
    Generate the URL for the view specified as viewname of the object that is versioned by the object specified as resource.
    Assumes that resource extends ResourceVersionMixin, and therefore has a versioned_object attribute.
    """
    kwargs = kwargs or {}
    kwargs.update({
        resource.get_url_kwarg(): resource.mnemonic
    })
    return reverse_resource(resource.versioned_object, viewname, args, kwargs, request, format, **extra)


def add_user_to_org(userprofile, organization):
    transaction_complete = False
    if not userprofile.id in organization.members:
        try:
            organization.members.append(userprofile.id)
            userprofile.organizations.append(organization.id)
            organization.save()
            userprofile.save()
            transaction_complete = True
        finally:
            if not transaction_complete:
                userprofile.organizations.remove(organization.id)
                organization.members.remove(userprofile.id)
                userprofile.save()
                organization.save()


def remove_user_from_org(userprofile, organization):
    transaction_complete = False
    if userprofile.id in organization.members:
        try:
            organization.members.remove(userprofile.id)
            userprofile.organizations.remove(organization.id)
            organization.save()
            userprofile.save()
            transaction_complete = True
        finally:
            if not transaction_complete:
                userprofile.organizations.add(organization.id)
                organization.members.add(userprofile.id)
                userprofile.save()
                organization.save()
