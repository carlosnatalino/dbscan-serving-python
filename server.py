from concurrent import futures
import logging

from sklearn.cluster import DBSCAN

import grpc

import dbscanserving_pb2
import dbscanserving_pb2_grpc

class DbscanServer(dbscanserving_pb2_grpc.DetectorServicer):

    def __init__(self) -> None:
        pass

    def Detect(self, request, context):
        # logging.debug('DbscanServer::Detect')
        clusters = DBSCAN(eps=request.eps, min_samples=request.min_samples).fit_predict([[x for x in sample.features] for sample in request.samples])
        response = dbscanserving_pb2.DetectionResponse()
        for cluster in clusters:
            response.cluster_indices.append(cluster)
        # print('detect request', request, response)
        # print('\ndetect response', response)
        return response


if __name__ == '__main__':
    logging.basicConfig()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    dbscanserving_pb2_grpc.add_DetectorServicer_to_server(DbscanServer(), server)
    server.add_insecure_port('[::]:50051')
    print('starting...')
    server.start()
    server.wait_for_termination()
