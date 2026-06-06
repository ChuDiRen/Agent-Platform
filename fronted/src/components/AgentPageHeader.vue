<script setup lang="ts">
import { useRouter } from 'vue-router'

defineProps<{
  title: string
}>()

const router = useRouter()
</script>

<template>
  <header class="agent-page-header">
    <button class="logo" @click="router.push('/agent-hub')">
      <div class="logo-icon">熊</div>
      <span>{{ title }}</span>
    </button>

    <div class="header-meta">
      <button class="outline-btn" @click="router.push('/agent-hub')">返回智能体管理</button>
    </div>
  </header>
</template>

<style scoped lang="scss">
.agent-page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
  padding: 20px 24px;
  gap: 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 0;
  background: transparent;
  color: #1E88E5;
  font-size: 22px;
  font-weight: 700;
  cursor: pointer;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #1E88E5, #1565C0);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 800;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;
}

.outline-btn {
  padding: 6px 16px;
  border: 1px solid #d0d5dd;
  border-radius: 8px;
  background: #fff;
  color: #5f6c80;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #1E88E5;
    color: #1E88E5;
  }
}

@media (max-width: 720px) {
  .agent-page-header {
    align-items: flex-start;
    flex-direction: column;
    padding: 16px;
  }

  .header-meta {
    flex-wrap: wrap;
  }

}
</style>
