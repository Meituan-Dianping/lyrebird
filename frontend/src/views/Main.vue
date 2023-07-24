<template>
  <div class="shading">
    <AppBar />

    <!-- The navigation drawer display from y-axis 0px by default -->
    <!-- keep the navigation drawer from being blocked by the app bar by margin-top, which is mt-11 -->

    <!-- mini-variant-width cannot set the initial width of the unfloding animation  -->
    <!-- <v-navigation-drawer mini-variant-width=50> -->

    <v-navigation-drawer
      app
      absolute
      permanent
      width="200"
      floating
      expand-on-hover
      height="calc(100vh - 44px - 28px)"
      class="background mt-11 side-navgation"
    >
      <v-list nav dense>
        <v-list-item-group v-model="activeMenuItemIndex" active-class="v-item--active">
          <v-list-item
            v-for="(menuItem, index) in menu"
            :key="index"
            link
            @click.native="menuItemOnClick(menuItem, index)"
          >
            <v-list-item-icon>
              <v-icon>{{ menuItem.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-title style="font-weight:700;">{{ menuItemTitle(menuItem) }}</v-list-item-title>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>

    <v-main class="ma-3">
      <v-toolbar-title class="mb-2 page-title">{{ activeMenuItemName }}</v-toolbar-title>
      <keep-alive exclude="datamanager">
        <!-- Cache children component exclude datamanager . Because v-treeview component has memory leak if it in the keep-alive tag -->
        <router-view class="router-container background" />
      </keep-alive>
    </v-main>

    <v-footer app color="primary" class="main-footer">
      <StatusBar />
      <v-spacer />
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
    StatusInfo,
  },
  mounted() {
    this.$store.dispatch('loadMenu')
    this.$store.dispatch('loadManifest')
    this.$store.dispatch('loadConfig')
    this.$store.dispatch('loadAllStatusList')
    this._keydownListener = e => {
      this.$bus.$emit('keydown', e)
    }
    document.addEventListener('keydown', this._keydownListener)
  },
  beforeDestroy() {
    document.removeEventListener('keydown', this._keydownListener)
    this.$io.removeListener('statusBarUpdate', this.loadAllStatusList)
    this.$io.removeListener('datamanagerUpdate', this.loadDataMap)
    this.$io.removeListener('msgSuccess', this.successMessage)
    this.$io.removeListener('msgInfo', this.infoMessage)
    this.$io.removeListener('msgError', this.errorMessage)
    this.$bus.$off('msg.success', this.successMessage)
    this.$bus.$off('msg.loading', this.loadingMessage)
    this.$bus.$off('msg.info', this.infoMessage)
    this.$bus.$off('msg.error', this.errorMessage)
    this.$bus.$off('msg.destroy', this.destroyMessage)
  },
  created() {
    this.$bus.$on('msg.success', this.successMessage)
    this.$bus.$on('msg.loading', this.loadingMessage)
    this.$bus.$on('msg.info', this.infoMessage)
    this.$bus.$on('msg.error', this.errorMessage)
    this.$bus.$on('msg.destroy', this.destroyMessage)
    this.$io.on('statusBarUpdate', this.loadAllStatusList)
    this.$io.on('datamanagerUpdate', this.loadDataMap)
    this.$io.on('msgSuccess', this.successMessage)
    this.$io.on('msgInfo', this.infoMessage)
    this.$io.on('msgError', this.errorMessage)
  },
  watch: {
    activeMenuItemIndex(newValue, oldValue) {
      if (newValue !== oldValue) {
        this.refreshPage(newValue)
      }
    },
  },
  computed: {
    menu() {
      return this.$store.state.menu
    },
    manifest() {
      return this.$store.state.manifest
    },
    activeMenuItemIndex: {
      get() {
        return this.$store.state.activeMenuItemIndex
      },
      set(val) {
        // 1,val is undefined when index is not changed
        // 2,In order to solve the problem of losing the selected state, first assign ActiveMenuItemIndex to -1,
        //  and the real value will be set by method menuItemOnClick
        this.$store.commit('setActiveMenuItemIndex', -1)
      },
    },
    activeMenuItemName() {
      if (this.$store.state.activeMenuItem == null) {
        return ''
      } else {
        return this.$store.state.activeMenuItem.title
      }
    },
  },
  methods: {
    menuItemTitle(menuItem) {
      return menuItem.title
    },
    menuItemOnClick(menuItem, index) {
      // 更新activeMenuItem
      // 点击后，activeMenuItem更新，触发watch，操作页面更新
      this.$store.commit('setActiveMenuItemIndex', index)
      this.$store.dispatch('updateActiveMenuItem', menuItem)
    },
    refreshPage(menuItemIndex) {
      // 更新 router
      let menuItem = this.$store.state.menu[menuItemIndex]
      if (!menuItem) {
        return
      }
      if (menuItem.type === 'router') {
        if (menuItem.name === 'plugin-view' || menuItem.name === 'plugin-container') {
          let lastPluginSrc = this.$store.state.plugin.src
          if (lastPluginSrc === null || lastPluginSrc.split('?')[0] !== menuItem.params.src) {
            this.$store.commit('plugin/setSrc', menuItem.params.src)
          }
        }
        this.$router.push({ name: menuItem.name, params: menuItem.params })
      } else {
        window.open(menuItem.path, '_self')
      }
    },
    loadAllStatusList() {
      this.$store.dispatch('loadAllStatusList')
    },
    loadDataMap() {
      this.$store.dispatch('loadDataMap')
    },
    successMessage(msg) {
      this.$Message.success({
        content: msg,
        duration: 3,
        closable: true,
      })
    },
    loadingMessage(msg) {
      this.$Message.loading({
        content: msg,
        duration: 3,
        closable: true,
      })
    },
    infoMessage(msg) {
      this.$Message.info({
        content: msg,
        duration: 0,
        closable: true,
      })
    },
    errorMessage(msg) {
      this.$Message.error({
        content: msg,
        duration: 0,
        closable: true,
      })
    },
    destroyMessage() {
      this.$Message.destroy()
    },
  },
}
</script>

