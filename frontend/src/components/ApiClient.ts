import axios, { AxiosResponse } from 'axios';

const server = 'http://127.0.0.1:5000';
// Create an Axios instance
const apiClient = axios.create({
  baseURL: server,
})
const AXIOS_CONTROLLER_ABORT_MSG = 'CanceledError: canceled'

apiClient.interceptors.response.use((response) => response, (error) => {
  if (error == 'AxiosError: Network Error') {
    console.log("AxiosError.message=" + error.message)
    if (error.message !== 'Network Error') throw new Error(error.message);
    else throw new Error("Could not connect to backend server: " + server);
  }
  throw error;
});

const processDownloadProgress = (progressEvent, errorCallbackFnc, successCallback) => {
  let eventObj = undefined;
  if (progressEvent.event?.currentTarget) {
    eventObj = progressEvent.event?.currentTarget;
  } else if (progressEvent.event?.srcElement) {
    eventObj = progressEvent.event?.srcElement;
  } else if (progressEvent.event?.target) {
    eventObj = progressEvent.event?.target;
  }
  // with load data {"loaded":3198,"bytes":8,"rate":33,"event":{"isTrusted":true},"lengthComputable":false,"download":true}
  // without load data is a backend error '{"loaded":0,"bytes":0,"event":{"isTrusted":true},"lengthComputable":false,"download":true}') {
  if (progressEvent.loaded == 0) {
    errorCallbackFnc();
    return;
  }
  if (!eventObj) return;
  var dataChunk = eventObj.response;
  if (dataChunk != '')
    successCallback(dataChunk)
}


export const openDownloadedFile = (res: AxiosResponse, name: string) => {
    // document.open(URL.createObjectURL(new Blob([res.data], { type: 'application/zip' })))
    const type = res.headers['content-type']
    const blob = new Blob([res.data], { type: type, encoding: 'UTF-8' })
    const link = document.createElement('a')
    link.href = window.URL.createObjectURL(blob)
    link.download = name //res.headers['Content-Disposition'].split('filename=')[1]
    link.click()
    link.remove()
    // return window.open(res.data, '_blank');
}

export { apiClient, processDownloadProgress, AXIOS_CONTROLLER_ABORT_MSG };
