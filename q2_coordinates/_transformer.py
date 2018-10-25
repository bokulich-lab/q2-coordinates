# ----------------------------------------------------------------------------
# Copyright (c) 2017-2018, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
import qiime2

from .plugin_setup import plugin
from ._format import CoordinatesFormat


def _read_dataframe(fh):
    # Using `dtype=object` and `set_index` to avoid type casting/inference
    # of any columns or the index.
    df = pd.read_csv(fh, sep='\t', header=0, index_col=0, dtype=object)
    return df


@plugin.register_transformer
def _1(data: pd.DataFrame) -> (CoordinatesFormat):
    ff = CoordinatesFormat()
    with ff.open() as fh:
        data.to_csv(fh, sep='\t', header=True)
    return ff


@plugin.register_transformer
def _2(ff: CoordinatesFormat) -> (pd.DataFrame):
    with ff.open() as fh:
        df = _read_dataframe(fh)
        return df.apply(lambda x: pd.to_numeric(x, errors='ignore'))


@plugin.register_transformer
def _3(ff: CoordinatesFormat) -> (qiime2.Metadata):
    with ff.open() as fh:
        return qiime2.Metadata(_read_dataframe(fh))
