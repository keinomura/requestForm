import { createRouter, createWebHistory } from 'vue-router';
import RequestList from '../components/RequestList.vue';

const routes = [
  { path: '/', name: 'RequestList', component: RequestList }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
