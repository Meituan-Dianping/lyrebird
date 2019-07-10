import axios from 'axios'

export const searchGroupByName = (name) => {
    return new axios({
        url: '/api/search/group/name/' + name
    })
}
