import * as api from '../api'
import {bus} from '../eventbus'

export default {
  state: {
    bandwidth: "UNLIMITED",
    bandwidthTemplates: []
  },
  mutations: {
    setBandwidth(state, bandwidth) {
      state.bandwidth = bandwidth
    },
    setBandwidthTemplates(state, bandwidthTemplates) {
      state.bandwidthTemplates = bandwidthTemplates
    }
  },
  actions: {
    loadBandwidth(context) {
      api
        .getBandwidth()
        .then(response => {
          if (response.data.code === 1000) {
            context.commit('setBandwidth', response.data.bandwidth)
          } else {
            bus.$emit('msg.error', 'loadBandwidth failed')
          }
        })
        .catch(error => {
          bus.$emit('msg.error','loadBandwidth failed '+ error.data.message)
        })
    },

    loadBandwidthTemplates(context) {
      api
        .getBandwidthTemplates()
        .then(response => {
          if (response.data.code === 1000) {
            context.commit(
              'setBandwidthTemplates',
              response.data.bandwidth_templates
            )
          } else {
            bus.$emit('msg.error', 'loadBandwidthTemplates failed')
          }
        })
        .catch(error => {
          bus.$emit('msg.error', 'loadBandwidthTemplates failed ' + error.data.message)
        })
    },

    updateBandwidth(context, templateName) {
      api
        .updateBandwidth(templateName)
        .then(response => {
          if (response.data.code === 1000) {
            console.log(response.data.bandwidth)
            context.commit('setBandwidth', response.data.bandwidth)
          } else {
            bus.$emit('msg.error', response.data.message)
          }
        })
        .catch(error => {
          bus.$emit('msg.error', 'updateBandwidthTemplate failed ' + error.data.message)
        })
    }
  }
}
