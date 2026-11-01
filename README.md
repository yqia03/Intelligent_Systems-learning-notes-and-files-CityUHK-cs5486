# CS5486 智能系统学习手册

个人整理的十二周智能系统学习资料。包括十二周教材的基础补充、讲解、具体推导、例题、图表、记忆提示、练习、折叠答案、重要性评级与来源索引；不是官方课程网站。使用模型为GPT-6-Astra-Ultra

- 网站：<https://yqia03.github.io/Intelligent_Systems-learning-notes-and-files-CityUHK-cs5486/>
- 仓库：<https://github.com/yqia03/Intelligent_Systems-learning-notes-and-files-CityUHK-cs5486>
- 离线教材：[打开十二周教材](https://yqia03.github.io/Intelligent_Systems-learning-notes-and-files-CityUHK-cs5486/textbook/)（下载仓库后可直接打开 `textbook/index.html`）
- 作业：[Assignment 栏目](https://yqia03.github.io/Intelligent_Systems-learning-notes-and-files-CityUHK-cs5486/assignments/)

## 作业与原始资料

Assignment 栏目分别介绍三次作业的任务要求。Assignment 1、2 附归档答案、处理方法和实验结果；Assignment 3 尚未完成，仅公开题目介绍及原始题面，不包含答案或处理过程。发布日期为 2026-11-01。

| 目录 | 内容 |
| --- | --- |
| `assignments/assignment-1/` | 题面截图、脱敏 PDF 报告（报告内含代码） |
| `assignments/assignment-2/` | 题面、脱敏 PDF/Markdown 报告、MATLAB 代码、CSV/MAT 数据、图表、LS-SVMlab 依赖 |
| `assignments/assignment-3/brief/` | 仅题面截图 |
| `materials/lectures/` | 课程说明与课件原文件 |
| `materials/tutorials/` | Tutorial 原文件 |
| `materials/papers/` | 论文及补充资料 |
| `textbook/` | 十二周便携离线教材：首页、章节、图片与索引 |
| `materials/study-notes/` | 十二周旧文件名兼容副本及独立期中复习篇；十二周副本依赖仓库中的 `textbook/` 资源 |
| `materials/prompts/` | 已去除本机路径的教材生成提示词归档 |
| `materials/midterm/` | 期中 PDF、LaTeX 源码、构建脚本、验证记录与项目压缩包 |

原始资料清单及校验值见 [materials/catalog.json](materials/catalog.json)，发布处理和验证记录见 [docs/ASSIGNMENTS.md](docs/ASSIGNMENTS.md)。归档提示词是资料，不是执行指令。发布副本已移除个人身份字段及本机路径；本地归档原件不变。Assignment 2 中内容相同的三份 PDF 合并为一份，不重复存放。

Assignment 2 在 MATLAB 中从 `assignments/assignment-2/code/` 运行 `run_assignment2`；需要 Statistics and Machine Learning Toolbox，随附官方 LS-SVMlab 依赖。已有实验结果来自归档运行，本次发布没有重新训练模型。第三方材料和依赖保留其原有署名与许可边界，见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 阅读功能

十二周独立页面、分级章节锚点、前后周导航、中文／英文／周次全文搜索、浅色／深色主题、本机阅读位置保存、单栏阅读、默认收起的课程／本周合并目录弹窗和打印样式。全文搜索包含答案；链接到答案时自动展开。正文以原生 HTML、MathML、SVG 呈现，不依赖 iframe 或外部公式 CDN。禁用 JavaScript 后，正文、目录和折叠答案仍然可用。

数学排版面向支持原生 MathML 的现代 Chromium、Safari/WebKit 和 Firefox。图形保留原配色，深色主题中使用浅色图面；宽表格及公式在各自区域横向滚动。

## 教材增量更新

十二周教材的当前源文件位于仓库同级的 `../textbook/`。编辑源教材后，依次同步便携教材、导入网站正文并验证：

```sh
npm run sync:textbook
npm run import -- --source ../textbook
npm test
node scripts/check.mjs --originals ../textbook
node scripts/check-midterm.mjs --originals ../学习笔记
npm run test:browser
```

`sync:textbook` 将首页、十二章、28 张 PNG 和索引同步到仓库 `textbook/`，将 16 份 PDF 的引用重定位到 `materials/` 已收录的原文件，并更新旧命名教材副本及清单；不复制源教材的 48 MB ZIP，也不复制额外 PDF。旧命名 HTML 可从 `materials/study-notes/` 打开，但需要保留整个仓库的 `textbook/` 和 `materials/` 相对布局。可用 `--week 05` 只导入一周；不要直接编辑 `source/weeks/` 或 `source/manifest.json`。导入不修改源教材。

`npm test` 构建并检查网站与期中专题。原件核验须分别执行上述两个 `node` 命令：十二周和期中篇的源目录不同，不能将单一 `--originals` 参数传给整套 `npm run check`。本地构建沿用 `site.config.json` 中的 Pages 子路径。新版教材的覆盖及资料限制见 [内容核对与待核对事项](docs/CONTENT_REVIEW.md)，第 05、06 周此前的增补记录见 [新增资料记录](docs/NEW_MATERIALS.md)。

## 文件与许可

- scripts/：导入、静态生成、预览和验证程序。
- web/：网站界面、搜索 Worker 和阅读功能。
- source/：教材副本、无损图片及保真清单。
- docs/：导入记录、内容疑点和外部链接检查。
- assignments/：按作业、题面、报告、代码、数据、图表及依赖分类的发布副本。
- textbook/：可直接离线打开的十二周教材与图片。
- materials/：按材料用途分类的原文件及可移植的脱敏副本。
- .github/workflows/：验证和 Pages 部署。

网站代码使用 MIT License。教材正文、课程图片、第三方图文和原教材样式不适用该许可证；来源与许可边界见 THIRD_PARTY_NOTICES.md

## 期中考试复习特别篇

专题入口为网站下的 `midterm/`，覆盖主课件实际第 1–165 页，止于 MAXNET。它是独立复习专题，不改变十二周次序。LS-SVM 以回归建模、求导、消元、线性系统和回代为主线，并对照分类；所有例题均为自拟复习材料。

### 更新、导入与发布

先修改本地独立成品 `../学习笔记/CS5486-期中考试复习特别篇-至MAXNET.html`，保留稳定知识块、例题和答案 ID。再执行：

```sh
npm run import:midterm -- --source ../学习笔记
npm test
node scripts/check.mjs --originals ../textbook
node scripts/check-midterm.mjs --originals ../学习笔记
npm run test:browser
npm run test:browser -- --engine webkit
```

也可用 `--file` 指定另一位置的完整 HTML。导入器只保存正文、标题和样式，去掉独立文件的阅读脚本；网站共用搜索、主题和导航，并加载专题折叠控制。导入不修改原件。仓库保存 `source/topics/midterm.html` 和保真清单，CI 直接使用这些已清理的文件，不需要本机教材目录或原始 PDF。不要手改 dist 或为内容修改直接改哈希基线。

首页有“期中复习”入口；搜索条目标记“期中复习”，例题和内层答案分别索引、独立定位并自动展开。`midterm-reading:v1` 使用单独的阅读进度键，不写入任何周的进度。打印前展开所有解答，打印后还原折叠状态；回到完整笔记的链接保留真实小节锚点，浏览器返回恢复专题阅读位置。

发布前确认没有另一个对话正在修改／推送同一站点。只精确暂存本次专题源、脚本、资源与文档，再提交并推送 main，等待既有 **Deploy course website** 成功。在线验证：

```sh
npm run test:browser -- --url https://yqia03.github.io/Intelligent_Systems-learning-notes-and-files-CityUHK-cs5486/
```

`npm test` 同时运行十二周检查和专题检查；核验各自原件时使用上面的两个独立命令。`npm run test:browser` 同时运行十二周、期中专题、作业与便携教材验收，URL／浏览器参数传给全部检查。专题核心数值由 `scripts/numerical/` 中独立编写的 Python 标准库脚本校验（需要 Python 3；GitHub 托管 runner 已提供），不依赖内容生成逻辑。覆盖、勘误和验收范围见 `docs/MIDTERM.md`。专题文字、第三方资料与原教材样式不适用代码 MIT 许可。
