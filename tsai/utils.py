# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/000_utils.ipynb (unless otherwise specified).

__all__ = ['totensor', 'toarray', 'to3dtensor', 'to2dtensor', 'to1dtensor', 'to3darray', 'to2darray', 'to1darray',
           'to3d', 'to2d', 'to1d', 'to2dPlus', 'to3dPlus', 'to2dPlusTensor', 'to2dPlusArray', 'to3dPlusTensor',
           'to3dPlusArray', 'Todtype', 'bytes2size', 'bytes2GB', 'delete_all_in_dir', 'reverse_dict', 'is_tuple',
           'itemify', 'is_none', 'ifisnone', 'ifnoneelse', 'ifisnoneelse', 'ifelse', 'is_not_close', 'test_not_close',
           'stack', 'cat2int', 'cycle_dl']

# Cell
from .imports import *

# Cell
def totensor(o):
    if isinstance(o, torch.Tensor): return o
    elif isinstance(o, np.ndarray):  return torch.from_numpy(o)
    assert False, f"Can't convert {type(o)} to torch.Tensor"


def toarray(o):
    if isinstance(o, np.ndarray): return o
    elif isinstance(o, torch.Tensor): return o.cpu().numpy()
    assert False, f"Can't convert {type(o)} to np.array"


def to3dtensor(o):
    o = totensor(o)
    if o.ndim == 3: return o
    elif o.ndim == 1: return o[None, None]
    elif o.ndim == 2: return o[:, None]
    assert False, f'Please, review input dimensions {o.ndim}'


def to2dtensor(o):
    o = totensor(o)
    if o.ndim == 2: return o
    elif o.ndim == 1: return o[None]
    elif o.ndim == 3: return o[0]#torch.squeeze(o, 0)
    assert False, f'Please, review input dimensions {o.ndim}'


def to1dtensor(o):
    o = totensor(o)
    if o.ndim == 1: return o
    elif o.ndim == 3: return o[0,0]#torch.squeeze(o, 1)
    if o.ndim == 2: return o[0]#torch.squeeze(o, 0)
    assert False, f'Please, review input dimensions {o.ndim}'


def to3darray(o):
    o = toarray(o)
    if o.ndim == 3: return o
    elif o.ndim == 1: return o[None, None]
    elif o.ndim == 2: return o[:, None]
    assert False, f'Please, review input dimensions {o.ndim}'


def to2darray(o):
    o = toarray(o)
    if o.ndim == 2: return o
    elif o.ndim == 1: return o[None]
    elif o.ndim == 3: return 0[0]#np.squeeze(o, 0)
    assert False, f'Please, review input dimensions {o.ndim}'


def to1darray(o):
    o = toarray(o)
    if o.ndim == 1: return o
    elif o.ndim == 3: o = 0[0,0]#np.squeeze(o, 1)
    elif o.ndim == 2: o = 0[0]#np.squeeze(o, 0)
    assert False, f'Please, review input dimensions {o.ndim}'


def to3d(o):
    if o.ndim == 3: return o
    if isinstance(o, np.ndarray): return to3darray(o)
    if isinstance(o, torch.Tensor): return to3dtensor(o)


def to2d(o):
    if o.ndim == 2: return o
    if isinstance(o, np.ndarray): return to2darray(o)
    if isinstance(o, torch.Tensor): return to2dtensor(o)


def to1d(o):
    if o.ndim == 1: return o
    if isinstance(o, np.ndarray): return to1darray(o)
    if isinstance(o, torch.Tensor): return to1dtensor(o)


def to2dPlus(o):
    if o.ndim >= 2: return o
    if isinstance(o, np.ndarray): return to2darray(o)
    elif isinstance(o, torch.Tensor): return to2dtensor(o)


def to3dPlus(o):
    if o.ndim >= 3: return o
    if isinstance(o, np.ndarray): return to3darray(o)
    elif isinstance(o, torch.Tensor): return to3dtensor(o)


def to2dPlusTensor(o):
    return to2dPlus(totensor(o))


def to2dPlusArray(o):
    return to2dPlus(toarray(o))


def to3dPlusTensor(o):
    return to3dPlus(totensor(o))


def to3dPlusArray(o):
    return to3dPlus(toarray(o))


def Todtype(dtype):
    def _to_type(o, dtype=dtype):
        if o.dtype == dtype: return o
        elif isinstance(o, torch.Tensor): o = o.to(dtype=dtype)
        elif isinstance(o, np.ndarray): o = o.astype(dtype)
        return o
    return _to_type

# Cell
def bytes2size(size_bytes):
    if size_bytes == 0: return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

def bytes2GB(byts):
    return round(byts / math.pow(1024, 3), 2)

# Cell
def delete_all_in_dir(tgt_dir, exception=None):
    if exception is not None and len(L(exception)) > 1: exception = tuple(exception)
    for file in os.listdir(tgt_dir):
        if exception is not None and file.endswith(exception): continue
        file_path = os.path.join(tgt_dir, file)
        if os.path.isfile(file_path) or os.path.islink(file_path): os.unlink(file_path)
        elif os.path.isdir(file_path): shutil.rmtree(file_path)

# Cell
def reverse_dict(dictionary):
    return {v: k for k, v in dictionary.items()}

# Cell
def is_tuple(o): return isinstance(o, tuple)

# Cell
def itemify(*o, tup_id=None):
    items = L(*o).zip()
    if tup_id is not None: return L([item[tup_id] for item in items])
    else: return items

# Cell
def is_none(o):
    return o in [[], [None], None]

def ifisnone(a, b):
    "`a` if `a` is None else `b`"
    return None if is_none(a) else b

def ifnoneelse(a, b, c=None):
    "`b` if `a` is None else `c`"
    return b if a is None else ifnone(c, a)

def ifisnoneelse(a, b, c=None):
    "`b` if `a` is None else `c`"
    return b if is_none(a) else ifnone(c, a)

def ifelse(a, b, c):
    "`b` if `a` is True else `c`"
    return b if a else c

# Cell
def is_not_close(a,b,eps=1e-5):
    "Is `a` within `eps` of `b`"
    if hasattr(a, '__array__') or hasattr(b,'__array__'):
        return (abs(a-b)>eps).all()
    if isinstance(a, (Iterable,Generator)) or isinstance(b, (Iterable,Generator)):
        return is_not_close(np.array(a), np.array(b), eps=eps)
    return abs(a-b)>eps

# Cell
def test_not_close(a,b,eps=1e-5):
    "`test` that `a` is within `eps` of `b`"
    test(a,b,partial(is_not_close,eps=eps),'not_close')

# Cell
@patch
def mul_min(x:torch.Tensor, axes=None, keepdim=False):
    if axes is None: return x.min()
    axes = reversed(sorted(axes if is_listy(axes) else [axes]))
    min_x = x
    for ax in axes: min_x, _ = min_x.min(ax, keepdim)
    return min_x

@patch
def mul_max(x:torch.Tensor, axes=None, keepdim=False):
    if axes is None: return x.max()
    axes = reversed(sorted(axes if is_listy(axes) else [axes]))
    max_x = x
    for ax in axes: max_x, _ = max_x.max(ax, keepdim)
    return max_x

# Cell
def stack(o, axis=0):
    if isinstance(o[0], torch.Tensor): return torch.stack(tuple(o), dim=axis)
    else: return np.stack(o, axis)

# Cell
def cat2int(o):
    cat = Categorize()
    cat.setup(o)
    return stack(TfmdLists(o, cat)[:])

# Cell
def cycle_dl(dl):
    for _ in dl: _