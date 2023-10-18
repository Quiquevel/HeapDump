from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from functions.heapdump import getHeapdump

pod_exec = APIRouter(tags=["v1"])
class heapDumpModel(BaseModel):
    functionalEnvironment: str
    cluster: str
    region: str
    namespace: str
    pod: list
    action: str

    #to validate the cluster parameter
    @validator("cluster")
    def validate_cluster(cls, v):
        if not any(x in v for x in ["ohe","bks","probks","dmzbbks","ohe","probks","dmzbbks","azure","prodarwin","dmzbdarwin","proohe","dmzbohe","confluent"]):
            raise HTTPException(status_code=400, detail=f"{v} value is not valid for cluster")
        return v
    
    #to validate the region parameter
    @validator("region")
    def validate_region(cls, v):
        if not any(x in v for x in ["bo1","bo2","weu1","weu2"]):
            raise HTTPException(status_code=400, detail=f"{v} value is not valid for region")
        return v
    
#Calling to the principal function
@pod_exec.post("/heapdump")
async def execute_heapdump(target: heapDumpModel):
    return await getHeapdump(functionalEnvironment=target.functionalEnvironment, cluster=target.cluster, region=target.region, namespace=target.namespace, pod=target.pod, action=target.action)