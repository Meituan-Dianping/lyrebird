<template>
  <div>
    <v-system-bar app dense flat height="38px" color="primary">
      <div class="logo">
        <img src="@/assets/lyrebird.shadow.png" />
        <span>Lyrebird</span>
      </div>
      <v-spacer/>
      <!-- todo:change theme -->
      <v-btn icon @click="changeTheme" v-show="false">
        <v-icon size="18px" color="white" v-if= this.$vuetify.theme.dark>mdi-brightness-4</v-icon>
        <v-icon size="18px" color="#9e9e9e" v-else >mdi-brightness-5</v-icon>
      </v-btn>
      <notice-center></notice-center>
    </v-system-bar>

    <v-navigation-drawer app permanent expand-on-hover width="200px">
      <v-list nav dense> 
        <v-list-item-group v-model="activeMenuItemIndex" active-class="v-list-active">
          <v-list-item v-for="(menuItem, index) in menu" :key="index" link @click.native="menuItemOnClick(menuItem, index)">
            <v-list-item-icon>
              <v-icon>{{menuItem.icon}}</v-icon> 
            </v-list-item-icon>
            <v-list-item-title style="font-weight:700;">{{menuItemTitle(menuItem)}}
            </v-list-item-title>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <div class="main-container">
        <router-view></router-view>
      </div>
    </v-main>

    <v-footer app color="primary" class="main-footer">
      <span class="main-footer-status-placeholder"></span>
      <span v-show="activatedGroupName" class="main-footer-status-no-pointer">
        <b>Activated mock group: {{activatedGroupName}}</b>
        <Icon type="md-close-circle" style="cursor:pointer;" @click="resetActivatedData" />
      </span>
      <StatusBar />
      <v-spacer></v-spacer>
      <StatusInfo />
    </v-footer>
  </div>
</template>

<script>
import NoticeCenter from '@/views/notice/NoticeCenter.vue'
import StatusBar from '@/views/statusbar/StatusBar.vue'
import StatusInfo from '@/views/statusbar/StatusInfo.vue'

export default {
  name: 'MainLayout',
  components: {
    NoticeCenter,
    StatusBar,
    StatusInfo
  },
  mounted () {
    this.$store.dispatch('loadMenu')
    this.$store.dispatch('loadManifest')
    this._keydownListener = (e) => {
      this.$bus.$emit('keydown', e)
    }
    document.addEventListener('keydown', this._keydownListener)
  },
  beforeDestroy () {
    document.removeEventListener('keydown', this._keydownListener)
    this.$io.removeListener('activatedGroupUpdate', this.loadActivatedGroup)
    this.$io.removeListener('msgSuccess', this.successMessage) 
  },
  created () {
    this.$bus.$on('msg.success', this.successMessage)
    this.$bus.$on('msg.loading', this.loadingMessage)
    this.$bus.$on('msg.info', this.infoMessage)
    this.$bus.$on('msg.error', this.errorMessage)
    this.$bus.$on('msg.destroy', this.destroyMessage)
    this.$io.on('activatedGroupUpdate', this.loadActivatedGroup)
    this.$io.on('msgSuccess', this.successMessage)
  },
  watch: {
    activeMenuItemIndex (newValue, oldValue) {
      if (newValue !== oldValue) {
        this.refreshPage(newValue)
      }
    }
  },
  computed: {
    menu () {
      return this.$store.state.menu
    },
    manifest () {
      return this.$store.state.manifest
    },
    activeMenuItemIndex: {
      get () {
        return this.$store.state.activeMenuItemIndex
      },
      set (val) {
        // 1,val is undefined when index is not changed
        // 2,In order to solve the problem of losing the selected state, first assign ActiveMenuItemIndex to -1, 
        //  and the real value will be set by method menuItemOnClick
        this.$store.commit('setActiveMenuItemIndex', -1)


        
      }
    },
    activatedGroupName () {
      const activatedGroups = this.$store.state.inspector.activatedGroup
      if (activatedGroups === null) {
        return null
      }
      if (Object.keys(activatedGroups) === 0) {
        return null
      }
      let text = ''
      for (const groupId in activatedGroups) {
        text = text + activatedGroups[groupId].name + ' '
      }
      return text
    }
  },
  methods: {
    changeTheme () {
      this.$vuetify.theme.dark = !this.$vuetify.theme.dark
    },
    menuItemTitle (menuItem) {
        return menuItem.title
    },
    menuItemOnClick (menuItem, index) {
      // 更新activeMenuItem
      // 点击后，activeMenuItem更新，触发watch，操作页面更新
      this.$store.commit('setActiveMenuItemIndex', index)
      this.$store.dispatch('updateActiveMenuItem', menuItem)
    },
    refreshPage (menuItemIndex) {
      // 更新 router
      let menuItem = this.$store.state.menu[menuItemIndex]
      if (!menuItem) {
        return
      }
      if (menuItem.type === 'router') {
        if (menuItem.name === 'plugin-view' || menuItem.name === 'plugin-container') {
          this.$store.commit('plugin/setSrc', menuItem.params.src)
        }
        this.$router.push({ name: menuItem.name, params: menuItem.params })
      } else {
        window.open(menuItem.path, '_self')
      }
    },
    resetActivatedData () {
      this.$store.dispatch('deactivateGroup')
    },
    loadActivatedGroup () {
      this.$store.dispatch('loadActivatedGroup')
    },
    successMessage (msg) {
      this.$Message.success({
        content: msg,
        duration: 3,
        closable: true
      })
    },
    loadingMessage (msg) {
      this.$Message.loading({
        content: msg,
        duration: 3,
        closable: true
      })
    },
    infoMessage (msg) {
      this.$Message.info({
        content: msg,
        duration: 0,
        closable: true
      })
    },
    errorMessage (msg) {
      this.$Message.error({
        content: msg,
        duration: 0,
        closable: true
      })
    },
    destroyMessage () {
      this.$Message.destroy()
    },
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
.logo span {
  color: white;
  font-size: 18px;
  font-weight: bolder;
  font-style: italic;
  margin-left: 15px;
  text-shadow: #000 3px 4px 5px
}
.logo img {
  margin-left: 8px;
  padding-top: 4px;
  width: 28px
}
.main-header {
  height: 38px;
  line-height: 38px;
  padding: 0;
  margin: 0;
  background-color: #0fccbf;
}
.main-footer {
  height: 28px;
  line-height: 28px;
  padding: 0;
}
.main-container {
  height: calc(100vh - 66px);
  background: #fff;
}
.v-list-active {
  background-color: #eeeef9;
  color: #5F5CCA !important;
}
.v-list-item:not(.v-list-item--active):not(.v-list-item--disabled) {
  color: #9B9CB7 !important;
}
</style>

<style>
.ivu-split-pane {
  overflow: hidden;
}
.main-footer-status-no-pointer {
  padding: 0px 4px;
  margin: 0px 3px;
  height: 100%;
  color: #f8f8f9;
  font-size: 12px;
  display: inline-block;
}
.main-footer-status {
  padding: 0px 4px;
  margin: 0px 3px;
  height: 100%;
  color: #515a6e;
  font-size: 12px;
  cursor: pointer;
  display: inline-block;
}
.main-footer-status:hover {
  background-color: #4BD2c0;
}
.main-footer-status-button {
  color: #f8f8f9;
}
.main-footer-status-placeholder {
  margin-left: 5px;
}
</style>
