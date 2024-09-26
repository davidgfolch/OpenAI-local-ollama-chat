<script>
import ChatHeader from './components/ChatHeader.vue';
import ChatContainer from './components/ChatContainer.vue';

export default {
  components: {
    ChatHeader,
    ChatContainer
  },
  data() {
    return {
      messages: [{
        'q': 'Hola AI!',
        'a': 'Hola! en que puedo ayudarte?'
      }]
    }
  }
}
</script>

<template>
  <ChatHeader msg="Ask local Ollama" />
  <ChatContainer :initial-messages="messages" />
</template>

<style>
@import url('https://fonts.googleapis.com/css?family=Lato');
* {
	box-sizing: border-box;
}

body {
	background: url('assets/background1.png');
	background-size: cover;
	background-position: center	center;
	
	display: flex;
	align-items: center;
	justify-content: center;
	flex-direction: column;

	min-height: 100vh;
	font-family: 'Lato', sans-serif;
	margin: 0 0 50px;
}

/* Add some basic styling to the chat app */
body {
  color: gray;
  background-color: black;
}
</style>