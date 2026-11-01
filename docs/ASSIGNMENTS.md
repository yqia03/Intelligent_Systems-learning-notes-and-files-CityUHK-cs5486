# Assignment 栏目与资料发布记录

更新日期：2026-11-01（香港时间）。

## 发布范围

新增 `assignments/` 栏目及三次作业的独立介绍页，接入首页、全站导航、站点地图和全文搜索。题目中文导读以三张原题截图为准，个人处理说明以归档报告为准。

- Assignment 1：双极性感知机、ADALINE 的 OR/XOR 分类，以及 Sigmoid MLP、Gaussian RBF 的 XOR 分类。发布脱敏 PDF，保留原报告中的 Python 代码、图形和结论。归档中没有独立 notebook；PDF 原有部分 HTML 表格输出显示为 `IPython.core.display.HTML object` 占位文本，此次不补造原始结果。
- Assignment 2：双输入 `sin(x+y)` 回归、固定 Gaussian 核、100 个训练样本、SVR/LS-SVM 精度与速度比较。发布脱敏 PDF/Markdown、MATLAB 脚本、CSV/MAT、三张图及原始 LS-SVMlab ZIP 和展开源码。归档中三份 PDF 的字节完全相同，使用一份中性名称的报告去重。
- Assignment 3：只发布 MAXNET、kWTA、Hopfield 的任务介绍和题面。未发布答案、计算结果或个人处理过程；检查脚本强制其文件目录仅含题面截图。

其他原始材料按 `materials/lectures`、`tutorials`、`papers`、`study-notes`、`prompts`、`midterm` 分类，共 61 份材料。清单记录用途、相对来源、发布字节数、原文件与发布文件 SHA-256 及修改标记。系统文件、临时渲染产物、缓存、构建输出和本机私有原件不纳入提交。提示词只作为历史资料保存，不作为当前执行指令。

## 脱敏与完整性

所有变更作用于发布副本，本地归档原件保持不变。

1. 两份报告共九页，使用真正删除内容的 PDF redaction 移除姓名、EID、学号和身份标题；清除文档信息、XMP、附件、注释与链接。逐页渲染复核，并检查提取文字及解压对象流。除身份行和中性标题外，学术正文与原文一致。
2. Markdown 和 MATLAB 文件去除身份字段及个人绝对路径。脚本使用相对于自身的 `code`、`data`、`figures`、`solution`、`dependencies` 目录；后续生成报告同样不写入个人身份。
3. MAT v5 仅替换 provenance metadata 数据块并修正 subsystem offset；其余 39 个数据块，包括 MATLAB opaque 模型、table 及 workspace，保持字节一致。27 组可读取数值变量与原件一致，解压后的 UTF-8/UTF-16 内容通过个人标识和路径扫描。
4. 题面 PNG 去除 EXIF，保留图像数据；实验图移除非必要元数据。官方依赖 ZIP 与 82 个展开文件保持字节一致，保留第三方署名与说明。
5. 61 份材料中，18 份独立 PDF 均保持原字节。提示词、Week11 一处本机路径、期中验证记录及压缩包中的个人路径已去除；派生校验值同步更新。13 份独立 HTML 的 PDF 链接按新目录调整，2013 个本地链接和 1387 个锚点通过核对。包含 ZIP 内 PDF 的扫描覆盖 3279 个解压对象/字典。

## 验证与限制

`npm test` 检查教材保真、数学核验、站内链接、作业页面、搜索、下载资源、资料清单 SHA-256 和 Assignment 3 发布边界。`npm run test:browser` 验证桌面/移动端、主题、搜索、报告下载与无 JavaScript 阅读。检查结果以本次本地执行和对应 GitHub Actions 的结果为准。

本次本地验收全部通过：21 个生成页面、3223 个站内链接、938 条搜索段落；Chromium 与 WebKit 各 113 个场景（原课程 92、期中专题 12、作业 9），没有页面错误、控制台错误或资源失败。独立数据核验还确认 CSV 误差、计时中位数与 MAT 数值一致，LS-SVM 直接线性系统预测与存档结果一致。

本次未重新执行 MATLAB 模型训练。当前本机 MATLAB 在启动时报告 Qt 处理器兼容性错误，因此脱敏 MAT 的 MATLAB 运行时重新载入尚未验证；已完成格式、偏移、数值及未修改块的字节核验。网站数值和计时明确引用原归档实验，不表示本次重新测量，也不作一般性能保证。

仓库已更名，`site.config.json` 同步采用 GitHub API 返回的当前仓库名和 Pages 子路径。资料发布沿用 `main` 的既有 **Deploy course website** 工作流。
