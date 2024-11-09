<template>
  <v-container class="my-2">
    <v-card>
      <v-card-title>要望一覧</v-card-title>
      <v-data-table
        :headers="headers"
        :items="requests"
        class="elevation-1"
        item-key="id"
        dense
        :item-class="getRowClass"

      ></v-data-table>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const headers = [
{ text: 'ID', value: 'id' },
  { text: '内容', value: 'content' },
  { text: '部署', value: 'requester_department' },
  { text: '氏名', value: 'requester_name' },
  { text: '日時', value: 'input_date' },
  { text: '対応状況', value: 'status' },
  { text: '最新コメント', value: 'response_comment' },
];

const requests = ref([]);

const fetchRequests = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:5000/requests');
    requests.value = response.data;
  } catch (error) {
    console.error("APIからのデータ取得に失敗しました:", error);
  }
};

const viewDetails = (id) => {
  console.log("詳細ページのID:", id);
};

const getRowClass = (item) => {
  if (item.status === '未対応') return 'status-pending';
  if (item.status === '対応中') return 'status-in-progress';
  if (item.status === '完了') return 'status-completed';
  return '';
};

onMounted(() => {
  fetchRequests();
});
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

.status-pending {
  background-color: #ffcccc;
}
.status-in-progress {
  background-color: #fff3cd;
}
.status-completed {
  background-color: #d4edda;
}
</style>