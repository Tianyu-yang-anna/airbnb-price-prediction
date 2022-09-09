import sys

sys.path.append('housing_price/.')
from common.utils import Property_factory
from datetime import datetime as dt, timedelta
import pandas_gbq
from google.oauth2 import service_account
from pathlib import Path
import os
import pandas as pd

time_format = '%m-%d'
table_time_format = '%Y-%m-%d %H:%M:%S'
prop = Property_factory.get_instance()
credential_path = prop['credential_path']
projectId = prop['project']
credentials = service_account.Credentials.from_service_account_file(
    credential_path)
pandas_gbq.context.credentials = credentials
pandas_gbq.context.project = projectId
citymap = {
    'nyc': ('New York', 'New York', 'US'),
    'la': ('Los Angeles', 'California', 'US'),
    'sh': ('Shanghai', 'Shanghai', 'China'),
    'chicago': ('Cook', 'Illinois', 'US'),
}
rootpath = Path(sys.path[0])
covidpath = os.path.join(rootpath, 'static', 'data', 'covid')

def get_citymap():
    return citymap

def query_prediction_request(city):
    filepath = os.path.join(covidpath, 'predict', 'city_{}.csv'.format(city))
    df = pd.read_csv(filepath, header=0)
    data = {'date': [], 'predictions': []}
    for index, row in df.iterrows():
        data['date'].append(row['date'])
        data['predictions'].append(str(row['predictions']))
    return data


def query_common_request(city):
    filepath = os.path.join(covidpath, 'history', 'city_history_{}.csv'.format(city))
    df = pd.read_csv(filepath, header=0)
    data = {'date': [], 'new': []}
    for index, row in df.iterrows():
        data['date'].append(row['date'])
        data['new'].append(str(row['new']))
    return data


def query_data_with_length(cityname, state, country, days):
    source_table = prop['covid_dest_table']
    SQL = "SELECT * FROM (SELECT C.date, C.new FROM {} C WHERE C.city=@city AND C.state=@state AND C.country=@country \
        ORDER BY C.date DESC LIMIT {}) AS C2 ORDER BY C2.date".format(
        source_table, days)
    query_config = {
        'query': {
            'parameterMode':
            'NAMED',
            'queryParameters': [{
                'name': 'city',
                'parameterType': {
                    'type': 'STRING'
                },
                'parameterValue': {
                    'value': cityname
                }
            }, {
                'name': 'state',
                'parameterType': {
                    'type': 'STRING'
                },
                'parameterValue': {
                    'value': state
                }
            }, {
                'name': 'country',
                'parameterType': {
                    'type': 'STRING'
                },
                'parameterValue': {
                    'value': country
                }
            }]
        }
    }
    df = pandas_gbq.read_gbq(SQL, configuration=query_config)
    return df


def query_data_with_dates(city, state, country, dateStart, dateEnd):
    source_table = prop['covid_dest_table']
    SQL = "SELECT C.date, C.new FROM {} C WHERE C.date BETWEEN @dateStart AND @dateEnd"\
        " AND C.city=@city AND C.state=@state AND C.country=@country ORDER BY C.date".format(source_table)
    query_config = {
        'query': {
            'parameterMode':
            'NAMED',
            'queryParameters': [{
                'name': 'dateStart',
                'parameterType': {
                    'type': 'TIMESTAMP'
                },
                'parameterValue': {
                    'value': dateStart
                }
            }, {
                'name': 'dateEnd',
                'parameterType': {
                    'type': 'TIMESTAMP'
                },
                'parameterValue': {
                    'value': dateEnd
                }
            }, {
                'name': 'city',
                'parameterType': {
                    'type': 'STRING'
                },
                'parameterValue': {
                    'value': city
                }
            }, {
                'name': 'state',
                'parameterType': {
                    'type': 'STRING'
                },
                'parameterValue': {
                    'value': state
                }
            }, {
                'name': 'country',
                'parameterType': {
                    'type': 'STRING'
                },
                'parameterValue': {
                    'value': country
                }
            }]
        }
    }
    df = pandas_gbq.read_gbq(SQL, configuration=query_config)
    return df

# print(query_prediction_request('nyc'))
# data = query_common_data('Shanghai', 'Shanghai', 'China', '05-04-2021',
#                          '06-02-2021')
# print(data)
