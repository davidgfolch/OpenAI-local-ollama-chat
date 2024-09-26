<script setup>
import { ref, onMounted, defineProps, nextTick } from 'vue';
import ChatMessage from './ChatMessage.vue';
import ChatError from './ChatError.vue';
import ApiClient from './ApiClient.js';
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
const scrollDown = () => {
  const el = scrollDiv.value;
  if (el) {
    nextTick().then(() => el.scrollIntoView({ behavior: 'smooth' }));
  } else {
    console.error("Can't scroll down scrollDiv not found!");
  }
};

const loadHistory = () => {
  let q = null, a = null;
  ApiClient.get(`/api/v1/chat/${user.value}`)
    .then(res => {
      if (res.data.response.length === 0) {
        messages.value = props.initialMessages;
      }
      res.data.response.forEach((msg) => {
        if (msg.q) q = msg.q;
        if (msg.a) a = msg.a;
        if (a != null && q != null) {
          messages.value.push({ q, a });
          scrollDown();
          q = null, a = null;
        }
      });
    })
    .catch(handleError)
    .finally(resetApiCall);
};

const setAnswer = (answer, resetQuestion) => {
  messages.value.push({ q: question.value, a: answer });
  if (resetQuestion) question.value = '';
  scrollDown();
};

const handleError = (err) => {
  messages.value.pop()
  error.value.show(err)
};

const resetApiCall = () => {
  loading.value = false;
  scrollDown();
};

const sendMessage = async () => {
  loading.value = true;
  error.value.reset()
  setAnswer('Waiting for response...');
  ApiClient.post('/api/v1/chat', { user: user.value, question: question.value })
    .then(res => {
      messages.value.pop();
      setAnswer(res.data.response);
      question.value = '';
    })
    .catch(handleError)
    .finally(resetApiCall);
};

onMounted(() => { // Lifecycle hook
  loadHistory();
});

</script>

<template>
  <div class="chat-container">
    <ul class="chat">
      <ChatMessage v-for="(msg, index) in messages" :key="index" :msg="msg" :total="messages.length" :index="index" :loading="loading"/>
      <ChatError ref="error"/>
      <li><p></p></li>
    </ul>
    <input type="text" class="text_input" placeholder="Message..." v-model="question" @keyup.enter="sendMessage" :disabled="loading"/>
  </div>
  <div ref="scrollDiv"></div>
</template>

<style>
@import url("../assets/chatContainer.css");
</style>
