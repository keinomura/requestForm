<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-toolbar-title>要望管理システム</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn text to="/">
        <v-icon left>mdi-view-list</v-icon>
        一覧
      </v-btn>
      <v-btn text to="/add-request">
        <v-icon left>mdi-plus-box</v-icon>
        新規追加
      </v-btn>
      <v-btn text @click="toggleMode">
        <v-icon left>{{ isAdminMode ? 'mdi-eye' : 'mdi-account' }}</v-icon>
        {{ isAdminMode ? '閲覧入力モードへ移動' : '管理用へ移動' }}
      </v-btn>
      <v-spacer></v-spacer>
    </v-app-bar>
    <v-main class="main-content">
      <router-view :isAdminMode="isAdminMode" />
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue';

const isAdminMode = ref(false);

const toggleMode = () => {
  isAdminMode.value = !isAdminMode.value;
};
</script>

<style scoped>
.main-content {
  margin-top: 64px; /* v-app-barの高さに合わせて調整 */
  padding: 0 10px;
}

.v-btn {
  margin-left: 8px;
}
/* 全体のレイアウト設定 */
#app {
  font-family: Arial, sans-serif;
  max-width: 100%;
  overflow-x: hidden;
}
/* ヘッダーとナビゲーションバーのスタイル */
header {
  background-color: #007bff;
  padding: 15px;
  color: white;
  text-align: center;
  position: sticky;
  top: 0;
  width: 100%;
  z-index: 1000;
}

/* ナビゲーションリンクのスタイル */
nav a {
  color: #fff;
  margin: 0 15px;
  text-decoration: none;
  font-weight: bold;
}

nav a:hover {
  text-decoration: underline;
}

/* メインコンテンツのスタイル */
main {
  padding: 20px;
  width: 100%;
  box-sizing: border-box;
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .v-app-bar .v-toolbar-title {
    font-size: 1.2rem;
  }
  
  .v-btn {
    margin-left: 4px;
    padding: 0 8px !important;
  }
  
  .v-btn__content {
    font-size: 0.8rem;
  }
  
  .v-icon {
    font-size: 1.2rem !important;
  }
}

@media (max-width: 480px) {
  .v-app-bar .v-toolbar-title {
    font-size: 1rem;
    max-width: 120px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .v-btn {
    min-width: unset !important;
    margin-left: 2px;
    padding: 0 4px !important;
  }
  
  .v-btn__content {
    font-size: 0.7rem;
  }
  
  .v-icon {
    font-size: 1rem !important;
  }
}
</style>
