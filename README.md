# hermes-kits

给家人/朋友的 Hermes Agent 用的技能包。每个包都是**一段提示词**安装：对方把提示词贴进自己的 Hermes，它自己下载、装好、自测。

## 已有的包

| 包 | 作用 | 下载 |
|---|---|---|
| `md-to-docx` | Markdown → Word（公式原生、表格边框、代码块底色、页码） | [最新版](https://github.com/StevenZhao666/hermes-kits/releases/latest/download/md-to-docx.zip) |

## 给转交人（你）看的

1. 把 `prompts/<包名>.txt` 里那段话发给对方，别的什么都不用发。
2. 对方问「怎么装」→ 让他把整段贴给 Hermes，不用理解。
3. 对方说装不上 → 让他把 Hermes 的**原始报错**截给他，不要转述。

## 给未来的自己：怎么加新包

```
kits/<包名>/            # 包本体：SKILL.md + scripts/ + README.md
prompts/<包名>.txt      # 一段提示词，指向 releases/latest/download/<包名>.zip
```

发版：

```bash
git add -A && git commit -m "update <包名>" && git push
# 然后把 kits/<包名> 打成 zip，作为新的 release 资产上传，文件名必须是 <包名>.zip
```

提示词里的下载链接用 `releases/latest/download/<包名>.zip`，永远指向最新版，不用改提示词。

## 原则

- **只有一段提示词。** 对方不懂技术，多一个文件就多一个失败点。
- **安装交给对方的 Hermes。** 它会自检环境、装依赖、跑测试。
- **包里不带个人路径、项目名、密钥。**
