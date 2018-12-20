import inspect

import torch
from torch_geometric.utils import scatter_


class MessagePassing(torch.nn.Module):
    def __init__(self, aggr='add'):
        super(MessagePassing, self).__init__()

        self.message_args = inspect.getargspec(self.message)[0][1:]
        self.update_args = inspect.getargspec(self.update)[0][2:]
        print("DRIN")

    def propagate(self, aggr, edge_index, **kwargs):
        assert aggr in ['add', 'mean', 'max']

        for key, value in kwargs.items():
            kwargs[key] = value.unsqueeze(-1) if value.dim() == 1 else value
        kwargs['edge_index'] = edge_index

        row, col = edge_index

        size = None
        message_args = []
        for arg in self.message_args:
            if arg[-2:] == '_i':
                tmp = kwargs[arg[:-2]]
                size = tmp.size(0)
                message_args.append(tmp[row])
            elif arg[-2:] == '_j':
                tmp = kwargs[arg[:-2]]
                size = tmp.size(0)
                message_args.append(tmp[col])
            else:
                message_args.append(kwargs[arg])

        update_args = [kwargs[arg] for arg in self.update_args]

        out = self.message(*message_args)
        out = scatter_(aggr, out, row, dim_size=size)
        out = self.update(out, *update_args)

        return out

    def message(self, x_j):
        return x_j

    def update(self, aggr_out):
        return aggr_out

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)
