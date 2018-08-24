<template>
    <div>
        <row class="button-bar">
            <button-bar></button-bar>
        </row>
        <row>
        <i-col span="12">
            <data-list class="container-left"></data-list>
        </i-col>
        <i-col span="12">
            <data-detail class="container-right"></data-detail> 
        </i-col>
        </row>
    </div>
</template>

<script>
module.exports = {
    components: {
        "button-bar": httpVueLoader('static/vue/datamanager/button-bar.vue'),
        "data-list": httpVueLoader('static/vue/datamanager/data-list.vue'),
        "data-detail": httpVueLoader('static/vue/datamanager/data-detail.vue')
    }
}
</script>

<style>
  .button-bar {
    margin-bottom: 5px
  }

  .container-left {
    margin-right: 5px
  }

  .container-right {
    margin-left: 5px
  }
</style>
