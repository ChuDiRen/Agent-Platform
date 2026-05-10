# Agent-Platform 项目搭建教程

从零开始搭建一个全栈项目（Vue 3 前端 + FastAPI 后端），小白也能跟着做。

## 前置准备

### 安装必要工具

| 工具 | 用途 | 下载地址 |
|------|------|----------|
| Node.js (v20+) | 前端运行环境 | https://nodejs.org |
| Python (3.11+) | 后端运行环境 | https://python.org |
| pnpm | 前端包管理器 | `npm install -g pnpm` |
| Git | 版本控制 | https://git-scm.com |
| VS Code | 代码编辑器 | https://code.visualstudio.com |

验证安装：
```bash
node -v      # 应显示 v20.x
python --version  # 应显示 3.11+
pnpm -v      # 应显示 8.x 或更高
git --version
```

---

## 第一部分：初始化仓库

### 1.1 创建项目根目录

```bash
mkdir Agent-Platform
cd Agent-Platform
git init
```

### 1.2 创建 .gitignore

在项目根目录创建 `.gitignore` 文件，内容如下：

```gitignore
# 依赖
node_modules/
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
venv/
.venv/

# 环境变量
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/

# 系统文件
.DS_Store
Thumbs.db

# 日志
*.log

# 测试与缓存
.pytest_cache/
.mypy_cache/

# 构建产物
fronted/dist/
backend/*.db
```

---

## 第二部分：搭建前端项目

### 2.1 创建 Vue 3 项目

```bash
# 使用 pnpm 创建 Vite + Vue + TypeScript 项目
pnpm create vite fronted --template vue-ts

# 进入项目目录
cd fronted

# 安装基础依赖
pnpm install
```

### 2.2 安装项目依赖

```bash
# 生产依赖（路由、状态管理、UI 框架、HTTP 请求等）
pnpm add vue-router pinia pinia-plugin-persistedstate element-plus @element-plus/icons-vue axios nprogress js-cookie

# 开发依赖（类型定义、代码规范、构建工具等）
pnpm add -D @types/node @types/nprogress sass terser \
  eslint eslint-plugin-vue @typescript-eslint/eslint-plugin @typescript-eslint/parser \
  prettier eslint-config-prettier eslint-plugin-prettier \
  unplugin-auto-import unplugin-vue-components
```

### 2.3 配置路径别名

编辑 `vite.config.ts`，添加 `@` 别名指向 `src` 目录：

```ts
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default ({ mode }: any) => {
  const env = loadEnv(mode, process.cwd())
  return defineConfig({
    base: './',
    plugins: [
      vue(),
      AutoImport({
        imports: ['vue', 'vue-router'],
        dts: 'src/auto-import.d.ts',
        resolvers: [ElementPlusResolver()],
      }),
      Components({
        resolvers: [ElementPlusResolver()],
      }),
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@use "@/assets/style/_variables.scss" as *;`,
        },
      },
    },
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
    build: {
      outDir: env.VITE_ENV === 'production' ? 'dist' : 'dist-test',
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: false,
          drop_debugger: true,
        },
      },
    },
  })
}
```

编辑 `tsconfig.app.json`，在 `compilerOptions` 中添加路径映射：

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

### 2.4 创建目录结构

```bash
mkdir -p src/api/modules src/assets/style src/components src/router src/store src/utils src/views
```

### 2.5 创建环境变量文件

**`.env.development`**（开发环境使用 Vite 代理，URL 为空）:
```
VITE_ENV = development
VITE_APP_WEB_URL = ''
```

**`.env.production`**（生产环境填写真实 API 地址）:
```
VITE_ENV = production
VITE_APP_WEB_URL = 'https://your-api.com'
```

### 2.6 创建 SCSS 全局变量

**`src/assets/style/_variables.scss`**:
```scss
// 颜色变量
$primary-color: #409eff;
$success-color: #67c23a;
$warning-color: #e6a23c;
$danger-color: #f56c6c;
$info-color: #909399;

$text-primary: #303133;
$text-regular: #606266;
$text-secondary: #909399;
$text-placeholder: #c0c4cc;

$border-color: #dcdfe6;
$background-color: #f5f7fa;

// 常用混入
@mixin flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

@mixin ellipsis($lines: 1) {
  overflow: hidden;
  text-overflow: ellipsis;
  @if $lines == 1 {
    white-space: nowrap;
  } @else {
    display: -webkit-box;
    -webkit-line-clamp: $lines;
    -webkit-box-orient: vertical;
  }
}
```

**`src/assets/style/reset.scss`**:
```scss
*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

