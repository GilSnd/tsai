# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/002_data.core.ipynb (unless otherwise specified).

__all__ = ['NumpyTensor', 'ToNumpyTensor', 'TSTensor', 'ToTSTensor', 'NumpyTensorBlock', 'TSTensorBlock',
           'TorchDataset', 'NumpyDataset', 'TSDataset', 'NumpyDatasets', 'TSDatasets', 'add_ds', 'NumpyDataLoader',
           'show_tuple', 'TSDataLoader', 'NumpyDataLoaders', 'TSDataLoaders']

# Cell
from ..imports import *
from ..utils import *
from .external import *
from ..models.InceptionTime import *

# Cell
import torch
import re
from torch._six import container_abcs, string_classes, int_classes

# Cell
class NumpyTensor(TensorBase):
    "Returns a `tensor` of type torch.float32 and class `NumpyTensor` that has a show method"
    def __new__(cls, o, **kwargs):
        if isinstance(o, (list, L)): o = stack(o)
        res = cast(tensor(o), cls)
        res._meta = kwargs
        return res
    def __getitem__(self, idx):
        res = super().__getitem__(idx)
        return res.as_subclass(type(self))
    def __repr__(self):
        if self.numel() == 1: return f'{self}'
        else: return f'NumpyTensor(shape:{list(self.shape)})'
    def show(self, ax=None, ctx=None, title=None, title_color='black', **kwargs):
        if self.ndim != 2: self = type(self)(to2dtensor(self))
        ax = ifnone(ax,ctx)
        if ax is None: fig, ax = plt.subplots(**kwargs)
        ax.plot(self.T)
        ax.axis(xmin=0, xmax=self.shape[-1] - 1)
        ax.set_title(title, weight='bold', color=title_color)
        plt.tight_layout()
        return ax

class ToNumpyTensor(Transform):
    "Transforms np.ndarray to NumpyTensor"
    def encodes(self, o:np.ndarray): return NumpyTensor(o)

# Cell
class TSTensor(NumpyTensor):
    '''Returns a tensor oftype torch.float32 and class TSTensor that has a show method'''
    @property
    def vars(self): return self.shape[-2]
    @property
    def len(self): return self.shape[-1]
    def __repr__(self):
        if self.numel() == 1: return f'{self}'
        elif self.ndim >= 3:   return f'TSTensor(samples:{self.shape[-3]}, vars:{self.shape[-2]}, len:{self.shape[-1]})'
        elif self.ndim == 2: return f'TSTensor(vars:{self.shape[-2]}, len:{self.shape[-1]})'
        elif self.ndim == 1: return f'TSTensor(len:{self.shape[-1]})'

class ToTSTensor(Transform):
    def encodes(self, o:np.ndarray): return TSTensor(o)

# Cell
class NumpyTensorBlock():
    def __init__(self, type_tfms=None, item_tfms=None, batch_tfms=None, dl_type=None, dls_kwargs=None):
        self.type_tfms  =                 L(type_tfms)
        self.item_tfms  = ToNumpyTensor + L(item_tfms)
        self.batch_tfms =                 L(batch_tfms)
        self.dl_type,self.dls_kwargs = dl_type,({} if dls_kwargs is None else dls_kwargs)

class TSTensorBlock():
    def __init__(self, type_tfms=None, item_tfms=None, batch_tfms=None, dl_type=None, dls_kwargs=None):
        self.type_tfms  =              L(type_tfms)
        self.item_tfms  = ToTSTensor + L(item_tfms)
        self.batch_tfms =              L(batch_tfms)
        self.dl_type,self.dls_kwargs = dl_type,({} if dls_kwargs is None else dls_kwargs)

# Cell
class TorchDataset():
    def __init__(self, X, y=None): self.X, self.y = X, y
    def __getitem__(self, idx): return (self.X[idx],) if self.y is None else (self.X[idx], self.y[idx])
    def __len__(self): return len(self.X)

class NumpyDataset():
    def __init__(self, X, y=None, types=None): self.X, self.y, self.types = X, y, types
    def __getitem__(self, idx):
        if self.types is None: return (self.X[idx], self.y[idx]) if self.y is not None else (self.X[idx])
        else: return (self.types[0](self.X[idx]), self.types[1](self.y[idx])) if self.y is not None else (self.types[0](self.X[idx]))
    def __len__(self): return len(self.X)
    @property
    def c(self): return 0 if self.y is None else 1 if isinstance(self.y[0], float) else len(np.unique(self.y))

