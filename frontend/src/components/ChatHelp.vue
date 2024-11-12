<script setup>
</script>

<template>
    <li class="help">
        <h2>Welcome to Ollama local chat!</h2>
        <p>This help is scrollable, please scroll down to see it all.</p>
        <h3>Start asking anything to your preferred LLM.</h3>
        <p>Just write the message in the box below and send it clicking the send button (or Ctrl+Enter).<br />
            A stream request/response will start & text will be displayed as soon as chunks are transmitted from backend
            &lt;- Ollama .</p>
        <h3>Uploading files</h3>
        <p>Upload files and/or folders clicking <img class="optionIcon" src="../assets/chatgpt/file.webp" /> and <img
                class="optionIcon" src="../assets/chatgpt/folder.webp" />.</p>
        <p>Mention any file with @ prefix in the question to be added as embed file to LLM.<br />
            Uploaded files assistant will show you the matching files as you write, use &DownArrowUpArrow; to move in
            list and &#8626;
            to select.</p>
        <h3>Manage messages</h3>
        <p>Chat history: You can select existing in the input list or create new one just typing it.</p>
        <p>You can stop and delete an ongoing question request/response stream by clicking the trash <img
                class="optionIcon" src="../assets/chatgpt/trash.webp" /> icon in the message.<br />
            You can delete a message (question/answer) by clicking the trash <img class="optionIcon"
                src="../assets/chatgpt/trash.webp" /> icon in the message.<br />
            You can delete ALL messages history by clicking the trash <img class="optionIcon"
                src="../assets/chatgpt/trash.webp" /> icon below the textbox.
        </p>
        <h3>Advanced prompts</h3>
        <h4>Multiple requests parametrization</h4>
        <p>The frontend allows to trigger several questions (sequentially) to the LLM.  You only need to provide a {variable} in the question & set the variable values in a single line.</p>
            <pre style="border: 1px solid black">
            <code>
    Genera un ejemplo de código completo con {variable} en python.

    variable=Django, Flask, NumPy, Pandas, Matplotlib, Scikit-learn, Requests
            </code>
        </pre>
        <h3>Options</h3>
        <p>Show/hide the options by clicking the gear <img class="optionIcon" src="../assets/chatgpt/settings.webp" />
            icon in the message.</p>
        <ul>
            <li>Ability: you can change the ability of the backend LLM</li>
            <li>Model: you can choose the backend model from the ones available in Ollama.</li>
            <li>Temperature: choose model temperature (0 -> more predictable, 0.9 -> more creativity).</li>
            <li>History: you can change the history of the backend LLM</li>
            <li>Export: export history from langchain json format to a base README.md markdown file.  Moves each response code blocks into a organized folder & files. Returning a ZIP file.</li>
        </ul>
    </li>
</template>

<style scoped>
.help {
    background-color: rgba(255, 255, 255, 0.4);
    margin: 1em auto;
    padding: 0.5em 1em 0.5em 1em;
    border: 0px;
    border-radius: 1.5em;
    box-shadow: 0em 0em 0.5em 0.5em rgba(255, 255, 255, 0.5);
    max-height: 20em;
    overflow-y: scroll;
    /* -webkit-mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 1), rgba(0, 0, 0, 0));
    -webkit-mask-size: 100% 100%;
    -webkit-mask-repeat: no-repeat;
    -webkit-mask-position: top, bottom; */
}

.optionIcon {
    width: 2em;
    height: em;
}
</style>