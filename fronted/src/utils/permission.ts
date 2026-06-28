import router from '@/router'
import { getToken } from '@/utils/auth'
import NProgress from '@/utils/nprogress'

const whiteList = ['/login', '/register']

router.beforeEach((to) => {
  NProgress.start()
  document.title = (to.meta.title as string) || 'Vue3 App'

  const token = getToken()
  if (token) {
    if (to.path === '/login') {
      return { path: '/projects' }
    }
  } else {
    if (!whiteList.includes(to.path)) {
      return `/login?redirect=${encodeURIComponent(to.fullPath)}`
    }
  }
})

router.afterEach(() => {
  NProgress.done()
})
