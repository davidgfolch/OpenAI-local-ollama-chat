<script setup>
import { ref, onMounted, defineProps, nextTick } from 'vue';
import ChatMessage from './ChatMessage.vue';
import ChatError from './ChatError.vue';
import ApiClient from './ApiClient.js';
import hljs from 'highlight.js';
import scrollDown from './utils.js';
// Props
const props = defineProps({
  initialMessages: {
    type: Array,
    default: () => []
  }
});
// Reactive data
const user = ref('me');
const loading = ref(false);
const question = ref('¿Cuál es el framework de AI más popular para Python?');
const messages = ref([]);
// Refs
const scrollDiv = ref(null);
const error = ref();
// Methods
const highLightCode = () => nextTick().then(() => hljs.highlightAll());
const loadHistory = () => {
  let q = null, a = null;
  loading.value = true;
  ApiClient.get(`/api/v1/chat/${user.value}`).then(res => {
    if (res.data.response.length === 0) {
      messages.value = props.initialMessages;
    }
    res.data.response.forEach((msg) => {
      if (msg.q) q = msg.q;
      if (msg.a) a = msg.a;
      if (a != null && q != null) {
        messages.value.push({ q, a });
        scrollDown(scrollDiv.value);
        highLightCode();
        q = null, a = null;
      }
    });
  }).catch(handleError).finally(resetApiCall);
};
const setAnswer = (answer, resetQuestion) => {
  messages.value.push({ q: '<p>' + question.value + '</p>', a: answer });
  if (resetQuestion) question.value = '';
  scrollDown(scrollDiv.value);
  highLightCode();
};
const handleError = (err) => {
  messages.value.pop()
  error.value.show(err)
};
const resetApiCall = () => {
  loading.value = false;
  scrollDown(scrollDiv.value);
};
const sendMessage = async () => {
  loading.value = true;
  error.value.reset()
  setAnswer('<p>Waiting for response...</p>');
  ApiClient.post('/api/v1/chat', { user: user.value, question: question.value }).then(res => {
    messages.value.pop();
    setAnswer(res.data.response);
    question.value = '';
  }).catch(handleError).finally(resetApiCall);
};
const deleteChat = async () => {
  loading.value = true;
  error.value.reset()
  setAnswer('Waiting for response...');
  ApiClient.get(`/api/v1/chat/delete/${user.value}`).then(res => {
    console.log("delete response=" + res);
    messages.value.length = 0;
  }).catch(handleError).finally(resetApiCall);
};
onMounted(() => { // Lifecycle hook
  loadHistory();
});
</script>

<template>
  <div class="chat-container">
    <ul class="chat">
      <ChatMessage v-for="(msg, index) in messages" :key="index" :msg="msg" :total="messages.length" :index="index"
        :loading="loading" />
      <ChatError ref="error" />
    </ul>
    <input type="text" class="text_input" placeholder="Message..." v-model="question" @keyup.enter="sendMessage"
      :disabled="loading" />
    <img class="icon" src="../assets/trash.webp" alt="Delete chat" title="Delete chat" @click="deleteChat"
      :disabled="loading">
  </div>
  <div ref="scrollDiv" class="scrollDiv"></div>
</template>

<style>
@import url("https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/dark.min.css");

.chat-container {
  background-color: rgba(0, 0, 0, 0.4);
  border-radius: 25px;
  box-shadow: 0px 0px 10px 5px rgba(0, 0, 0, 0.7);
  overflow: hidden;
  padding: 15px;
  position: relative;
  min-width: 100em;
  /* min-width: 50%; */
  margin-left: 2em;
  margin-right: 2em;
}

.chat {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.text_input {
  font-size: 16px;
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 10px 15px;
  width: 100%;
}

.scrollDiv {
  padding: 0;
  margin: 0;
}

.icon {
  border-radius: 50%;
  box-shadow: 0px 10px 10px 0px rgba(26, 21, 21, 0.7);
  object-fit: cover;
  position: relative;
  float: right;
  width: 3em;
  height: 3em;
}

</style>