a { text-decoration: none; color: inherit; }
ul, ol { list-style: none; }
img { max-width: 100%; vertical-align: middle; }
input, button, textarea { outline: none; border: none; }
```

**`src/assets/style/global.scss`**:
```scss
@use 'variables' as *;
// 全局样式
```

**`src/assets/style/elementReset.scss`**:
```scss
// Element Plus 样式覆盖（按需自定义）
```

### 2.7 创建工具类

**`src/utils/auth.ts`** — Token 管理:
```ts
import Cookies from 'js-cookie'

const TOKEN_KEY = 'vue3_token'

export function getToken(): string | undefined {
  return Cookies.get(TOKEN_KEY)
}

export function setToken(token: string): void {
  Cookies.set(TOKEN_KEY, token, { expires: 7 })
}

export function removeToken(): void {
  Cookies.remove(TOKEN_KEY)
}
```

**`src/utils/nprogress.ts`** — 进度条:
```ts
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

NProgress.configure({ showSpinner: false })
export default NProgress
```

**`src/utils/permission.ts`** — 路由守卫:
```ts
import router from '@/router'
import { getToken } from '@/utils/auth'
import NProgress from '@/utils/nprogress'

const whiteList = ['/login']

router.beforeEach((to, _from, next) => {
  NProgress.start()
  document.title = (to.meta.title as string) || 'Vue3 App'
  const token = getToken()
  if (token) {
    to.path === '/login' ? next({ path: '/home' }) : next()
  } else {
    whiteList.includes(to.path) ? next() : next(`/login?redirect=${to.path}`)
  }
})

router.afterEach(() => NProgress.done())
```

**`src/utils/getAssestsFile.ts`** — 静态资源:
```ts
export function getAssetsFile(url: string): string {
  return new URL(`../assets/${url}`, import.meta.url).href
}
```

### 2.8 创建 API 封装

**`src/api/baseUrl.ts`**:
```ts
const env = import.meta.env.VITE_ENV

// 开发环境使用 Vite 代理，不需要完整 URL
// 生产环境使用环境变量配置的 URL
const baseUrlMap: Record<string, string> = {
  development: import.meta.env.VITE_APP_WEB_URL || '',
  production: import.meta.env.VITE_APP_WEB_URL || '',
}

export const baseUrl = baseUrlMap[env] ?? ''
```

**`src/api/http.ts`**:
```ts
import axios, { type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { getToken } from '@/utils/auth'
import NProgress from '@/utils/nprogress'
import { baseUrl } from './baseUrl'

const service = axios.create({ baseURL: baseUrl, timeout: 15000 })

// 请求拦截器：自动附带 token
service.interceptors.request.use((config) => {
  NProgress.start()
  const token = getToken()
  if (token) config.headers['Authorization'] = token
  return config
})

// 响应拦截器：统一错误处理
service.interceptors.response.use(
  (response: AxiosResponse) => {
    NProgress.done()
    return response.status === 200 ? response.data : Promise.reject(new Error('请求失败'))
  },
  (error) => {
    NProgress.done()
    error.response?.status === 401
      ? ElMessage.error('登录已过期')
      : ElMessage.error(error.message || '网络异常')
    return Promise.reject(error)
  },
)

export function get<T>(url: string, params?: object): Promise<T> {
  return service.get(url, { params }) as Promise<T>
}

export function post<T>(url: string, data?: object): Promise<T> {
  return service.post(url, data) as Promise<T>
}

export default service
```

### 2.9 创建路由

**`src/router/index.ts`**:
```ts
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/home' },
  { path: '/home', name: 'Home', component: () => import('@/views/Home.vue'), meta: { title: '首页' } },
  { path: '/login', name: 'Login', component: () => import('@/views/Login.vue'), meta: { title: '登录' } },
]

export default createRouter({ history: createWebHistory(), routes })
```

### 2.10 创建状态管理

**`src/store/store.ts`**:
```ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const userName = ref('')

  function setToken(val: string) { token.value = val }
  function setUserInfo(info: { userName: string }) { userName.value = info.userName }
  function logout() { token.value = ''; userName.value = '' }

  return { token, userName, setToken, setUserInfo, logout }
}, {
  persist: { key: 'user_info', storage: localStorage, paths: ['token', 'userName'] },
})
```

### 2.11 创建页面组件

**`src/views/Home.vue`**:
```vue
<script setup lang="ts">
defineOptions({ name: 'Home' })
</script>

