<script setup>
import { ref, onMounted, defineProps, defineExpose, nextTick } from 'vue';
import ChatMessage from './ChatMessage.vue';
import ChatError from './ChatError.vue';
import ChatOptions from './ChatOptions.vue';
import { apiClient, processDownloadProgress } from './ApiClient.js';
import hljs from 'highlight.js';
import { checkUnclosedCodeBlockMd, scrollDown } from './utils.js';
import { showdown } from "vue-showdown";

// Props
const props = defineProps({
  initialMessages: {  // TODO: INITIAL MESSAGES
    type: Array,
    default: () => []
  }
});
// Vars
const mdConverter = new showdown.Converter();
let cancelledStream = false;
// Reactive data
const user = ref('localUser');
const loading = ref(false);
const question = ref('');
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
  apiClient.get(`/api/v1/chat/${user.value}`).then(res => {
    if (res.data.response.length === 0) {  // TODO: INITIAL MESSAGES
      messages.value = props.initialMessages;
      return;
    }
    res.data.response.forEach((msg) => {
      if (msg.q) q = msg.q;
      if (msg.a) a = msg.a;
      if (a != null && q != null) {
        messagePush(q, a);
        scrollDownChat()
        highLightCode();
        q = null, a = null;
      }
    });
  }).catch(handleError).finally(resetApiCall);
};
const mdToHtml = (msg) => mdConverter.makeHtml(checkUnclosedCodeBlockMd(msg));
const messagePush = (q, a) => messages.value.push({ q: mdToHtml(q), a: mdToHtml(a) });
const setAnswer = (answer, resetQuestion) => {
  messagePush(question.value, answer);
  if (resetQuestion) question.value = '';
  scrollDownChat()
  highLightCode();
};
const handleError = (error) => chatError.value.show(error);
const resetApiCall = () => {
  scrollDownEnabled = true;
  loading.value = false;
  scrollDownChat()
};
const errorCallbackFnc = () => {
  if (cancelledStream) {
    cancelledStream = false;
    return;
  }
  messages.value.pop();
  handleError("Stream chat response was empty.  Did you start ollama service?  Checkout backend logs.");
}
const stream = async (q) => {
  question.value = q
  if (question.value.trim() == '') return
  loading.value = true;
  cancelledStream = false;
  errorReset();
  setAnswer('<p>Waiting for response...</p>');
  scrollDownEnabled = false;
  const options = chatOptions.value;
  const body = { model: options.model, user: user.value, question: question.value, history: options.history, ability: options.ability };
  apiClient.post('/api/v1/chat-stream', body, {
    onDownloadProgress: (progressEvent) =>
      processDownloadProgress(progressEvent,
        () => errorCallbackFnc(),
        (dataChunk) => {
          dataChunk = checkUnclosedCodeBlockMd(dataChunk)
          messages.value.pop();
          setAnswer(dataChunk);
        })
  }).then(() => question.value = '')
    .catch(e => {
      messages.value.pop()
      handleError(e);
    }).finally(() => {
      if (messages.value.length > 0 && messages.value[messages.value.length - 1]['a'] == '<p>Waiting for response...</p>')
        errorCallbackFnc(); //TODO: chrome don't pass through ApiClient.js -> processDownloadProgress() -> progressEvent.loaded == 0
      resetApiCall();
    });
};
const messagesReset = () => {
  messages.value = [];
  nextTick(() => loadHistory());
};
const deleteMessage = (index) => {
  errorReset();
  apiClient.get(`/api/v1/chat/delete/${user.value}/${index}`)
    .then(() => messages.value.splice(index, 1))
    .catch(e => {
      handleError(e);
      scrollDownChat();
    });
}
const cancelStreamSignal = () => {
  errorReset();
  apiClient.get(`/api/v1/chat/cancel/${user.value}`)
    .then(() => cancelledStream = true)
    .catch(e => {
      handleError(e);
      scrollDownChat();
    });
}

onMounted(() => loadHistory());
defineExpose({ errorReset, setAnswer, messagesReset, handleError, scrollDownChat, stream, cancelStreamSignal, deleteMessage });
</script>


<template>
  <div class="chat-container">
    <ul class="chat">
      <ChatMessage v-for="(msg, index) in messages" :key="index" :msg="msg" :total="messages.length" :index="index"
        :loading="loading" @cancel-stream-signal="cancelStreamSignal()" @delete-message="deleteMessage(index)" />
      <ChatError ref="chatError" />
    </ul>
  </div>
  <ChatOptions :question="question" :loading="loading" :user="user" :view-settings="false" @error-reset="errorReset()"
    @handle-error="e => handleError(e)" @set-answer="a => setAnswer(a)" @messages-reset="messagesReset()"
    @scroll-down-chat="scrollDownChat" @stream="q => stream(q)" ref="chatOptions" />
  <div ref="scrollDiv" class="scrollDiv"></div>
</template>


<style>
@import url("https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/dark.min.css");

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

.scrollDiv {
  padding: 0;
  margin: 0;
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
