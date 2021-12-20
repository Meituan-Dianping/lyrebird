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
      <!-- <span v-for="status in statusTopRightList">
        {{statusBarDetail}}
      </span> -->

      <!-- Add Bandwidth here -->
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
    },
    statusBarDetail () {
      return this.$store.state.statusbar.statusBarDetail
    }
  },
  methods: {
    changeTheme () {
      this.$vuetify.theme.dark = !this.$vuetify.theme.dark
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
.logo img {
  width: 200px
}
.main-footer {
  height: 28px;
  line-height: 28px;
  padding: 0;
}
</style>
