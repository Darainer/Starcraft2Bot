"""Optional neural dependency; no game imports, identifiers or control authority."""

import torch
from torch import Tensor, nn


class RecurrentCore(nn.Module):
    def __init__(self, input_size: int = 512, hidden_size: int = 256) -> None:
        super().__init__()
        self.hidden_size = hidden_size
        self.cell = nn.GRUCell(input_size, hidden_size)

    def forward(self, semantic: Tensor, memory: Tensor, reset: Tensor) -> Tensor:
        """Each batch row belongs to one environment/participant; reset before use."""
        memory = memory * (~reset.bool()).to(memory.dtype).unsqueeze(-1)
        result: Tensor = self.cell(semantic, memory)
        return result

    def initial(self, batch_size: int = 1) -> Tensor:
        return torch.zeros(batch_size, self.hidden_size, device=next(self.parameters()).device)
