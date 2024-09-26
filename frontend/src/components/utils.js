import { nextTick } from 'vue';

const scrollDown = (el) => {
    if (el) {
        nextTick().then(() => el.scrollIntoView({ behavior: 'smooth' }));
    } else {
        console.error("Can't scroll down scrollDiv not found!");
    }
}

export default scrollDown;