# Django Libraries
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

# Portal App Views
from cloudscape.portal.ui.app.auth.views import AuthView
from cloudscape.portal.ui.app.admin.views import AdminView
from cloudscape.portal.ui.app.home.views import HomeView
from cloudscape.portal.ui.app.hosts.views import HostsView
from cloudscape.portal.ui.app.formula.views import FormulaView

# URL Pattern Matching
urlpatterns = patterns('',
                       
    # Default redirect to home view
    url(r'^$', RedirectView.as_view(url=reverse_lazy('auth'))),
    
    # Portal authentication
    url(r'^auth$', AuthView.as_view(), name='auth'),
    
    # Administration
    url(r'^admin.*$', AdminView.as_view(), name='admin'),
    
    # Portal home view
    url(r'^home$', HomeView.as_view(), name='home'),
    
    # Portal hosts view
    url(r'^hosts.*$', HostsView.as_view(), name='hosts'),
    
    # Portal formulas view
    url(r'^formula.*$', FormulaView.as_view(), name='formula'),
    
    # Catch all other URL patterns and redirect to authentication page
    url(r'^.*/$', RedirectView.as_view(url=reverse_lazy('auth')))
)
