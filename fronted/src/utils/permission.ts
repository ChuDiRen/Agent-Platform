import router from '@/router'
import { getToken } from '@/utils/auth'
import NProgress from '@/utils/nprogress'

const whiteList = ['/login', '/register']

router.beforeEach((to, _from, next) => {
  NProgress.start()
  document.title = (to.meta.title as string) || 'Vue3 App'

  const token = getToken()
  if (token) {
    if (to.path === '/login') {
      next({ path: '/home' })
    } else {
      next()
    }
  } else {
    if (whiteList.includes(to.path)) {
      next()
    } else {
      next(`/login?redirect=${to.path}`)
    }
  }
})

router.afterEach(() => {
  NProgress.done()
})
