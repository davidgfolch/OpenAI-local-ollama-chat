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
    border: 0px;
    border-radius: 1.5em;
    box-shadow: 0px 0px 10px 5px rgba(255, 255, 255, 0.7);
    background-color: #f66;
    color: #fff
}
</style>