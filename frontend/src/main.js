// main.js
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'


const vuetify = createVuetify({
  components,
  directives,
})

createApp(App).use(vuetify).use(router).mount('#app')

// // Vuetifyのインスタンス作成
// const vuetify = createVuetify();
// const app = createApp(App);

// // 必要なプラグインの設定
// app.use(router);
// app.use(vuetify);

// // アプリをマウント
// app.mount('#app');