class TSDataset():
    def __init__(self, X, y=None, types=None, sel_vars=None, sel_steps=None):
        self.X, self.y, self.types = X, y, types
        self.sel_vars = ifnone(sel_vars, slice(None))
        self.sel_steps = ifnone(sel_steps,slice(None))
    def __getitem__(self, idx):
        if self.types is None: return (self.X[idx, self.sel_vars, self.sel_steps], self.y[idx]) if self.y is not None else (self.X[idx])
        else: return (self.types[0](self.X[idx, self.sel_vars, self.sel_steps]), self.types[1](self.y[idx])) if self.y is not None else (self.types[0](self.X[idx]))
    def __len__(self): return len(self.X)
    @property
    def c(self): return 0 if self.y is None else 1 if isinstance(self.y[0], float) else len(np.unique(self.y))
    @property
    def vars(self): return self[0][0].shape[-2]
    @property
    def len(self): return self[0][0].shape[-1]

# Cell
class NumpyDatasets(Datasets):
    "A dataset that creates tuples from X (and y) and applies `tfms` of type item_tfms"
    _xtype, _ytype = NumpyTensor, None # Expected X and y output types (must have a show method)
    def __init__(self, X=None, y=None, items=None, tfms=None, tls=None, n_inp=None, dl_type=None, inplace=False, **kwargs):
        self.inplace = inplace
        if tls is None:
            X = itemify(X, tup_id=0)
            y = itemify(y, tup_id=0) if y is not None else y
            items = tuple((X)) if y is None else tuple((X,y))
            self.tfms = L(ifnone(tfms,[None]*len(ifnone(tls,items))))
        self.tls = L(tls if tls else [TfmdLists(item, t, **kwargs) for item,t in zip(items,self.tfms)])
        self.n_inp = (1 if len(self.tls)==1 else len(self.tls)-1) if n_inp is None else n_inp
        if len(self.tls[0]) > 0:
            self.ptls = L([tl if not self.inplace else tl[:] if type(tl.items[0]).__name__ == 'memmap' else tensor(stack(tl[:])) for tl in self.tls])
            self.types = [ifnone(_typ, type(tl[0]) if isinstance(tl[0], torch.Tensor) else tensor) for tl,_typ in zip(self.tls, [self._xtype, self._ytype])]

    def __getitem__(self, it):
        return tuple([typ(ptl[it]) if i==0 else typ(ptl[it]) for i,(ptl,typ) in enumerate(zip(self.ptls,self.types))])

    def subset(self, i): return type(self)(tls=L(tl.subset(i) for tl in self.tls), n_inp=self.n_inp, inplace=self.inplace, tfms=self.tfms)

    def _new(self, X, *args, y=None, **kwargs):
        items = ifnoneelse(y,tuple((X)),tuple((X, y)))
        return super()._new(items, tfms=self.tfms, do_setup=False, **kwargs)

    def show_at(self, idx, **kwargs):
        self.show(self[idx], **kwargs)
        plt.show()

    @property
    def items(self): return tuple([tl.items for tl in self.tls])
    @items.setter
    def items(self, vs):
        for tl,c in zip(self.tls, vs): tl.items = v


class TSDatasets(NumpyDatasets):
    "A dataset that creates tuples from X (and y) and applies `item_tfms`"
    _xtype, _ytype = TSTensor, None # Expected X and y output types (torch.Tensor - default - or subclass)
    def __init__(self, X=None, y=None, items=None, sel_vars=None, sel_steps=None, tfms=None, tls=None, n_inp=None, dl_type=None,
                 inplace=False, **kwargs):
        self.inplace = inplace
        if tls is None:
            X = itemify(X, tup_id=0)
            y = itemify(y, tup_id=0) if y is not None else y
            items = tuple((X,)) if y is None else tuple((X,y))
            self.tfms = L(ifnone(tfms,[None]*len(ifnone(tls,items))))
        self.sel_vars = ifnone(sel_vars, slice(None))
        self.sel_steps = ifnone(sel_steps,slice(None))
        self.tls = L(tls if tls else [TfmdLists(item, t, **kwargs) for item,t in zip(items,self.tfms)])
        self.n_inp = (1 if len(self.tls)==1 else len(self.tls)-1) if n_inp is None else n_inp
        if len(self.tls[0]) > 0:
            self.ptls = L([tl if not self.inplace else tl[:] if type(tl.items[0]).__name__ == 'memmap' else tensor(stack(tl[:])) for tl in self.tls])
            self.types = L([ifnone(_typ, type(tl[0]) if isinstance(tl[0], torch.Tensor) else tensor) for tl,_typ in zip(self.tls, [self._xtype, self._ytype])])

    def __getitem__(self, it):
        return tuple([typ(ptl[it])[...,self.sel_vars, self.sel_steps] if i==0 else typ(ptl[it]) for i,(ptl,typ) in enumerate(zip(self.ptls,self.types))])

    def subset(self, i): return type(self)(tls=L(tl.subset(i) for tl in self.tls), n_inp=self.n_inp,
                                           inplace=self.inplace, tfms=self.tfms, sel_vars=self.sel_vars, sel_steps=self.sel_steps)
    @property
    def vars(self): return self[0][0].shape[-2]
    @property
    def len(self): return self[0][0].shape[-1]


