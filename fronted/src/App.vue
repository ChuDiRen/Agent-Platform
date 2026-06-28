<script setup lang="ts"></script>

<template>
  <div class="app-wrapper bg-grid">
    <div class="bg-orb bg-orb--primary" />
    <div class="bg-orb bg-orb--secondary" />
    <router-view />
  </div>
</template>

<style lang="scss">
#app {
  width: 100%;
  height: 100%;
}

.app-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}
</style>
