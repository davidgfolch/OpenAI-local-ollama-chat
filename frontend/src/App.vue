<script setup>
import { onMounted } from 'vue';
import ChatHeader from './components/ChatHeader.vue';
import ChatContainer from './components/ChatContainer.vue';


const setBackgroundImage = () => {
	document.body.style = "background: url('/background" + (Math.floor(Math.random() * 4) + 1) + ".png'); 	background-repeat: no-repeat; background-size: cover; background-attachment: fixed;";
	setTimeout(setBackgroundImage, 60000);
}

onMounted(setBackgroundImage);
</script>

<template>
	<ChatHeader msg="OpenAi local Ollama chat" />
	<ChatContainer />
</template>

<style>
@import url('https://fonts.googleapis.com/css?family=Lato');

* {
	box-sizing: border-box;
}

body {
	background-color: black;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-direction: column;
	min-height: 100vh;
	font-family: 'Lato', sans-serif;
}
</style>
