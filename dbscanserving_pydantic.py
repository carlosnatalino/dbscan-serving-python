import dbscanserving_pb2
import dbscanserving_pb2_grpc
from protobuf2pydantic import message2pydantic as msg2py


class DetectionRequest(msg2py(dbscanserving_pb2.DetectionRequest)):
    pass


class DetectionResponse(msg2py(dbscanserving_pb2.DetectionResponse)):
    pass


class Sample(msg2py(dbscanserving_pb2.Sample)):
    pass
