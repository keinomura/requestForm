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
          <v-btn color="secondary" @click="openUpdateDialog(item)">進捗を入力</v-btn>
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="isDialogOpen" max-width="500px">
      <v-card>
        <v-card-title>進捗情報の更新</v-card-title>
        <v-card-text>
          <v-form ref="form">
            <v-text-field
              v-model="currentRequest.status"
              label="対応状況"
              required
            ></v-text-field>
            <v-textarea
              v-model="currentRequest.response_comment"
              label="最新コメント"
              required
            ></v-textarea>
            <v-text-field
              v-model="currentRequest.assigned_department"
              label="担当部署"
              required
            ></v-text-field>
            <v-text-field
              v-model="currentRequest.assigned_person"
              label="担当者名"
              required
            ></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="closeDialog">キャンセル</v-btn>
          <v-btn color="blue darken-1" text @click="updateProgress">更新</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="isCommentsDialogOpen" max-width="600px">
      <v-card>
        <v-card-title>コメント一覧</v-card-title>
        <v-card-text>
          <v-list>
            <v-list-item v-for="comment in comments" :key="comment.response_date">
              <v-list-item-content>
                <v-list-item-title>{{ comment.handler_name }} ({{ comment.handler_department }})</v-list-item-title>
                <v-list-item-subtitle>{{ comment.response_comment }}</v-list-item-subtitle>
                <v-list-item-subtitle>更新日時: {{ comment.response_date }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="closeCommentsDialog">閉じる</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

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
  { title: '登録日時', key: 'input_date' },
  { title: '対応状況', key: 'status' },
  { title: '最新コメント', key: 'response_comment' },
  { title: '更新日時', key: 'update_date' },
  { title: '担当部署', key: 'assigned_department' },
  { title: '担当者名', key: 'assigned_person' },
  { title: 'アクション', key: 'actions', sortable: false },
];

const requests = ref([]);
const isDialogOpen = ref(false);
const isCommentsDialogOpen = ref(false);
const currentRequest = ref({});
const comments = ref([]);

const fetchRequests = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:5000/requests');
    requests.value = response.data.map(request => {
      return {
        ...request,
        input_date: new Date(request.input_date).toLocaleString('ja-JP', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
        }),
        update_date: request.update_date ? new Date(request.update_date).toLocaleString('ja-JP', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
        }) : '',
      };
    });
  } catch (error) {
    console.error("APIからのデータ取得に失敗しました:", error);
  }
};

const openUpdateDialog = (item) => {
  currentRequest.value = { ...item };
  isDialogOpen.value = true;
};

const closeDialog = () => {
  isDialogOpen.value = false;
};

const updateProgress = async () => {
  try {
    currentRequest.value.update_date = new Date().toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
    await axios.put(`http://127.0.0.1:5000/requests/${currentRequest.value.id}`, currentRequest.value);
    fetchRequests(); // 更新後にリストを再取得
    closeDialog();
  } catch (error) {
    console.error("進捗情報の更新に失敗しました:", error);
  }
};

const viewDetails = async (id) => {
  try {
    const response = await axios.get(`http://127.0.0.1:5000/requests/${id}/comments`);
    comments.value = response.data;
    isCommentsDialogOpen.value = true;
  } catch (error) {
    console.error("コメントの取得に失敗しました:", error);
  }
};

const closeCommentsDialog = () => {
  isCommentsDialogOpen.value = false;
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