<style>
@import url("../assets/chatContainer.css");
</style>

<script>
import { nextTick } from 'vue';
// https://github.com/miaolz123/vue-markdown?tab=readme-ov-file#es6-vue-cli-users
// import VueMarkdown from 'vue-markdown'; don't work properly, too complicated
import ChatMessage from './ChatMessage.vue'

export default {
  components: {
    ChatMessage
  },
  data() {
    return {
      user: "me",
      loading: false,
      error: '',
      question: '¿Cuál es es framework de AI mas popular para Python?',
      messages: []
    }
  },
  props: ['initialMessages'],
  methods: {
    scrollDown() {
      const el = this.$refs.scrollDiv;
      if (el) { // Use el.scrollIntoView() to instantly scroll to the element
        nextTick().then(() => el.scrollIntoView({behavior: 'smooth'}));
      } else console.error("Can't scroll down @chatContainer not found!");
    },
    loadHistory() {
      var q,a=null;
      this.$apiClient.get('/api/v1/chat/'+this.user)
        .then(res => {
          if (res.data.response.length == 0)
             this.messages=this.initialMessages;
          res.data.response.map(msg => {
            if (msg.q) q=msg.q;
            if (msg.a) a=msg.a;
            if (a!=null & q!=null) {
              this.messages.push({"q": q, "a": a});
              this.scrollDown();
              q=null;
              a=null;
            }
          })
        })
      .catch(error => this.handleError(error))
      .finally(() => this.resetApiCall());
    },
    setAnswer(answer, resetQuestion=false) {
      this.messages.push({"q": this.question, "a": answer});
      if (resetQuestion) this.question='';
      this.scrollDown();
    },
    handleError(error) {
      this.messages.pop();
      this.error=error;
      console.error(error);
    },
    resetApiCall() {
      this.loading = false;
      this.scrollDown();
    },
    async sendMessage() {
      this.loading=true;
      this.error='';
      this.setAnswer("Waiting for response...")
      this.$apiClient.post('/api/v1/chat', { user: this.user, question: this.question }).then(res => {
          this.messages.pop();
          this.setAnswer(res.data.response)
          this.question='';
        })
        .catch(error => this.handleError(error))
        .finally(() => this.resetApiCall());
    },
  },
  mounted() {
    this.loadHistory();
  }
}
</script>

<template>
  <div class="chat-container">
    <ul class="chat">
      <ChatMessage v-for="(msg, index) in messages" :key="index" :msg="msg" :total="messages.length" :index="index" v-bind:loading="loading"/>
      <li class="api-error" v-if="error!=''" v-html="error"></li>
      <li><p></p></li>
    </ul>
    <input type="text" class="text_input" placeholder="Message..." v-model="question" @keyup.enter="sendMessage" v-bind:disabled="loading"/>
  </div>
  <div ref="scrollDiv"></div>
</template>