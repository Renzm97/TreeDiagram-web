from typing import Dict, List, Tuple
from app.models import TreeNode, RelationType
import json
import os

class TreeDiagramGenerator:
    def __init__(self):
        self.node_width = 120      # 节点宽度（像素）
        self.node_height = 60      # 节点高度（像素）
        self.level_height = 150    # 层级之间的垂直间距（像素）
        self.node_spacing = 10     # 同级节点之间的水平间距（像素）
        
    def calculate_tree_layout(self, node: TreeNode, level: int = 0) -> Dict:
        """计算树形图的布局"""
        if not node.children:
            return {
                'node': node,
                'level': level,
                'width': 1,
                'children': []
            }
        
        children_layouts = []
        total_width = 0
        
        for child in node.children:
            child_layout = self.calculate_tree_layout(child, level + 1)
            children_layouts.append(child_layout)
            total_width += child_layout['width']
        
        return {
            'node': node,
            'level': level,
            'width': max(1, total_width),
            'children': children_layouts
        }
    
    def assign_positions(self, layout: Dict, start_x: float = 0) -> Dict:
        """为每个节点分配x, y坐标"""
        y = layout['level'] * self.level_height + 50
        
        if not layout['children']:
            # 叶子节点
            x = start_x + self.node_width / 2
            layout['x'] = x
            layout['y'] = y
            return layout
        
        # 计算子节点位置
        current_x = start_x
        for child_layout in layout['children']:
            child_width = child_layout['width'] * (self.node_width + self.node_spacing)
            self.assign_positions(child_layout, current_x)
            current_x += child_width
        
        # 父节点位置居中
        first_child_x = layout['children'][0]['x']
        last_child_x = layout['children'][-1]['x']
        layout['x'] = (first_child_x + last_child_x) / 2
        layout['y'] = y
        
        # 为有关系类型的节点计算关系节点位置
        if layout['node'].relation_type and layout['children']:
            relation_y = y + self.level_height / 5 * 2
            layout['relation_x'] = layout['x']
            layout['relation_y'] = relation_y
        
        return layout
    
    def generate_svg(self, layout: Dict) -> str:
        """生成SVG图形"""
        svg_content = []
        
        # 计算SVG尺寸
        max_x = self._get_max_x(layout) + 100
        max_y = self._get_max_y(layout) + 100
        
        # 使用viewBox属性使SVG可以自适应缩放
        svg_content.append(f'<svg width="100%" height="100%" viewBox="0 0 {max_x} {max_y}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">')
        
        # 添加样式
        svg_content.append('''
        <defs>
            <style>
                .node-rect {
                    fill: #4A90E2;
                    stroke: #2E5A8A;
                    stroke-width: 2;
                    rx: 5;
                }
                .node-circle {
                    fill: #4A90E2;
                    stroke: #2E5A8A;
                    stroke-width: 2;
                }
                .node-text {
                    fill: white;
                    font-family: Arial, sans-serif;
                    font-size: 12px;
                    text-anchor: middle;
                    dominant-baseline: middle;
                }
                .connection-line {
                    stroke: #333;
                    stroke-width: 2;
                    fill: none;
                }
                .relation-text {
                     fill: #333;
                     font-family: Arial, sans-serif;
                     font-size: 12px;
                     font-weight: bold;
                     text-anchor: middle;
                     dominant-baseline: middle;
                 }
                 .relation-bg {
                     fill: #F5F5F5;
                     stroke: #4A90E2;
                     stroke-width: 2;
                 }
            </style>
        </defs>
        ''')
        
        # 绘制连接线和关系标识
        self._draw_connections(layout, svg_content)
        
        # 绘制节点
        self._draw_nodes(layout, svg_content)
        
        svg_content.append('</svg>')
        
        return '\n'.join(svg_content)
    
    def _get_max_x(self, layout: Dict) -> float:
        max_x = layout['x'] + self.node_width / 2
        for child in layout.get('children', []):
            child_max_x = self._get_max_x(child)
            max_x = max(max_x, child_max_x)
        return max_x
    
    def _get_max_y(self, layout: Dict) -> float:
        max_y = layout['y'] + self.node_height
        for child in layout.get('children', []):
            child_max_y = self._get_max_y(child)
            max_y = max(max_y, child_max_y)
        return max_y
    
    def _draw_connections(self, layout: Dict, svg_content: List[str]):
        """绘制连接线和关系标识"""
        if not layout.get('children'):
            return
        
        parent_x = layout['x']
        parent_y = layout['y'] + self.node_height / 2
        
        # 如果有关系类型，先绘制关系节点
        if layout['node'].relation_type and 'relation_x' in layout:
            relation_x = layout['relation_x']
            relation_y = layout['relation_y']
            relation_text = layout['node'].relation_type.value.upper()
            
            # 从父节点到关系节点的连接线（垂直向下）
            svg_content.append(f'<line x1="{parent_x}" y1="{parent_y}" x2="{relation_x}" y2="{relation_y - 15}" class="connection-line"/>')
            
            # 绘制关系节点（圆形背景）
            svg_content.append(f'<circle cx="{relation_x}" cy="{relation_y}" r="15" class="relation-bg"/>')
            # 关系标识文字
            svg_content.append(f'<text x="{relation_x}" y="{relation_y}" class="relation-text">{relation_text}</text>')
            
            # 从关系节点到各个子节点的折线连接
            middle_y = relation_y + 30  # 中间水平线的y坐标
            
            # 1. 从关系节点垂直向下到中间水平线（只绘制一次）
            svg_content.append(f'<line x1="{relation_x}" y1="{relation_y + 15}" x2="{relation_x}" y2="{middle_y}" class="connection-line"/>')
            
            for child_layout in layout['children']:
                child_x = child_layout['x']
                child_y = child_layout['y'] - self.node_height / 2
                
                # 2. 从中间水平线水平连接到子节点x坐标
                svg_content.append(f'<line x1="{relation_x}" y1="{middle_y}" x2="{child_x}" y2="{middle_y}" class="connection-line"/>')
                # 3. 从中间水平线垂直向上连接到子节点
                svg_content.append(f'<line x1="{child_x}" y1="{middle_y}" x2="{child_x}" y2="{child_y}" class="connection-line"/>')
        else:
            # 没有关系类型时，直接连接父子节点
            for child_layout in layout['children']:
                child_x = child_layout['x']
                child_y = child_layout['y'] - self.node_height / 2
                
                # 直接从父节点到子节点的连接线
                svg_content.append(f'<line x1="{parent_x}" y1="{parent_y}" x2="{child_x}" y2="{child_y}" class="connection-line"/>')
        
        # 递归绘制子节点的连接线
        for child_layout in layout['children']:
            self._draw_connections(child_layout, svg_content)
    
    def _draw_nodes(self, layout: Dict, svg_content: List[str]):
        """绘制节点"""
        x = layout['x']
        y = layout['y']
        node = layout['node']
        
        # 处理文本换行
        lines = self._wrap_text(node.name, 10)
        
        if node.is_leaf or not node.children:
            # 叶子节点 - 圆形
            # radius = min(self.node_width, self.node_height) / 2 - 5
            radius = 50
            svg_content.append(f'<circle cx="{x}" cy="{y}" r="{radius}" class="node-circle"/>')
        else:
            # 非叶子节点 - 矩形
            rect_x = x - self.node_width / 2
            rect_y = y - self.node_height / 2
            svg_content.append(f'<rect x="{rect_x}" y="{rect_y}" width="{self.node_width}" height="{self.node_height}" class="node-rect"/>')
        
        # 绘制文本
        if len(lines) == 1:
            svg_content.append(f'<text x="{x}" y="{y}" class="node-text">{lines[0]}</text>')
        else:
            line_height = 14
            start_y = y - (len(lines) - 1) * line_height / 2
            for i, line in enumerate(lines):
                text_y = start_y + i * line_height
                svg_content.append(f'<text x="{x}" y="{text_y}" class="node-text">{line}</text>')
        
        # 递归绘制子节点
        for child_layout in layout.get('children', []):
            self._draw_nodes(child_layout, svg_content)
    
    def _wrap_text(self, text: str, max_chars: int) -> List[str]:
        """文本换行处理"""
        if len(text) <= max_chars:
            return [text]
        
        lines = []
        current_line = ""
        
        for char in text:
            if len(current_line) >= max_chars and char in [' ', '，', '。', '、']:
                lines.append(current_line)
                current_line = ""
            else:
                current_line += char
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def generate_html(self, tree_data: TreeNode) -> str:
        """生成完整的HTML页面"""
        layout = self.calculate_tree_layout(tree_data)
        layout = self.assign_positions(layout)
        svg_content = self.generate_svg(layout)
        
        # HTML模板部分
        html_head = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>树形图</title>
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            height: 100%;
            overflow: hidden;
        }}
        body {{
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }}
        .container {{
            flex: 1;
            display: flex;
            flex-direction: column;
            width: 95%;
            margin: 10px auto;
            background: white;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            text-align: center;
            margin-bottom: 10px;
        }}
        .header h1 {{
            margin: 0;
            padding: 5px 0;
        }}
        .diagram-container {{
            flex: 1;
            text-align: center;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 5px;
            background: white;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .diagram-container svg {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}
        .controls {{
            margin: 10px 0;
            text-align: center;
        }}
        button {{
            background: #4A90E2;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            margin: 0 5px;
        }}
        button:hover {{
            background: #357ABD;
        }}
        .zoom-controls {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>树形图</h1>
        </div>
        <div class="controls">
            <button onclick="downloadImage()">保存为JPG</button>
            <button onclick="downloadSVG()">保存为SVG</button>
            <div class="zoom-controls">
                <button onclick="zoomIn()">放大</button>
                <button onclick="zoomOut()">缩小</button>
                <button onclick="resetZoom()">重置</button>
            </div>
        </div>
        <div class="diagram-container" id="diagram">
            {svg_content}
        </div>
    </div>
'''

        # JavaScript部分，使用普通字符串避免f-string的问题
        js_script = '''
    <script>
        /* 缩放与拖动相关变量和函数 */
        let currentZoom = 1;
        const zoomFactor = 0.1;
        const svgElement = document.querySelector('svg');
        const diagramContainer = document.getElementById('diagram');
        
        /* 拖动相关变量 */
        let isDragging = false;
        let startX, startY;
        let translateX = 0;
        let translateY = 0;
        
        /* 初始化拖动事件监听 */
        diagramContainer.addEventListener('mousedown', startDrag);
        diagramContainer.addEventListener('mousemove', drag);
        diagramContainer.addEventListener('mouseup', endDrag);
        diagramContainer.addEventListener('mouseleave', endDrag);
        
        /* 触摸设备支持 */
        diagramContainer.addEventListener('touchstart', handleTouchStart);
        diagramContainer.addEventListener('touchmove', handleTouchMove);
        diagramContainer.addEventListener('touchend', handleTouchEnd);
        
        function handleTouchStart(e) {
            const touch = e.touches[0];
            startDrag({clientX: touch.clientX, clientY: touch.clientY});
            e.preventDefault();
        }
        
        function handleTouchMove(e) {
            if (isDragging) {
                const touch = e.touches[0];
                drag({clientX: touch.clientX, clientY: touch.clientY});
                e.preventDefault();
            }
        }
        
        function handleTouchEnd() {
            endDrag();
        }
        
        function startDrag(e) {
            /* 只有在放大状态下才能拖动 */
            if (currentZoom <= 1) return;
            
            isDragging = true;
            startX = e.clientX - translateX;
            startY = e.clientY - translateY;
            diagramContainer.style.cursor = 'grabbing';
        }
        
        function drag(e) {
            if (!isDragging) return;
            
            translateX = e.clientX - startX;
            translateY = e.clientY - startY;
            applyTransform();
        }
        
        function endDrag() {
            isDragging = false;
            diagramContainer.style.cursor = 'grab';
        }
        
        function zoomIn() {
            currentZoom += zoomFactor;
            applyTransform();
            updateCursor();
        }
        
        function zoomOut() {
            currentZoom = Math.max(0.1, currentZoom - zoomFactor);
            translateX = translateY = 0; /* 缩小时重置位置 */
            applyTransform();
            updateCursor();
        }
        
        function resetZoom() {
            currentZoom = 1;
            translateX = translateY = 0;
            applyTransform();
            updateCursor();
        }
        
        function updateCursor() {
            diagramContainer.style.cursor = currentZoom > 1 ? 'grab' : 'default';
        }
        
        function applyTransform() {
            /* 应用缩放和平移变换 */
            svgElement.style.transform = `scale(${currentZoom}) translate(${translateX / currentZoom}px, ${translateY / currentZoom}px)`;
            svgElement.style.transformOrigin = 'center center';
        }

        function downloadSVG() {
            const svg = document.querySelector('svg');
            const svgData = new XMLSerializer().serializeToString(svg);
            const svgBlob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
            const url = URL.createObjectURL(svgBlob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = 'tree_diagram.svg';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }
        
        function downloadImage() {
            const svg = document.querySelector('svg');
            const svgData = new XMLSerializer().serializeToString(svg);
            
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            /* 获取SVG的viewBox尺寸 */
            const viewBox = svg.getAttribute('viewBox').split(' ');
            const width = parseFloat(viewBox[2]);
            const height = parseFloat(viewBox[3]);
            
            canvas.width = width;
            canvas.height = height;
            
            img.onload = function() {
                ctx.fillStyle = 'white';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0, width, height);
                
                canvas.toBlob(function(blob) {
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = 'tree_diagram.jpg';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    URL.revokeObjectURL(url);
                }, 'image/jpeg', 0.95);
            };
            
            img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
        }
        
        /* 初始化页面时设置默认状态 */
        updateCursor();
    </script>
</body>
</html>
'''
        
        # 组合HTML和JavaScript
        return html_head + js_script 