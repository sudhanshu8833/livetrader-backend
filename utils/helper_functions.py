from datamanagement.services.models import User
from datamanagement.services import BinanceBroker, OrderService, SignalService
from datamanagement.services.models import BinanceApi, PositionUser, Logs
from utils.common_functions import log_info
import asyncio
from asgiref.sync import sync_to_async, async_to_sync
from celery import group, shared_task, chord


def convert_to_numberic(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                try:
                    data[key] = float(value)
                except ValueError:
                    pass
    return data

def response_message(username, status, data = None, message = None):
    response = {
        'username': username,
        'status': status
    }
    if message:
        response['message'] = message
    if data:
        response['data'] = data
    return response

async def create_order_entry(data):
    order_service = OrderService(BinanceBroker)
    if "admin" in data['username']:
        usernames = await sync_to_async(list)(User.objects.filter(live=True, blacklist = 0).values_list('username', flat=True))
        filtered_usernames = []
        for username in usernames:
            try:
                binance_api = await BinanceApi.objects.aget(username=username, market=data['market'].lower())
                filtered_usernames.append(username)
            except Exception as e:
                pass


        usernames = filtered_usernames
    elif isinstance(data['username'], str):
            usernames = [data['username']]
    else:
        usernames = data['username']

    tasks = []
    for username in usernames:
        tasks.append(order_service.create_entry_order_for_user(username, data))

    responses = await asyncio.gather(*tasks)
    return responses


async def async_task_wrapper(type, api_list, data):
    tasks = []
    for api_id in api_list:
        api = await BinanceApi.objects.aget(id = api_id)
        client = BinanceBroker(api.api_key, api.secret_key, api.testnet, api.market)
        signal_service = SignalService(client)
        if type == 'entry':
            tasks.append(signal_service.create_entry_order_for_user(api.username, data))
        else:
            position = await PositionUser.objects.aget(username = api.username, status = "OPEN", source = data['alert_id'])
            tasks.append(signal_service.create_exit_order_for_user(position, data))
    responses = await asyncio.gather(*tasks)
    return responses

@shared_task
def task_wrapper(type, api_list, data):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(async_task_wrapper(type, api_list, data))


def create_order_signal(data, order_type = 'entry'):
    usernames = list(User.objects.filter(live=True, blacklist = 0).values_list('username', flat=True))
    apis = []
    for username in usernames:
        try:
            binance_api = BinanceApi.objects.get(username=username, market=data['market'].lower())
            apis.append(binance_api)
        except Exception as e:
            pass

    api_1 = []
    api_2 = []
    api_index = 0
    for api in apis:
        if api_index % 2 == 0:
            api_1.append(api.id)
        else:
            api_2.append(api.id)
        api_index += 1

    task_1 = task_wrapper.s(order_type, api_1, data).set(priority=0)
    task_2 = task_wrapper.s(order_type, api_2, data).set(priority=0)

    task_group = group([task_1, task_2])
    result = task_group.apply_async()
    response = result.get()
    response = response[0] + response[1]
    return response


async def create_order_exit(data):
    order_service = OrderService(BinanceBroker)

    if 'admin' in data['username']:
        usernames = await sync_to_async(list)(User.objects.filter(live=True, blacklist = 0).values_list('username', flat=True))
        filtered_usernames = []
        for username in usernames:
            try:
                binance_api = await BinanceApi.objects.aget(username=username, market=data['market'].lower())
                filtered_usernames.append(username)
            except:
                pass
        usernames = filtered_usernames
    elif isinstance(data['username'], str):
            usernames = [data['username']]
    else:
        usernames = data['username']

    tasks = []
    for username in usernames:
        tasks.append(order_service.create_exit_order_for_user(username, data))

    responses = await asyncio.gather(*tasks)
    return responses

async def close_all_open_positions(username = None):
    order_service = OrderService(BinanceBroker)
    if username:
        positions = await sync_to_async(list)(PositionUser.objects.filter(username=username, status='OPEN'))
    else:
        positions = await sync_to_async(list)(PositionUser.objects.filter(status='OPEN'))
    tasks = []
    for position in positions:
        try:
            data = {
                'symbol': position.symbol,
                'market': position.market,
                'order_type': 'market',
                'side': 'sell' if position.direction == 'LONG' else 'buy'
            }
            if(position.source == 0):
                tasks.append(order_service.create_exit_order_for_user(position.username, data, position))
            else:
                binance_api = await BinanceApi.objects.aget(username=position.username, market=data['market'].lower())
                client = BinanceBroker(binance_api.api_key, binance_api.secret_key, binance_api.testnet, binance_api.market)
                signal_service = SignalService(client)
                data['alert_id'] = position.source
                tasks.append(signal_service.create_exit_order_for_user(position, data))
        except Exception as e:
            print(str(e))
    responses = await asyncio.gather(*tasks)
    return responses

async def cancel_order(data):
    try:
        order_service = OrderService(BinanceBroker)
        response_data = await order_service.cancel_order(data['username'], data['order_id'], data['symbol'], data['market'])
        response = response_message(data['username'], 'SUCCESS', data = response_data)
        log_info(response)
        return response
    except Exception as e:
        response = response_message(data['username'], 'ERROR', message = str(e))
        log_info(response)
        return response

@sync_to_async
def fetch_live_apis():
    return list(BinanceApi.objects.filter(user__live=True, user__blacklist=0))

async def login_user(user_api):
    try:
        broker = BinanceBroker(user_api.api_key, user_api.secret_key, user_api.testnet, user_api.market)
        balance = await broker.fetch_balance()
        if balance is None:
            await sync_to_async(user_api.deactivate)()
            raise Exception('Failed to login user')

        await sync_to_async(user_api.activate)()
        return response_message(user_api.username, 'SUCCESS', message = 'User logged in successfully')
    except Exception as e:
        await sync_to_async(user_api.deactivate)()
        return response_message(user_api.username, 'ERROR', message = str(e))

@async_to_sync
async def login_users(username = None):
    if username:
        users_api = [await BinanceApi.objects.aget(username = username)]
    else:
        users_api = await fetch_live_apis()

    tasks = []
    for user in users_api:
        tasks.append(login_user(user))

    responses = await asyncio.gather(*tasks)
    return responses

def create_order_log_entry(data):
    logs_message = ""
    SUCCESS = []
    ERROR = []

    for order in data:
        if order['status'] == 'SUCCESS':
            SUCCESS.append(order['username'])
        else:
            ERROR.append({
                'username': order['username'],
                'message': order['message']
            })

    if len(SUCCESS) > 0:
        logs_message += f"Orders created successfully for {', '.join(SUCCESS)}"

    if len(SUCCESS) and len(ERROR):
        logs_message += ' and '

    if len(ERROR) > 0:
        logs_message += f"Orders failed for {', '.join([f'''{error['username']} (Reason: {error['message']})''' for error in ERROR])}"

    return logs_message

def cancel_order_log_entry(data):
    log_message = ""
    if data['status'] == 'SUCCESS':
        log_message += f"Order for {data['username']} cancelled successfully"
    else:
        log_message += f"Order failed to cancel for {data['username']} (Reason: {data['message']})"
    return log_message

async def close_user_open_positions(username, data):
    try:
        binance_api = await BinanceApi.objects.aget(username=username, market=data['market'].lower())
        client = BinanceBroker(binance_api.api_key, binance_api.secret_key, binance_api.testnet, binance_api.market)
        signal_service = SignalService(client)
        return await signal_service.close_open_positions_for_user(username, data['symbol'])
    except:
        pass
