from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('settings/update/<int:pk>/', views.SettingsUpdate.as_view(),
         name='update-settings'),
    path('settings/create', views.SettingsCreate.as_view(),
         name='create-settings'),
    path('token', views.TokenView.as_view(), name='token'),
    path('refresh_token', views.RefreshTokenView.as_view(),
         name='refresh_token'),
    path('signature', views.CreateSignatureView.as_view(), name='signature'),
    path('signer', views.CreateSigner.as_view(), name='signer'),
    path('sign/<int:pk>', views.Sign.as_view(), name='sign'),
    path('signed/<int:pk>', views.DemoSignerReturnView.as_view(),
         name='signed')
]
