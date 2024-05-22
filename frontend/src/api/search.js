import axios from 'axios'

export const searchGroupByName = (name) => {
    return axios({
        url: '/api/search/group?search_str=' + encodeURIComponent(name)
    })
}
