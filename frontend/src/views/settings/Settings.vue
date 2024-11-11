<template>
    <v-container class="settings-container">
        <!-- 你的页面内容 --> 
        <Split v-model="split" min=265px>
        <div slot="left">
            <setting-list></setting-list>
        </div>
        <div slot="right">
            <setting-detail></setting-detail>
        </div>
        </Split>
    </v-container>
</template>

<script>
import SettingList from '@/views/settings/SettingList.vue'
import SettingDetail from '@/views/settings/SettingDetail.vue'
export default {
    data () {
        return {
            split: 0.3,
            settingInfoList: [
                
            ],
            settingInfoDetail: {

            },
        }
    },
    components: {SettingList, SettingDetail},
    computed: {},
    watch: {}
}
</script>

<style scoped>
.settings-container {
  max-width: 1200px !important;
  margin-left: auto;
  margin-right: auto;
}
</style>
