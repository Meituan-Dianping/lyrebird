import axios from 'axios'

export const searchGroupByName = (name) => {
    return axios({
        url: '/api/search/group/name/' + name
    })
}