# Cell
def add_ds(dsets, X, y=None, test_items=None, rm_tfms=None, with_labels=False, inplace=False):
    "Create test datasets from X (and y) using validation transforms of `dsets`"
    items = ifnoneelse(y,tuple((X,)),tuple((X, y)))
    with_labels = ifnoneelse(y,False,True)
    if isinstance(dsets, (Datasets, NumpyDatasets, TSDatasets)):
        tls = dsets.tls if with_labels else dsets.tls[:dsets.n_inp]
        new_tls = L([tl._new(item, split_idx=1) for tl,item in zip(tls, items)])
        if rm_tfms is None: rm_tfms = [tl.infer_idx(get_first(item)) for tl,item in zip(new_tls, items)]
        else:               rm_tfms = tuplify(rm_tfms, match=new_tls)
        for i,j in enumerate(rm_tfms): new_tls[i].tfms.fs = new_tls[i].tfms.fs[j:]
        if isinstance(dsets, TSDatasets):
            return TSDatasets(tls=new_tls, n_inp=dsets.n_inp, inplace=inplace, tfms=dsets.tfms, sel_vars=dsets.sel_vars, sel_steps=dsets.sel_steps)
        elif isinstance(dsets, NumpyDatasets):
            return NumpyDatasets(tls=new_tls, n_inp=dsets.n_inp, inplace=inplace, tfms=dsets.tfms)
        elif isinstance(dsets, Datasets): return Datasets(tls=new_tls)
    elif isinstance(dsets, TfmdLists):
        new_tl = dsets._new(items, split_idx=1)
        if rm_tfms is None: rm_tfms = dsets.infer_idx(get_first(items))
        new_tl.tfms.fs = new_tl.tfms.fs[rm_tfms:]
        return new_tl
    else: raise Exception(f"This method requires using the fastai library to assemble your data.Expected a `Datasets` or a `TfmdLists` but got {dsets.__class__.__name__}")

@patch
def add_test(self:NumpyDatasets, X, y=None, test_items=None, rm_tfms=None, with_labels=False, inplace=False):
    return add_ds(self, X, y=y, test_items=test_items, rm_tfms=rm_tfms, with_labels=with_labels, inplace=inplace)

@patch
def add_unlabeled(self:NumpyDatasets, X, test_items=None, rm_tfms=None, with_labels=False, inplace=False):
    return add_ds(self, X, y=None, test_items=test_items, rm_tfms=rm_tfms, with_labels=with_labels, inplace=inplace)

# Cell
_batch_tfms = ('after_item','before_batch','after_batch')

