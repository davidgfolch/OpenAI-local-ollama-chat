
const checkUnclosedCodeBlockMd = (data: string) => {
    const codePos = data.lastIndexOf("```");
    if (codePos != -1) {
        const tail = data.substring(codePos - 3)
        if (tail.match(/```[a-zA-Z]+/gm))
            return data + '\n```'
    }
    return data
}

const msToTime = (ms: number) => {
    const total_seconds = parseInt(Math.floor(ms / 1000).toFixed(0));
    const total_minutes = parseInt(Math.floor(total_seconds / 60).toFixed(0));
    const total_hours = parseInt(Math.floor(total_minutes / 60).toFixed(0));
    const seconds = parseInt((total_seconds % 60).toFixed(0));
    const minutes = parseInt((total_minutes % 60).toFixed(0));
    const hours = parseInt((total_hours % 24).toFixed(0));//   if (seconds < 60) return seconds + " Sec";
    if (hours > 0)
        return hours + ":" + minutes + ":" + seconds;
    else if (minutes > 0)
        return minutes + ":" + seconds;
    return (seconds < 10 ? '0' : '') + seconds + " seg."
}

const insertAtCursor = (el: HTMLTextAreaElement | HTMLInputElement, text: string, offset = 0) => {
    //console.log("insertAtCursor => element=" + el + " text=" + text + " offset=" + offset);
    if (document.selection) { //IE support
        console.log("insertAtCursor IE document.selection=" + document.selection);
        el.focus();
        const sel = document.selection.createRange();
        console.log("insertAtCursor IE sel.text=" + sel.text);
        sel.text = text;
    } else if (el.selectionStart || el.selectionStart == 0) { //MOZILLA and others
        console.log("insertAtCursor MOZILLA and others el.selectionStart=" + el.selectionStart + ' el.selectionEnd=' + el.selectionEnd);
        const startPos = el.selectionStart + offset;
        const endPos = el.selectionEnd;
        text = el.value.substring(0, startPos) + text + el.value.substring(endPos, el.value.length)
        console.log("insertAtCursor el.value=" + el.value);
        el.value = text;
    } else {
        el.value += text;
    }
    return el.value;
}

export { checkUnclosedCodeBlockMd, msToTime, insertAtCursor }