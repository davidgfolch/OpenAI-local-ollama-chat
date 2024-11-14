import { AxiosResponse } from "axios";
import hljs from 'highlight.js';
import { nextTick } from 'vue';

// hljs.configure(hljs.)
export const highLightCode = (elementId: string = null) =>
    nextTick().then(() => {
        if (elementId) {
            highlightElementById('question-' + elementId)
            highlightElementById('answer-' + elementId)
        } else hljs.highlightAll()
    })

const highlightElementById = (elementId: string) =>
    document.querySelectorAll('#' + elementId + ' > span > pre > code:not([data-highlighted=yes])')
        .forEach(e => hljs.highlightElement(e))

export const loadHistoryMapper = (res: AxiosResponse, callback: Function) => {
    let q = null, a = null, id = null, metadata = null;
    res.data.response.forEach((msg: any) => {
        if (msg.q) q = msg.q;
        if (msg.a) {
            a = msg.a;
            metadata = msg.metadata;
            id = msg.id;
        }
        if (a != null && q != null) {
            callback(q, a, id, JSON.parse(metadata))
            q = null, a = null
        }
    });
}

export const answerMetadataMapper = (answer: string, streamTimeStart: number) => {
    const arr = answer.split("#|S|E|P#")
    if (arr.length == 1)
        return { text: answer, currentChunkId: '', metadataJson: '' }
    const currentChunkId = arr[0]
    const modelName = arr[1]
    const langchainChat = arr[2]
    const text = arr[3]
    const metadataStr = arr[4]
    const now = Date.now()
    let metadata = arr.length > 4 ? metadataStr : '{"total_duration": ' + (now - streamTimeStart) + '}'
    let metadataJson = JSON.parse(metadata)
    metadataJson['total_duration'] = now - streamTimeStart
    metadataJson['model'] = modelName
    metadataJson['langchainChat'] = langchainChat
    return { text: text, currentChunkId: currentChunkId, metadataJson: metadataJson }
}

export const createBodyParams = (ops, question: string, user: string) => {
    return { model: ops.model, temperature: ops.temperature, user: user, question: question, history: ops.history, ability: ops.ability };
}

export const checkHistoryName = (name: string) => {
    if (!name) 
        return 'Could not load history messages, select current history in options fields.'
    if (name.match('[/:]'))
        return 'Invalid history name, should be like: '+name.replaceAll(/\/|:/g,'-')
}