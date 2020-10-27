from django.urls import path
from .views import PlaceView, CreateView, PayView, QueryView, CommentView

app_name = 'order'
urlpatterns = [
    path('place/', PlaceView.as_view(), name='place'),
    path('create/', CreateView.as_view(), name='create'),
    path('pay/', PayView.as_view(), name='pay'),
    path('query/', QueryView.as_view(), name='query'),
    path('comment/<int:order_id>/', CommentView.as_view(), name='comment')
]
