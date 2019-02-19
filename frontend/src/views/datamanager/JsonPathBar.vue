<template>
    <div class="json-path-bar">
        <label v-if="jsonPath">{{jsonPath}}</label>
    </div>
</template>

<script>
export default {
    computed: {
        jsonPath() {
            return this.$store.state.dataManager.jsonPath
        }
    }
};
</script>

<style scoped>
.json-path-bar {
float: right;
display: flex;
align-items: center;
font-size: 11px;
margin-left: 10px
}
</style>
