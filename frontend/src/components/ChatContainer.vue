<script setup>
import { ref, onMounted, defineProps, defineExpose, nextTick } from 'vue';
import ChatMessage from './ChatMessage.vue';
import ChatError from './ChatError.vue';
import ChatOptions from './ChatOptions.vue';
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
const chatError = ref('');
const chatOptions = ref();
const prompt = ref(null);
// Methods
const highLightCode = () => nextTick().then(() => hljs.highlightAll());
const errorReset = () => chatError.value.reset();
const scrollDownChat = () => scrollDown(scrollDiv.value);
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
        scrollDownChat()
        highLightCode();
        q = null, a = null;
      }
    });
    // nextTick(() => prompt.value.focus());
  }).catch(handleError).finally(resetApiCall);
};
const setAnswer = (answer, resetQuestion) => {
  messages.value.push({ q: '<p>' + question.value + '</p>', a: answer });
  if (resetQuestion) question.value = '';
  scrollDownChat()
  highLightCode();
};
const handleError = (error) => {
  messages.value.pop()
  chatError.value.show(error);
};
const resetApiCall = () => {
  loading.value = false;
  scrollDownChat()
};
const sendMessage = async () => {
  loading.value = true;
  errorReset();
  setAnswer('<p>Waiting for response...</p>');
  const body = { user: user.value, question: question.value, history: chatOptions.value.history, ability: chatOptions.value.ability };
  ApiClient.post('/api/v1/chat', body).then(res => {
    messages.value.pop();
    setAnswer(res.data.response);
    question.value = '';
  }).catch(handleError).finally(resetApiCall);
};
const messagesReset = () => {
  messages.value = [];
  nextTick(() => loadHistory());
};
onMounted(() => { // Lifecycle hook
  loadHistory();
});
defineExpose({ errorReset, setAnswer, messagesReset, handleError, scrollDownChat });
</script>

<template>
  <div class="chat-container">
    <ul class="chat">
      <ChatMessage v-for="(msg, index) in messages" :key="index" :msg="msg" :total="messages.length" :index="index"
        :loading="loading" />
      <ChatError ref="chatError" />
    </ul>
    <input type="text" class="text_input" placeholder="Message..." v-model="question" @keyup.enter="sendMessage"
      :disabled="loading" ref="prompt" autofocus />
    <img class="icon" src="../assets/veloai/send.png" alt="AI response" title="AI response" @click="sendMessage"
      :disabled="loading">
  </div>
  <ChatOptions :view-settings="false" :user="user" @error-reset="errorReset()" @set-answer="a => setAnswer(a)"
    @messages-reset="messagesReset()" @scroll-down-chat="scrollDownChat" ref="chatOptions" />
  <div ref="scrollDiv" class="scrollDiv"></div>
</template>

<style>
@import url("https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/dark.min.css");

.buttons {
  background-color: rgba(0, 0, 0, 0.4);
  border-radius: 1.5em;
  box-shadow: 0px 0px 10px 5px rgba(0, 0, 0, 0.7);
  padding: 1em;
  position: relative;
  clear: both;
  min-width: 5em;
  margin-top: 2em;
  margin-left: 2em;
  margin-right: 2em;
}

.chat-container {
  background-color: rgba(0, 0, 0, 0.4);
  border-radius: 1.5em;
  box-shadow: 0px 0px 10px 5px rgba(0, 0, 0, 0.7);
  overflow: hidden;
  padding: 1em;
  position: relative;
  min-width: 10em;
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
  margin-bottom: 2em;
}

.text_input {
  background-color: black;
  color: white;
  font-size: 16px;
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 1em 0em 1em 1em;
  margin: 3em 2em 0em 0em;
  width: 100%;
}

.scrollDiv {
  padding: 0;
  margin: 0;
}

.icon {
  border-radius: 50%;
  box-shadow: 0px 0px 10px 5px rgba(26, 21, 21, 0.7);
  object-fit: cover;
  position: relative;
  float: right;
  width: 3em;
  height: 3em;
}

.optionIcon {
  border-radius: 50%;
  box-shadow: 0px 0px 10px 5px rgba(26, 21, 21, 0.7);
  object-fit: cover;
  position: relative;
  float: right;
  width: 3em;
  height: 3em;
}
</style>
