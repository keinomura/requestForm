<template>
  <v-container class="my-2">
    <v-card>
      <v-card-title>
        要望一覧{{ isSearchDialogOpen }}
        <v-spacer></v-spacer>
        <!-- 検索ボタンの追加 -->
        <v-btn color="primary" @click="isSearchDialogOpen = true">検索</v-btn>
      </v-card-title>
      <!-- 検索フォームのダイアログ -->
      <v-dialog v-model="isSearchDialogOpen" max-width="600px">
        <v-card>
          <v-card-title>検索</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="searchRequests">
              <v-text-field v-model="search.content" label="内容" />
              <v-text-field v-model="search.requester_department" label="部署" />
              <v-text-field v-model="search.requester_name" label="氏名" />
              <v-text-field v-model="search.assigned_department" label="担当部署" />
              <v-text-field v-model="search.assigned_person" label="担当者名" />
              <v-btn type="submit" color="primary">検索</v-btn>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="isSearchDialogOpen = false">閉じる</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <v-data-table
        :headers="headers"
        :items="filteredRequests"
        class="elevation-1"
        item-key="id"
        dense
        :item-class="getRowClass"
      >
        <template v-slot:[`item.status`]="{ item }">
          <v-chip :color="getStatusColor(item.status)" dark>{{ item.status }}</v-chip>
        </template>
        <template v-slot:[`item.actions`]="{ item }">
          <v-btn color="primary" @click="viewDetails(item.id)">詳細を見る</v-btn>
          <v-btn
            color="secondary"
            @click="openUpdateDialog(item)"
            :disabled="!isAdminMode && item.status === '対応完了（電カル委員会承認）'"
          >進捗を入力</v-btn>
          <v-btn
            v-if="isAdminMode"
            color="red"
            @click="openDeleteDialog(item)"
          >削除</v-btn>
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="isDialogOpen" max-width="500px">
      <v-card>
        <v-card-title>進捗情報の更新</v-card-title>
        <v-card-text>
          <v-form ref="form">
            <v-select
              v-model="currentRequest.status"
              :items="filteredStatusOptions"
              label="対応状況"
              required
            ></v-select>
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
          <v-btn color="blue darken-1" text @click="checkPassword">更新</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="isPasswordDialogOpen" max-width="500px">
      <v-card>
        <v-card-title>#電カル委員会完了承認パスワード確認</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="updatePassword"
            label="パスワード"
            type="password"
            required
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="closePasswordDialog">キャンセル</v-btn>
          <v-btn color="blue darken-1" text @click="updateProgress">確認</v-btn>
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

    <v-dialog v-model="isDeleteDialogOpen" max-width="500px">
      <v-card>
        <v-card-title>要望の削除</v-card-title>
        <v-card-text>
          <p>ID: {{ currentRequest.id }}</p>
          <p>内容: {{ currentRequest.content }}</p>
          <p>登録日: {{ currentRequest.input_date }}</p>
          <v-text-field
            v-model="deletePassword"
            label="削除用パスワードを入力してください"
            type="password"
            required
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="closeDeleteDialog">キャンセル</v-btn>
          <v-btn color="red" text @click="deleteRequest">削除</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import axios from 'axios';
import { useRoute } from 'vue-router';
import { defineProps } from 'vue';

const props = defineProps({
  isAdminMode: Boolean
});

const route = useRoute();
// const isAdminMode = ref(route.params.isAdminMode || false);

// watch(() => route.params.isAdminMode, (newVal) => {
//   isAdminMode.value = newVal;
// });

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

const statusOptions = [
  '未対応',
  '覚知（対応検討中）',
  '覚知（対応中）',
  '要病院対応',
  '一時対応完了（要作業）',
  '対応完了（承認前）',
  '対応完了（電カル委員会承認）',
  '要追加情報',
  '対応保留',
  '対応不可'
];

const filteredStatusOptions = computed(() => {
  if (props.isAdminMode) {
    return statusOptions;
  } else {
    return statusOptions.filter(option => option !== '対応完了（電カル委員会承認）');
  }
});

const requests = ref([]);

// 検索モード
const search = ref({
  content: '',
  requester_department: '',
  requester_name: '',
  assigned_department: '',
  assigned_person: ''
});
const isSearchDialogOpen = ref(false);

const filteredRequests = computed(() => {
  return requests.value.filter(request => {
    const matchesContent = request.content?.includes(search.value.content) ?? true;
    const matchesRequesterDepartment = request.requester_department?.includes(search.value.requester_department) ?? true;
    const matchesRequesterName = request.requester_name?.includes(search.value.requester_name) ?? true;
    const matchesAssignedDepartment = request.assigned_department?.includes(search.value.assigned_department) ?? true;
    const matchesAssignedPerson = request.assigned_person?.includes(search.value.assigned_person) ?? true;

    return matchesContent && matchesRequesterDepartment && matchesRequesterName && matchesAssignedDepartment && matchesAssignedPerson;
  });
});

