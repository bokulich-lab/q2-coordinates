# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2.plugin.model as model
from qiime2.plugin import ValidationError


def _validate_record_min_len(cells, current_line_number, exp_len):
    if len(cells) < exp_len:
        raise ValidationError(
            "Expected data record to be TSV with ≥ {0} "
            "fields. Detected {1} fields at line {2}:\n\n{3!r}"
            .format(exp_len, len(cells), current_line_number, cells))


def _validate_file_not_empty(has_data):
    if not has_data:
        raise ValidationError(
            "There must be at least one data record present in the "
            "file in addition to the header line.")


class CoordinatesFormat(model.TextFileFormat):
    def _validate_(self, level):
        n_records = {'min': 10, 'max': None}[level]
        with self.open() as fh:
            # validate header
            # for now we will not validate any information in the header.
            line = fh.readline()

            # validate body
            has_data = False
            for line_number, line in enumerate(fh, start=2):
                cells = line.strip().split('\t')
                _validate_record_min_len(cells, line_number, 2)
                for cell in cells[1:]:
                    try:
                        float(cell)
                    except ValueError:
                        raise ValidationError(
                            "Expected data to be comprised of float values. "
                            "Found non-float value {0} at line {1}"
                            .format(cell, line_number))
                has_data = True
                if n_records is not None and (line_number - 1) >= n_records:
                    break

            _validate_file_not_empty(has_data)


CoordinatesDirectoryFormat = model.SingleFileDirectoryFormat(
    'CoordinatesDirectoryFormat', 'coordinates.tsv',
    CoordinatesFormat)

import csv

from ..plugin_setup import plugin


class QuadTreeFormat(model.TextFileFormat):
    def _validate_(self, level):
        with self.open() as fh:
            header, records_seen, is_min = None, 0, level == 'min'
            fh_ = csv.reader(fh, delimiter='\t')
            file_ = enumerate(fh_, 1) if is_min else zip(range(1, 11), fh_)
            for i, cells in file_:
                if header is None:
                    if len(cells) < 2:
                        raise ValidationError(
                            'Found header on line %d with the following '
                            'columns: %s (length: %d), expected at least 2 '
                            'columns.' % (i, cells, len(cells)))
                    else:
                        header = cells
                else:
                    if len(cells) != len(header):
                        raise ValidationError(
                            'Line %d has %s cells (%s), expected %s.'
                            % (i, len(cells), cells, len(header)))

                    records_seen += 1

            # The first non-comment and non-blank row observed will always be
            # the header row, and since we have no requirement on the field
            # names (because they are dynamically defined), so no need to check
            # for the presence (or validity) of a header row at this point.

            if records_seen == 0:
                raise ValidationError('No records found in file, only '
                                      'observed comments, blank lines, and/or '
                                      'a header row.')


QuadTreeDiversityDirectoryFormat = model.SingleFileDirectoryFormat(
    'QuadTreeDirectoryFormat', 'quadtree.tsv',
    QuadTreeDiversityFormat)


plugin.register_formats(QuadTreeFormat, QuadTreeDirectoryFormat)
       
