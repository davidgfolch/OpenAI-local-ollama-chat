<script setup>
import { ref, defineExpose } from 'vue'

const error = ref('');

function show(err) {
    error.value = err
    console.error(err)
}

function reset() {
    error.value = ''
}

defineExpose({ show, reset })
</script>

<template>
    <li class="api-error" v-if="error !== ''" v-html="error"></li>
</template>

<style scoped>
.api-error {
    max-width: 80%;
    margin: 40px auto;
    padding: 20px;
    border: 1px solid #ddd;
    border: 1px solid #ddd;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
    background-color: #f66;
    color: #fff
}
</style>