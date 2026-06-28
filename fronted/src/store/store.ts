import { defineStore } from 'pinia'
import { ref } from 'vue'
import { removeToken } from '@/utils/auth'

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

    function resetUser() {
      token.value = ''
      userName.value = ''
      avatar.value = ''
      role.value = ''
    }

    function logout() {
      removeToken()
      resetUser()
    }

    return { token, userName, avatar, role, setToken, setUserInfo, resetUser, logout }
  },
  {
    persist: {
      key: 'user_info',
      storage: localStorage,
      paths: ['token', 'userName', 'avatar', 'role'],
    },
  },
)
