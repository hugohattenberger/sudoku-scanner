#  2 Creation du modèle
import torch.nn as nn
import torch as torch

# Résultats reproductible
random_state = 42

# Calcul sur GPU si disponible
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class ResNetBlock(nn.Module):

  def __init__(self, in_ch, out_ch, stride = 1):
    super().__init__()
    self.conv_block = nn.Sequential(
        nn.BatchNorm2d(in_ch),
        nn.ReLU(),
        nn.Conv2d(in_ch, out_ch, kernel_size = 3, padding = 1, stride = stride, bias = False ),
        nn.BatchNorm2d(out_ch),
        nn.ReLU(),
        nn.Conv2d(out_ch, out_ch, kernel_size = 3, padding = 1, stride = 1, bias = False))

    if stride != 1 or in_ch != out_ch:
        self.shortcut = nn.Conv2d(in_ch, out_ch, kernel_size = 1, stride = stride, bias = False)
    else:
        self.shortcut = nn.Identity()

  def forward(self, x):

    return self.conv_block(x) + self.shortcut(x)

class ResNet(nn.Module):
  def __init__(self):
    super().__init__()
    self.model = nn.Sequential(
        nn.Conv2d(1,32, kernel_size = 3, padding = 1, bias = False),
        ResNetBlock(32,32),
        ResNetBlock(32,64, stride = 2),
        ResNetBlock(64,128, stride = 2),
        ResNetBlock(128,256, stride = 2),

        nn.AdaptiveAvgPool2d(1),
        nn.Flatten(),
        nn.Linear(256,10)
    )

  def forward(self,x):
    return self.model(x)

model = ResNet().to(device)
print(model)