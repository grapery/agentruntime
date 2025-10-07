# API 文档

Flask API项目的完整API接口文档。

## 目录

- [基础接口](#基础接口)
- [用户管理API](#用户管理api)
- [产品管理API](#产品管理api)
- [错误处理](#错误处理)
- [响应格式](#响应格式)

## 基础接口

### 服务状态

**GET** `/`

获取服务基本状态信息。

**响应示例：**
```json
{
  "message": "Flask API服务运行中",
  "version": "1.0.0",
  "databases": ["PostgreSQL", "Redis", "MySQL"]
}
```

### 健康检查

**GET** `/api/health`

检查服务健康状态，包括数据库连接状态。

**响应示例：**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "services": {
    "postgresql": "healthy",
    "redis": "healthy"
  }
}
```

### Redis连接测试

**GET** `/api/redis/test`

测试Redis连接和基本操作。

**响应示例：**
```json
{
  "success": true,
  "message": "Redis连接正常",
  "test_results": {
    "string_operation": "Hello Redis!",
    "list_operation": ["item1", "item2", "item3"],
    "hash_operation": {
      "field1": "value1",
      "field2": "value2"
    }
  }
}
```

## 用户管理API

### 获取用户列表

**GET** `/api/users`

获取用户列表，支持分页和搜索。

**查询参数：**
- `page` (int, 可选): 页码，默认1
- `per_page` (int, 可选): 每页数量，默认10
- `search` (string, 可选): 搜索关键词

**响应示例：**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "full_name": "管理员",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 1,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### 创建用户

**POST** `/api/users`

创建新用户。

**请求体：**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "full_name": "新用户",
  "is_active": true
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "username": "newuser",
    "email": "newuser@example.com",
    "full_name": "新用户",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "message": "用户创建成功"
}
```

### 获取用户详情

**GET** `/api/users/{id}`

获取指定用户的详细信息。

**路径参数：**
- `id` (int): 用户ID

**响应示例：**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "管理员",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "from_cache": false
}
```

### 更新用户信息

**PUT** `/api/users/{id}`

更新用户信息。

**路径参数：**
- `id` (int): 用户ID

**请求体：**
```json
{
  "username": "updateduser",
  "email": "updated@example.com",
  "full_name": "更新用户",
  "is_active": false
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "updateduser",
    "email": "updated@example.com",
    "full_name": "更新用户",
    "is_active": false,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T12:00:00"
  },
  "message": "用户更新成功"
}
```

### 删除用户

**DELETE** `/api/users/{id}`

删除指定用户。

**路径参数：**
- `id` (int): 用户ID

**响应示例：**
```json
{
  "success": true,
  "message": "用户删除成功"
}
```

## 产品管理API

### 获取产品列表

**GET** `/api/products`

获取产品列表，支持分页、分类和搜索。

**查询参数：**
- `page` (int, 可选): 页码，默认1
- `per_page` (int, 可选): 每页数量，默认10
- `category` (string, 可选): 产品分类
- `search` (string, 可选): 搜索关键词

**响应示例：**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "笔记本电脑",
      "description": "高性能笔记本电脑",
      "price": "5999.99",
      "stock_quantity": 10,
      "category": "电子产品",
      "is_available": true,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 1,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### 创建产品

**POST** `/api/products`

创建新产品。

**请求体：**
```json
{
  "name": "新产品",
  "description": "产品描述",
  "price": 99.99,
  "stock_quantity": 50,
  "category": "分类",
  "is_available": true
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "新产品",
    "description": "产品描述",
    "price": "99.99",
    "stock_quantity": 50,
    "category": "分类",
    "is_available": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "message": "产品创建成功"
}
```

## 错误处理

### 错误响应格式

所有错误响应都遵循统一格式：

```json
{
  "success": false,
  "error": "错误描述信息"
}
```

### 常见错误码

- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `409 Conflict`: 资源冲突（如用户名已存在）
- `500 Internal Server Error`: 服务器内部错误

### 错误示例

**用户不存在：**
```json
{
  "success": false,
  "error": "用户不存在"
}
```

**用户名已存在：**
```json
{
  "success": false,
  "error": "用户名已存在"
}
```

## 响应格式

### 成功响应

所有成功响应都包含 `success: true` 字段：

```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

### 分页响应

列表接口支持分页，分页信息格式：

```json
{
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 100,
    "pages": 10,
    "has_next": true,
    "has_prev": false
  }
}
```

### 缓存信息

某些接口会返回缓存信息：

```json
{
  "from_cache": true
}
```
