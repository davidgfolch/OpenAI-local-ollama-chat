<script setup>
import { onMounted } from 'vue';
import ChatHeader from './components/ChatHeader.vue';
import ChatContainer from './components/ChatContainer.vue';

const bgIndex = ref(0);
const bgImages = ["1", "1_2", "2", "2_3", "3", "3_4", "4", "4_1"]
const setBackgroundImage = () => {
	document.body.style = "background: url('/background" + bgImages[bgIndex.value] + ".png'); background-repeat: no-repeat; background-size: cover; background-attachment: fixed;";
	bgIndex.value = bgIndex.value + 1;
	if (bgIndex.value >= bgImages.length)
		bgIndex.value = 0;
	setTimeout(setBackgroundImage, 3000);
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
