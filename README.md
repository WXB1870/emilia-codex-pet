# 爱蜜莉雅 Codex 桌宠 · Emilia Codex Pet

一个非官方《Re:Zero》爱蜜莉雅桌宠素材包，包含透明精灵图、安装工具和可复现的动画预览。适用于采用 `pet.json` 与精灵图格式的 Codex 本地宠物目录。

![俯身脸旁比耶](previews/hover.gif)

**当前状态：素材与设置页预览已验证；桌面浮窗的悬停动作同步仍有未解决的问题。** 本项目以实验版本发布，不把设置页预览成功视为桌面交互已经通过验证。

## 内容

- 完整 v2 精灵图：1536 × 2288，8 列 × 11 行，单格 192 × 208，73 个有效姿势。
- 待机、左右跑动、挥手、悬停俯身比耶、失败、等待、工作和检查动作。
- 16 个鼠标跟随方向。
- 本地安装、精灵图验证、逐帧导出、重新组装及 GIF 预览工具。

![左右跑动](previews/running.gif)

## 安装

需要 Python 3.9 或更新版本。推荐在虚拟环境中安装依赖：

```sh
git clone https://github.com/WXB1870/emilia-codex-pet.git
cd emilia-codex-pet
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python tools/install.py --dry-run
python tools/install.py
```

安装器默认使用 `$CODEX_HOME/pets/emilia-anime`；未设置 `CODEX_HOME` 时使用 `~/.codex/pets/emilia-anime`。已有目录会先完整备份。安装器只复制这个宠物的文件，不更改全局配置、登录信息或当前宠物选择。

安装后在应用的宠物设置页刷新，选择“爱蜜莉雅”。本地宠物与账号云端宠物的同步行为取决于客户端版本；本安装器不会替用户创建或更新云端宠物。

Windows 可使用 PowerShell 创建并启用虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python tools/install.py
```

如果要测试到其他目录：

```sh
python tools/install.py --destination ./test-pet
```

## 编辑与验证

```sh
# 验证精灵图的尺寸、有效格及透明空格
python tools/atlas.py validate pet/emilia-anime/spritesheet.png

# 导出可编辑的独立帧
python tools/atlas.py extract pet/emilia-anime/spritesheet.png --output work/frames

# 修改帧图后重新组装；不缩放、插帧或自动重画
python tools/atlas.py build work/frames --output work/spritesheet.png

# 生成各状态的 GIF 预览
python tools/atlas.py preview pet/emilia-anime/spritesheet.png --output work/previews
```

工具不会修改应用播放器。图片中重复的悬停姿势用于保持俯身比耶；播放时长仍由客户端控制。

运行工具验证：

```sh
python -m unittest discover -s tests -v
```

## 精灵图布局

| 行（从 0 开始） | 状态 | 有效帧数 |
| --- | --- | ---: |
| 0 | idle / 待机 | 6 |
| 1 | running-right / 向右跑动 | 8 |
| 2 | running-left / 向左跑动 | 8 |
| 3 | waving / 挥手 | 4 |
| 4 | jumping / 原生悬停槽，此包为俯身比耶 | 5 |
| 5 | failed / 失败反应 | 8 |
| 6 | waiting / 等待输入 | 6 |
| 7 | running / 工作状态 | 6 |
| 8 | review / 检查 | 6 |
| 9 | look-0 / 000°–157.5° | 8 |
| 10 | look-1 / 180°–337.5° | 8 |

未使用的 15 个格子完全透明。`jumping` 是客户端的槽位名，本素材中的对应动作不包含离地跳跃。

## 已知问题

用户已确认：设置页显示新版俯身比耶，桌面宠物浮窗仍显示旧动作；刷新以及隐藏后重新显示浮窗均未解决。素材文件、云端保存结果和设置页资源已核对，但尚未找到浮窗不同步的确定修复方法。

这不是“已完成修复”的发行版。没有修改或随包提供 Codex/ChatGPT 应用代码，也不包含相关内部资源、账号缓存或配置文件。

详见 [验证记录](docs/validation.json) 和 [素材来源与权利说明](ASSETS.md)。

## 来源与许可

原创安装与精灵图工具代码采用 [MIT License](LICENSE)。**MIT 不覆盖角色、图像、模型或其他第三方素材。**

形象参考来源为 [HaiKonofanDesu/konofan-live2d 的爱蜜莉雅模型](https://github.com/HaiKonofanDesu/konofan-live2d/tree/main/147%20-%20Emilia/4%20star%20emilia)。部分动作由内置图像生成工具重绘，部分动作沿用早期本地渲染版本。原始 Live2D 模型与 Cubism Core 未随本仓库分发。

本项目是非官方爱好者项目，与《Re:Zero》权利方及 OpenAI 无隶属或背书关系。角色素材的使用、修改与分发权限请查看 [ASSETS.md](ASSETS.md)，不要把代码的 MIT 许可当成第三方角色素材的授权。
