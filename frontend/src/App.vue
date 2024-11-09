<template>
  <div id="app">
    <header>
      <nav>
        <router-link to="/">要望一覧</router-link> |
        <router-link to="/add-request">新規要望の追加</router-link> |
        <router-link to="/update-progress">進捗情報の更新</router-link>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  name: 'App'
};
</script>

<style scoped>
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
}
</style>