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
    def __init__(self, embedding_net):
        super().__init__()
        self.embedding_net = embedding_net  # For example, a simple CNN

    def forward(self, x1, x2):
        out1 = self.embedding_net(x1)
        out2 = self.embedding_net(x2)
        return out1, out2


def load_model():
    device = torch.device("cpu")
    model = SiameseNetwork(SimpleEmbeddingNet())
    path = get_path_to_data(__file__) / "model/second_training_weights.pth"
    model.load_state_dict(torch.load(path, map_location=device, weights_only=True))
    model.eval()
    return model
