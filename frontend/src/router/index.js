import { createRouter, createWebHistory } from 'vue-router';
import RequestList from '../components/RequestList.vue';
import RequestForm from '../components/RequestForm.vue';

const routes = [
  { path: '/', name: 'RequestList', component: RequestList },
  { path: '/add-request', name: 'RequestForm', component: RequestForm },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
