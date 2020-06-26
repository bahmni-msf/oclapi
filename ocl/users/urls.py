from django.conf.urls import patterns, url, include

from collection.views import OrganizationCollectionListView
from orgs.views import OrganizationListView
from sources.views import OrganizationSourceListView
from users.models import UserProfile
from users.views import UserListView, UserDetailView, UserReactivateView, UserLoginView, UserSignUpView
from oclapi.models import NAMESPACE_PATTERN

__author__ = 'misternando'

urlpatterns = patterns('',
    url(r'^signup/$', UserSignUpView.as_view(), name='userprofile-signup'),
    url(r'^signup/verify-email/(?P<verification_token>[^/]+)/$', UserSignUpView.as_view(), name='userprofile-signup-verify-email'),
    url(r'^$', UserListView.as_view(), name='userprofile-list'),
    url(r'^login/$', UserLoginView.as_view(), name='user-login'),
    url(r'^(?P<user>' + NAMESPACE_PATTERN + ')/$', UserDetailView.as_view(), name='userprofile-detail'),
    url(r'^(?P<user>' + NAMESPACE_PATTERN + ')/reactivate/$', UserReactivateView.as_view(), name='userprofile-reactivate'),
    url(r'^(?P<user>' + NAMESPACE_PATTERN + ')/orgs/$', OrganizationListView.as_view(), {'related_object_type': UserProfile, 'related_object_kwarg': 'user'}, name='userprofile-orgs'),
    url(r'^(?P<user>' + NAMESPACE_PATTERN + ')/orgs/sources/$', OrganizationSourceListView.as_view(), name='userprofile-organization-source-list'),
    url(r'^(?P<user>' + NAMESPACE_PATTERN + ')/orgs/collections/$', OrganizationCollectionListView.as_view(), name='userprofile-organization-collection-list'),
    url(r'^(?P<user>' + NAMESPACE_PATTERN + ')/sources/', include('sources.urls')),
    url(r'^(?P<user>' + NAMESPACE_PATTERN + ')/collections/', include('collection.urls'))
)

