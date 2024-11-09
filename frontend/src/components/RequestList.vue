<template>

<div>
    <nav>
      <router-link to="/">要望一覧</router-link> |
      <router-link to="/add-request">新規要望の追加</router-link>
    </nav>
    <router-view />
  </div>
  <div class="container">
    <h1>要望一覧</h1>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>内容</th>
            <th>部署</th>
            <th>氏名</th>
            <th>入力日</th>
            <th>詳細</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in requests" :key="request.id">
            <td>{{ request.id }}</td>
            <td class="content-column">{{ request.content }}</td>
            <td>{{ request.requester_department }}</td>
            <td>{{ request.requester_name }}</td>
            <td>{{ new Date(request.input_date).toLocaleDateString() }}</td>
            <td><button @click="viewDetails(request.id)">詳細</button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      requests: []
    };
  },
  methods: {
    async fetchRequests() {
      try {
        const response = await axios.get('http://127.0.0.1:5000/requests');
        this.requests = response.data;
      } catch (error) {
        console.error("APIからのデータ取得に失敗しました:", error);
      }
    },
    viewDetails(id) {
      console.log("詳細ページのID:", id);
    }
  },
  mounted() {
    this.fetchRequests();
  }
};
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.table-container {
  max-height: 500px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 10px;
  border-bottom: 1px solid #ddd;
  text-align: center;
  white-space: nowrap;
}

th {
  background-color: #f9f9f9;
  font-weight: bold;
}

.content-column {
  text-align: left;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

button {
  padding: 5px 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}
</style>
