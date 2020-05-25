from django.urls import path
from django.conf.urls.static import static
from rednit import settings
from django.contrib.auth.decorators import login_required

from . import views
from social.views import HomeView, RegisterView, user_details, UserListView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('details/<str:pk>', user_details, name='user_detail'),
    path('accounts/register/', RegisterView.as_view(), name="register"),
    path('dialogs', login_required(views.DialogsView.as_view()), name='dialogs'),
    path('dialogs/create/<str:user_id>', login_required(views.CreateDialogView.as_view()), name='create_dialog'),
    path('dialogs/<str:chat_id>', login_required(views.MessagesView.as_view()), name='messages'),
    path('users_list/', UserListView.as_view(), name='list')

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATICFILES_DIRS)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
