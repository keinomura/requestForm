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
      >
        <template v-slot:item.actions="{ item }">
          <v-btn color="primary" @click="viewDetails(item.id)">詳細を見る</v-btn>
          <v-btn color="secondary" @click="updateProgress(item.id)">進捗を入力</v-btn>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const headers = [
  { title: 'ID', key: 'id' },
  { title: '内容', key: 'content' },
  { title: '部署', key: 'requester_department' },
  { title: '氏名', key: 'requester_name' },
  { title: '日時', key: 'input_date' },
  { title: '対応状況', key: 'status' },
  { title: '最新コメント', key: 'response_comment' },
  { title: 'アクション', key: 'actions', sortable: false },
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

const updateProgress = (id) => {
  console.log(`進捗を入力: ${id}`);
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
.completed-row {
  background-color: #e0ffe0;
}
</style>