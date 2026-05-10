const env = import.meta.env.VITE_ENV

// 开发环境使用 Vite 代理，不需要完整 URL
// 生产环境使用环境变量配置的 URL
const baseUrlMap: Record<string, string> = {
  development: import.meta.env.VITE_APP_WEB_URL || '',
  production: import.meta.env.VITE_APP_WEB_URL || '',
}

export const baseUrl = baseUrlMap[env] ?? ''
