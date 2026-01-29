# FaceFusion 二次开发记录

## 项目信息

- **项目名称**: FaceFusion
- **仓库地址**: https://github.com/kegeai888/facefusion
- **开发者**: 科哥 (kegeai888)
- **最后更新**: 2026-01-29

## 已完成的修改

### 1. 处理器名称汉化 (2026-01-29)

**问题**: 处理器选择框显示英文技术名称，不便于中文用户理解

**解决方案**:
- 在 `facefusion/locales.py` 中添加所有 11 个处理器的中英文翻译
- 修改 `facefusion/uis/components/processors.py` 实现翻译功能
- 使用 Gradio 元组格式 `[(显示名, 内部值)]` 实现 UI 显示中文，内部使用英文 ID

**涉及文件**:
- `facefusion/locales.py` - 添加翻译条目
- `facefusion/uis/components/processors.py` - 实现翻译逻辑

**处理器翻译对照表**:
| 英文 ID | 中文名称 |
|---------|---------|
| age_modifier | 年龄修改器 |
| background_remover | 背景移除器 |
| deep_swapper | 深度换脸器 |
| expression_restorer | 表情恢复器 |
| face_debugger | 人脸调试器 |
| face_editor | 人脸编辑器 |
| face_enhancer | 人脸增强器 |
| face_swapper | 换脸器 |
| frame_colorizer | 帧上色器 |
| frame_enhancer | 帧增强器 |
| lip_syncer | 唇形同步器 |

**技术要点**:
- Gradio CheckboxGroup 使用元组格式时，value 参数必须使用内部值
- 回调函数接收的是内部值，不需要再次转换
- 支持中英文切换，根据 `translator.CURRENT_LANGUAGE` 自动适配

**Git 提交**: `5bb09e6` - Add Chinese localization for processors and customize UI branding

---

### 2. 处理器选择框报错修复 (2026-01-29)

**问题**: 点击处理器选择框时页面报错

**原因分析**:
- 初始实现中错误地使用翻译后的名称作为 CheckboxGroup 的 value 参数
- 在 update_processors() 中不必要地调用 untranslate_processors()
- Gradio 元组格式 choices 返回的已经是内部值，不需要转换

**解决方案**:
- 修改 render() 函数，直接使用内部 ID 作为 value
- 移除 update_processors() 中的 untranslate_processors() 调用
- 简化代码逻辑，利用 Gradio 的自动转换机制

**关键代码修改**:
```python
# 修改前（错误）
processor_values = translate_processors(state_manager.get_item('processors'))
value = processor_values  # 错误！

# 修改后（正确）
value = state_manager.get_item('processors')  # 直接使用内部 ID
```

**经验教训**:
- 理解 UI 框架的工作机制很重要
- Gradio 元组格式会自动处理显示名称和值的映射
- 过度转换反而会导致问题

**涉及文件**:
- `facefusion/uis/components/processors.py`

---

### 3. UI 品牌定制 (2026-01-29)

**需求**: 定制页面图标和社区链接，指向自己的教程资源

**修改内容**:

#### 3.1 Favicon 图标更换
- 将所有 UI 布局的 favicon 从 `facefusion.ico` 改为 `favicon.png`
- 涉及 4 个布局文件：default.py, benchmark.py, jobs.py, webcam.py

**涉及文件**:
- `facefusion/uis/layouts/default.py`
- `facefusion/uis/layouts/benchmark.py`
- `facefusion/uis/layouts/jobs.py`
- `facefusion/uis/layouts/webcam.py`

#### 3.2 社区按钮文本和链接修改

页面底部三个随机显示的按钮全部修改为指向视频教程：

| 按钮 | 原文本 | 新文本 | 新链接 |
|------|--------|--------|--------|
| fund | 资助训练服务器 | 科哥汉化修改 点击获取视频教程->> | 飞书文档 |
| subscribe | 成为会员 | 科哥汉化修改 点击获取视频教程->> | 飞书文档 |
| join | 加入社区 | 科哥构建修改 点击获取视频教程->> | 飞书文档 |

**教程链接**: https://g1hzbw0p4dd.feishu.cn/docx/E1bBdyvUroOSh7x69EEc9AyDnDf?from=from_copylink

**涉及文件**:
- `facefusion/locales.py` - 修改按钮文本
- `facefusion/uis/components/about.py` - 修改链接地址

**Git 提交**:
- `5bb09e6` - Add Chinese localization for processors and customize UI branding
- `cf5f48c` - Update fund button to tutorial link
- `b90393e` - Update subscribe button to tutorial link

---

### 4. 配置文件优化 (2026-01-29)

**修改**: 设置默认遮挡模型为 xseg_3

**配置项**: `face_occluder_model = xseg_3`

**作用**:
- 提供更精确的人脸分割
- 改善边缘处理效果
- 适用于大多数换脸场景

**涉及文件**:
- `facefusion.ini`

**Git 提交**: `f9326eb` - Set default face occluder model to xseg_3

---

## 技术经验总结

### 1. Gradio UI 框架使用经验

