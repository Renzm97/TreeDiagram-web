# 树形图生成器 (TreeDiagram Web)

一个基于FastAPI和现代前端技术的树形图自动生成工具，支持将结构化数据转换为美观的树形图并导出为JPG/SVG格式。

## 功能特点

- 🌳 **自动树形图生成**: 根据结构化JSON数据自动生成树形图
- 🎨 **美观的UI设计**: 蓝色方形节点（非叶子节点）和圆形节点（叶子节点）
- 🔗 **关系标识**: 支持AND/OR关系连接标识
- 📱 **响应式设计**: 适配不同屏幕尺寸
- 💾 **多格式导出**: 支持JPG和SVG格式保存
- 🚀 **实时预览**: 在浏览器中实时查看生成的树形图
- 🧪 **完整测试**: 包含单元测试和API测试

## 项目结构

```
TreeDiagram-web/
├── app/                    # 后端代码
│   ├── __init__.py
│   ├── main.py            # FastAPI主应用
│   ├── models.py          # 数据模型
│   └── tree_generator.py  # 树形图生成器
├── web/                   # 前端代码
│   └── templates/
│       └── index.html     # 主页面模板
├── workspace/             # 生成的图片保存目录
├── requirements.txt       # 依赖包
├── run_api.py            # 程序入口
└── README.md             # 项目说明
```

## 快速开始

### 1. 创建虚拟环境和安装依赖

```bash
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
```

### 2. 启动服务

```bash
python run_api.py
```

服务将在 `http://127.0.0.1:8000` 启动。

### 3. 访问应用

在浏览器中打开 `http://127.0.0.1:8000`，即可看到树形图生成器界面。

## 数据格式

### JSON数据结构

```json
{
  "name": "节点名称",
  "children": [
    {
      "name": "子节点1"
    },
    {
      "name": "子节点2",
      "children": [...],
      "relation_type": "and"
    }
  ],
  "relation_type": "or"
}
```

### 字段说明

- `name`: 节点显示名称（必填）
- `children`: 子节点数组（可选，如果为空则自动判定为叶子节点）
- `relation_type`: 关系类型，可选值："and"、"or"


### 示例数据

```json
{
  "name": "智能运营界面",
  "children": [
    {
      "name": "数据界面",
      "children": [
        {
          "name": "数据统计"
        },
        {
          "name": "分析报告"
        }
      ],
      "relation_type": "and"
    },
    {
      "name": "机器连接界面",
      "children": [
        {
          "name": "连接状态"
        },
        {
          "name": "设备监控"
        }
      ],
      "relation_type": "or"
    }
  ],
  "relation_type": "or"
}
```

## API接口

### 生成树形图

**POST** `/api/generate-tree`

请求体：
```json
{
  "root_node": {
    "name": "根节点",
    "children": [...],
    "relation_type": "or"
  }
}
```

响应：
```json
{
  "success": true,
  "message": "树形图生成成功",
  "image_path": "tree_diagram_20231201_143022.html"
}
```

### 获取生成的HTML

**GET** `/api/tree-html/{filename}`

### 健康检查

**GET** `/api/health`

## 运行测试

### 运行所有测试

```bash
# API测试
python test/test_api.py

# 单元测试
python test/test_tree_generator.py
```

### 使用pytest运行测试

```bash
pip install pytest
pytest test/
```

## 技术栈

### 后端
- **FastAPI**: 现代Python Web框架
- **Pydantic**: 数据验证和设置管理
- **Uvicorn**: ASGI服务器

### 前端
- **HTML5/CSS3**: 现代Web标准
- **JavaScript**: 原生JS，无需框架依赖
- **SVG**: 矢量图形生成

### 其他
- **Jinja2**: 模板引擎
- **pytest**: 测试框架

## 特性说明

### 1. 节点样式
- **非叶子节点**: 蓝色圆角矩形
- **叶子节点**: 蓝色圆形
- **文本**: 白色字体，支持自动换行

### 2. 连接线
- **样式**: 直角连接线
- **关系标识**: AND/OR标识显示在连接线上

### 3. 自动布局
- **层级布局**: 自动计算节点层级
- **居中对齐**: 父节点自动居中于子节点
- **间距控制**: 合理的节点间距

### 4. 导出功能
- **JPG格式**: 高质量图片导出
- **SVG格式**: 矢量图形导出
- **浏览器下载**: 直接在浏览器中下载

### 5. 响应式设计
- **移动端适配**: 支持手机和平板访问
- **自适应布局**: 根据屏幕尺寸调整布局

## 部署建议

### 开发环境
```bash
python run_api.py
```

### 生产环境
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。详情请参阅 `LICENSE` 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 邮件: your-email@example.com

---

**注意**: 生成的图片文件保存在 `workspace/` 目录中，请确保该目录有写入权限。 
