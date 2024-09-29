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
const viewSettings = ref(false);
const history = ref("My history");
const ability = ref("Eres un asistente especializado en ingenieria de software.");
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
  error.value.show("<p>" + err + "</p><p>" + err.response.data.error + "</p>");
};
const resetApiCall = () => {
  loading.value = false;
  scrollDown(scrollDiv.value);
};
const sendMessage = async () => {
  loading.value = true;
  error.value.reset()
  setAnswer('<p>Waiting for response...</p>');
  let body = { user: user.value, question: question.value, history: history.value, ability: ability.value };
  ApiClient.post('/api/v1/chat', body).then(res => {
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
const settings = async () => {
  viewSettings.value = !viewSettings.value;
  scrollDown(scrollDiv.value);
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
  </div>
  <div class="buttons">
    <div class="buttons" :hidden="viewSettings">
      <input type="text" class="text_input" v-model="ability"
        placeholder="Artificial intelligence system ability (describe any hability in natural language)"
        title="Artificial intelligence system ability (describe any hability in natural language)" />
    </div>
    <div class="buttons" :hidden="viewSettings">
      <input type="text" class="text_input" v-model="history" placeholder="Current chat history"
        title="Current chat history" />
    </div>
    <img class="optionIcon" src="../assets/trash.webp" alt="Delete chat" title="Delete chat" @click="deleteChat"
      :disabled="loading">
    <img class="optionIcon" src="../assets/settings.webp" alt="Delete chat" title="Settings" @click="settings"
      :disabled="loading">
  </div>
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