**CheckboxGroup 元组格式**:
```python
# 正确用法
choices = [('显示名称', '内部值'), ...]
value = ['内部值1', '内部值2']  # 使用内部值，不是显示名称

# 回调函数接收的是内部值
def callback(selected_values):
    # selected_values 是内部值列表，如 ['face_swapper', 'face_enhancer']
    pass
```

**关键点**:
- choices 使用元组时，UI 显示第一个元素（label），但 value 使用第二个元素
- 回调函数接收的是内部值，不需要手动转换
- value 参数必须使用内部值，不能使用显示名称

### 2. 国际化 (i18n) 实现

**翻译系统架构**:
- `facefusion/locales.py` - 主翻译文件
- `facefusion/translator.py` - 翻译引擎
- `translator.CURRENT_LANGUAGE` - 当前语言设置（'zh' 或 'en'）

**翻译键命名规范**:
```python
# UI 组件翻译
'uis.component_name': '翻译文本'

# 帮助文本翻译
'help.option_name': '帮助文本'

# 关于页面翻译
'about.button_name': '按钮文本'
```

**最佳实践**:
- 保持中英文翻译键结构一致
- 使用有意义的键名，便于维护
- 翻译文本简洁明了，符合目标语言习惯

### 3. Git 提交规范

**提交信息格式**:
```
标题：简短描述（50 字符以内）

- 详细说明第一点
- 详细说明第二点
- 详细说明第三点

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**提交原则**:
- 每次提交只包含相关的修改
- 提交信息清晰描述修改内容和原因
- 使用英文编写提交信息（国际化项目）
- 分多次提交，便于回滚和追踪

### 4. 应用重启注意事项

**重启流程**:
```bash
# 1. 停止旧进程
pkill -9 -f "facefusion.py run"

# 2. 等待端口释放
sleep 3

# 3. 启动新进程
nohup ./start_app.sh > /root/facefusion/app.log 2>&1 &

# 4. 等待启动完成
sleep 20

# 5. 验证端口监听
lsof -i :7860
```

**注意事项**:
- 修改配置文件后需要重启应用
- 修改 Python 代码后需要重启应用
- 修改翻译文件后需要重启应用
- 确保端口完全释放后再启动

---

## 待优化项目

### 1. 按钮随机显示优化

**当前状态**: 三个按钮都指向同一个教程链接，但仍然随机显示

**优化建议**:
- 可以移除随机选择逻辑，固定显示一个按钮
- 或者为不同按钮设置不同的教程内容

**涉及文件**: `facefusion/uis/components/about.py`

### 2. 未使用的辅助函数清理

**当前状态**: `processors.py` 中的 `translate_processors()` 和 `untranslate_processors()` 函数未被使用

**优化建议**:
- 可以删除这两个函数，简化代码
- 或者保留作为备用，添加注释说明

**涉及文件**: `facefusion/uis/components/processors.py`

### 3. 更多 UI 元素汉化

**待汉化内容**:
- 各处理器的配置选项（模型选择、参数调整等）
- 错误提示信息
- 进度提示信息
- 帮助文本

**涉及文件**: 各处理器模块的 `locales.py` 文件

### 4. 配置文件完善

**待配置项**:
- 其他处理器的默认模型
- 默认输出质量参数
- 默认执行参数

**涉及文件**: `facefusion.ini`

---

## 问题排查记录

### 问题 1: 处理器选择框点击报错

**现象**: 点击处理器选择框时页面报错

**排查过程**:
1. 检查浏览器控制台 - 无明显错误
2. 检查应用日志 - 无错误信息
3. 测试 Gradio CheckboxGroup 行为 - 发现元组格式的工作机制
4. 分析代码逻辑 - 发现 value 参数使用错误

**解决方案**: 修改 value 参数使用内部 ID

**经验**:
- UI 框架的行为需要通过测试验证
- 不要假设框架的工作方式，要实际测试
- 查看官方文档和示例代码

### 问题 2: 翻译不生效

**现象**: 修改翻译文件后，UI 仍显示旧文本

**原因**: 应用未重启，仍使用缓存的翻译

**解决方案**: 重启应用加载新翻译

**经验**:
- Python 模块在导入后会被缓存
- 修改代码或配置后需要重启应用
- 可以使用热重载工具（如 watchdog）自动重启

---

## 开发环境信息

- **Python 版本**: 3.12
- **操作系统**: Linux (Ubuntu)
- **主要依赖**:
  - Gradio - Web UI 框架
  - ONNX Runtime - 模型推理引擎
  - TensorRT - GPU 加速
  - FFmpeg - 视频处理

---

## 参考资源

- **项目文档**: CLAUDE.md
- **启动指南**: STARTUP_GUIDE.md
- **用户手册**: 用户使用手册.md
- **视频教程**: https://g1hzbw0p4dd.feishu.cn/docx/E1bBdyvUroOSh7x69EEc9AyDnDf?from=from_copylink

---

## 更新日志

- 2026-01-29: 完成处理器汉化、UI 品牌定制、配置优化
- 2026-01-29: 创建开发记录文档

---

**维护者**: 科哥 (kegeai888@gmail.com)