class NumpyDataLoader(TfmdDL):
    idxs = None
    do_item = noops # create batch returns indices
    def __init__(self, dataset, bs=64, shuffle=False, num_workers=None, batch_tfms=None, verbose=False, do_setup=True, **kwargs):
        "after_batch == batch_tfms"
        if num_workers is None: num_workers = min(16, defaults.cpus)
        for nm in _batch_tfms:
            if nm in kwargs:
                if nm in ['after_item','before_batch'] or (nm == 'after_batch' and batch_tfms is not None):
                    t = kwargs.get('after_batch', None)
                    assert t is None or (hasattr(t, 'fs') and t.fs[0].name == 'noop'), \
                    f'You should use batch tfms instead of {nm}'
            if nm == 'after_batch' and batch_tfms is not None: kwargs[nm] = Pipeline(batch_tfms)
            kwargs[nm] = Pipeline(kwargs.get(nm,None))
        bs = min(bs, len(dataset))
        super().__init__(dataset, bs=bs, shuffle=shuffle, num_workers=num_workers, **kwargs)
        if do_setup:
            for nm in _batch_tfms:
                pv(f"Setting up {nm}: {kwargs[nm]}", verbose)
                kwargs[nm].setup(self)

    def create_batch(self, b):
        it = b if self.shuffle else slice(b[0], b[0] + self.bs)
        self.idxs = b
        return self.dataset[it]

    def create_item(self, s): return s

    def get_idxs(self):
        idxs = Inf.count if self.indexed else Inf.nones
        if self.n is not None: idxs = list(range(len(self.dataset)))
        if self.shuffle: idxs = self.shuffle_fn(idxs)
        return idxs

    @delegates(plt.subplots)
    def show_batch(self, b=None, ctxs=None, max_n=9, nrows=3, ncols=3, figsize=(16, 10), **kwargs):
        b = self.one_batch()
        db = self.decode_batch(b, max_n=max_n)
        if figsize is None: figsize = (ncols*6, max_n//ncols*4)
        if ctxs is None: ctxs = get_grid(min(len(db), nrows*ncols), nrows=None, ncols=ncols, figsize=figsize, **kwargs)
        for i,ctx in enumerate(ctxs): show_tuple(db[i], ctx=ctx)

    @delegates(plt.subplots)
    def show_results(self, b, preds, ctxs=None, max_n=9, nrows=3, ncols=3, figsize=(16, 10), **kwargs):
        t = self.decode_batch(b, max_n=max_n)
        p = self.decode_batch((b[0],preds), max_n=max_n)
        if figsize is None: figsize = (ncols*6, max_n//ncols*4)
        if ctxs is None: ctxs = get_grid(min(len(t), nrows*ncols), nrows=None, ncols=ncols, figsize=figsize, **kwargs)
        for i,ctx in enumerate(ctxs):
            title = f'True: {t[i][1]}\nPred: {p[i][1]}'
            color = 'green' if t[i][1] == p[i][1] else 'red'
            t[i][0].show(ctx=ctx, title=title, title_color=color)

@delegates(plt.subplots)
def show_tuple(tup, **kwargs):
    "Display a timeseries plot from a decoded tuple"
    tup[0].show(title='unlabeled' if len(tup) == 1 else tup[1], **kwargs)

class TSDataLoader(NumpyDataLoader):
    @property
    def vars(self): return self.dataset[0][0].shape[-2]
    @property
    def len(self): return self.dataset[0][0].shape[-1]

# Cell
_batch_tfms = ('after_item','before_batch','after_batch')

class NumpyDataLoaders(DataLoaders):
    _xblock = NumpyTensorBlock
    _dl_type = NumpyDataLoader
    def __init__(self, *loaders, path='.', device=default_device()):
        self.loaders,self.path = list(loaders),Path(path)
        self.device = device

    @classmethod
    @delegates(DataLoaders.from_dblock)
    def from_numpy(cls, X, y=None, splitter=None, valid_pct=0.2, seed=0, item_tfms=None, batch_tfms=None, **kwargs):
        "Create timeseries dataloaders from arrays (X and y, unless unlabeled)"
        if splitter is None: splitter = RandomSplitter(valid_pct=valid_pct, seed=seed)
        getters = [ItemGetter(0), ItemGetter(1)] if y is not None else [ItemGetter(0)]
        dblock = DataBlock(blocks=(cls._xblock, CategoryBlock),
                           getters=getters,
                           splitter=splitter,
                           item_tfms=item_tfms,
                           batch_tfms=batch_tfms)

        source = itemify(X) if y is None else itemify(X,y)
        return cls.from_dblock(dblock, source, **kwargs)

    @classmethod
    def from_dsets(cls, *ds, path='.', bs=64, num_workers=0, batch_tfms=None, device=None, shuffle_train=True, **kwargs):
        default = (shuffle_train,) + (False,) * (len(ds)-1)
        defaults = {'shuffle': default, 'drop_last': default}
        kwargs = merge(defaults, {k: tuplify(v, match=ds) for k,v in kwargs.items()})
        kwargs = [{k: v[i] for k,v in kwargs.items()} for i in range_of(ds)]
        if not is_listy(bs): bs = [bs]
        if len(bs) != len(ds): bs = bs * len(ds)
        device = ifnone(device,default_device())
        return cls(*[cls._dl_type(d, bs=b, num_workers=num_workers, batch_tfms=batch_tfms, **k) \
                     for d,k,b in zip(ds, kwargs, bs)], path=path, device=device)

class TSDataLoaders(NumpyDataLoaders):
    _xblock = TSTensorBlock
    _dl_type = TSDataLoader

# Cell
@patch
def cws(self:DataLoader):
    target = torch.Tensor(self.dataset.items[-1]).to(dtype=torch.int64)
    # Compute samples weight (each sample should get its own weight)
    class_sample_count = torch.tensor(
        [(target == t).sum() for t in torch.unique(target, sorted=True)])
    weights = 1. / class_sample_count.float()
    return (weights / weights.sum()).to(default_device())