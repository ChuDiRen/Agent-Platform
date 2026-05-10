import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore(
  'user',
  () => {
    const token = ref('')
    const userName = ref('')
    const avatar = ref('')
    const role = ref('')

    function setToken(val: string) {
      token.value = val
    }

    function setUserInfo(info: { userName: string; avatar: string; role: string }) {
      userName.value = info.userName
      avatar.value = info.avatar
      role.value = info.role
    }

    function logout() {
      token.value = ''
      userName.value = ''
      avatar.value = ''
      role.value = ''
    }

    return { token, userName, avatar, role, setToken, setUserInfo, logout }
  },
  {
    persist: {
      key: 'user_info',
      storage: localStorage,
      paths: ['token', 'userName', 'avatar', 'role'],
    },
  },
)
