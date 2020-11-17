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
