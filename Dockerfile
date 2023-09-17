FROM python:latest

ADD *.py /srv/homography/
ADD requirements.txt /srv/homography/


WORKDIR /srv/homography


RUN python3 -m venv ./venv
RUN . ./venv/bin/activate && python -m pip install -r ./requirements.txt


EXPOSE 9001
CMD ["./venv/bin/uvicorn", "homography:web", "--port", "9001", "--host", "0.0.0.0"]