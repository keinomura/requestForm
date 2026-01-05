<template>
  <v-container class="my-2">
    <v-card>
      <v-card-title>
          要望一覧
          <v-btn icon @click="isSearchDialogOpen = true" class="mx-10">
            <v-icon>mdi-magnify</v-icon>
          </v-btn>
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
              <v-select v-model="search.status" :items="statusOptions" label="対応状況" multiple />
              <v-row>
                <v-col cols="6">
                  <v-text-field v-model="search.input_date_start" label="登録日: 開始日時" type="date" />
                  <v-dialog v-model="menu1" max-width="290px">
                    <v-date-picker v-model="search.input_date_start" @change="menu1 = false"></v-date-picker>
                  </v-dialog>
                </v-col>
                <v-col cols="6">
                  <v-text-field v-model="search.input_date_end" label="登録日: 終了日時" type="date" />
                  <v-dialog v-model="menu2" max-width="290px">
                    <v-date-picker v-model="search.input_date_end" @change="menu2 = false"></v-date-picker>
                  </v-dialog>
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="6">
                  <v-text-field v-model="search.update_date_start" label="更新日: 開始日時" type="date" />
                  <v-dialog v-model="menu3" max-width="290px">
                    <v-date-picker v-model="search.update_date_start" @change="menu3 = false"></v-date-picker> 
                  </v-dialog>
                </v-col>
                <v-col cols="6">
                  <v-text-field v-model="search.update_date_end" label="更新日: 終了日時" type="date" />
                  <v-dialog v-model="menu4" max-width="290px">
                    <v-date-picker v-model="search.update_date_end" @change="menu4 = false"></v-date-picker>
                  </v-dialog>
                </v-col>
              </v-row>
              <v-row justify="center">
                <v-col cols="auto">
                  <v-btn type="submit" color="primary">
                    <v-icon left>mdi-magnify</v-icon>
                    検索
                  </v-btn>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="isSearchDialogOpen = false">
              <v-icon left>mdi-cancel</v-icon>
              閉じる
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      
  <!-- デスクトップ表示用のテーブル (大画面: 1920px以上) -->
  <div class="d-none d-xl-block">
    <v-data-table
      :headers="headers"
      :items="filteredRequests"
      class="elevation-1"
      item-key="request_uuid"
      dense
      :item-class="getRowClass"
      item-value="request_uuid"
      show-expand
    >
      <template v-slot:[`item.content`]="{ item }">
        <div class="content-cell">{{ item.content }}</div>
      </template>
      <template v-slot:[`item.status`]="{ item }">
        <v-chip :color="getStatusColor(item.status)" dark>{{ item.status }}</v-chip>
      </template>
      <template v-slot:expanded-row="{ columns, item }">
        <tr>
          <td :colspan="columns.length">
            <v-card flat>
              <v-card-text>
                <v-list dense>
                  <v-list-item>
                    <template v-slot:default>
                      <div class="v-list-item-title">{{ item.response_comment }}</div>
                      <div class="v-list-item-subtitle">
                        <v-chip x-small :color="getHandlerColor(item.handler_company)" class="mr-1" v-if="item.handler_company">
                          {{ item.handler_company }}
                        </v-chip>
                        {{ item.assigned_department }} {{ item.assigned_person }} {{ item.update_date }}
                      </div>
                    </template>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </td>
        </tr>
      </template>
      <template v-slot:[`item.actions`]="{ item }">
        <v-btn color="primary" @click="viewDetails(item.request_uuid)">
          <v-icon left>mdi-eye</v-icon>
          詳細
        </v-btn>
        <v-btn
          color="secondary"
          @click="openUpdateDialog(item)"
          :disabled="!isAdminMode && item.status === '対応完了（電カル委員会承認）'"
        >
          <v-icon left>mdi-pencil</v-icon>
          進捗
        </v-btn>
        <v-btn
          v-if="isAdminMode"
          color="red"
          @click="openDeleteDialog(item)"
        >
          <v-icon left>mdi-delete</v-icon>
        </v-btn>
      </template>
    </v-data-table>
  </div>
  
  <!-- 中間サイズ画面用のカードビュー (960px-1920px) -->
  <div class="d-none d-md-block d-xl-none">
    <v-container fluid>
      <v-row>
        <v-col cols="12" v-for="item in filteredRequests" :key="item.request_uuid" class="pa-2">
          <v-card :class="getCardClass(item.status)" elevation="2" class="medium-card">
            <v-card-title class="text-subtitle-1 py-2 d-flex justify-space-between">
              <div class="d-flex align-center">
                <span class="mr-2">No.{{ item.index }}</span>
                <v-chip :color="getStatusColor(item.status)" dark small class="mr-2">{{ item.status }}</v-chip>
              </div>
              <div class="text-caption">{{ item.update_date }}</div>
            </v-card-title>
            
            <!-- 内容セクション - 最も目立つように -->
            <v-card-text class="medium-content-section py-3">
              <p class="text-body-1 font-weight-medium medium-content">{{ item.content }}</p>
            </v-card-text>
            
            <!-- 詳細情報セクション -->
            <v-row no-gutters>
              <v-col cols="12" md="6" lg="4">
                <v-card-text class="py-2 px-4 grey lighten-4">
                  <v-row dense>
                    <v-col cols="12" sm="6">
                      <p class="text-caption mb-1"><strong>部署:</strong> {{ item.requester_department }}</p>
                    </v-col>
                    <v-col cols="12" sm="6">
                      <p class="text-caption mb-1"><strong>氏名:</strong> {{ item.requester_name }}</p>
                    </v-col>
                    <v-col cols="12">
                      <p class="text-caption mb-1"><strong>登録日時:</strong> {{ item.input_date }}</p>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-col>
              
              <v-col cols="12" md="6" lg="4">
                <v-card-text class="py-2 px-4 grey lighten-5">
                  <v-row dense>
                    <v-col cols="12">
                      <p class="text-caption mb-1"><strong>担当部署:</strong> {{ item.assigned_department || '未設定' }}</p>
                    </v-col>
                    <v-col cols="12">
                      <v-chip small :color="getHandlerColor(item.handler_company)" class="mb-1 mr-1" v-if="item.handler_company">
                        {{ item.handler_company }}
                      </v-chip>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-col>
              
              <v-col cols="12" lg="4">
                <v-card-text class="py-2 px-4" v-if="item.response_comment">
                  <p class="text-caption font-weight-bold">最新コメント:</p>
                  <p class="text-body-2 comment-text-medium">{{ item.response_comment }}</p>
                </v-card-text>
              </v-col>
            </v-row>
            
            <!-- ボタンセクション -->
            <v-card-actions class="pa-3 justify-end">
              <v-btn color="primary" class="mx-1" @click="viewDetails(item.request_uuid)">
                <v-icon left>mdi-eye</v-icon>
                詳細
              </v-btn>
              <v-btn
                color="secondary"
                class="mx-1"
                @click="openUpdateDialog(item)"
                :disabled="!isAdminMode && item.status === '対応完了（電カル委員会承認）'"
              >
                <v-icon left>mdi-pencil</v-icon>
                進捗
              </v-btn>
              <v-btn
                v-if="isAdminMode"
                color="red"
                class="mx-1"
                @click="openDeleteDialog(item)"
              >
                <v-icon left>mdi-delete</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
      
      <!-- モバイル表示用のカードビュー -->
      <div class="d-md-none">
        <v-card-text class="pa-0">
          <v-container fluid>
            <v-row>
              <v-col cols="12" v-for="item in filteredRequests" :key="item.request_uuid" class="pa-2">
                <v-card :class="getCardClass(item.status)" elevation="2" class="mobile-card">
                  <v-card-title class="text-subtitle-1 py-2 d-flex justify-space-between">
                    <div class="d-flex align-center">
                      <span class="mr-2">No.{{ item.index }}</span>
                      <v-chip :color="getStatusColor(item.status)" dark x-small class="mr-2">{{ item.status }}</v-chip>
                    </div>
                    <div class="text-caption">{{ item.update_date }}</div>
                  </v-card-title>
                  
                  <!-- 内容セクション - より目立つように -->
                  <v-card-text class="content-section py-3">
                    <p class="text-body-1 font-weight-medium mobile-content">{{ item.content }}</p>
                  </v-card-text>
                  
                  <!-- 詳細情報セクション -->
                  <v-card-text class="py-2 px-4 grey lighten-4">
                    <v-row dense>
                      <v-col cols="6">
                        <p class="text-caption mb-1"><strong>部署:</strong> {{ item.requester_department }}</p>
                      </v-col>
                      <v-col cols="6">
                        <p class="text-caption mb-1"><strong>氏名:</strong> {{ item.requester_name }}</p>
                      </v-col>
                    </v-row>
                    <v-row dense>
                      <v-col cols="12">
                        <p class="text-caption mb-1"><strong>登録日時:</strong> {{ item.input_date }}</p>
                      </v-col>
                    </v-row>
                  </v-card-text>
                  
                  <!-- 対応情報セクション -->
                  <v-card-text v-if="item.handler_company || item.assigned_department" class="py-2 px-4 handler-info">
                    <v-chip small :color="getHandlerColor(item.handler_company)" class="mb-1 mr-1" v-if="item.handler_company">
                      {{ item.handler_company }}
                    </v-chip>
                    <v-chip small color="blue-grey lighten-4" class="mb-1" v-if="item.assigned_department">
                      {{ item.assigned_department }}
                    </v-chip>
                  </v-card-text>
                  
                  <!-- コメントセクション -->
                  <template v-if="item.response_comment">
                    <v-divider></v-divider>
                    <v-card-text class="py-2">
                      <p class="text-caption font-weight-bold">最新コメント:</p>
                      <p class="text-body-2 comment-text">{{ item.response_comment }}</p>
                      <p class="text-caption">{{ item.assigned_department }} {{ item.assigned_person }}</p>
                    </v-card-text>
                  </template>
                  
                  <!-- ボタンセクション - モバイルでの操作性向上 -->
                  <v-card-actions class="pa-3 justify-space-between">
                    <v-btn small color="primary" class="px-2" @click="viewDetails(item.request_uuid)">
                      <v-icon small left>mdi-eye</v-icon>
                      詳細
                    </v-btn>
                    <v-btn
                      small
                      color="secondary"
                      class="px-2"
                      @click="openUpdateDialog(item)"
                      :disabled="!isAdminMode && item.status === '対応完了（電カル委員会承認）'"
                    >
                      <v-icon small left>mdi-pencil</v-icon>
                      進捗
                    </v-btn>
                    <v-btn
                      v-if="isAdminMode"
                      small
                      color="red"
                      class="px-2"
                      @click="openDeleteDialog(item)"
                    >
                      <v-icon small left>mdi-delete</v-icon>
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </div>
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
              <v-select
                v-model="currentRequest.handler_company"
                :items="companyOptions"
                label="対応会社"
                required
              ></v-select>
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
          <v-btn color="blue darken-1" text @click="closeDialog">
            <v-icon left>mdi-cancel</v-icon>
            キャンセル
          </v-btn>
          <v-btn color="blue darken-1" text @click="checkPassword">
            <v-icon left>mdi-check</v-icon>
            更新
          </v-btn>
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
            <v-list-item v-for="comment in comments" :key="comment.response_uuid">
              <template v-slot:default>
                <v-row>
                  <v-col cols="10">
                    <div class="v-list-item-title"> {{ comment.index }}. {{ comment.response_comment }}</div>
                    <div class="v-list-item-subtitle">
                      {{ comment.handler_name }} 
                      <div class="mt-1">
                        <v-chip x-small :color="getHandlerColor(comment.handler_company)" class="mr-1" v-if="comment.handler_company">
                          {{ comment.handler_company }}
                        </v-chip>
                        <v-chip x-small color="blue-grey lighten-4" v-if="comment.handler_department">
                          {{ comment.handler_department }}
                        </v-chip>
                      </div>
                      <div class="mt-1">更新日時: {{ comment.response_date }}</div>
                    </div>
                  </v-col>
                  <v-col cols="2" v-if="isAdminMode">
                    <v-btn icon @click="openDeleteCommentDialog(comment.response_uuid)">
                      <v-icon color="red">mdi-delete</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </template>
            </v-list-item>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="closeCommentsDialog">
            <v-icon left>mdi-cancel</v-icon>
            閉じる
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="isDeleteDialogOpen" max-width="500px">
      <v-card>
        <v-card-title>要望の削除</v-card-title>
        <v-card-text>
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
          <v-btn color="blue darken-1" text @click="closeDeleteDialog">
        <v-icon left>mdi-cancel</v-icon>
        キャンセル
      </v-btn>
      <v-btn color="red" text @click="deleteRequest">
        <v-icon left>mdi-delete</v-icon>
        削除
      </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="isDeleteCommentDialogOpen" max-width="500px">
      <v-card>
        <v-card-title>コメントの削除</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="deleteCommentPassword"
            label="削除用パスワードを入力してください"
            type="password"
            required
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="closeDeleteCommentDialog">
            <v-icon left>mdi-cancel</v-icon>
            キャンセル</v-btn>
          <v-btn color="red" text @click="confirmDeleteComment">
            <v-icon left>mdi-delete</v-icon>
            削除</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
