<template>
    <div>
      <h1>要望一覧</h1>
      <ul>
        <li v-for="request in requests" :key="request.id">
          {{ request.requester_name }} - {{ request.content }}
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import { ref, onMounted } from 'vue';
  
  export default {
    setup() {
      const requests = ref([]);
  
      onMounted(() => {
        axios.get('http://127.0.0.1:5000/requests')
          .then(response => {
            requests.value = response.data;
          })
          .catch(error => {
            console.error('APIからのデータ取得に失敗しました:', error);
          });
      });
  
      return {
        requests
      };
    }
  };
  </script>
  