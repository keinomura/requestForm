<template>
    <v-container>
      <v-card>
        <v-card-title>新規要望の追加</v-card-title>
        <v-card-text>
          <v-form ref="form">
            <v-text-field label="内容" v-model="content" required></v-text-field>
            <v-text-field label="部署" v-model="requester_department" required></v-text-field>
            <v-text-field label="氏名" v-model="requester_name" required></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" @click="submitRequest">追加</v-btn>
          <v-btn text @click="$router.push('/')" style="background-color: blueviolet;">キャンセル</v-btn>
        </v-card-actions>
      </v-card>
    </v-container>
</template>
  
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        content: '',
        requester_department: '',
        requester_name: ''
      };
    },
    methods: {
      async submitRequest() {
        try {
          await axios.post('http://127.0.0.1:5000/requests', {
            content: this.content,
            requester_department: this.requester_department,
            requester_name: this.requester_name
          });
          alert('要望が追加されました');
          this.content = '';
          this.requester_department = '';
          this.requester_name = '';
        } catch (error) {
          console.error('エラーが発生しました:', error);
          alert('要望の追加に失敗しました');
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
  
  input[type="text"] {
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
  