# Metabolica — 電子生命育成計画

> 毎日の世界の情報を「代謝」し、不可逆な計算コストを払って一本のDNA鎖に刻み込む。
> 生きた時間と消費したエネルギーは偽造できない。それ自体が価値になる。

## コンセプト

**Proof-of-Life** — 現実世界のデータを食った生命の証。

Public APIから日々の情報を自動収集し、計算コストの高い処理（代謝）を通してDNA塩基配列に変換する。180日間育成した後、全DNAチェインを一つのNFTとしてmintする。

## アーキテクチャ

| レイヤー | サービス | 役割 |
|---------|---------|------|
| コア | EC2 t3.micro | Python Daemon（生命体の心臓） |
| 蘇生 | Lambda + CloudWatch Events | EC2自動停止を突破する不死機構 |
| 蓄積 | S3 | 生データ + DNA配列の保存 |
| 状態 | DynamoDB | 生命体のstate管理 |
| 分析 | Comprehend | 感情分析・キーフレーズ抽出 |
| API | API Gateway + Lambda | 生命体の状態をJSON APIで公開 |
| 顔 | CloudFront + S3 | フロントエンド（生命体の可視化） |

## コアループ — Daily Metabolism

```
COLLECT   ← Public APIs巡回
DIGEST    ← Comprehend/ローカルNLP
METABOLIZE ← 意図的に重い計算（Hashchain, Argon2, GA, CA）
ENCODE    → 当日のDNA塩基配列を生成
APPEND    → S3 + DynamoDB に記録
```

### 代謝臓器

| 臓器 | 手法 | 役割 |
|------|------|------|
| 胃 | Hashchain (SHA-256 × 数百万回) | 計算時間が証明になるダイジェスト |
| 肝臓 | KDF (Argon2id) | メモリハード関数で偽造困難な圧縮 |
| 心臓 | Genetic Algorithm | 当日データで世代を回し「今日の遺伝子」を生成 |
| 脳 | Cellular Automata (Rule 110等) | 時間発展で生命体の「姿」を生成 |

## データソース

| カテゴリ | API |
|---------|-----|
| ニュース | NewsAPI, Guardian API |
| 天気 | OpenWeatherMap |
| 宇宙 | NASA APOD, ISS位置 |
| 経済 | Alpha Vantage |
| 技術 | GitHub Events, HackerNews |
| 暗号資産 | CoinGecko |

## 技術スタック

- **言語**: Python 3.12+
- **Daemon**: systemd管理
- **AWS**: EC2, Lambda, S3, DynamoDB, Comprehend, CloudWatch, API Gateway, CloudFront
- **計算**: hashlib (SHA-256), argon2-cffi, DEAP (GA), numpy (CA)
- **NFT**: web3.py, IPFS (Pinata/nft.storage)
- **可視化**: Pillow / matplotlib

## NFT化

育成期間（180日）終了後、全DNAチェインのMerkle Rootを算出し、Cellular Automata履歴からビジュアルを生成。メタデータ + 画像をIPFSにpinし、ERC-721としてmintする。

## ライセンス

MIT
