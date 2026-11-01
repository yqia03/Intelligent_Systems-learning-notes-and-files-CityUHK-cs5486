import { root, read, json, write, all, attr, text, norm, esc, parse, fs, path } from './lib.mjs';

export async function buildAssignments({ shell, url, searchIndex, repository }) {
  const assignments = await json('source/assignments/assignments.json');
  await fs.cp(path.join(root, 'assignments'), path.join(root, 'dist/assignments/files'), { recursive: true });
  const route = a => `assignments/${a.id}/`;
  const fileURL = (a, file) => url(`assignments/files/${a.id}/${file}`);
  async function image(a, file, alt, caption, className = '') {
    const bytes = await fs.readFile(path.join(root, 'assignments', a.id, file));
    // All assignment brief and figure assets are PNGs. Explicit dimensions avoid
    // layout shifts; generated figures keep their original binary data.
    if (bytes.toString('hex', 0, 8) !== '89504e470d0a1a0a') throw new Error(`Expected PNG: ${file}`);
    return `<figure class="assignment-figure ${className}"><a href="${fileURL(a, file)}"><img src="${fileURL(a, file)}" width="${bytes.readUInt32BE(16)}" height="${bytes.readUInt32BE(20)}" alt="${esc(alt)}" loading="lazy"></a><figcaption>${esc(caption)} · <a href="${fileURL(a, file)}">查看原图</a></figcaption></figure>`;
  }
  function index(body, a) {
    const doc = parse(body);
    let current = { anchor: 'page-title', title: `Assignment ${a.number} · ${a.title}`, text: '' };
    const records = [current];
    function visit(node) {
      if (node.nodeName === '#text') { current.text += node.value; return; }
      if (/^h[2-3]$/.test(node.tagName || '')) { current = { anchor: attr(node, 'id'), title: norm(text(node)), text: '' }; records.push(current); }
      for (const child of node.childNodes || []) visit(child);
      if (/^(p|li|td|th|tr|h[1-6]|figcaption|dd|dt)$/.test(node.tagName || '')) current.text += ' ';
    }
    visit(doc);
    searchIndex.push(...records.map(r => ({ kind: 'assignment', label: `Assignment ${a.number}`, week: a.id, weekTitle: `Assignment ${a.number} 作业${a.number} ${a.title}`, title: r.title, breadcrumb: `作业 · Assignment ${a.number}`, href: url(route(a)) + '#' + r.anchor, text: norm(r.text) })).filter(r => r.text));
  }
  const cards = assignments.map(a => `<li><a class="assignment-card" href="${url(route(a))}"><span class="site-eyebrow">Assignment ${a.number}</span><h2>${esc(a.title)}</h2><p>${esc(a.summary)}</p><span class="assignment-card-status ${a.completed ? '' : 'assignment-status-pending'}">${esc(a.status)}</span><span class="assignment-card-meta">${esc(a.due)} 截止 · ${a.points} 分 <span aria-hidden="true">→</span></span></a></li>`).join('');
  await write('dist/assignments/index.html', shell({ title: '课程作业与个人解答', route: 'assignments/', body: `<div class="assignment-index"><header class="assignment-header"><p class="site-eyebrow">CS5486 · ASSIGNMENTS</p><h1>课程作业与个人解答</h1><p class="site-lead">按作业查看题目要求、原题截图与个人完成记录。</p><p>Assignment 1、2 已发布解答。Assignment 3 尚未完成，暂不发布处理过程。题目要求与个人报告结论分别标明，便于对照查阅。</p></header><ol class="assignment-card-grid">${cards}</ol><p class="assignment-source-note">原题截图属于课程材料；个人报告为学习记录，不代表官方标准答案。报告与代码的身份信息已移除。<a href="${url('about/')}">来源与许可说明</a></p></div>` }));
  for (const a of assignments) {
    const downloads = [...a.downloads];
    if (a.number === 2) downloads.push({ path: 'dependencies/LSSVMlabv1_8_R2009b_R2011a.zip', label: 'LS-SVMlab 1.8 依赖包', format: 'ZIP', note: '原始第三方依赖；许可与来源见包内文件及仓库说明。' });
    const requirements = `<section aria-labelledby="requirements"><h2 id="requirements">原题要求（中文整理）</h2><p>以下为原题内容的中文导读；细节与表述以原题截图为准。</p><ol>${a.requirements.map(s => `<li>${esc(s)}</li>`).join('')}</ol></section>`;
    const original = `<section aria-labelledby="original"><h2 id="original">原题截图</h2>${await image(a, `brief/${a.id}.png`, `Assignment ${a.number} 原题截图，包含课程布置的任务、截止时间与评分要求`, '原始作业题面；点击图片可单独查看', 'assignment-brief')}</section>`;
    const files = a.completed ? `<section aria-labelledby="downloads"><h2 id="downloads">报告与文件</h2><p><a href="https://github.com/${repository}/tree/main/assignments/${a.id}">在仓库查看完整作业目录</a>；也可克隆或下载整个仓库以保留文件结构。</p><ul class="assignment-downloads">${downloads.map(d => `<li><a href="${fileURL(a, d.path)}" download><strong>${esc(d.label)}</strong><span>${esc(d.format)} <span aria-hidden="true">↓</span></span></a><p>${esc(d.note)}</p></li>`).join('')}</ul></section>` : '';
    const figures = a.number === 2 ? `<section aria-labelledby="figures"><h2 id="figures">个人报告图表</h2><p>三张图直接来自归档实验，两个预测曲面使用一致的坐标轴、色彩范围与视角。</p>${await image(a, 'figures/training_samples.png', '目标函数 z = sin(x + y) 的 100 个真实训练样本三维散点图', '100 个真实训练样本')}${await image(a, 'figures/svr_surface.png', 'epsilon-SVR 预测曲面以及真实训练样本与训练点预测结果', 'ε-SVR：黑色圆圈为真实样本，红色加号为训练点预测')}${await image(a, 'figures/lssvm_surface.png', 'LS-SVM 预测曲面，使用与 SVR 一致的坐标轴、色彩范围与视角', 'LS-SVM：与 ε-SVR 相同的展示尺度')}</section>` : '';
    const related = `<section aria-labelledby="related"><h2 id="related">对应学习章节</h2><ul>${a.related.map(r => `<li><a href="${url(`weeks/${r.week}/`)}#${esc(r.anchor)}">第 ${r.week} 周 · ${esc(r.label)}</a></li>`).join('')}</ul></section>`;
    const content = await read(`source/assignments/${a.id}.html`);
    const body = `<article class="site-document assignment-document"><nav aria-label="作业导航" class="assignment-breadcrumb"><a href="${url('assignments/')}">← 全部作业</a><span>Assignment ${a.number}</span></nav><header class="assignment-header"><p class="site-eyebrow">CS5486 · ASSIGNMENT ${a.number}</p><h1 id="page-title">${esc(a.title)}</h1><p class="site-lead">${esc(a.summary)}</p><dl class="assignment-facts"><div><dt>截止时间</dt><dd>${esc(a.due)}</dd></div><div><dt>分值</dt><dd>${a.points} 分</dd></div><div><dt>发布状态</dt><dd>${esc(a.status)}</dd></div></dl></header><nav aria-label="本页目录" class="assignment-page-nav"><a href="#requirements">题目要求</a><a href="#original">原题截图</a>${a.completed ? '<a href="#solution">个人解答</a><a href="#downloads">报告与文件</a>' : '<a href="#publication-status">完成状态</a>'}</nav>${requirements}${original}${content}${figures}${files}${related}<p class="assignment-source-note">题面属于课程材料；${a.completed ? '个人解答仅记录本次实验与理解。' : '本页暂未发布个人解答。'}<a href="${url('about/')}">来源与许可说明</a></p></article>`;
    index(body, a);
    await write(`dist/${route(a)}index.html`, shell({ title: `Assignment ${a.number}｜${a.title}`, route: route(a), body }));
  }
  return assignments.map(a => ({ id: a.id, number: a.number, completed: a.completed, href: url(route(a)) }));
}
