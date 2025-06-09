from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
from datetime import datetime

from app.models import TreeDiagramRequest, TreeDiagramResponse, TreeNode
from app.tree_generator import TreeDiagramGenerator

app = FastAPI(title="TreeDiagram API", version="1.0.0")

# 创建必要的目录
os.makedirs("workspace", exist_ok=True)
os.makedirs("web/static", exist_ok=True)
os.makedirs("web/templates", exist_ok=True)

# 静态文件和模板
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

# 树形图生成器
generator = TreeDiagramGenerator()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """主页面"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/generate-tree", response_model=TreeDiagramResponse)
async def generate_tree_diagram(request: TreeDiagramRequest):
    """生成树形图API"""
    try:
        # 生成HTML内容
        html_content = generator.generate_html(request.root_node)
        
        # 保存HTML文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tree_diagram_{timestamp}.html"
        filepath = os.path.join("workspace", filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return TreeDiagramResponse(
            success=True,
            message="树形图生成成功",
            image_path=filename
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成树形图时出错: {str(e)}")

@app.get("/api/tree-html/{filename}")
async def get_tree_html(filename: str):
    """获取生成的HTML文件"""
    try:
        filepath = os.path.join("workspace", filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        return HTMLResponse(content=content)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件时出错: {str(e)}")

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "OK", "message": "TreeDiagram API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 