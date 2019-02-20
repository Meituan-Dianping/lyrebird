<template>
    <div>
        <label v-if="jsonPath">Json Path: {{jsonPath}}</label>
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

<style>
</style>