<template>
  <div class="home-container">
    <h1>欢迎使用 Vue 3 + TypeScript + Pinia</h1>
    <el-button type="primary" @click="$router.push('/login')">前往登录</el-button>
  </div>
</template>

<style scoped lang="scss">
.home-container {
  @include flex-center;
  flex-direction: column;
  height: 100%;
  gap: 16px;
}
</style>
```

**`src/views/Login.vue`**:
```vue
<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/store'

defineOptions({ name: 'Login' })
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const form = reactive({ username: '', password: '' })

function handleLogin() {
  userStore.setToken('mock_token')
  userStore.setUserInfo({ userName: form.username })
  router.push((route.query.redirect as string) || '/home')
}
</script>

<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>用户登录</h2>
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" type="password" show-password /></el-form-item>
        <el-form-item><el-button type="primary" @click="handleLogin">登录</el-button></el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.login-container { @include flex-center; height: 100%; background: $background-color; }
.login-card { width: 420px; h2 { text-align: center; margin-bottom: 24px; } }
</style>
```

### 2.12 创建入口文件

**`src/App.vue`**:
```vue
<script setup lang="ts"></script>
<template><router-view /></template>
<style lang="scss">#app { width: 100%; height: 100%; }</style>
```

**`src/main.ts`**:
```ts
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import '@/assets/style/reset.scss'
import '@/assets/style/global.scss'
import '@/utils/permission'

const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
```

### 2.13 配置代码规范

**`.eslintrc.cjs`**:
```js
module.exports = {
  root: true,
  env: { browser: true, node: true, es2021: true },
  parser: 'vue-eslint-parser',
  parserOptions: { parser: '@typescript-eslint/parser', ecmaVersion: 'latest', sourceType: 'module' },
  extends: ['eslint:recommended', 'plugin:vue/vue3-recommended', 'plugin:@typescript-eslint/recommended', 'plugin:prettier/recommended', 'prettier'],
  globals: { defineProps: 'readonly', defineEmits: 'readonly', defineExpose: 'readonly' },
  rules: {
    'vue/multi-word-component-names': 'off',
    '@typescript-eslint/no-explicit-any': 'off',
    semi: ['warn', 'never'],
  },
}
```

**`.prettierrc.cjs`**:
```js
module.exports = {
  printWidth: 100, tabWidth: 2, semi: false, singleQuote: true,
  trailingComma: 'all', bracketSpacing: true, arrowParens: 'always',
}
```

**`.eslintignore`** 和 **`.prettierignore`**:
```
node_modules
dist
*.d.ts
```

### 2.14 更新 package.json scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build:dev": "vite build --mode development",
    "build:prod": "vite build --mode production",
    "lint": "eslint src --fix --ext .ts,.tsx,.vue,.js,.jsx",
    "prettier": "prettier --write ."
  }
}
```

### 2.15 启动前端

```bash
pnpm dev
```

访问 http://localhost:8000 看到页面即成功。

---

## 第三部分：搭建后端项目

### 3.1 创建项目结构

```bash
cd ..  # 回到项目根目录
mkdir -p backend/app/{core,api/v1/endpoints,models,schemas,crud,db,tests,utils}
mkdir -p backend/alembic/versions
```

### 3.2 创建虚拟环境并安装依赖

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\pip install -r requirements.txt

# Linux/Mac
# source venv/bin/activate
# pip install -r requirements.txt
```

**`requirements.txt`**:
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
alembic>=1.13.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
```

### 3.3 创建配置文件

**`.env`**:
```
PROJECT_NAME=My FastAPI App
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=change-me-in-production-please
DEBUG=true
```

**`app/core/config.py`**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI App"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 3.4 创建安全模块

**`app/core/security.py`**:
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return jwt.encode({"exp": expire, "sub": subject}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### 3.5 创建数据库模块

**`app/db/base_class.py`** — SQLAlchemy 声明式基类:
```python
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    id: int
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
```

**`app/db/session.py`** — 数据库引擎:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

**`app/db/base.py`** — 导入所有模型（用于创建表）:
```python
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
```

### 3.6 创建数据模型

**`app/models/user.py`**:
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), index=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 3.7 创建 Pydantic Schema

