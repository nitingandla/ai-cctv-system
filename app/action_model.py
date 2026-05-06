import torch
import torchvision.transforms as transforms
from torchvision.models.video import r3d_18
import cv2
model = r3d_18(pretrained=True)
model.eval()
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((112, 112)),
    transforms.ToTensor()
])
frame_buffer = []
def predict_action(frame):
    global frame_buffer
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = transform(frame)
    frame_buffer.append(frame)
    if len(frame_buffer) > 8:   
        frame_buffer.pop(0)
    if len(frame_buffer) == 8:
        clip = torch.stack(frame_buffer)
        clip = clip.permute(1, 0, 2, 3)
        clip = clip.unsqueeze(0)
        with torch.no_grad():
            output = model(clip)
        return torch.argmax(output).item()
    return None