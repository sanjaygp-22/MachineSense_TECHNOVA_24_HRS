import torch
import torch.nn as nn
import torch.nn.functional as F


class MelSpectrogramAutoencoder(nn.Module):
    """
    Convolutional Autoencoder for Log-Mel Spectrogram reconstruction.
    Input shape: (Batch, 1, 128, Time)
    Output shape: (Batch, 1, 128, Time) reconstructed spectrogram
    """
    def __init__(self, in_channels: int = 1):
        super(MelSpectrogramAutoencoder, self).__init__()

        # Encoder
        self.enc_conv1 = nn.Conv2d(in_channels, 32, kernel_size=3, padding=1)
        self.enc_bn1 = nn.BatchNorm2d(32)
        self.enc_pool1 = nn.MaxPool2d(2, 2)

        self.enc_conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.enc_bn2 = nn.BatchNorm2d(64)
        self.enc_pool2 = nn.MaxPool2d(2, 2)

        self.enc_conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.enc_bn3 = nn.BatchNorm2d(128)
        self.enc_pool3 = nn.MaxPool2d(2, 2)

        # Decoder
        self.dec_up1 = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False)
        self.dec_conv1 = nn.Conv2d(128, 64, kernel_size=3, padding=1)
        self.dec_bn1 = nn.BatchNorm2d(64)

        self.dec_up2 = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False)
        self.dec_conv2 = nn.Conv2d(64, 32, kernel_size=3, padding=1)
        self.dec_bn2 = nn.BatchNorm2d(32)

        self.dec_up3 = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False)
        self.dec_conv3 = nn.Conv2d(32, in_channels, kernel_size=3, padding=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        orig_h, orig_w = x.shape[2], x.shape[3]

        # Encoder pass
        e1 = F.relu(self.enc_bn1(self.enc_conv1(x)))
        p1 = self.enc_pool1(e1)

        e2 = F.relu(self.enc_bn2(self.enc_conv2(p1)))
        p2 = self.enc_pool2(e2)

        e3 = F.relu(self.enc_bn3(self.enc_conv3(p2)))
        p3 = self.enc_pool3(e3)

        # Decoder pass
        d1 = F.relu(self.dec_bn1(self.dec_conv1(self.dec_up1(p3))))
        d2 = F.relu(self.dec_bn2(self.dec_conv2(self.dec_up2(d1))))
        reconstructed = self.dec_conv3(self.dec_up3(d2))

        # Dynamic interpolation to match exact input (128, Time) dimensions
        if reconstructed.shape[2:] != (orig_h, orig_w):
            reconstructed = F.interpolate(reconstructed, size=(orig_h, orig_w), mode='bilinear', align_corners=False)

        return reconstructed


def get_autoencoder_parameter_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
