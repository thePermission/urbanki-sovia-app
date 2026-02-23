import torch
import torch.nn.functional as F
from torch import nn

from sovia.utils.file_handling import get_path_to_data


class SimpleEmbeddingNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(4, 64, 5)  # Input: 3 channels (RGB)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(self.conv1.out_channels, 128, 5)
        self.adaptive_pool = nn.AdaptiveAvgPool2d((4, 4))
        adaptive_avg_pool_output_size = self.adaptive_pool.output_size[0] * self.adaptive_pool.output_size[1]
        self.fc1 = nn.Linear(self.conv2.out_channels * adaptive_avg_pool_output_size, 256)
        self.fc2 = nn.Linear(self.fc1.out_features, 128)
        self.dropout = nn.Dropout(p=0.3)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.dropout(x)
        x = self.adaptive_pool(x)  # Ensure output spatial size is 4x4
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x


class SiameseNetwork(nn.Module):
    def __init__(
            self,
            embedding_net,
            *,
            init_scale: float = 10.0,
            init_margin: float = 1.0,
            learnable_margin: bool = True,
            learnable_scale: bool = False,
    ):
        super().__init__()
        self.embedding_net = embedding_net  # For example, a simple CNN

        if init_scale <= 0:
            raise ValueError("init_scale must be > 0")

        self._scale_param = nn.Parameter(torch.tensor(float(init_scale)), requires_grad=learnable_scale)

        if learnable_margin:
            self.margin = nn.Parameter(torch.tensor(float(init_margin)), requires_grad=True)
        else:
            self.register_buffer("margin", torch.tensor(float(init_margin)), persistent=True)

    @property
    def scale(self) -> torch.Tensor:
        # garantiert > 0 und numerisch stabil
        return F.softplus(self._scale_param)

    def forward(self, x1, x2):
        out1 = self.embedding_net(x1)
        out2 = self.embedding_net(x2)
        return out1, out2

    def forward_with_classification(self, x1, x2):
        """Neue Methode die Sigmoid-Similarity zurückgibt"""
        out1 = self.embedding_net(x1)
        out2 = self.embedding_net(x2)
        # Distanz berechnen
        dist = torch.nn.functional.pairwise_distance(out1, out2)
        similarity = torch.sigmoid(dist)
        return similarity

    def forward_with_logits(self, x1, x2):
        """
        Gibt einen Logit zurück (unbounded), geeignet für BCEWithLogits/FocalLossLogit.
        Wichtig: KEIN Sigmoid hier anwenden.

        In deinem Fall bedeutet label=1: "Bilder sind unterschiedlich" (difference).
        Deshalb wollen wir:
          - kleine Distanz => niedriger Logit => p~0 (nicht unterschiedlich)
          - große Distanz  => hoher Logit   => p~1 (unterschiedlich)
        """
        out1 = self.embedding_net(x1)
        out2 = self.embedding_net(x2)
        dist = torch.nn.functional.pairwise_distance(out1, out2)
        logits = self.scale * (dist - self.margin)
        return logits

    def forward_with_probability(self, x1, x2):
        """Nur für Inferenz/Metriken: Wahrscheinlichkeit (difference) aus Logit."""
        logits = self.forward_with_logits(x1, x2)
        prob = torch.sigmoid(logits)
        return prob


def load_model():
    device = torch.device("cpu")
    model = SiameseNetwork(SimpleEmbeddingNet())
    path = get_path_to_data(__file__) / "model.pth"
    model.load_state_dict(torch.load(path, map_location=device, weights_only=True))
    model.eval()
    return model
