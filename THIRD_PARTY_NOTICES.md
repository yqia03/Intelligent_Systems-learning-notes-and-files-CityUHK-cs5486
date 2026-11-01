# 教材及第三方内容说明

本站是个人整理的 CS5486 智能系统学习资料，不是官方课程网站。十二周是依照学习依赖整理的阅读顺序，不代表官方授课周历。

## 许可范围

MIT License 仅适用于新编写的网站代码（scripts/、web/）、构建和部署配置及新增项目文档。下列内容不因收录在仓库中而变为 MIT 许可：

- source/weeks/ 中的教材正文、数学推导、练习、引用及原教材样式；
- source/assets/ 中从教材无损提取的原始图片；
- 构建输出中的教材内容、MathML、SVG、原教材共享样式与每周补充样式；
- textbook/ 中的便携教材、正文、样式和图片；
- materials/ 中的课程课件、Tutorial、论文、独立学习教材及其截图、图表、引文等内容；
- assignments/ 中的课程题面、个人报告及实验资料；第三方软件依赖遵循其自身条款。

教材及第三方内容的权利归相应作者或权利人所有。已知来源沿用各周正文、图注和来源索引的说明。原文件未给出明确再分发许可的部分，不在此宣称已取得该许可；来源说明与个人学习用途说明本身不构成授权。

## 主要资料来源

- Lecture_slides_full semester.pdf：主课件，按 PDF 实际页序定位。
- CS5486-2026.pdf：课程说明。
- Tutorial 1.pdf、Tutorial 2- M-P neuron.pdf、Perceptron_Adaline.pdf、Tutorial 7 - SVM and LS-SVM_1.pdf：课程辅助材料。
- TLU.pdf、ASSPM-Lippmann1987.pdf、Nature1986.pdf、CS-Broomhead-Lowe1988.pdf：原教材采用的补充材料及论文。
- 2026-10-15增量采用的SVR.pdf、SVR-tutorial.pdf（Smola / Schölkopf）、NPL-LS_SVM.pdf（Suykens / Vandewalle，1999）、LS-SVM-load.pdf（Espinoza等，2007）及Adaptive Resonance Theory.pdf：用于第05、06周核验和增补，采用范围见docs/NEW_MATERIALS.md；原PDF按类别收录于 materials/。
- 各周正文列出的原始论文、作者机构页面和官方软件文档：保留原外部链接，不将其内容整体镜像至本站。

2026-11-01 起，原始 PDF、独立 HTML 教材、生成提示词与期中资料按用途收录于 materials/，文件清单见 materials/catalog.json；含本机路径的文件使用脱敏发布副本。收录不改变原文件的著作权与许可。教材中的 28 张 PNG 按内容哈希原样复制，无重新编码；具体文件、SHA-256、尺寸及原有替代文本见 source/manifest.json。每张图片的归属、课件页码和说明继续保留在正文邻近图注及来源段落。

新编写的网站不增添无来源教学结论。原教材中的“教学补充”“经核实的纠正”“资料限制”等标记均予以保留。

## 软件依赖

parse5、PostCSS、Playwright 及其传递依赖按各自的软件许可证使用。具体版本由 package-lock.json 锁定；安装包内保留其 LICENSE。它们的许可不替代教材和课程资料的内容许可。

Assignment 2 随附归档使用的 LS-SVMlab 1.8 工具箱（KU Leuven），保留原始压缩包和解压后的源文件及其中署名、引用与使用说明。上游来源为 <https://www.esat.kuleuven.be/sista/lssvmlab/>。工具箱不适用本站的 MIT License；模型比较结果来自个人归档实验，不代表工具箱作者或课程方的评测结论。

如对内容归属、授权范围或错误有反馈，请在本仓库提交 Issue，并附相应周次、小节或图片及可核对依据。

## 期中考试复习专题

`source/topics/midterm.html` 是独立复习资料，包含原创重述、自拟例题和教学示意图，以及对课程资料与论文的来源定位。它与十二周教材正文、原教材样式一样，不适用网站程序的 MIT 许可；引用的第三方内容权利仍归原权利人所有。配套 PDF 与 LaTeX 源文件收录于 materials/midterm/。专题代码（导入、构建、搜索、折叠控制与验证脚本）适用代码许可。
