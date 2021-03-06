__authors__ = "Ian Goodfellow"
__copyright__ = "Copyright 2010-2012, Universite de Montreal"
__credits__ = ["Ian Goodfellow"]
__license__ = "3-clause BSD"
__maintainer__ = "Ian Goodfellow"
__email__ = "goodfeli@iro"
from pylearn2.datasets.dataset import Dataset

class TransformerDataset(Dataset):
    """
        A dataset that applies a transformation on the fly
        as examples are requested.
    """
    def __init__(self, raw, transformer, cpu_only = False):
        """
            raw: a pylearn2 Dataset that provides raw data
            transformer: a pylearn2 Block to transform the data
        """
        self.raw = raw
        self.transformer = transformer
        self.transformer.cpu_only = cpu_only

    def get_batch_design(self, batch_size):
        X = self.raw.get_batch_design(batch_size)
        X = self.transformer.perform(X)
        return X

    def get_batch_topo(self, batch_size):
        """ there's no concept of a topology-aware
        transformation right now so we just treat the
        dataset as consisting of big 1D images
        this is kind of a hack, long term solution is
        to make topo pipeline support having 0 topological
        dimensions (right now I believe it only supports 2,
        it should support N >= 0)"""
        X = self.get_batch_design(batch_size)
        return X.reshape(X.shape[0],X.shape[1],1,1)

    def iterator(self, mode=None, batch_size=None, num_batches=None,
                 topo=None, targets=None, rng=None):

        raw_iterator = self.raw.iterator(mode, batch_size, num_batches, topo, targets, rng)

        final_iterator = TransformerIterator(raw_iterator, self)

        return final_iterator

    def has_targets(self):
        return self.raw.y is not None


class TransformerIterator(object):

    def __init__(self, raw_iterator, transformer_dataset):
        self.raw_iterator = raw_iterator
        self.transformer_dataset = transformer_dataset

    def __iter__(self):
        return self

    def next(self):

        raw_batch = self.raw_iterator.next()

        if self.raw_iterator._targets:
            rval = (self.transformer_dataset.transformer.perform(raw_batch[0]), raw_batch[1])
        else:
            rval = self.transformer_dataset.transformer.perform(raw_batch)

        return rval

    @property
    def num_examples(self):
        return self.raw_iterator.num_examples
