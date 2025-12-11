from datetime import datetime, UTC

from src.client.client import Client


client = Client()


def get_positions_test():
    positions = client.get_positions()
    print(positions)

def datetime_format_test(time):
    try:
        formatted_time = datetime.strptime(time.strip(), "%Y-%m-%d")
        print(formatted_time)
    except ValueError as e:
        print(e.args)

def login_test(login, password):
    user = client.login(login, password)
    res = client.create_application({'documents': 'справка', 'expert_conclusion': 'больной', 'status_id': 3})
    print(res)

def utc_test():
    print(datetime.utcnow())
    print(datetime.now(UTC).replace(tzinfo=None))

def time_test():
    submission_date = datetime.strptime('2025-11-03', '%Y-%m-%d').date()
    print(submission_date)

#datetime_format_test('20-14-2')
#login_test('mihail', '12345')
#utc_test()
time_test()
