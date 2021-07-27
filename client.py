import grpc
import random

import dbscanserving_pb2
import dbscanserving_pb2_grpc

if __name__ == '__main__':
    channel = grpc.insecure_channel('localhost:50051')
    stub = dbscanserving_pb2_grpc.DetectorStub(channel)
    request = dbscanserving_pb2.DetectionRequest()

    request.eps = 100.5
    request.min_samples = 50

    for _ in range(200):
        sample = dbscanserving_pb2.Sample()
        for __ in range(100):
            sample.features.append(random.uniform(0., 10.))
        request.samples.append(sample)
    
    for _ in range(100):
        sample = dbscanserving_pb2.Sample()
        for __ in range(100):
            sample.features.append(random.uniform(50., 60.))
        request.samples.append(sample)
    
    for _ in range(10):
        sample = dbscanserving_pb2.Sample()
        for __ in range(100):
            sample.features.append(random.uniform(100000.0, 20000000000.0))
        request.samples.append(sample)

    response = stub.Detect(request)
    print(f'Response: {response}')
