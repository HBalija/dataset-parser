#!/usr/bin/env python3

import argparse
import pandas as pd
import requests
import sys
from datetime import datetime, timedelta
from io import StringIO


DATA_ENDPOINT = 'http://lameapi-env.ptqft8mdpd.us-east-2.elasticbeanstalk.com/data'
DEFAULT_KEYLIST = ['temperature', 'humidity', 'light', 'co2', 'humidityratio', 'occupancy']


def parse_args():
    """
    Parse and return script input arguments.
    """

    # Initialize parser object
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--start', required=True)
    parser.add_argument('-e', '--end', required=True)
    parser.add_argument('-k', '--kpi_list', nargs='+')

    args = parser.parse_args()

    try:
        """
        Convert required "start" and "end" input args into datetime objects.
        Only date is required as input parametar (format: --start/end m/d/y).
        For the end date to be included in results, timedelta of 1 day is added.
        """
        args.start = parse_date(args.start, csv=False)
        args.end = parse_date(args.end, csv=False) + timedelta(days=1)

        if args.start > args.end:
            raise ValueError()

    except ValueError:
        sys.exit('Valid input for "start" and "end" should be provided in m/d/y format')

    """
    kpi_list argument is optional (format: --kpi_list arg1 arg2 ...)

    If input is provided in format: --kpi_list arg1,arg2,...,
    values are splitted into list using comma as delimiter.

    If kpi_list arg is not provided, default list of args is used (all columns).
    """
    if not args.kpi_list:
        args.kpi_list = DEFAULT_KEYLIST
    elif len(args.kpi_list) == 1 and ',' in args.kpi_list[0]:
        args.kpi_list = args.kpi_list[0].split(',')

    return args


def create_dataframe():
    """
    Fetch dataset and return dataframe object.

    Handle response errors
    """
    r = requests.get(DATA_ENDPOINT)
    if r.status_code != 200:
        raise ValueError('Data cannot be reached, server error')

    data = r.json()['data']
    if not data:
        # responese data --> {'ok': True, 'data': ''}
        raise ValueError('Dataset is empty')

    buffer = StringIO(data)
    data_frame = pd.read_csv(buffer, parse_dates=['date'], date_parser=parse_date)

    return data_frame


def setup_working_dataframe(df, date_from, date_to):
    """
    Return dataframe in specified date range with lowercase header names.
    """
    df.columns = [name.lower() for name in df.columns]
    mask = (df['date'] > date_from) & (df['date'] < date_to)
    return df.loc[mask]


def parse_date(date_string, csv=True):
    """
    Cast string to a datetime object.

    csv flag:
    - user "start" and "end" inputs are in date formats
    - endpoint data parsed to csv includes both date and time
    """
    parse_string = '%m/%d/%y %H:%M' if csv else '%m/%d/%y'
    return datetime.strptime(date_string, parse_string)


def get_percent_change(key):
    """
    Return percent change using column first and last results.
    """
    first_value = df[key].iloc[0]
    last_value = df[key].iloc[-1]

    try:
        pc = f'{(last_value - first_value) / first_value * 100}%'
    except ZeroDivisionError:
        pc = 'N/A'

    return pc


def return_results(df, keylist):
    """
    Return results dict.

    Results dict includes results for
    """
    results = {}

    for key in keylist:

        # skip processing if key not valid dataframe header column name
        if key not in df.columns:
            continue

        results[key] = {
            "percent_change": get_percent_change(key),
            "last_value": df[key].iloc[-1],
            "first_value": df[key].iloc[0],
            "lowest": df[key].min(),
            "highest": df[key].max(),
            "mode": df[key].mode()[0],
            "average": df[key].mean(),
            "median": df[key].median()
        }

    return results


if __name__ == '__main__':

    # parse args
    args = parse_args()

    df = create_dataframe()
    df = setup_working_dataframe(df, args.start, args.end)
    sys.stdout.write(f'{return_results(df, args.kpi_list)}\n')
