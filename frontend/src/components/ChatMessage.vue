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
        <img class="logo loading" src="../assets/loading.gif" v-if="total == index + 1 & loading" />
        <p v-html="msg.a"></p>
    </li>
</template>

<style scoped>
.message {
    background-color: rgba(255, 255, 255, 0.9);
    border-radius: 50px;
    box-shadow: 0px 15px 5px 0px rgba(0, 0, 0, 0.5);
    position: relative;
    margin-bottom: 30px;
}

.message.left {
    padding: 15px 20px 15px 70px;
}

.message.right {
    align-self: flex-end;
    padding: 15px 70px 15px 20px;
}

.logo {
    border-radius: 50%;
    box-shadow: 0px 10px 10px 0px rgba(0, 0, 0, 0.7);
    object-fit: cover;
    position: absolute;
    left: 10px;
    top: -10px;
    width: 50px;
    height: 50px;
}

.message.right .logo {
    left: auto;
    right: 10px;
}

.message p {
    margin: 0;
}
</style>
