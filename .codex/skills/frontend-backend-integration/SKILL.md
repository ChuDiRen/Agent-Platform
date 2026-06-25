---
name: frontend-backend-integration
description: 前后端联调规范，包含跨域代理配置、API 对接流程、接口定义规范、错误处理等
user_invocable: true
---

# 前后端联调规范

## 触发条件
用户要求实现前后端联调、API 对接、解决跨域问题时触发。

## 端口规范

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 | 3000 | Vite 开发服务器 |
| 后端 | 8000 | FastAPI / Uvicorn |

## 跨域解决方案

### 方案一：Vite 代理（推荐，开发环境）

在 `vite.config.ts` 中配置代理：

```ts
server: {
  host: '0.0.0.0',
  port: 3000,
  open: true,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
},
```

**工作原理**：
- 前端请求 `http://localhost:3000/api/v1/users/login`
- Vite 代理自动转发到 `http://localhost:8000/api/v1/users/login`
- 浏览器看到的是同源请求，无跨域问题

**环境变量配置**（`.env.development`）：
```
VITE_ENV = development
VITE_APP_WEB_URL = ''  # 使用代理时为空
```

### 方案二：后端 CORS（备用，生产环境）

在后端 `main.py` 中配置 CORS：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 指定前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## API 接口规范

### 后端接口定义

**请求 Schema**：
```python
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str
```

**响应 Schema**：
```python
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User
```

**端点定义**：
```python
@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    # 业务逻辑
    return LoginResponse(access_token=token, user=user)
```

### 前端 API 模块

**`src/api/user.ts`**：
```ts
import { post, get } from './http'

// 类型定义
export interface LoginRequest {
  email: string
  password: string
}

export interface UserInfo {
  id: number
  email: string
  full_name: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

// API 函数
export function login(data: LoginRequest): Promise<LoginResponse> {
  return post<LoginResponse>('/api/v1/users/login', data)
}

export function getUserInfo(userId: number): Promise<UserInfo> {
  return get<UserInfo>(`/api/v1/users/${userId}`)
}
```

## 前端对接流程

### 1. 创建 API 类型定义

在 `src/api/` 下创建模块文件，定义请求/响应接口。

### 2. 创建 API 函数

使用 `src/api/http.ts` 中封装的 `get`、`post` 方法。

### 3. 页面调用 API

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { login } from '@/api/user'
import { ElMessage } from 'element-plus'

const loading = ref(false)

async function handleLogin() {
  loading.value = true
  try {
    const res = await login({ email: 'test@example.com', password: '123456' })
    // 处理成功
    ElMessage.success('登录成功')
  } catch (error: any) {
    // 处理错误
    ElMessage.error(error?.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}
</script>
```

### 4. Token 管理

登录成功后保存 token：
```ts
import { setToken } from '@/utils/auth'

// 登录成功后
setToken(res.access_token)
```

请求时自动携带 token（已在 `src/api/http.ts` 中配置拦截器）。

## 错误处理规范

### 后端错误格式

```python
from fastapi import HTTPException

# 400: 请求参数错误
raise HTTPException(status_code=400, detail="邮箱已注册")

# 401: 认证失败
raise HTTPException(status_code=401, detail="邮箱或密码错误")

# 404: 资源不存在
raise HTTPException(status_code=404, detail="用户不存在")
```

### 前端错误处理

```ts
try {
  await someApi()
} catch (error: any) {
  const message = error?.response?.data?.detail || '操作失败'
  ElMessage.error(message)
}
```

## 联调检查清单

- [ ] 后端服务运行在 8000 端口
- [ ] 前端服务运行在 3000 端口
- [ ] Vite 代理配置正确（`/api` -> `http://localhost:8000`）
- [ ] 环境变量 `VITE_APP_WEB_URL` 为空（开发环境）
- [ ] 后端接口使用 JSON Body 接收参数
- [ ] 前端 API 模块定义了完整的类型
- [ ] 错误处理使用统一的 `ElMessage` 提示

## 常见问题

### Q1: 请求 404
检查后端路由前缀是否正确（通常为 `/api/v1/xxx`）。

### Q2: 请求跨域
确认 Vite 代理配置是否正确，环境变量是否为空。

### Q3: Token 未携带
检查 `src/api/http.ts` 中的请求拦截器是否正确读取 token。

### Q4: 后端收不到参数
确认使用 JSON Body（`request body`）而非 Query Params。
