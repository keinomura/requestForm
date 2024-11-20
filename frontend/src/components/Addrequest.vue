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
          <v-spacer></v-spacer>
        <v-btn text color="blue darken-1" @click="$router.push('/')">
          <v-icon left>mdi-cancel</v-icon>
          キャンセル
        </v-btn>
        <v-btn text color="primary" @click="submitRequest">
          <v-icon left>mdi-plus-box</v-icon>
          追加
        </v-btn>
        </v-card-actions>
      </v-card>
    </v-container>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const content = ref('');
const requester_department = ref('');
const requester_name = ref('');
const router = useRouter();

const submitRequest = async () => {
  try {
    await axios.post('http://127.0.0.1:5000/requests', {
      content: content.value,
      requester_department: requester_department.value,
      requester_name: requester_name.value,
    });
    alert('要望が追加されました');
    content.value = '';
    requester_department.value = '';
    requester_name.value = '';
    router.push('/'); //追加したら要望一覧画面に遷移
  } catch (error) {
    console.error('エラーが発生しました:', error);
    alert('要望の追加に失敗しました');
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

  button:hover {
    background-color: #0056b3;
  }

</style>