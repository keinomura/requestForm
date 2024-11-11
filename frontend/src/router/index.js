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

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
