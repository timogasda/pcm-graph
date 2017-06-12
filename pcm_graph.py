#!/usr/bin/env python
import argparse
import csv
import sys
import datetime

import numpy as np
import matplotlib.pyplot as plt

DAY_COL = 0
TIME_COL = 1


def _parse_csv(args):
    series = []
    series_labels = []

    with open(args.input, 'r') as f:
        reader = csv.reader(f, delimiter=';')

        # read and skip both header lines
        header = next(reader)
        subheader = next(reader)

        # discover available nodes when necessary
        if args.nodes == 'all':
            args.nodes = []
            for title in header:
                if title.startswith('Socket'):
                    args.nodes.append(int(title[6:]))

        # create proper series labels by appending sub-header to current
        # main header
        current_head = header[0]
        for i, col in enumerate(subheader):
            if header[i]:
                current_head = header[i]

            series_labels.append(current_head + ' ' + col)
            series.append([])

        # read values and write into series
        for line in reader:
            for i, val in enumerate(line):
                val = str(val).strip()

                if '%' in val:
                    val = float(val[:-1])

                try:
                    series[i].append(float(val))
                except ValueError:
                    series[i].append(val)

    # accumulate data from all QPI links for each node
    if not args.separate_qpi:
        current_series = None
        current_label = None
        for i, header in enumerate(header):
            if not header:
                if current_series:
                    for x, y in enumerate(series[i]):
                        current_series[x] += y
            elif header.startswith('SKT') and ('traffic' in header or 'data' in header):
                if current_series:
                    series.append(current_series)
                    series_labels.append(current_label)

                current_series = series[i][:]
                current_label = header
            else:
                if current_series:
                    series.append(current_series)
                    series_labels.append(current_label)
                    current_series = None

    return series_labels, series


def _create_time_series(series):
    x_series = []

    fake_day = datetime.date(2010, 1, 1)
    first_time = None

    for x, point in enumerate(series[TIME_COL]):
        # point is something like: 11:10:46.215
        h, m, s = [int(n) for n in point[:-4].split(':')]
        milli = int(point[-3:])
        u = datetime.time(h, m, s, milli * 1000)

        if not first_time:
            first_time = datetime.datetime.combine(fake_day, u)

        delta = (datetime.datetime.combine(fake_day, u) - first_time)
        x_series.append(delta.total_seconds())

    return x_series


def _plot(args, series, series_labels, x_series):
    plt.style.use(args.style)

    # define color space
    color_space = len(args.nodes)
    if args.separate_qpi:
        color_space *= 3

    color_n = 0
    color_list = plt.cm.Set1(np.linspace(0, 1, color_space))

    for i, y_series in enumerate(series):
        label = series_labels[i]

        if not label.startswith('SKT'):
            continue

        if args.percentages != ('percent' in label):
            continue

        if (not any([('SKT{}t'.format(n)) in label for n in args.nodes])) and (not any([('SKT{}d'.format(n)) in label for n in args.nodes])):
            continue

        if not args.separate_qpi and ' QPI' in label:
            continue

        if not ('dataIn' in label or 'trafficOut' in label):
            continue

        # print('{0}\t{1}'.format(label, sum(y)))
        # print(color_list[color_n % color_space])
        style = '-'
        if 'dataIn' in label:
            style = '--'

        # sort in case PCM mixed up the order:
        y = [b for (x, b) in sorted(zip(x_series, y_series))]
        x = sorted(x_series)

        if not args.percentages:
            y_per_sec = []
            for index, value in enumerate(y):
                if index == 0:
                    y_per_sec.append(value)
                else:
                    y_per_sec.append(
                        value / (x_series[index] - x_series[index - 1]))
            y = y_per_sec

        plt.plot(sorted(x_series), y, label=label, linewidth=2, linestyle=style,
                 color=color_list[color_n % color_space])
        color_n += 1

    plt.xticks(range(int(max(x_series) + 2)))

    if args.title:
        plt.title(args.title)

    plt.xlabel('Time (s)')

    if args.percentages:
        plt.ylabel('QPI Traffic (%)')
    else:
        plt.ylabel('QPI Traffic (MB/s)')

    plt.legend()

    plt.tight_layout()


def main(args):
    series_labels, series = _parse_csv(args)

    if not len(series_labels) or not len(series):
        print('No data found!')
        return

    # make sure that all data is from the same day
    if series[DAY_COL][0] != series[DAY_COL][-1]:
        print('We currently do not support measurements spanning more than a day. Sorry!')
        return

    # create correct x-series
    x_series = _create_time_series(series)

    # print(x_series)
    _plot(args, series, series_labels, x_series)

    plt.savefig(args.output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input', help='Path to the CSV file that contains the PCM results')
    parser.add_argument(
        '-o', '--output', help='Path to output file. Defaults to %input%.png')
    parser.add_argument('-n', '--nodes', default='all',
                        help='List of nodes to plot (e.g., 0,1,2,3)')
    parser.add_argument('-p', '--percentages', action='store_true',
                        help='Use the percentage values for traffic instead of absolute values')
    parser.add_argument('-q', '--separate-qpi', action='store_true',
                        help='Plot traffic for all QPI links separately')
    parser.add_argument('-s', '--style', default='classic',
                        help='Define a custom matplotlib style to use, see `matplotlib.style`')
    parser.add_argument('-t', '--title', help='Title of the figure')
    args = parser.parse_args()

    # normalize arguments
    if not args.output:
        args.output = '{0}.png'.format(args.input)

    if args.nodes != 'all':
        try:
            args.nodes = [int(node) for node in args.nodes.split(',')]
        except Exception as e:
            print(e)
            print('Error parsing node list argument!')
            sys.exit(1)

    main(args)
