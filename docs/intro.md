# Agent 工具清单

一套自己做的工具和技能包。分两类：

- **技能包**：装进 Hermes，让 agent 多一项能力（转 Word、转 PDF）
- **桌面工具**：装给你自己用，双击就开（写笔记、查词、取色、改网卡）

---

## 一句话拿走

把这句话连同链接发给任何一个 AI agent，它自己读目录、自己挑、自己装：

```
读 https://raw.githubusercontent.com/StevenZhao666/hermes-kits/main/CATALOG.md
按我的情况挑 1-2 个装好，装完告诉我装了什么、怎么打开、有什么限制。
```

不需要打包、不需要解压、不需要教它怎么装。目录里每条都写了依赖、适合谁、怎么装、有什么限制。

---

## 里面有什么

| 名字 | 给谁 | 一句话 |
|---|---|---|
| MarkdownViewer | 所有人 | 一个 html 文件，双击就能写带公式的笔记 |
| md-to-docx | 要交 Word 的人 | Markdown 转 Word，公式原生、表格有边框 |
| md-to-pdf | 要交 PDF 的人 | Markdown 转 PDF，中文排版和页码都像样 |
| Smart Dictionary | 读英文文档的人 | 划词即查，本地词库 + AI 补全 |
| ColorPicker | 不靠眼睛辨色的人 | 取到 `#RRGGBB`，直接和选项比对 |
| Network Optimizer | Wi-Fi 慢的人 | 锁 5GHz、关节能，跑前跑后测速 |
| SimpleTrainer | 健身的人 | 三步生成自己的训练打卡页 |
| Gauss Elim | 学线代的人 | 精确分数解方程，不要浮点误差 |

完整列表（含游戏、写作、Canvas 样例）：[CATALOG.md](../CATALOG.md)

---

## 为什么这样发

以前是发 zip：对方要解压、找目录、可能装错，出问题还得远程。

现在只发一个链接。目录是给 agent 读的，它自己判断平台、装依赖、验证能不能跑，最后用三句人话汇报。人不需要懂任何技术细节。

---

## 链接

- 目录（agent 读）：https://raw.githubusercontent.com/StevenZhao666/hermes-kits/main/CATALOG.md
- 目录（人看）：https://github.com/StevenZhao666/hermes-kits/blob/main/CATALOG.md
- 仓库：https://github.com/StevenZhao666/hermes-kits

---

## 维护

新增工具时：

1. 单文件放 `tools/<名字>/`，独立项目只登记链接
2. 在 `CATALOG.md` 补一条（五项格式），同步 `catalog.json`
3. 发布前跑脱敏扫描，确认没有个人路径和密钥
