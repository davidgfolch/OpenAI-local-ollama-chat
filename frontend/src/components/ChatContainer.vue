<script setup>
import { ref, onMounted, defineProps, defineExpose, nextTick } from 'vue';
import ChatMessage from './ChatMessage.vue';
import ChatError from './ChatError.vue';
import ChatOptions from './ChatOptions.vue';
import ApiClient from './ApiClient.js';
import hljs from 'highlight.js';
import scrollDown from './utils.js';
import { showdown } from "vue-showdown";

// Props
const props = defineProps({
  initialMessages: {
    type: Array,
    default: () => []
  }
});
const mdConverter = new showdown.Converter();

// Reactive data
const user = ref('me');
const loading = ref(false);
const question = ref('Dame un ejemplo de código TensorFlow en python, así como la instalación con conda de las librerias necesarias.');
const messages = ref([]);
// Refs
const scrollDiv = ref(null);
const chatError = ref('');
const chatOptions = ref();
// Methods
const highLightCode = () => nextTick().then(() => hljs.highlightAll());
const errorReset = () => chatError.value.reset();
var scrollDownEnabled = true;
const scrollDownChat = () => { if (scrollDownEnabled) scrollDown(scrollDiv.value); }
const loadHistory = () => {
  let q = null, a = null;
  loading.value = true;
  ApiClient.get(`/api/v1/chat/${user.value}`).then(res => {
    if (res.data.response.length === 0) {
      messages.value = props.initialMessages;
    }
    res.data.response.forEach((msg) => {
      if (msg.q) q = msg.q;
      if (msg.a) a = mdConverter.makeHtml(checkUnclosedCodeBlockMd(msg.a));
      if (a != null && q != null) {
        messages.value.push({ q, a });
        scrollDownChat()
        highLightCode();
        q = null, a = null;
      }
    });
  }).catch(handleError).finally(resetApiCall);
};
const setAnswer = (answer, resetQuestion) => {
  messages.value.push({ q: '<p>' + question.value + '</p>', a: mdConverter.makeHtml(answer) });
  if (resetQuestion) question.value = '';
  scrollDownChat()
  highLightCode();
};
const handleError = (error) => {
  chatError.value.show(error);
};
const resetApiCall = () => {
  scrollDownEnabled = true;
  loading.value = false;
  scrollDownChat()
};
const checkUnclosedCodeBlockMd = (data) => {
  const codePos = data.lastIndexOf("```");
  if (codePos != -1) {
    console.log("found last markdown in pos=" + codePos);
    const tail = data.substr(codePos - 3)
    if (tail.match(/```[a-zA-Z]+/gm)) {
      return data + '\n```'
    }
  }
  return data
}
const useStream = true
const invoke = async () => {
  if (question.value.trim() == '') return
  loading.value = true;
  errorReset();
  scrollDownEnabled = true;
  setAnswer('<p>Waiting for response...</p>');
  scrollDownEnabled = false;
  const options = chatOptions.value;
  const body = { model: options.model, user: user.value, question: question.value, history: options.history, ability: options.ability };
  const url = useStream ? '/api/v1/chat-stream' : '/api/v1/chat'
  ApiClient.post(url, body, {
    onDownloadProgress: (progressEvent) => {
      let eventObj = undefined;
      if (progressEvent.event?.currentTarget) {
        eventObj = progressEvent.event?.currentTarget;
      } else if (progressEvent.event?.srcElement) {
        eventObj = progressEvent.event?.srcElement;
      } else if (progressEvent.event?.target) {
        eventObj = progressEvent.event?.target;
      }
      if (!eventObj) return;
      var dataChunk = eventObj.response;
      dataChunk = checkUnclosedCodeBlockMd(dataChunk)
      messages.value.pop();
      setAnswer(dataChunk);
    }
  }).then(() => {
    question.value = ''
  }).catch(e => {
    messages.value.pop()
    handleError(e);
  }).finally(resetApiCall);
  // https://stackoverflow.com/questions/72781074/piping-the-response-into-a-variable-using-streams-axios-node-js
  // axios.get responseType: 'stream' https://stackoverflow.com/questions/71534322/http-stream-using-axios-node-js
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
    <textarea rows="3" v-model="question"
              class="text_input" placeholder="Message..."
              :disabled="loading" autofocus>
    </textarea>

    <!-- <input type="text" class="text_input" placeholder="Message..." v-model="question" @keyup.enter="invoke"
      :disabled="loading" autofocus /> -->
    <img class="icon" src="../assets/veloai/send.png" alt="Ask AI" title="Ask AI" @click="invoke" :disabled="loading">
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
