from django.urls import path
from app import views
from app.views import UploadView, ExtractView

app_name = 'app'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('upload', UploadView.as_view(), name='upload_file'),
    path('extract', ExtractView.as_view(), name='extract_text')
]