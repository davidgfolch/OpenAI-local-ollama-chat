<script setup>
import { ref, defineProps, defineEmits } from 'vue'

const emit = defineEmits(['cancelStream', 'deleteMessage']);
// Props
const props = defineProps({
    msg: { type: Object },
    total: { type: Number },
    index: { type: Number },
    loading: { type: Boolean },
})
const collapsed = ref(false);
// Methods
const cancelStream = () => emit('cancelStream');
const deleteMessage = () => emit('deleteMessage');
const lastAndLoading = () => props.total == props.index + 1 & props.loading;
const collapseMessage = () => collapsed.value = !collapsed.value;
const msgClass = () => collapsed.value?'collapsed':'';
const rotateIfCollapsed = () => collapsed.value?'':'flipVertical';
</script>

<template>
    <li class="message right">
        <img class="logo" src="../assets/chatgpt/user.webp" alt="User question" title="User question">
        <span v-html="props.msg.q"></span>
    </li>
    <li class="message left">
        <img class="logo" src="../assets/chatgpt/ai.webp" :style="lastAndLoading() ? 'filter: brightness(50%)' : ''"
            alt="AI response" title="AI response">
        <img class="logo loading" src="../assets/loading.gif" v-if="lastAndLoading()" alt="Waiting for AI response"
            title="Waiting for AI response" />
        <div style="position: absolute; left: -0.5em; top: 0.5em">
            <img class="logo small-icon" src="../assets/chatgpt/trash.webp" v-if="lastAndLoading()"
                @click="cancelStream" alt="Cancel question" title="Cancel question">
            <img class="logo small-icon" src="../assets/chatgpt/trash.webp" v-if="!lastAndLoading()"
                @click="deleteMessage" alt="Delete message" title="Delete message">
            <img class="logo small-icon" src="../assets/chatgpt/collapse.webp" @click="collapseMessage()"
                :class="rotateIfCollapsed()" alt="Collapse message" title="Collapse message">
        </div>
        <span v-html="props.msg.a" :class="msgClass()"></span>
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

.collapsed {
    overflow-y: scroll;
    max-height: 4em;
    display: inline-block;
}

.flipVertical {
    transform: rotate(180deg);
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

.small-icon {
    top: 2.5em;
    width: 1.8em;
    height: 1.8em;
    position: relative;
    float: left;
    margin-left: 0.1em;
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
