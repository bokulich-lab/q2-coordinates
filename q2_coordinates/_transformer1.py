
import pandas as pd
import numpy as np

import qiime2

from ..plugin_setup import plugin
from . import QuadTreeFormat


def _read_quad_trees(fh):
    df = pd.read_csv(fh, sep='\t', header=0, dtype=object)
    df.set_index(df.columns[0], drop=True, append=False, inplace=True)
    df.index.name = None
    cols = df.columns
    df[cols] = df[cols].apply(pd.to_numeric, errors='ignore')
    return df


@plugin.register_transformer
def _1(data: pd.DataFrame) -> QuadTreeFormat:
    ff = QuadTreeFormat()
    with ff.open() as fh:
        data.to_csv(fh, sep='\t', header=True)
    return ff


@plugin.register_transformer
def _2(ff: QuadTreeFormat) -> pd.DataFrame:
    with ff.open() as fh:
        df = _read_quad_trees(fh)
        series = df.iloc[:, 0]
        if not np.issubdtype(series, np.number):
            raise ValueError('Non-numeric values detected in alpha diversity '
                             'estimates.')
        return series


@plugin.register_transformer
def _3(ff: QuadTreeFormat) -> qiime2.Metadata:
    with ff.open() as fh:
        df = _read_alpha_diversity(fh)
        df.index.name = 'Sample ID'
        return qiime2.Metadata(df)