**`app/schemas/user.py`**:
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True
```

### 3.8 创建泛型 CRUD 基类

**`app/crud/base.py`**:
```python
from typing import Any, Generic, Type, TypeVar, Optional
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**jsonable_encoder(obj_in))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
```

**`app/crud/user.py`**:
```python
from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(email=obj_in.email, hashed_password=get_password_hash(obj_in.password), full_name=obj_in.full_name)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

user = CRUDUser(User)
```

### 3.9 创建 API 路由

**`app/api/deps.py`** — 泛型路由基类:
```python
from typing import Any, Generic, Type, TypeVar
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.crud.base import CRUDBase
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CRUDRouter(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, crud: CRUDBase[...], prefix: str = "", tag: str = ""):
        self.crud = crud
        self.router = APIRouter(prefix=prefix, tags=[tag] if tag else [])
        self._register_routes()

    def _register_routes(self):
        @self.router.post("/", response_model=Any)
        def create_item(obj_in: CreateSchemaType, db: Session = Depends(get_db)):
            return self.crud.create(db, obj_in=obj_in)

        @self.router.get("/{item_id}", response_model=Any)
        def read_item(item_id: int, db: Session = Depends(get_db)):
            item = self.crud.get(db, item_id)
            if not item: raise HTTPException(status_code=404, detail="Item not found")
            return item

        @self.router.get("/", response_model=list[Any])
        def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
            return self.crud.get_multi(db, skip=skip, limit=limit)

        @self.router.put("/{item_id}", response_model=Any)
        def update_item(item_id: int, obj_in: UpdateSchemaType, db: Session = Depends(get_db)):
            item = self.crud.get(db, item_id)
            if not item: raise HTTPException(status_code=404, detail="Item not found")
            return self.crud.update(db, db_obj=item, obj_in=obj_in)

        @self.router.delete("/{item_id}", response_model=Any)
        def delete_item(item_id: int, db: Session = Depends(get_db)):
            item = self.crud.get(db, item_id)
            if not item: raise HTTPException(status_code=404, detail="Item not found")
            return self.crud.remove(db, id=item_id)
```

**`app/api/v1/endpoints/users.py`**:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.crud.user import user as user_crud
from app.schemas.user import User, UserCreate, UserUpdate

router = APIRouter()

@router.post("/", response_model=User)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    if user_crud.get_by_email(db, email=user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_crud.create(db, obj_in=user_in)

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get(db, user_id)
    if not user: raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=list[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return user_crud.get_multi(db, skip=skip, limit=limit)
```

### 3.10 创建主入口

**`app/main.py`**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import users

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_PREFIX}/openapi.json")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

@app.get("/health")
def health():
    return {"status": "ok"}
```

### 3.11 创建所有 `__init__.py`

所有 `__init__.py` 文件内容为空，仅用于 Python 包识别：

```bash
touch app/__init__.py app/core/__init__.py app/api/__init__.py app/api/v1/__init__.py
touch app/api/v1/endpoints/__init__.py app/models/__init__.py app/schemas/__init__.py
touch app/crud/__init__.py app/db/__init__.py app/tests/__init__.py app/utils/__init__.py
```

### 3.12 启动后端

```bash
.\venv\Scripts\uvicorn app.main:app --reload --port 8000
```

访问：
- API: http://localhost:8000
- Swagger 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc

---

## 第四部分：数据库迁移（可选）

### 4.1 初始化 Alembic

```bash
cd backend
.\venv\Scripts\alembic init alembic
```

### 4.2 修改 alembic/env.py

在文件中添加：

```python
from app.db.base import Base
target_metadata = Base.metadata

from app.core.config import settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

### 4.3 生成并执行迁移

```bash
# 生成迁移脚本
.\venv\Scripts\alembic revision --autogenerate -m "initial"

# 执行迁移
.\venv\Scripts\alembic upgrade head
```

---

## 第五部分：Docker 部署（可选）

### 5.1 后端 Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.2 docker-compose.yml

```yaml
version: "3.8"
services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5.3 启动

```bash
docker-compose up -d
```

---

## 第六部分：前后端联调

### 6.1 配置跨域代理

修改 `fronted/vite.config.ts`，添加代理配置解决跨域：

```ts
server: {
  host: '0.0.0.0',
  port: 3000,
  open: true,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',  // 后端地址
      changeOrigin: true,               // 修改 Origin 头
    },
  },
},
```

修改 `fronted/.env.development`（开发环境使用代理，URL 为空）：

```
VITE_ENV = development
VITE_APP_WEB_URL = ''
```

**工作原理**：
- 前端请求 `http://localhost:3000/api/v1/users/login`
- Vite 代理自动转发到 `http://localhost:8000/api/v1/users/login`
- 浏览器看到的是同源请求，不存在跨域问题

