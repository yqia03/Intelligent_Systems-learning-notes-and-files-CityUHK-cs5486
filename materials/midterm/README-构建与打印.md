# CS5486 期中材料：构建与打印

版本日期：2026-10-22（Asia/Hong_Kong）。范围严格依据新课件 `CS5486a-2026.pdf` 的实际187页。

## 成品

- `CS5486-期中Cheatsheet-双面五栏.pdf`：恰好2页，297 × 210 mm（A4横向），每页5栏，共10栏。正文5.3pt、行距6.3pt，标题6.2–8pt；常规数学上下标指定4.5pt。没有整页缩放或正文栅格化。
- `CS5486-期中Cheatsheet-配套例题与解析.pdf`：61页，210 × 297 mm（A4纵向），正文按LaTeX的11pt档（实际常规西文字号约10.91 PDF pt），56题；每题独立一页。第1页使用说明，第2–4页目录，第5–55页Q01–Q51，第56页混合自测题目，第57–61页Q52–Q56解析。57个PDF书签，包括56道题及混合自测。
- `内容覆盖与验证说明.md`：新课件187页逐页覆盖表、范围、纠错与验收记录。

所有题均为自拟复习题。教师消息来自用户提供，不作为题型比例或命题概率证据。“最高／最大”所指不明，未将全部模型改写成最大化。

## Cheatsheet 本次修改

知识点、定义、比较和条件统一使用英文完整短句，可直接组织为答卷答案。所有不用于写入试卷答案的说明均用中文，包括查找导航、Calculate/Forward/Check步骤、微例题设和代入说明、计算防错提醒；可直接作答的知识句保持英文。计算保留已知量、代入、更新或消元、答案和检查；删除所有配套题号、详解指向及外部例题引用，考试时可独立查用。30个知识块编号及十栏位置保持不变，复习例题册未改动。

## 项目文件

- `cheatsheet/main.tex`、`preamble.tex`、`front.tex`、`back.tex`：两页速查表；十个栏位由独立minipage明确安排。
- `practice/main.tex`、`preamble.tex`、`sections/*.tex`：使用说明、目录及56道配套练习。
- `common.tex`：共享数学宏与配色。
- `build.sh`：从源文件编译并复制两份成品。
- `validation/verify_calculations.py`、`calculation-results.json`：独立数值核验及结果。
- `validation/audit_outputs.py`、`pdf-audit.json`：PDF尺寸、字体嵌入、编号、页面、打印白边等检查。
- `validation/coverage.json`、`visual-review.json`：覆盖映射与人工视觉检查记录。
- `validation/language-revision.json`：本次语言调整前后531个数学片段核对，公式及数字未变。
- `validation/cheatsheet-rebuild.json`：解压源码包后独立重编译，核对两页文本与渲染像素相同。

唯一示意图为源码中的TikZ矢量SVM间隔图，无需外部图片；无需额外`assets/`图片文件。所有资源引用均相对项目目录；原课件和参考PDF只作为范围/版式依据，不是编译依赖，也不复制到项目包。

## 重复编译

安装含XeLaTeX、ctex、Fandol字体、AMS数学、TikZ、hyperref等常用宏包的TeX Live 2026或MacTeX（本次使用TeX Live 2026/Homebrew）。中文采用TeX Live附带的FandolSong Regular/Bold（部分默认标题或强调样式可能用FandolKai）；西文Latin Modern，数学Computer Modern/AMS。均已在成品中子集嵌入，不依赖收件设备安装字体。

在此项目目录执行：

```bash
bash build.sh
```

脚本每份文档运行XeLaTeX三遍，解决目录、书签、总页数引用。默认中间文件在`.build/`，两份成品保存在项目根目录。可通过绝对路径指定其他中间目录：

```bash
BUILD_DIR=/absolute/path/to/build bash build.sh
```

不要只打开`front.tex`编译；入口为两个`main.tex`。不要缩放整页，也不要在PDF打印对话框再次缩小字体。

## 重新核验与渲染

数值核验依赖Python 3与NumPy；PDF审核/渲染另需PyMuPDF：

```bash
python3 validation/verify_calculations.py
python3 validation/audit_outputs.py
python3 validation/audit_outputs.py --render-dir .build/qa
```

脚本失败会返回非零退出码。数学验证不解析LaTeX答案来生成“计算结果”，而使用单独的前向损失有限差分、直接原始最小二乘、网格搜索与KKT等方式检验手算。自动检查不能替代视觉检查；改动排版后应重新看所有受影响页，尤其长公式、数学脚标、负号和增广矩阵竖线。

本机附带的Poppler缺少Adobe-GB1 CMap，渲染中文可能产生假性缺字；最终检查使用系统Python的PyMuPDF/MuPDF，中文和嵌入字体正常。这是渲染环境限制，不是PDF缺字。可用其他支持嵌入中文字体的标准PDF阅读器查看。

## 打印

速查表：**A4、横向、彩色、双面、100%实际大小**，关闭“适应纸张／缩放”。通常选择**短边翻转**；在打印机预览核对背面文字与正面阅读方向一致。PDF本身未镜像、未旋转背面。两面白底、深正文、编号和文字均可辨；颜色不是唯一检索标识。

名义页边距6mm；最终渲染墨迹测量左约6.0mm、右约6.1mm、上约7.3mm，底部正面约15.9mm、背面约11.9mm。普通打印机可打印区域有差异，须以实际设备预览为准。

配套册：A4纵向、100%实际大小；可双面长边翻转。正文使用正常阅读字号，不沿用速查表小字。

没有实物打印设备，本次未进行实机打印测试。96dpi整体及300dpi栏位检查属于屏幕渲染验收；5.3pt速查表仍是小字号，应先预览或试印一张确认个人阅读舒适度。
