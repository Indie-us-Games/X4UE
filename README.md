# X4UE: Exporter for Unreal Engine
Exporter For Unreal Engine

# X4UEについて
BlenderからUnrealEngineへSkeletalMeshを出力する際のスケール、ルートボーンの向きに関する問題を自動解決するFBXエクスポーターアドオンです

## インストール方法

### ソースから
- リポジトリをチェックアウトorダウンロードする
- `x4ue` フォルダをzip圧縮する
- Blenderの`Preference > Addon`で、圧縮したzipファイルをAddonとしてインストールする


## 変更履歴
### v0.1.3 (2019-11-21)
- 公開

### v0.1.4 (2019-12-13)
- Armatureを使用せず、Objectの階層構造を用いて作成したモデルデータを、UE4のFBXインポートオプション `Import Meshes in Bone Hierarchy` をONにしてSkeletalMeshとしてインポートした際に、SkeletonのScaleに100が設定される問題に対応（NoArmatureMode）

### v0.1.5 (2019-12-24)
- NoArmatureMode適用時、Emptyオブジェクトを使用できるようにした
- 人型のようなmulti-ped構造をNoArmatureModeで作成したとき、BoneのLocationが意図しない方向にずれる問題を修正

### v0.1.6 (2019-12-26)
- NoArmatureMode適用時、Treeの中間にEmptyオブジェクトがあると、SkeletalMeshが分割されてしまう問題を修正
- Emptyオブジェクトを配置することで、 `Import Meshes in Bone Hierarchy` モードで取り込む際に追加のボーンを作成できるようになった

### v0.1.7 (2020-08-15)
- Export時にAction(Animation)を選択式で出力するオプション(ExportMode)を追加
```
- All animation export
  全アニメーションを出力
- Select export animation
  アニメーションを選択出力
- No animation export (Armature only)
  アニメーションを出力しない
```

### v0.1.8 (2023-06-19)
- Blender3.2以降でExport FBX for UE4時にエラーが出る問題を修正
- UE4表記をUEに修正
