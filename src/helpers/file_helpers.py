#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author    : Thomas Cuthbert
import os, sys
import logging
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def _validate_length(func):
    """Ensure length of two structures are equal.
    Raise ValueError if not."""
    def func_wrapper(a, b):
        if len(a) != len(b):
            print sys._current_frames()
            raise ValueError("Invalid args passed to %s" % sys._getframe().f_code.co_name)
        return func(a, b)
    return func_wrapper


def parse_xls(filep, indexes, sorting_pattern):
    """Parses an excel spreadsheet.

    :param filep: path to excel spreadsheet.
    :type filep: file
    :param indexes: tuple containing column indexes to be extracted.
    :type indexes: dict
    :param sorting_pattern: list containing regex patterns
    :type sorting_pattern: list
    :rtype: dict
    :return: data store indexed by IP address and data sorted by sorting_pattern

    """
    from xlrd import open_workbook


    def _sort_xls_data(data):
        "This function sorts the data returned by parse_xls."
        from re import match
        from copy import copy

        sorted_data = data
        sp = copy(sorting_pattern)
        while sp:
            regxp = sp.pop()
            sorted_data = sorted(sorted_data, key=lambda v: match(regxp, str(v)))
        return list(reversed(sorted_data))

    wbook = open(filep, 'rb').read()
    wbook = open_workbook(file_contents=wbook)
    ret = {}
    log = logging.getLogger(__name__)
    sheets = wbook.sheets()

    if len(sheets) != len(indexes):
        raise ValueError("Invalid args passed to %s" % sys._getframe().f_code.co_name)

    # Process workbook
    for sheet_num, sheet in enumerate(sheets):
        sheet_indexes = indexes[sheet_num]
        idx, column_numbers = sheet_indexes.popitem()
        # Process sheet row
        for row in range(sheet.nrows):
            col_data = []
            # Process interesting columns in row
            for col_index, col_num in enumerate(column_numbers):
                if col_num == idx:
                    # Remap idx to col_data index
                    idx = col_index
                data = sheet.cell(row, col_num).value
                if data is '':
                    continue
                col_data.append(data)
            # Make sure to not include incomplete rows
            if len(col_data) != len(column_numbers):
                continue
            ret[col_data[idx]] = _sort_xls_data(col_data)
    return ret


def parse_csv(filep):
    """Parse csv file and return dict containing site code to
    bandwidth mappings
    Keyword Arguments:
    filep -- file path to csv file
    """
    from csv import reader

    bw_map = dict()

    with open(filep, 'r') as csvfile:
        bw_reader = reader(csvfile, delimiter=',', dialect='excel', skipinitialspace=True)
        for row in bw_reader:
            sn = row[1]
            nm = row[2]
            bw = row[0]
            mt = row[3]
            bw_map[sn] = [bw, nm, mt]

    csvfile.close()
    return bw_map
