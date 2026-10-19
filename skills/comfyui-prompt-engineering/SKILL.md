---
name: comfyui-prompt-engineering
description: "Stable Diffusion 提示词结构：句子结构优于关键词堆砌、四种失效模式、权重语法的不确定性，以及为什么负面词救不回错误的 CFG。"
whenToUse: "ComfyUI 提示词 / prompt / 负面词 / 权重 / 出图不听描述 时"
license: MIT
---


# 提示词结构手册

> DSH 执行层（跑 API、提交工作流、取图）：见 `comfyui-studio` 技能。


## 一 · 结构优先，不是堆词

SD 的文本编码器对**句子结构**和**词序**敏感。堆 200 个词会互相稀释注意力。

```
✅ a red apple resting on a weathered wooden table, soft window light from the left,
   shallow depth of field, photorealistic
❌ apple, red, table, wood, light, photo, realistic, high quality, 8k, masterpiece, best
```

**顺序**：主体 → 动作/状态 → 环境 → 光线 → 风格 → 画质

## 二 · 四种失效与修法

| 症状 | 原因 | 修法 |
|---|---|---|
| 主体不出现 | 被后面大量修饰词稀释 | 主体前置，砍掉修饰词 |
| 出现两个主体 | 提示词里有并列主体 | 只留一个，其余写成属性 |
| 风格不生效 | 风格词太靠后 / 权重不足 | 风格词提前，或用权重语法 |
| 构图不受控 | 缺机位与景别描述 | 加 `close-up / wide shot / from above` |

## 三 · 权重语法（有不确定性）

```
(red apple:1.3)   加权
(red apple:0.7)   减权
[red apple]       部分前端等价于 1/1.1
```

⚠️ 不同前端/版本解析不完全一致。**给语法时必须说明在哪个前端验证过**，不能假设通用。

## 四 · 负面提示词的边界（实测）

我们的实测：
- 默认负面词（`blurry, low quality, watermark, text, deformed`）+ cfg 7 → 正常
- **cfg 16 时，负面词压不住过饱和与噪点**

**判据**：加了负面词仍崩 → 这是参数层问题，继续堆负面词无效。

## 五 · 风格一致性：固定前缀法

同一风格出多张，靠**一段不变的前缀**：

```
[固定] photorealistic product photography, soft studio lighting, neutral background
[变量] a red apple / a blue mug / a leather wallet
```

前缀一字不改，只换主体——比每次重写整句稳定得多。

## 六 · 无意义词要删

`8k`、`masterpiece`、`best quality`、`ultra detailed` 在现代模型里作用有限，且**会挤占注意力**。

不如写具体的：`sharp focus on the apple skin texture` 比 `masterpiece` 有用。

## 七 · 交付格式

```
问题定位（主体/风格/构图/权重哪一类）
改写后提示词（可直接粘贴）
改动理由（哪一段起什么作用）
预期变化
```

## 八 · 红线

- 不给「万能提示词」，必须针对用户的实际主体
- 不推荐无意义堆词
- 权重语法标注验证环境
- 负面词压不住的问题直接说「是参数问题」
