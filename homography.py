#!./venv/bin/python

import sys


import numpy as np
import cv2 as cv
from cv2.typing import MatLike as cvMat

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional


class Homography:
    H: cvMat

    # initialize homography matrix
    def __init__(self, cam_points, map_points):
        cam_pts = np.array(cam_points).reshape(-1, 1, 2)
        map_pts = np.array(map_points).reshape(-1, 1, 2)
        self.H, _ = cv.findHomography(cam_pts, map_pts, cv.RANSAC, 5.0)

    # calculate point position
    def getPointPosition(self, point):
        if len(point) == 2:
            point.append(1)
        p = np.array(np.dot(self.H, point))
        return [p[0] / p[2], p[1] / p[2]]

    # returns 4 points for bbox
    def getBBoxPosition(self, bbox):
        return [self.getPointPosition(p) for p in self.bboxToPoints(bbox)]

    # convert bbox to points array
    def bboxToPoints(self, bbox: list[float]) -> list[list[float]]:
        return [
            [bbox[0], bbox[1]],
            [bbox[0] + bbox[2], bbox[1]],
            [bbox[0] + bbox[2], bbox[1] + bbox[3]],
            [bbox[0], bbox[1] + bbox[3]],
        ]


# initialization tests
cam_points = [[0.2, 0.2], [0.85, 0.24], [0.86, 0.83], [0.32, 0.77]]
map_points = [[0.47, 0.24], [0.73, 0.25], [0.73, 0.82], [0.48, 0.74]]

H = Homography(cam_points, map_points)
p = H.getPointPosition([0.2, 0.2])

if round(p[0], 2) != 0.47 or round(p[1], 2) != 0.24:
    print("ERROR: something wrong", [0.2, 0.2], "=>", p, file=sys.stderr)

p = H.getBBoxPosition([0.2, 0.2, 0.65, 0.57])
if len(p) != 4:
    print("ERROR: bbox points is wrong:", p)


#
# web API to find homography matrix and calculate projection positions
#

# init fastapi
web = FastAPI()


class HomographyReq(BaseModel):
    id: int
    fov_cam: list[list[float]]
    fov_map: list[list[float]]
    items: Optional[list[dict]] | None = None
    bbox: Optional[list[float]] | None = None
    points: Optional[list[list[float]]] | None = None


class HomographyResp(BaseModel):
    items: list[dict]
    points: list[list[float]]


@web.post("/", response_model=HomographyResp)
async def HomographyHandler(req: HomographyReq):
    # calc matrix
    H = Homography(req.fov_cam, req.fov_map)

    # response
    resp = {
        "points": [],
        "items": [],
    }

    # if request has bbox calculate it projection position
    if req.bbox is not None and len(req.bbox) == 4:
        resp["points"] = H.getBBoxPosition(req.bbox)

    if req.points is not None:
        for p in req.points:
            resp["points"].append(H.getPointPosition(p))

    # calculate positon for the each item in request
    if req.items is not None and len(req.items) > 0:
        for item in req.items:
            if "data" not in item:
                item["data"] = {}
            item["data"]["points"] = H.getBBoxPosition(item["bbox"])

            resp["items"].append(item)

    return resp
