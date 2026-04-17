import os
import requests
from dotenv import load_dotenv

load_dotenv()
app_id = os.getenv("FEISHU_APP_ID")
app_secret = os.getenv("FEISHU_APP_SECRET")
print(f"App ID: {app_id}")
url_token = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
resp = requests.post(url_token, json={"app_id": app_id, "app_secret": app_secret})
print("Token resp:", resp.json())
token = resp.json().get("tenant_access_token")

# Create a small dummy image
image_path = "test_dummy.png"
with open(image_path, "wb") as f:
    f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\x0d\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')

url_img = "https://open.feishu.cn/open-apis/im/v1/images"
headers = {"Authorization": f"Bearer {token}"}
with open(image_path, "rb") as f:
    form_files = {
        "image_type": (None, "message"),
        "image": (os.path.basename(image_path), f, "image/png")
    }
    resp = requests.post(url_img, headers=headers, files=form_files)
    print("Upload status:", resp.status_code)
    print("Upload content:", resp.content)
