import logging
from logging.config import dictConfig
from concurrent import futures

from sklearn.cluster import DBSCAN

import grpc

import dbscanserving_pb2
import dbscanserving_pb2_grpc

from multiprocessing import Process

# dependencies of the rest service
import uvicorn
from fastapi import FastAPI, HTTPException
from dbscanserving_pydantic import DetectionRequest, DetectionResponse

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] [%(levelname)s] [%(name)s] [%(module)s:%(lineno)s] - %(message)s',
    }},
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'to_file': {
                'level': 'DEBUG',
                'formatter': 'default',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'messages.log',
                'maxBytes': 5000000,
                'backupCount': 10
            },
    },
    'root': {
        'level': 'DEBUG',  # TODO: select here the level of logging that you want
        'handlers': ['console']
        # , 'to_file']
    }
})
grpc_logger = logging.getLogger('grpc')
rest_logger = logging.getLogger('rest')


class DBSCANServer(dbscanserving_pb2_grpc.DetectorServicer):

    def __init__(self) -> None:
        pass

    def Detect(self, request: dbscanserving_pb2.DetectionResponse, context):
        grpc_logger.debug('DBSCANServer::Detect')
        if len(request.dimensions) != 2:
            context.set_details("The dimensions must have `2` elements.")
            grpc_logger.debug("The dimensions must have `2` elements.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return dbscanserving_pb2.DetectionResponse()
        if request.dimensions[0] != len(request.samples):
            context.set_details("The sample dimension declared does not match with the number of samples received.")
            grpc_logger.debug("The sample dimension declared does not match with the number of samples received.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return dbscanserving_pb2.DetectionResponse()
        # TODO: implement the validation of the features dimension
        clusters = DBSCAN(eps=request.eps, min_samples=request.min_samples).fit_predict([[x for x in sample.features] for sample in request.samples])
        response = dbscanserving_pb2.DetectionResponse()
        for cluster in clusters:
            response.cluster_indices.append(cluster)
        # print('detect request', request, response)
        # print('\ndetect response', response)
        return response


app = FastAPI()

@app.post("/detect", response_model=DetectionResponse)
async def detect(request: DetectionRequest):
    rest_logger.debug("REST called")
    # print(request)
    if len(request.dimensions) != 2:
        raise HTTPException(status_code=400, detail="The dimensions must have `2` elements.")
    if request.dimensions[0] != len(request.samples):
        raise HTTPException(status_code=400, detail="The sample dimension declared does not match with the number of samples received.")
    # TODO: implement the validation of the features dimension
    clusters = DBSCAN(eps=request.eps, min_samples=request.min_samples).fit_predict([[x for x in sample.features] for sample in request.samples])
    # print(clusters)
    response = DetectionResponse()
    for cluster in clusters:
        response.cluster_indices.append(cluster)
    return response


def run_rest_server():
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == '__main__':
    logging.basicConfig()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    dbscanserving_pb2_grpc.add_DetectorServicer_to_server(DBSCANServer(), server)
    server.add_insecure_port('[::]:50051')
    print('starting...')
    server.start()

    rest_process = Process(target=run_rest_server)
    rest_process.start()

    try:
        server.wait_for_termination()
    except:
        rest_process.terminate()