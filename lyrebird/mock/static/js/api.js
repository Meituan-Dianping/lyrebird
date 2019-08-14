class LyrebirdAPI {
    //------Lyrebird status--------    

    /**
    Get lyrebird status
    {
        code: 1000,
        message: 'success',
        ip: '',
        mock.port: 9090,
        proxy.port: 4272
    }
    */
    getStatus(){
        return axios({
            url: '/api/status'
        })
    }
    
    //------Inspector flow---------

    /**
    Get flow list
    [
        {
            "id": "e4b83576-2937-4214-b564-568622ff1295",
            "request": {
            "method": "GET",
            "url": "http://host:port/path?query"
            },
            "response": {
            "code": 200,
            "mock": "proxy"
            },
            "response-time": 0.03377985954284668,
            "time": 1536027095.846837
        },
        ...
    ]
    */
    getFlowList(){
        return axios({
            url: '/api/flow'
        })
    }

    /**
    Clear flow list
    */
    deleteFlowList(){
        return axios({
            url: '/api/flow',
            method: 'DELETE'
        })
    }

    /**
    Save selected flow to current activated mock data group
    useage:
    this.$api.saveFlowList(
        {
            ids:[ ..selected flow id array..],
            group:'target group name'
        }
    )
    */
    saveFlowList(data){
        return axios({
            url: '/api/flow',
            method: 'POST',
            data: data
        })
    }

    /**
    Get flow detail by id
    {
        "id": "457978c4-e62b-4464-9750-fc0fa14253d1",
        "request": {
            "data": null,
            "headers": {
            "key": "value",
            ...
            },
            "method": "GET",
            "url": "req url"
        },
        "response": {
            "code": 200,
            "data": 'response content',
            "headers": {
            "Content-Type": "text/html; charset=UTF-8",
            ...
            }
        },
        "response-time": 0.036998748779296875,
        "time": 1536027095.235757
    }
    */
    getFlowDetail(flowID){
        return axios({
            url: '/api/flow/'+flowID
        })
    }

    //------Mock data manager------
    /**
    Get group name list
    return:
    [
        'GroupNameA',
        'GroupNameB'
    ]
    */
    getGroups(){
        return axios({
            url: '/api/mock'
        })
    }

    /**
    Get data list by data group name
    {
        "conf": {
            "filters": [
            {
                "contents": [
                "/fe"
                ],
                "response": "fe_c07ba164-bbd4-4f02-bd54-7d78a078a09d"
            }
            ],
            "parent": null
        },
        "data": [
            [
            "fe_c07ba164-bbd4-4f02-bd54-7d78a078a09d",
            "data/Test/fe_c07ba164-bbd4-4f02-bd54-7d78a078a09d"
            ]
        ]
    }
    */
    getDataList(groupId){
        return axios({
            url: '/api/mock/'+groupId
        })
    }

    /**
    Get mock data detail
    {
        "request": {
            "data": null,
            "headers": {
            "Accept-Encoding": "gzip, deflate",
            ...
            },
            "method": "POST",
            "url": "http://host"
        },
        "response": {
            "code": 200,
            "data": null,
            "headers": {
            "Cache-Control": "no-cache",
            ...
            }
        }
    }
    */
    getDataDetail(groupId, dataId){
        return axios({
            url: '/api/mock/'+groupId+'/data/'+dataId
        })
    }

    updateDataDetail(groupName, dataName, dataDetail){
        return axios({
            url: '/api/mock/'+groupName+'/data/'+dataName,
            method: 'PUT',
            data: JSON.stringify(dataDetail)
        })
    }

    /**
    Get activated data group ID
    */
    getActivatedGroup(){
        return axios({
            url: '/api/mock/activated'
        })
    }

    /**
    Activate data group by ID
    */
    activateGroup(groupId){
        return axios({
            url: '/api/mock/'+groupId+'/activate',
            method: 'PUT'
        })
    }
}


const api = new LyrebirdAPI()
