import { AxiosResponse } from "axios";

const loadHistoryMapper = (res: AxiosResponse, callback: Function) => {
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

const answerMetadataMapper = (answer: string, streamTimeStart: number) => {
    const arr = answer.split("#|S|E|P#")
    if (arr.length == 1)
        return { text: answer, currentChunkId:'', metadataJson: '' }
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

export { loadHistoryMapper, answerMetadataMapper }