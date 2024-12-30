<template>
    <div class="container">
      <h2>進捗情報の更新</h2>
      <form @submit.prevent="submitProgress">
        <div class="form-group">
          <label for="request_id">要望ID</label>
          <input type="number" id="request_id" v-model="request_id" required />
        </div>
        <div class="form-group">
          <label for="status">対応状況</label>
          <select id="status" v-model="status">
            <option value="未対応">未対応</option>
            <option value="対応中">対応中</option>
            <option value="完了">完了</option>
          </select>
        </div>
        <div class="form-group">
          <label for="response_comment">対応コメント</label>
          <input type="text" id="response_comment" v-model="response_comment" />
        </div>
        <div class="form-group">
          <label for="handler_name">担当者名</label>
          <input type="text" id="handler_name" v-model="handler_name" />
        </div>
        <button type="submit">更新</button>
        <button type="button" @click="$router.push('/')" style="background-color: blueviolet;">キャンセル</button>
      </form>
    </div>
    

  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        request_id: '',
        status: '未対応',
        response_comment: '',
        handler_name: ''
      };
    },
    methods: {
      async submitProgress() {
        try {
          const apiUrl = import.meta.env.VITE_API_URL;
          await axios.put(`${apiUrl}/responses/${this.request_id}`, {
            status: this.status,
            response_comment: this.response_comment,
            handler_name: this.handler_name
          });

          alert('進捗情報が更新されました');
          this.request_id = '';
          this.status = '未対応';
          this.response_comment = '';
          this.handler_name = '';
        } catch (error) {
          console.error('エラーが発生しました:', error);
          alert('進捗情報の更新に失敗しました');
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .container {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f9f9f9;
  }
  
  .form-group {
    margin-bottom: 15px;
  }
  
  label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
  }
  
  input[type="text"], input[type="number"], select {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
  
  button {
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
}

button:hover {
  background-color: #0056b3;
}

  </style>
  