# Service for calculating coordinates for maps

## run

```shell
python -m venv ./venv
source ./venv/bin/activate
pip install  -r requirements.txt
uvicorn homography:web --port 9001 --reload
```

## requirements

```txt
fastapi==0.103.1
numpy==1.26.0
opencv-python==4.8.0.76
pydantic==2.3.0
uvicorn==0.23.2
```
