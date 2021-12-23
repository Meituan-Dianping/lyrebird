<template>
  <div>
    <AppBar/>

    <!-- The navigation drawer display from y-axis 0px by default -->
    <!-- keep the navigation drawer from being blocked by the app bar by margin-top, which is mt-11 -->

    <!-- mini-variant-width cannot set the initial width of the unfloding animation  -->
    <!-- <v-navigation-drawer mini-variant-width=50> -->

    <v-navigation-drawer
      absolute
      permanent
      expand-on-hover 
      width=200
      height="calc(100% - 44px)"
      class="background mt-11"
    >
      <v-list nav dense> 
        <v-list-item-group v-model="activeMenuItemIndex" active-class="v-item--active">
          <v-list-item v-for="(menuItem, index) in menu" :key="index" link @click.native="menuItemOnClick(menuItem, index)">
            <v-list-item-icon>
              <v-icon>{{menuItem.icon}}</v-icon> 
            </v-list-item-icon>
            <v-list-item-title style="font-weight:700;">{{menuItemTitle(menuItem)}}</v-list-item-title>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>

    <v-main class="background">
      <router-view style="margin-left:66px; background-color:white"/>
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
import svgIcon from 'vue-svg-icon/Icon.vue'
import AppBar from '@/views/appbar/AppBar.vue'
import StatusBar from '@/views/statusbar/StatusBar.vue'
import StatusInfo from '@/views/statusbar/StatusInfo.vue'

export default {
  name: 'MainLayout',
  components: {
    svgIcon,
    AppBar,
    StatusBar,
    StatusInfo
  },
  mounted () {
    this.$store.dispatch('loadMenu')
    this.$store.dispatch('loadManifest')
    this.$store.dispatch('loadConfig')
    this.$store.dispatch('loadAllStatusList')
    this._keydownListener = (e) => {
      this.$bus.$emit('keydown', e)
    }
    document.addEventListener('keydown', this._keydownListener)
  },
  beforeDestroy () {
    document.removeEventListener('keydown', this._keydownListener)
    this.$io.removeListener('activatedGroupUpdate', this.loadActivatedGroup)
    this.$io.removeListener('statusBarUpdate', this.loadAllStatusList)
    this.$io.removeListener('msgSuccess', this.successMessage) 
  },
  created () {
    this.$bus.$on('msg.success', this.successMessage)
    this.$bus.$on('msg.loading', this.loadingMessage)
    this.$bus.$on('msg.info', this.infoMessage)
    this.$bus.$on('msg.error', this.errorMessage)
    this.$bus.$on('msg.destroy', this.destroyMessage)
    this.$io.on('activatedGroupUpdate', this.loadActivatedGroup)
    this.$io.on('statusBarUpdate', this.loadAllStatusList)
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
    loadAllStatusList () {
      this.$store.dispatch('loadAllStatusList')
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

<style>
.v-item--active {
  background-color: #5A57C4 10%;
  color: #5A57C4 !important;
}
.v-item--active:not(.v-list-item--active):not(.v-list-item--disabled) {
  color: #9B9CB7 !important;
} 
.main-footer {
  height: 28px;
  line-height: 28px;
  padding: 0;
}
.main-container {
  height: calc(100vh - 44px - 28px);
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
  background-color: #6A67D4;
}
.main-footer-status:active {
  background-color: #7B79D0;
}
.main-footer-status-button {
  color: #f8f8f9;
}
.main-footer-status-placeholder {
  margin-left: 5px;
}
</style>
