# X4UE: Exporter for Unreal Engine
Exporter For Unreal Engine

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

