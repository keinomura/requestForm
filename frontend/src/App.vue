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
import { useRouter } from 'vue-router';

const isAdminMode = ref(false);
// const router = useRouter();

const toggleMode = () => {
  isAdminMode.value = !isAdminMode.value;
};
</script>

<style scoped>
.main-content {
  margin-top: 64px; /* v-app-barの高さに合わせて調整 */
}

.v-btn {
  margin-left: 8px;
}
/* 全体のレイアウト設定 */
#app {
  font-family: Arial, sans-serif;
}
/* ヘッダーとナビゲーションバーのスタイル */
header {
  background-color: #007bff;
  padding: 15px;
  color: white;
  text-align: center;
  position: sticky;
  top: 0;
  width: 60%;
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
}
</style>