<style>
.page-title {
  font-weight: 600;
  font-family: PingFangSC-Semibold;
  font-size: 16px;
  color: #000520;
  line-height: 20px;
}
.router-container {
  height: calc(100vh - 44px - 40px - 28px - 12px);
  /* total:100vh
    header: 44px
    title: 40px
    extension-container
    margin-bottom: 12px
    footer: 28px
    */
}
.ivu-split-trigger-con {
  z-index: 2;
}
.v-item--active {
  background-color: #5a57c4 10%;
  color: #5a57c4 !important;
}
.v-item--active:not(.v-list-item--active):not(.v-list-item--disabled) {
  color: #9b9cb7 !important;
}
.main-footer {
  height: 28px;
  line-height: 28px;
  padding: 0;
}
.v-list-active {
  background-color: #eeeef9;
  color: #5f5cca !important;
}
.v-list-item:not(.v-list-item--active):not(.v-list-item--disabled) {
  color: #9b9cb7 !important;
}
</style>

<style>
.side-navgation {
  z-index: 4;
}
.ivu-split-pane {
  overflow: hidden;
}
.ivu-split-trigger {
  border-bottom: 1px solid #dcdee2;
  border-top: 1px solid #dcdee2;
}
.save-btn {
  color: #fff;
  font-size: 0.6rem;
  text-align: center;
  line-height: 3rem;
  width: 3rem;
  height: 3rem;
  position: fixed;
  right: 60px;
  bottom: 60px;
  border-radius: 50%;
  z-index: 2;
}
.save-btn-detail {
  width: 36px !important;
  height: 36px !important;
}
.save-btn-icon {
  font-size: 20px !important;
  width: 20px !important;
  height: 20px !important;
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
  background-color: #6a67d4;
}
.main-footer-status:active {
  background-color: #7b79d0;
}
.main-footer-status-button {
  color: #f8f8f9;
}
.main-footer-status-placeholder {
  margin-left: 5px;
}
.v-text-field--outlined fieldset {
  border: 1px #d9dade solid;
}
.v-btn {
  text-transform: none;
  letter-spacing: 0;
}
</style>