// import { useRoute } from 'vue-router';
import { defineProps } from 'vue';

const props = defineProps({
  isAdminMode: Boolean
});

const headers = [
  { text: 'No.', value: 'index', sortable: false, width: '50px' },
  { title: '内容', key: 'content', width: '30%' },  // 内容列を広く設定
  { title: '部署', key: 'requester_department', width: '10%' },
  { title: '氏名', key: 'requester_name', width: '10%' },
  { title: '登録日時', key: 'input_date', width: '10%' },
  { title: '対応状況', key: 'status', width: '10%' },
  { title: '対応企業', key: 'handler_company', width: '10%' },
  { title: '担当部署', key: 'assigned_department', width: '10%' },
  { title: 'コメント', key: 'data-table-expand', width: '5%' },
  { title: '更新日時', key: 'update_date', width: '10%' },
  { title: '', key: 'actions', sortable: false, width: '15%' },
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

const companyOptions = [
  '電子カルテシステム',
  'ネットワークシステム',
  '画像システム',
  'その他'
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
  assigned_person: '',
  status: [],
  input_date_start: null,
  input_date_end: null,
  update_date_range: null
});
const isSearchDialogOpen = ref(false);
const menu1 = ref(false);
const menu2 = ref(false);
const menu3 = ref(false);
const menu4 = ref(false);

