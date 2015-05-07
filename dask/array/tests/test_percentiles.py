import numpy as np
import pytest

import dask.array as da
import dask


def eq(a, b):
    if isinstance(a, da.Array):
        a = a.compute(get=dask.get)
    if isinstance(b, da.Array):
        b = b.compute(get=dask.get)
    c = a == b
    if isinstance(c, np.ndarray):
        c = c.all()
    return c


@pytest.mark.skipif(int(np.__version__[2]) < 8, reason="Need numpy > 1.8")
def test_percentile():
    d = da.ones((16,), chunks=(4,))
    assert eq(da.percentile(d, [0, 50, 100]), [1, 1, 1])

    x = np.array([0, 0, 5, 5, 5, 5, 20, 20])
    d = da.from_array(x, chunks=(3,))

    assert eq(da.percentile(d, [0, 50, 100]), [0, 5, 20])

    x = np.array(['a', 'a', 'd', 'd', 'd', 'e'])
    d = da.from_array(x, chunks=(3,))
    assert eq(da.percentile(d, [0, 50, 100]), ['a', 'd', 'e'])


def test_percentile_with_categoricals():
    try:
        import pandas as pd
    except ImportError:
        return
    x0 = pd.Categorical(['Alice', 'Bob', 'Charlie', 'Dennis', 'Alice', 'Alice'])
    x1 = pd.Categorical(['Alice', 'Bob', 'Charlie', 'Dennis', 'Alice', 'Alice'])

    dsk = {('x', 0): x0, ('x', 1): x1}

    x = da.Array(dsk, 'x', chunks=((6, 6),))

    p = da.percentile(x, [50])
    assert (p.compute().categories == x0.categories).all()
    assert (p.compute().codes == [0]).all()


@pytest.mark.skipif(int(np.__version__[2]) < 8, reason="Need numpy > 1.8")
def test_percentiles_with_empty_arrays():
    x = da.ones(10, chunks=((5, 0, 5),))
    assert da.percentile(x, [10, 50, 90]).compute().tolist() == [1, 1, 1]
