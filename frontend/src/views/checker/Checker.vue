<template>
  <div class="demo-split">
    <Split v-model="split1">
      <div slot="left">
        <checker-list></checker-list>
      </div>
      <div slot="right">
        <checker-detail></checker-detail>
      </div>
    </Split>
  </div>
</template>

<script>
import CheckerList from "@/views/checker/CheckerList.vue";
import CheckerDetail from "@/views/checker/CheckerDetail.vue";

export default {
  name: "Checker",
  data() {
    return {
      split1: 0.2,
      split4: 0.8
    };
  },
  components: {
    CheckerList,
    CheckerDetail
  },
  created() {
    this.$store.dispatch('loadCheckers')
  },
  computed: {
    
  },
  mounted: function() {

  },
  computed: {

  },
  methods: {

  }
};
</script>

<style scoped>
.demo-split{
  height: calc(100vh - 66px);
  border: 1px solid #dcdee2;
}
</style>