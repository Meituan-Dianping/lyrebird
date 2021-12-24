<template>
  <div>
    <v-app-bar app dense elevation="3" height="44" color="background">
      <v-app-bar-nav-icon width="30">
          <img src="@/assets/logo.svg" width="40" class="ml-3"/>
      </v-app-bar-nav-icon>
      <v-app-bar-title width="30">
          <img src="@/assets/lyrebird.svg" width="120"/>
      </v-app-bar-title>
      <v-spacer/>

      <!-- Load plugin status which placement is top-right -->
      <span v-for="item in statusTopRightList" :key="item.id" class="mr-1 top-bar-item">
        <v-select
          v-model="item.src.selectedValue"
          :items="item.src.allItem"
          item-text="text"
          item-value="api"
          :prepend-icon="item.prepend_icon"
          dense
          @change="onChangeItem"
        />
      
      </span>

      <!-- Add Bandwidth here -->
      <span>
        <Poptip
          content="content"
          placement="top-start"
          width="250"
        >
          <b>Bandwidth: {{bandwidthExplanation}} </b>
          <div slot="title">
            <b>Bandwidth</b>
          </div>
          <div slot="content">
            <Row type="flex" justify="space-around">
              <Col span="12" v-for="(item, index) in bandwidthTemplates" :key="index">
                <Button
                  style="min-width:95px;margin-top:5px;"
                  :class="item.bandwidth == bandwidth ? 'bandwidth-btn-highlight' : ''"
                  @click.prevent="updateBandwidth(item.template_name)"
                >{{ item.template_name }}</Button>
              </Col>
            </Row>
          </div>
        </Poptip>
      </span>
      <!-- <Bandwidth/> -->

      <!-- Settings -->
      <!-- Not display -->
      <v-btn icon plain v-show="false">
        <v-icon size="18px" color="accent">mdi-cogs</v-icon>
      </v-btn>

      <!-- Theme -->
      <!-- Not display -->
      <v-btn icon plain @click="changeTheme" v-show="false">
        <v-icon size="18px" color="accent" v-if="this.$vuetify.theme.dark">mdi-brightness-4</v-icon>
        <v-icon size="18px" color="accent" v-else>mdi-brightness-5</v-icon>
      </v-btn>

      <NoticeCenter/>
    </v-app-bar>
  </div>
</template>

<script>
import Bandwidth from '@/views/appbar/Bandwidth.vue'
import NoticeCenter from '@/views/notice/NoticeCenter.vue'
import { makeRequest } from '@/api'

export default {
  name: 'MainLayout',
  components: {
    Bandwidth,
    NoticeCenter,
  },
  mounted () {
    this.$store.dispatch('loadBandwidth')
    this.$store.dispatch('loadBandwidthTemplates')
  },
  created () {
  },
  computed: {
    statusTopRightList () {
      return this.$store.state.statusbar.statusTopRightList
    },
    bandwidth () {
      return this.$store.state.bandwidth.bandwidth
    },
    bandwidthTemplates () {
      return this.$store.state.bandwidth.bandwidthTemplates
    },
    bandwidthExplanation () {
      for (let v of this.bandwidthTemplates) {
        if (this.bandwidth == v['bandwidth']) {
          if (this.bandwidth == -1) {
            return v['template_name']
          }
          else {
            return `${v['template_name']} ( ${v['bandwidth']} Kb/s)`
          }
        }
      }
    }
  },
  methods: {
    changeTheme () {
      this.$vuetify.theme.dark = !this.$vuetify.theme.dark
    },
    onChangeItem (api) {
      makeRequest(api)
        .then(response => {
          if (response.data && response.data.message) {
            this.$bus.$emit('msg.success', response.data.message)
          }
        })
        .catch(error => {
          this.$bus.$emit('msg.error', error.data.message)
        })
    },
    updateBandwidth (template_name) {
      this.$store.dispatch('updateBandwidth', template_name)
    }
  }
}
</script>

<style scoped>
.logo {
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.logo img {
  width: 200px
}
.main-footer {
  height: 28px;
  line-height: 28px;
  padding: 0;
}
.top-bar-item {
  width: 90px + 6px + 24px;
  height: 30px;
}
.top-bar-item-icon {
  width: 24px;
  height: 24px;
}
.top-bar-item-select {
  width: 90px;
  height: 26px;
  margin-left: 6px;
}
</style>
