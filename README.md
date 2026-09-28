# LiangYou IconLibrary

良友媒体图标库，供支持 `name / description / icons` 格式的播放器导入。

## 订阅地址

```text
https://raw.githubusercontent.com/MaddestAlistar/LiangYou-IconLibrary/main/LiangYou-Emby-Icons.json
```

当前收录 **3,135** 个图标索引（2026-09-29 整理）。本次核对全部 7 个来源，在原有 2,104 条基础上去重新增 **1,031** 条，并修复恩秀库中 ChenCheng、KiTi 两个已更名的图片地址。

新增条目按规范化图片 URL 和相同文件内容去重；相同内容通过图片文件哈希（Git blob SHA-1）比对，本次另外排除 94 条地址不同但文件相同的条目。同名但不同样式的图标继续保留，新重名项附有来源名称和必要的序号，便于选用。既有条目的名称及相对顺序保持不变。

## 良友专属图标

内置 5 个良哥看未来专属图标，文件保存在 `icons/liangyou/`。**每次合并、去重、更新或排序时，都必须将以下 5 项按此顺序固定在订阅列表开头，其他来源图标只能排在其后。**

1. 良友-流云音乐
2. 良友-CarPlay
3. 良友-3ayne虎影
4. 良友-Player
5. 良友-熊猫

更新前后须核对这 5 项的名称、图片地址和排列顺序，并确认 JSON 可解析、图标名称及规范化 URL 无重复。

## 来源与致谢

下表为 2026-09-29 本次同步结果；“本次去重后新增”按表中来源顺序统计，已在本库或前序来源收录的条目不再重复添加。

| 来源 | 原始订阅地址 | 当前原始条目 | 本次去重后新增 |
| --- | --- | ---: | ---: |
| 离歌 | https://raw.githubusercontent.com/lige47/lige_icon/main/lige-emby-icon.json | 571 | 1 |
| 恩秀 | https://raw.githubusercontent.com/sooyaaabo/IconLibrary/main/Emby-Icon.json | 716 | 7 |
| 萝卜猫 | https://raw.githubusercontent.com/Carrottor/carrot_icon_1/main/carrot_icon.json | 49 | 0 |
| Zzz | https://juhe.greentea520.xyz/share/78aspf.json | 592 | 0 |
| huangxd- | https://gist.githubusercontent.com/huangxd-/86eca2c70feed2f7e8ebbac1f012f893/raw/icons.json | 264 | 5 |
| TFEL | https://emby-icon.vercel.app/TFEL-Emby.json | 522 | 429 |
| Sakura / baiitang（基于 Softlyx） | https://raw.githubusercontent.com/baiitang/Sakura/main/Fileball/Fang/tubiao.json | 590 | 589 |

TFEL 与 Sakura / baiitang 为本次新增来源。Sakura 方形图标库基于 Softlyx 的作品继续整理，相关署名一并保留。

本仓库的第三方图标以**链接索引**形式收录，图片仍由原来源托管，版权与署名归原作者或相关权利人。5 个良友专属图标由本仓库托管。部分原库收录其他作者作品，请参阅各原始项目的说明。这里是手动整理快照；原地址变更、图片失效或原库新增图标时不会自动同步。欢迎通过 Issue 反馈错链或署名问题。
