import axios from 'axios'

//------Notice manager------
/**
Get notification list
return:
{
  'noticeList': [],
  'notRemindList': []
}
*/
export const getNoticeList = () => {
    return axios({
        url: '/api/notice'
    })
}

//------Notice manager------
/**
Delete notification by key
*/
export const deleteNotice = (key) => {
    return axios({
        url: '/api/notice',
        data: { key },
        method: 'DELETE'
    })
}

//------Notice manager------
/**
Change notification status by key
return:
*/
export const updateNoticeStatus = (key, status) => {
    return axios({
        url: '/api/notice',
        data: { key, status },
        method: 'PUT'
    })
}
