import grpc
import random
import requests
import time

import dbscanserving_pb2
import dbscanserving_pb2_grpc
from dbscanserving_pydantic import DetectionRequest, DetectionResponse, Sample


if __name__ == '__main__':
    channel = grpc.insecure_channel('localhost:50051')
    stub = dbscanserving_pb2_grpc.DetectorStub(channel)

    sum_grpc = 0
    sum_rest = 0

    for ida in range(200):

        request = dbscanserving_pb2.DetectionRequest()
        rest_request = DetectionRequest()

        request.dimensions.append(310)
        rest_request.dimensions.append(310)
        request.dimensions.append(100)
        rest_request.dimensions.append(100)
        request.eps = rest_request.eps = 100.5
        request.min_samples = rest_request.min_samples = 50

        for _ in range(200):
            grpc_sample = dbscanserving_pb2.Sample()
            rest_sample = Sample()
            for __ in range(100):
                grpc_sample.features.append(random.uniform(0., 10.))
                rest_sample.features.append(random.uniform(0., 10.))
            request.samples.append(grpc_sample)
            rest_request.samples.append(rest_sample)
        
        for _ in range(100):
            grpc_sample = dbscanserving_pb2.Sample()
            rest_sample = Sample()
            for __ in range(100):
                grpc_sample.features.append(random.uniform(50., 60.))
                rest_sample.features.append(random.uniform(50., 60.))
            request.samples.append(grpc_sample)
            rest_request.samples.append(rest_sample)
        
        for _ in range(10):
            grpc_sample = dbscanserving_pb2.Sample()
            rest_sample = Sample()
            for __ in range(100):
                grpc_sample.features.append(random.uniform(5000., 6000.))
                rest_sample.features.append(random.uniform(5000., 6000.))
            request.samples.append(grpc_sample)
            rest_request.samples.append(rest_sample)

        start = time.time_ns()
        response = stub.Detect(request)
        end = time.time_ns()
        sum_grpc += (end - start) / 1.e6  # converts ns to ms

        # print(f'gRPC response: {response.cluster_indices}')
        start = time.time_ns()
        response = requests.post("http://localhost:8080/detect", json=rest_request.dict())
        end = time.time_ns()
        sum_rest += (end - start) / 1.e6  # convert ns to ms
        # print('RAW: ', response.content)
        response_obj = DetectionResponse.parse_raw(response.text)
        # print(f'REST response: {response_obj}')
        print("RESPONSE:", ida)

    print('Avg. time gRPC: {:.2f}'.format(sum_grpc / 200))
    print('Avg. time REST: {:.2f}'.format(sum_rest / 200))
