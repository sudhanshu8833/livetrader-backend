from .views import BackTestView

# from .views import TokenObtainPairView
from django.urls import path

urlpatterns = [
    path('', BackTestView.as_view(
        {
            'post': 'process_backtest',
        }
    ))
]