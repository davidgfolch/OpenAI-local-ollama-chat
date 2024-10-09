import axios from 'axios';

const server = 'http://127.0.0.1:5000';
// Create an Axios instance
const apiClient = axios.create({
  baseURL: server,
})

apiClient.interceptors.response.use((response) => response, (error) => {
  if (error == 'AxiosError: Network Error') {
    console.log("error.message=" + error.message)
    if (error.message !== 'Network Error') throw new Error(error.message);
    else throw new Error("Could not connect to backend server: " + server);
  }
  throw error;
});

const processDownloadProgress = (progressEvent, errorCallbackFnc, successCallback) => {
  // console.log("progressEvent=" + JSON.stringify(progressEvent));
  let eventObj = undefined;
  if (progressEvent.event?.currentTarget) {
    eventObj = progressEvent.event?.currentTarget;
  } else if (progressEvent.event?.srcElement) {
    eventObj = progressEvent.event?.srcElement;
  } else if (progressEvent.event?.target) {
    eventObj = progressEvent.event?.target;
  }
  // console.log("eventObj="+JSON.stringify(eventObj));
  // with load data {"loaded":3198,"bytes":8,"rate":33,"event":{"isTrusted":true},"lengthComputable":false,"download":true}
  // without load data is a backend error '{"loaded":0,"bytes":0,"event":{"isTrusted":true},"lengthComputable":false,"download":true}') {
  if (progressEvent.loaded == 0) {
    errorCallbackFnc();
    return;
  }
  if (!eventObj) return;
  var dataChunk = eventObj.response;
  successCallback(dataChunk)
}

export { apiClient, processDownloadProgress };
