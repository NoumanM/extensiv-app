import json

def header_payload(session_id):
    payload = json.dumps({
        "columns": [
            "FullyAllocated", "IsClosed", "CanConfirm", "CanCancel", "CanUnconfirm", "FacilityId", "CustomerId",
            "BatchOrderId", "BatchUri", "EditUri", "FileSummariesUri", "CustomerUri", "CanSplit", "CanAllocate",
            "PickJobId", "IsPickDone", "CanDeallocate", "CanExportToTmw", "ParcelLabelType", "RowNumber", "Customer",
            "OrderId", "CreationDate", "PickDoneDate", "ProcessDate", "ReferenceNum", "SkuAndQty", "PickJobAssignee",
            "Status"
        ],
        "orderSearchInfo": {
            "IndexOptionsSearchBy": 0,
            "IndexOptionsReferenceNumber": 0,
            "IndexOptionsCustomerId": 0,
            "IndexOptionsFacilityId": 0,
            "IndexOptionsPoNum": 0,
            "IndexOptionsShipTo": 0,
            "IndexOptionsOrderNote": 0,
            "IndexOptionsStatus": "4",
            "IndexOptionsAsn": 2,
            "IndexOptionsInventoryAllocated": 2,
            "OrderNote": "",
            "StartDate": "",
            "EndDate": "",
            "Sku": "",
            "PurchaseOrderNumber": "",
            "SelectedSkus": "",
            "SelectedCustomer": 0,
            "SelectedFacility": 0,
            "ShowSku": True,
            "ShowBatchName": True,
            "SearchTarget": ""
        }
    })
    headers = {
        'COOKIE': f'ASP.NET_SessionId={session_id}',
        'Content-Type': 'application/json'
    }

    return payload, headers