// dialog
const isDialogOpen = ref(false);
const isCommentsDialogOpen = ref(false);
const isPasswordDialogOpen = ref(false);
const isDeleteDialogOpen = ref(false);

// password
const deletePassword = ref('');
const passForDelete = 'del3377'
const updatePassword = ref('');
const passForUpdate = 'del3377'

// 進捗更新
const previousStatus = ref(''); //statusが電子カルテ委員会承認を判断するための変数
const currentRequest = ref({}); // 進捗更新用のデータ

// 詳細コメント表示
const comments = ref([]);

// 一覧表示用データ取得
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

const searchRequests = () => {
  // 検索ロジックは既にfilteredRequestsで実装されているため、ここではダイアログを閉じるだけです
  isSearchDialogOpen.value = false;
};



// 詳細ダイアログ処理
const viewDetails = async (id) => {
  try {
    const response = await axios.get(`http://127.0.0.1:5000/requests/${id}/comments`);
    comments.value = response.data.map(comment => {
      return {
        ...comment,
        response_date: new Date(comment.response_date).toLocaleString('ja-JP', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
        }),
      };
    });
    isCommentsDialogOpen.value = true;
  } catch (error) {
    console.error("コメントの取得に失敗しました:", error);
  }
};

const closeCommentsDialog = () => {
  isCommentsDialogOpen.value = false;
};

// 進捗更新ダイアログ処理
const openUpdateDialog = (item) => {
  currentRequest.value = { ...item };
  previousStatus.value = item.status; // 現在のステータスを保存
  updatePassword.value = ''; // パスワードフィールドをリセット
  isDialogOpen.value = true;
};

const closeDialog = () => {
  isDialogOpen.value = false;
};

const updateProgress = async () => {
  if (currentRequest.value.status === '対応完了（電カル委員会承認）' && updatePassword.value !== passForUpdate) {
    alert('パスワードが間違っています');
    return;
  }

  try {
    currentRequest.value.update_date = new Date()
    console.log('保存' + currentRequest.value.update_date)
    await axios.put(`http://127.0.0.1:5000/requests/${currentRequest.value.id}`, currentRequest.value);
    fetchRequests(); // 更新後にリストを再取得
    closeDialog();
    closePasswordDialog();
  } catch (error) {
    console.error("進捗情報の更新に失敗しました:", error);
  }
};

// 削除ダイアログ処理
const openDeleteDialog = (item) => {
  currentRequest.value = item;
  deletePassword.value = ''; // パスワードフィールドをリセット
  isDeleteDialogOpen.value = true;
};

const closeDeleteDialog = () => {
  isDeleteDialogOpen.value = false;
};

const deleteRequest = async () => {
  if (deletePassword.value !== passForDelete) {
    alert('パスワードが間違っています');
    return;
  }

  try {
    await axios.delete(`http://127.0.0.1:5000/requests/${currentRequest.value.id}`);
    alert('要望が削除されました');
    fetchRequests();
    closeDeleteDialog();
  } catch (error) {
    console.error("要望の削除に失敗しました:", error);
  }
};

// パスワード入力ダイアログ処理
const checkPassword = () => {
  if (currentRequest.value.status === '対応完了（電カル委員会承認）'|| previousStatus.value === '対応完了（電カル委員会承認）') {
    isPasswordDialogOpen.value = true;
  } else {
    updateProgress();
  }
};

const closePasswordDialog = () => {
  isPasswordDialogOpen.value = false;
};





// const getRowClass = (item) => {
//   if (item.status === '未対応') return 'status-pending';
//   if (item.status === '対応中') return 'status-in-progress';
//   if (item.status === '完了') return 'status-completed';
//   return '';
// };



const getStatusColor = (status) => {
  switch (status) {
    case '未対応':
      return 'red';
    case '覚知（対応検討中）':
      return 'orange';
    case '覚知（対応中）':
      return 'yellow';
    case '要病院対応':
      return 'blue';
    case '一時対応完了（要作業）':
      return 'light-green';
    case '対応完了（承認前）':
      return 'green';
    case '対応完了（電カル委員会承認）':
      return 'teal';
    case '要追加情報':
      return 'purple';
    case '対応保留':
      return 'grey';
    case '対応不可':
      return 'black';
    default:
      return 'grey';
  }
};

onMounted(() => {
  fetchRequests();
});
</script>

<style scoped>
.completed-row {
  background-color: #e0ffe0;
}
.status-in-progress {
  background-color: #fff3cd;
}
.status-completed {
  background-color: #d4edda;
}
</style>