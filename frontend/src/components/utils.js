import { nextTick } from 'vue';

const scrollDown = (el) => {
    if (el) {
        nextTick().then(() => el.scrollIntoView({ behavior: 'smooth' }));
    } else {
        console.error("Can't scroll down scrollDiv not found!");
    }
}

const checkUnclosedCodeBlockMd = (data) => {
    const codePos = data.lastIndexOf("```");
    if (codePos != -1) {
        const tail = data.substr(codePos - 3)
        if (tail.match(/```[a-zA-Z]+/gm)) {
            return data + '\n```'
        }
    }
    return data
}

export { scrollDown, checkUnclosedCodeBlockMd };