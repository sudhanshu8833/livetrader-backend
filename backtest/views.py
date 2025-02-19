from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.response import Response
from backtest.modules import BacktestFeeds, Strategy
from datetime import datetime
from collections.abc import Mapping

class BackTestView(viewsets.ViewSet):

    def process_backtest(self, request):
        '''
            Create a new order
            args:
                alert_id: 8
                side: str
                symbol: str # BTCUSDT
                order_type: str [market, limit]
                market: str [SPOT, FUTURE]
                multiplier: int
                leverage: int
                tp1: float
                tp2: float
                tp3: float
                break_even: float
                stop_loss: float
                entry: True
        '''

        data = request.data
        strategy = Strategy()
        backtest_feeds = BacktestFeeds(strategy)
        backtest_feeds.start_feeds()
        response = strategy.to_dict()
        return Response(response, status=200)