<template>
  <div>
    <v-app-bar app dense elevation="3" height="44" color="background">
      <v-app-bar-title width="30">
        <img src="@/assets/logo.svg" width="40" class="app-bar-logo" style="margin: 12px 12px 0px -8px;"/>
        <img src="@/assets/lyrebird.svg" width="120" class="app-bar-lyrebird" style="margin-bottom:8px;"/>
      </v-app-bar-title>
      <v-spacer/>

      <!-- Load plugin status which placement is top-right -->
      <span v-for="item in statusTopRightList" :key="item.id" class="top-bar-item mr-5">
        <v-select
          v-model="item.src.selected"
          :items="item.src.allItem"
          item-text="text"
          item-value="api"
          :prepend-icon="item.prepend_icon"
          dense
          outlined
          color="primary"
          height="26"
          class="top-bar-item-select"
          :menu-props="{ bottom: true, offsetY: true }"
          @change="onChangeItem"
        />
      </span>

      <!-- Add Bandwidth here -->
      <Bandwidth />
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
  },
  created () {
  },
  computed: {
    statusTopRightList () {
      return this.$store.state.statusbar.statusTopRightList
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
    }
  }
}
</script>

<style>
.logo {
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.logo img {
  width: 200px
}
app-bar-logo {
  
}
app-bar-lyrebird {

}
.main-footer {
  height: 28px;
  line-height: 28px;
  padding: 0;
}
.top-bar-item {
  width: 140px !important;
  height: 26px;
  margin-bottom: 9px;
  margin-top: 9px;
}
.top-bar-item-select {
  width: 140px;
  min-height: 26px !important;
  height: 26px !important;
  font-size: 14px;
  font-weight: 400;
  line-height: 14px;
  font-family: PingFangSC-Regular;
}
.top-bar-item .v-input__slot {
  min-height: 26px !important;
  height: 26px !important;
}
.top-bar-item .v-select__selections{
  min-height: 26px !important;
  height: 26px !important;
  padding: 6px 0 !important;
}
.top-bar-item .v-select__selection {
  line-height: 14px;
  margin: 0 4px 17px 0 !important;
}
.top-bar-item .v-input__append-inner {
  margin-top: 7px !important;
}
.top-bar-item .v-input__icon--append {
  width: 14px;
  height: 14px;
  min-width: 14px;
  margin-bottom: 15px;
  margin-left: 0;
}
.top-bar-item .v-input__prepend-outer {
  width: 24px;
  height: 24px;
  line-height: 24px;
  min-width: 24px;
  margin-bottom: 10px;
  margin-left: 0;
  margin-right: 8px;
  margin-top: 2px !important;
}
.top-bar-item .v-icon {
  width: 14px;
  height: 14px;
  line-height: 14px;
  min-width: 14px;
}
</style>
