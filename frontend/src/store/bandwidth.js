import * as api from "../api";

export default {
  state: {
    bandwidth: -1,
    bandwidthTemplates: []
  },
  mutations: {
    setBandwidth(state, bandwidth) {
      state.bandwidth = bandwidth;
    },
    setBandwidthTemplates(state, bandwidthTemplates) {
      state.bandwidthTemplates = bandwidthTemplates;
    }
  },
  actions: {
    loadBandwidth(context) {
      api
        .getBandwidth()
        .then(response => {
          if (response.data.code === 1000) {
            context.commit("setBandwidth", response.data.bandwidth);
          } else {
            console.error("loadBandwidth failed", error);
          }
        })
        .catch(error => {
          console.error("loadBandwidth failed", error);
        });
    },

    loadBandwidthTemplates(context) {
      api
        .getBandwidthTemplates()
        .then(response => {
          if (response.data.code === 1000) {
            context.commit(
              "setBandwidthTemplates",
              response.data.bandwidth_templates
            );
          } else {
            console.error("loadBandwidthTemplates failed", error);
          }
        })
        .catch(error => {
          console.error("loadBandwidthTemplates failed", error);
        });
    },

    updateBandwidth(context, template_name) {
      api
        .updateBandwidth(template_name)
        .then(response => {
          if (response.data.code === 1000) {
            console.log(response.data.bandwidth);
            context.commit("setBandwidth", response.data.bandwidth);
          } else {
            console.error(response.data.message);
          }
        })
        .catch(error => {
          console.error("updateBandwidthTemplate failed", error);
        });
    }
  }
};