const filteredRequests = computed(() => {
  return requests.value.filter(request => {
    const matchesContent = request.content?.includes(search.value.content) ?? true;
    const matchesRequesterDepartment = request.requester_department?.includes(search.value.requester_department) ?? true;
    const matchesRequesterName = request.requester_name?.includes(search.value.requester_name) ?? true;
    const matchesAssignedDepartment = request.assigned_department?.includes(search.value.assigned_department) ?? true;
    const matchesAssignedPerson = request.assigned_person?.includes(search.value.assigned_person) ?? true;
    const matchesStatus = search.value.status.length === 0 || search.value.status.includes(request.status);
    const matchesInputDate = (!search.value.input_date_start || new Date(request.input_date) >= new Date(search.value.input_date_start)) &&
                              (!search.value.input_date_end || new Date(request.input_date) <= new Date(search.value.input_date_end));
    const matchesUpdateDate = (!search.value.update_date_start || new Date(request.update_date) >= new Date(search.value.update_date_start)) &&
                              (!search.value.update_date_end || new Date(request.update_date) <= new Date(search.value.update_date_end));

    return matchesContent && matchesRequesterDepartment && matchesRequesterName && matchesAssignedDepartment && matchesAssignedPerson && matchesStatus && matchesInputDate && matchesUpdateDate;
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
const passForDeleteComment = 'del3377'

// 進捗更新
const previousStatus = ref(''); //statusが電子カルテ委員会承認を判断するための変数
const currentRequest = ref({}); // 進捗更新用のデータ

// 詳細コメント表示
const comments = ref([]);

//コメント削除
// const deletePassword = ref('');
const deleteCommentPassword = ref('');
const deleteCommentUuid = ref('');
const isDeleteCommentDialogOpen = ref(false)


// 一覧表示用データ取得
const fetchRequests = async () => {
  try {
    const apiUrl = import.meta.env.VITE_API_URL;
    const response = await axios.get(`${apiUrl}/requests`);

    requests.value = response.data.map((request, index) => {
      return {
        ...request,
        index: index + 1,
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
const viewDetails = async (request_uuid) => {
  try {
    const apiUrl = import.meta.env.VITE_API_URL;
    const response = await axios.get(`${apiUrl}/requests/${request_uuid}/comments`);

    comments.value = response.data.map((comment, index) => {
      return {
        ...comment,
        index: index + 1,
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
  console.log(currentRequest.value); // currentRequestオブジェクトの内容を確認

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
    const apiUrl = import.meta.env.VITE_API_URL;
    await axios.put(`${apiUrl}/requests/${currentRequest.value.request_uuid}`, currentRequest.value);

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
    const apiUrl = import.meta.env.VITE_API_URL;
    await axios.delete(`${apiUrl}/requests/${currentRequest.value.request_uuid}`);

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

// コメントの削除処理
const openDeleteCommentDialog = (response_uuid) => {
  deleteCommentUuid.value = response_uuid;
  isDeleteCommentDialogOpen.value = true;
};

const closeDeleteCommentDialog = () => {
  isDeleteCommentDialogOpen.value = false;
};

const confirmDeleteComment = async () => {
  try {
    // パスワードチェックをここで行う（例: パスワードが "admin" であることを確認）
    if (deleteCommentPassword.value !== passForDeleteComment) {
      alert('パスワードが正しくありません');
      return;
    }
    const apiUrl = import.meta.env.VITE_API_URL;
    await axios.delete(`${apiUrl}/comments/${deleteCommentUuid.value}`);

    alert('コメントが削除されました');
    //コメント一覧に戻る。コメントが何もなければ要望一覧画面に戻る。
    viewDetails(currentRequest.value.request_uuid); // コメント削除後にコメント一覧を再取得
    closeDeleteCommentDialog();
    
  } catch (error) {
    console.error('コメントの削除に失敗しました:', error);
    alert('コメントの削除に失敗しました');
  }
};


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
const getRowClass = (item) => {
  if (item.status === '対応完了（電カル委員会承認）') {
    return 'completed-row';
  } else if (item.status.includes('対応中')) {
    return 'status-in-progress';
  } else if (item.status.includes('対応完了')) {
    return 'status-completed';
  }
  return '';
};

const getCardClass = (status) => {
  if (status === '対応完了（電カル委員会承認）') {
    return 'completed-card';
  } else if (status.includes('対応中')) {
    return 'in-progress-card';
  } else if (status.includes('対応完了')) {
    return 'completed-card';
  }
  return '';
};

const getHandlerColor = (company) => {
  switch (company) {
    case '電子カルテシステム':
      return 'indigo lighten-1';
    case 'ネットワークシステム':
      return 'deep-orange lighten-1';
    case '画像システム':
      return 'teal lighten-1';
    case 'その他':
      return 'blue-grey lighten-1';
    default:
      return 'grey lighten-1';
  }
};
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

/* カードビュー用のスタイル */
.completed-card {
  background-color: #e0ffe0;
}
.in-progress-card {
  background-color: #fff3cd;
}
.completed-card {
  background-color: #d4edda;
}

/* テーブル内の内容セルのスタイル */
.content-cell {
  font-weight: 500;
  padding: 8px 0;
  max-width: 100%;
  white-space: pre-line;
  line-height: 1.5;
}

/* 中間サイズ画面用のスタイル (960px-1920px) */
.medium-card {
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.medium-card:hover {
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15) !important;
}

.medium-content-section {
  background-color: #f9f9f9;
  border-left: 4px solid #1976d2;
  padding-left: 16px !important;
  margin-bottom: 8px;
}

.medium-content {
  line-height: 1.6;
  font-size: 1.05rem;
  font-weight: 500;
  word-break: break-word;
  color: #333;
}

.comment-text-medium {
  white-space: pre-line;
  max-height: 80px;
  overflow-y: auto;
  padding: 8px;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-size: 0.9rem;
}

/* モバイル表示の調整 */
@media (max-width: 960px) {
  .v-card-text p {
    margin-bottom: 4px;
  }
  
  .v-card-actions {
    padding: 8px;
  }
  
  .v-btn--small {
    margin: 0 4px;
    min-width: 70px !important;
  }
  
  .mobile-card {
    margin-bottom: 12px;
  }
  
  .content-section {
    background-color: #f9f9f9;
    border-left: 4px solid #1976d2;
    padding-left: 12px !important;
  }
  
  .handler-info {
    background-color: #f5f5f5;
    border-radius: 4px;
    padding: 8px 12px !important;
  }
  
  .handler-info .v-chip {
    margin-right: 4px;
    margin-bottom: 4px;
  }
  
  .comment-text {
    white-space: pre-line;
    max-height: 100px;
    overflow-y: auto;
    padding: 8px;
    background-color: #f5f5f5;
    border-radius: 4px;
  }
}

/* モバイルコンテンツの表示改善 */
.mobile-content {
  line-height: 1.6;
  font-size: 1rem;
  word-break: break-word;
}

/* 小さいモバイル画面用の追加調整 */
@media (max-width: 480px) {
  .v-btn--small {
    min-width: 60px !important;
    padding: 0 4px !important;
  }
  
  .v-card-actions {
    flex-wrap: wrap;
  }
  
  .mobile-content {
    font-size: 0.95rem;
  }
}

/* レスポンシブ調整 */
@media (min-width: 961px) and (max-width: 1919px) {
  .medium-card {
    border-radius: 8px;
  }
  
  .medium-content-section {
    border-radius: 4px;
  }
}
</style>
