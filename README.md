# hermes-kits

Hermes Agent 的技能包。每个包配一段提示词：贴给 Hermes，它自己判断要不要装、自己装、自己测。

## 已有的包

| 包 | 作用 | 下载 |
|---|---|---|
| `md-to-docx` | Markdown → Word（公式原生、表格边框、代码块底色、页码） | [最新版](https://github.com/StevenZhao666/hermes-kits/releases/download/packs/md-to-docx.zip) |
| `md-to-pdf` | Markdown → PDF（pandoc + Typst：原生公式、中文排版、表格、代码块、页码） | [最新版](https://github.com/StevenZhao666/hermes-kits/releases/download/packs/md-to-pdf.zip) |

## 交付方式

两种，按对方能不能收到文件选：

| 场景 | 发什么 |
|---|---|
| 能直接把 zip 发过去（聊天软件、网盘） | 发 `md-to-docx.zip` + `prompts/md-to-docx.txt` 那段话 |
| 只能发文字 | 发 `prompts/md-to-docx-链接.txt`，里面自带下载地址 |

两种提示词都要求接收方**什么都不用回答**：agent 自己查环境、自己判断、自己装，最后只用三句人话汇报。

## 加新包

```
kits/<包名>/            # 包本体：SKILL.md + README.md + scripts/ + demo
prompts/<包名>.txt      # 提示词（文件版）
prompts/<包名>-链接.txt # 提示词（链接版）
```

发版：

```bash
git add -A && git commit -m "update <包名>" && git push
# 打成 zip（根目录必须是 <包名>/ 文件夹），资产名等于 <包名>.zip
# 上传到固定的 packs 发行版（替换同名资产），不要每包建一个 release
```

**所有包的 zip 都挂在同一个 tag 为 `packs` 的发行版下**，链接形如
`https://github.com/StevenZhao666/hermes-kits/releases/download/packs/<包名>.zip`。

不要用 `releases/latest/download/<包名>.zip`：`latest` 是全局的"最新一个发行版"，
一旦为某个包单独发版，其它包的链接就会 404。

## 原则

- **只有一段话。** 接收方不回答问题、不看技术细节，多一个文件就多一个失败点。
- **检查在 agent 侧完成。** 自查、查重、装依赖、跑测试都是它的事；只把「装没装、能干什么、怎么用」翻译成人话。
- **不写关系称谓。** 同一份东西会发给不同的人，写死关系就过时了。
- **包里不带个人路径、项目名、密钥。**
