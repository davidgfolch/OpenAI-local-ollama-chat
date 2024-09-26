<script>
export default {
  props: ["msg", "total", "index", "loading"]
}
</script>

<template>
    <li class="message left">
        <img class="logo" src="../assets/user2.webp" alt="User question" title="User question">
        <p v-html="msg.q"></p>
    </li>
    <li class="message right">
        <img class="logo" src="../assets/ai2.webp" alt="AI response" title="AI response">
        <img class="logo loading" src="../assets/loading.gif" v-if="total==index+1 & loading"/>
        <p v-html="msg.a"></p>
    </li>
</template>
