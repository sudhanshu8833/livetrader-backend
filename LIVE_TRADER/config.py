from pydantic import BaseModel
from django.conf import settings
import json
from typing import Dict
from lt_types.index import IndexStaticData
from datetime import datetime

with open(f"{settings.STATIC_DATA_PATH}/index.json") as f:
    index_data = json.load(f)

STATIC_DATA_INDEX: Dict[str, IndexStaticData] = {}

for index, value in index_data.items():
    expiry = [datetime.strptime(expiry, '%Y-%m-%d') for expiry in value['options_expiry']]
    STATIC_DATA_INDEX[index] = IndexStaticData(
        options_expiry = expiry,
        futures_expiry=[],
        symbol = index,
        exchange = value['exchange'],
        lot_size = value['lot_size'],
        strike_gap = value['strike_gap'],
        holidays = [datetime.strptime(holiday, '%Y-%m-%d') for holiday in value['holidays']]
    )