### 6.2 创建前端 API 模块

**`src/api/user.ts`**：
```ts
import { post, get } from './http'

export interface LoginRequest {
  email: string
  password: string
}

export interface UserInfo {
  id: number
  email: string
  full_name: string
  is_active: boolean
  is_superuser: boolean
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

export function login(data: LoginRequest): Promise<LoginResponse> {
  return post<LoginResponse>('/api/v1/users/login', data)
}

export function getUserInfo(userId: number): Promise<UserInfo> {
  return get<UserInfo>(`/api/v1/users/${userId}`)
}
```

### 6.3 更新后端登录接口

**`app/schemas/user.py`** 添加登录相关 Schema：
```python
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User
```

**`app/api/v1/endpoints/users.py`** 修改登录端点：
```python
@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = user_crud.authenticate(db, email=login_data.email, password=login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    token = create_access_token(subject=str(user.id))
    return LoginResponse(access_token=token, token_type="bearer", user=user)
```

### 6.4 更新前端登录页面

**`src/views/Login.vue`** 对接真实 API：
```vue
<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/store'
import { login } from '@/api/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const loading = ref(false)
const form = reactive({ email: '', password: '' })

async function handleLogin() {
  loading.value = true
  try {
    const res = await login({ email: form.email, password: form.password })
    userStore.setToken(res.access_token)
    userStore.setUserInfo({
      userName: res.user.full_name || res.user.email,
      avatar: '',
      role: res.user.is_superuser ? 'admin' : 'user',
    })
    ElMessage.success('登录成功')
    router.push((route.query.redirect as string) || '/home')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>
```

### 6.5 测试联调流程

1. 启动后端：
```bash
cd backend
.\venv\Scripts\uvicorn app.main:app --reload --port 8000
```

2. 启动前端：
```bash
cd fronted
pnpm dev
```

3. 测试流程：
   - 访问 http://localhost:3000
   - 点击「注册账号」创建用户
   - 使用注册的邮箱和密码登录
   - 登录成功后跳转首页，显示用户信息

**跨域原理说明**：
- 前端运行在 `localhost:3000`，后端运行在 `localhost:8000`
- 直接请求会跨域，但通过 Vite 代理配置，`/api/*` 请求会自动转发到后端
- 浏览器看到的是同源请求（都是 3000 端口），不会触发跨域限制

---

## 常见问题

### Q1: pnpm 安装依赖报错
确保 Node.js 版本 >= 20.19，可使用 `nvm` 管理版本。

### Q2: SCSS 变量找不到
检查 `vite.config.ts` 中是否配置了 `css.preprocessorOptions.scss.additionalData`。

### Q3: 后端启动报数据库错误
确保 `.env` 中的 `DATABASE_URL` 正确，且已执行 `alembic upgrade head`。

### Q4: 前端请求后端跨域
后端已配置 CORS 允许所有来源，如需限制可修改 `app/main.py` 中的 `allow_origins`。

---

## 项目结构总览

```
Agent-Platform/
├── fronted/                    # 前端项目
│   ├── src/
│   │   ├── api/               # API 封装
│   │   ├── assets/style/      # SCSS 样式
│   │   ├── components/        # 公共组件
│   │   ├── router/            # 路由配置
│   │   ├── store/             # 状态管理
│   │   ├── utils/             # 工具函数
│   │   ├── views/             # 页面组件
│   │   ├── App.vue            # 根组件
│   │   └── main.ts            # 入口文件
│   ├── .env.development       # 开发环境变量
│   ├── .env.production        # 生产环境变量
│   ├── vite.config.ts         # Vite 配置
│   └── package.json
│
├── backend/                    # 后端项目
│   ├── app/
│   │   ├── core/              # 配置与安全
│   │   ├── api/               # API 路由
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic Schema
│   │   ├── crud/              # CRUD 操作
│   │   ├── db/                # 数据库连接
│   │   ├── tests/             # 测试
│   │   └── main.py            # 入口文件
│   ├── alembic/               # 数据库迁移
│   ├── .env                   # 环境变量
│   ├── requirements.txt       # Python 依赖
│   └── Dockerfile
│
├── .gitignore
├── CLAUDE.md                   # Claude Code 指导文件
└── docs/tutorial.md            # 本教程
```
