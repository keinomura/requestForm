<template>
    <div>
      <h2>新しい要望を追加</h2>
      <form @submit.prevent="submitRequest">
        <div>
          <label for="name">名前:</label>
          <input type="text" id="name" v-model="requesterName" required />
        </div>
        <div>
          <label for="content">内容:</label>
          <textarea id="content" v-model="content" required></textarea>
        </div>
        <button type="submit">送信</button>
      </form>
      <p v-if="message">{{ message }}</p>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import { ref } from 'vue';
  
  export default {
    setup() {
      const requesterName = ref('');
      const content = ref('');
      const message = ref('');
  
      const submitRequest = () => {
        axios.post('http://127.0.0.1:5000/requests', {
          requester_name: requesterName.value,
          content: content.value,
        })
        .then(response => {
          message.value = response.data.message;
          requesterName.value = '';
          content.value = '';
        })
        .catch(error => {
          console.error('データ送信エラー:', error);
          message.value = 'エラーが発生しました';
        });
      };
  
      return {
        requesterName,
        content,
        message,
        submitRequest,
      };
    },
  };
  </script>
  