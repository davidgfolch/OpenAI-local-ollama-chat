<script setup>
import { defineProps } from 'vue'
// import iconSets from './iconSets.ts' 
// Props
const props = defineProps({
    msg: { type: Object },
    total: { type: Number },
    index: { type: Number },
    loading: { type: Boolean }
})
</script>

<template>
    <li class="message right">
        <img class="logo" src="../assets/veloai/user.png" alt="User question" title="User question">
        <!-- <img class="logo" :src="iconSets['user']" alt="User question" title="User question"> -->
        <span v-html="props.msg.q"></span>
    </li>
    <li class="message left">
        <img class="logo" src="../assets/veloai/ai.png" alt="AI response" title="AI response">
        <img class="logo loading" src="../assets/loading.gif" v-if="total == index + 1 & loading"
            alt="Waiting for AI response" title="Waiting for AI response" />
        <span v-html="props.msg.a"></span>
    </li>
</template>

<style scoped>
.message {
    color: lightgray;
    border-radius: 1.5em;
    box-shadow: 0px 0px 10px 5px rgba(0, 0, 0, 0.5);
    position: relative;
    margin-bottom: 30px;
}

.message span p {
    padding-top: 0px;
}

.message.left {
    padding: 0em 1em 0em 4em;
    background-color: rgba(0, 150, 0, 0.5);
}

.message.right {
    align-self: flex-end;
    padding: 0em 4em 0em 1.5em;
    background-color: rgba(0, 0, 150, 0.5);
}

li span {
    padding: 0px;
}

.logo {
    border-radius: 50%;
    box-shadow: 0px 0px 10px 5px rgba(26, 21, 21, 0.7);
    object-fit: cover;
    position: absolute;
    left: 0.5em;
    top: -0.5em;
    width: 3em;
    height: 3em;
}

.loading {
    scale: 75%;
    left: 0.5em;
    top: -0.5em;
}

.message.right .logo {
    left: auto;
    right: 10px;
}

.message p {
    margin: 0;
}

pre {
    overflow: auto;
    max-width: 90em;
    display: inline-block !important;
}
</style>
