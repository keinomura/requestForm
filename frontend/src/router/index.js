import { createRouter, createWebHistory } from 'vue-router';
import RequestList from '../components/RequestList.vue';
// import RequestForm from '../components/RequestForm.vue';
import AddRequest from '../components/AddRequest.vue';


const routes = [
  { path: '/', name: 'RequestList', component: RequestList },
  { path: '/add-request', name: 'AddRequest', component: AddRequest },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
