import torch
import torch.nn as nn
import torch.nn.functional as F


class MelSpectrogramCNN(nn.Module):
    """
    2D Convolutional Neural Network for Log-Mel Spectrogram classification.
    Input shape: (Batch, 1, 128, Time)
    Output shape: (Batch, 1) raw logit output
    """
    def __init__(self, in_channels: int = 1, num_classes: int = 1):
        super(MelSpectrogramCNN, self).__init__()

        # Conv Block 1: 1 -> 32
        self.conv1 = nn.Conv2d(in_channels, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.drop1 = nn.Dropout(0.25)

        # Conv Block 2: 32 -> 64
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.drop2 = nn.Dropout(0.25)

        # Conv Block 3: 64 -> 128
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.drop3 = nn.Dropout(0.3)

        # Conv Block 4: 128 -> 256
        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(256)
        self.gap = nn.AdaptiveAvgPool2d((1, 1))
        self.drop4 = nn.Dropout(0.4)

        # Classification Head
        self.fc1 = nn.Linear(256, 64)
        self.drop5 = nn.Dropout(0.3)
        self.fc2 = nn.Linear(64, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Block 1
        x = self.drop1(self.pool1(F.leaky_relu(self.bn1(self.conv1(x)), 0.1)))

        # Block 2
        x = self.drop2(self.pool2(F.leaky_relu(self.bn2(self.conv2(x)), 0.1)))

        # Block 3
        x = self.drop3(self.pool3(F.leaky_relu(self.bn3(self.conv3(x)), 0.1)))

        # Block 4
        x = self.drop4(self.gap(F.leaky_relu(self.bn4(self.conv4(x)), 0.1)))

        # Flatten & Dense
        x = torch.flatten(x, 1)
        x = self.drop5(F.leaky_relu(self.fc1(x), 0.1))
        logits = self.fc2(x)
        return logits.squeeze(-1)


def get_parameter_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
