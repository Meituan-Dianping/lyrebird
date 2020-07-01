import axios from 'axios'

export const getFlowMode = () => {
    return axios({
        url: '/api/mode'
    })
}
