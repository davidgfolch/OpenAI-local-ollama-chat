<style>
@import url("../assets/chatContainer.css");</style>
<script>

import axios from 'axios';
import { nextTick } from 'vue';
// https://github.com/miaolz123/vue-markdown?tab=readme-ov-file#es6-vue-cli-users
// import VueMarkdown from 'vue-markdown'; dont work properly, too complicated

// Create an axios instance
const api = axios.create({
  baseURL: 'http://127.0.0.1:5000',
});

export default {
  data() {
    return {
      user: "me",
      loading: false,
      error: '',
      question: '¿Cual es es framework de AI mas popular para Python?',
      messages: []
    }
  },
  methods: {
    scrollDown() {
      // const el = this.$refs.chatContainer;
      const el = this.$refs.inputField;
      if (el) { // Use el.scrollIntoView() to instantly scroll to the element
        nextTick().then(() => el.scrollIntoView({behavior: 'smooth'}));
      }
      else console.error("Can't scroll down @chatContainer not found!");
    },
    loadHistory() {
      var a,q=null;
      api.get('/api/v1/chat/'+this.user)
        .then(res => {
          if (res.data.response.length == 0)
            this.fillMockData()
          res.data.response.map(msg => {
            if (msg.q) q=msg.q;
            if (msg.a) a=msg.a;
            if (a!=null & q!=null) {
              this.messages.push({"q": q, "a": a});
              this.scrollDown();
              a,q=null;
            }
          })
        })
      .catch(error => this.handleError(error))
      .finally(() => this.resetApiCall());
    },
    fillMockData() {
      this.messages.push({
        "q": "Hola AI!",
        "a": "Hola! en que puedo ayudarte?"
      }); 
      // for (let i = 0; i < 5; i++) {
      //   this.messages.push({
      //     "q": "¿Cual es es framework de AI mas popular para Python?",
      //     "a": "Una función de pérdida es un índice matemático que mide la distancia entre las predicciones realizadas por un modelo y los datos reales. Como tal tiene valor cuando las variable sea un dato real por lo general las medidas se refiere con base cero el cual indica si hay error o no ya que con ella podemos indicir el nivel de efectividad del modelo, por ende cuanto más alto, significa un grado muy alto en acuracidad y viceversa"
      //   }); 
      // }
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
      api.post('/api/v1/chat', { user: this.user, question: this.question }).then(res => {
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
    this.scrollDown();
  }
}
</script>

<template>
    <div class="chat-container">
    <ul class="chat" v-for="(msg, index) in messages" :key="index">
      <li class="message left">
        <img class="logo" src="../assets/user2.webp" alt="User question" title="User question">
        <p v-html="msg.q"></p>
      </li>
      <li class="message right">
        <img class="logo" src="../assets/ai2.webp" alt="AI response" title="AI response">
        <img class="logo loading" src="../assets/loading.gif" v-if="messages.length-1==index & loading"/>
        <p v-html="msg.a"></p>
      </li>
      <li class="api-error" v-if="error!='' & messages.length-1==index">{{ error }}</li>
    </ul>
    <input type="text" class="text_input" placeholder="Message..." v-model="question" @keyup.enter="sendMessage" v-bind:disabled="loading"/>
  </div>
  <div ref="inputField"></div>
</template>