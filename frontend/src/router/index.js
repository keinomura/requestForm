import { createRouter, createWebHistory } from 'vue-router';
import RequestList from '../components/RequestList.vue';
import AddRequest from '../components/AddRequest.vue';
import UpdateProgress from '../components/UpdateProgress.vue';


const routes = [
  { path: '/', name: 'RequestList', component: RequestList },
  { path: '/add-request', name: 'AddRequest', component: AddRequest },
  {
    path: '/update-progress',
    name: 'UpdateProgress',
    component: UpdateProgress
  },
];

// 以下のように、createWebHistory() の引数にベースURLを設定することで、
// ルーティングのベースURLを設定できます。

const router = createRouter({
  history: createWebHistory('/requestForm/'), // ベースURLを設定
  routes,
});

export default router;
