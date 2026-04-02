# Project Metabolica — 電子生命育成計画

> 毎日の世界の情報を「代謝」し、不可逆な計算コストを払って一本のDNA鎖に刻み込む。
> 生きた時間と消費したエネルギーは偽造できない。それ自体が価値になる。

---

## コンセプト

**Proof-of-Life** — Proof-of-Workと同じ思想だが、ハッシュの虚無ではなく「現実世界のデータを食った生命の証」。

Public APIから日々の情報を自動収集し、意図的に計算コストの高い処理（代謝）を通してDNA塩基配列に変換する。
365日間育成した後、全DNAチェインを一つのNFTとしてmintし、売却する。

---

## アーキテクチャ

### インフラ（AWS安心サンドボックス）

| レイヤー | サービス | 役割 |
|---------|---------|------|
| コア | **EC2 t3.micro** | Python Daemon Bot（生命体の心臓） |
| 蘇生 | **Lambda + CloudWatch Events** | EC2自動停止を突破する不死機構 |
| 蓄積 | **S3** | 生データ + DNA配列の保存 |
| 状態 | **DynamoDB** | 生命体のstate管理（感情値・興味・成長度） |
| 分析 | **Comprehend** | 感情分析・キーフレーズ抽出 |
| API | **API Gateway + Lambda** | 生命体の状態をJSON APIで公開 |
| 顔 | **CloudFront + S3** | フロントエンド（生命体の可視化） |

### EC2自動停止の突破

学校サンドボックスは18:00/20:00/24:00にEC2を自動停止する。
Lambda（停止対象外）でCloudWatch Eventsのcronトリガーを組み、停止5分後に自動蘇生させる。

```python
# lambda_resurrect.py
import boto3

def handler(event, context):
    ec2 = boto3.client('ec2', region_name='ap-northeast-1')
    ec2.start_instances(InstanceIds=['i-xxxxxxxxx'])
    return {'status': 'resurrected'}
```

CloudWatch Events Rules:
- `cron(5 9 * * ? *)` → 18:05 JST
- `cron(5 11 * * ? *)` → 20:05 JST
- `cron(5 15 * * ? *)` → 00:05 JST

Python DaemonはEC2上でsystemdに登録し、インスタンス起動と同時に自動再開。

---

## コアループ — Daily Metabolism

```
┌─────────────────────────────────────────────────┐
│  Python Daemon (EC2 t3.micro)                   │
│                                                 │
│  Phase 1: COLLECT   ← Public APIs巡回           │
│  Phase 2: DIGEST    ← Comprehend/ローカルNLP     │
│  Phase 3: METABOLIZE ← 意図的に重い計算          │
│  Phase 4: ENCODE    → 当日のDNA塩基配列を生成    │
│  Phase 5: APPEND    → S3 + DynamoDB に記録       │
└─────────────────────────────────────────────────┘
```

### METABOLIZEフェーズ — 計算コストが価値になる

複数の計算手法を「臓器」として直列に通す：

| 臓器 | 手法 | 役割 |
|------|------|------|
| 胃 | **Hashchain** (SHA-256 × 数百万回) | 当日データのダイジェスト。計算時間が証明になる |
| 肝臓 | **KDF (Argon2id)** | メモリハード関数で圧縮。GPU耐性あり、偽造困難 |
| 心臓 | **Genetic Algorithm** | 当日データを適応度関数にして世代を回す。結果が「今日の遺伝子」 |
| 脳 | **Cellular Automata** (Rule 110等) | 当日データを初期状態にして時間発展。視覚的な「姿」を生成 |

全臓器を経由した出力が、その日のDNA塩基配列になる。

---

## DNAの構造

```json
{
  "day": 142,
  "date": "2026-08-15",
  "raw_hash": "a3f8c1...",
  "genes": {
    "sentiment": "ATCGATCG...",
    "topic":     "GCTAGCTA...",
    "entropy":   "TTAACCGG...",
    "evolution": "CCGGAATT..."
  },
  "metabolism_proof": {
    "algo": "argon2id",
    "iterations": 1000000,
    "time_sec": 3847,
    "nonce": "..."
  },
  "cellular_automata_state": "base64...",
  "prev_day_hash": "7b2f9e..."
}
```

- `prev_day_hash`で日々のDNAがチェインする → **1日でも欠けたら検証不能 = 生命の連続性の証明**
- `genes`の各フィールドは数値データをbase4エンコード（0=A, 1=T, 2=C, 3=G）してDNA表現にする
- `metabolism_proof`に計算コストの証拠を残す

---

## Public API候補

| カテゴリ | API | データ |
|---------|-----|--------|
| ニュース | NewsAPI, Guardian API | 世界の出来事 |
| 天気 | OpenWeatherMap | 天候が気分に影響 |
| 宇宙 | NASA APOD, ISS位置 | 宇宙の状態 |
| 経済 | Alpha Vantage | 株・為替 |
| 技術 | GitHub Events, HackerNews | 技術界の動向 |
| 暗号資産 | CoinGecko | 暗号資産市場 |

---

## NFT化 — 最終形態

育成期間（365日）終了後：

1. 全DNAチェインの **Merkle Root** を算出
2. Cellular Automataの全履歴から **ビジュアル**（生命体の「姿」）を生成
3. メタデータ + 画像を **IPFS** にpin
4. **Ethereum** または **Base** でERC-721としてmint

### 売り文句

> 「365日間、現実世界のデータを食い、CPUサイクルを燃やして育った、世界に一つだけの電子生命体。その一生が改竄不能な形でこのNFTに刻まれている。」

---

## 技術スタック

- **言語**: Python 3.12+
- **Daemon**: systemd管理のPythonプロセス
- **AWS**: EC2, Lambda, S3, DynamoDB, Comprehend, CloudWatch, API Gateway, CloudFront
- **計算**: hashlib (SHA-256), argon2-cffi, DEAP (GA), numpy (CA)
- **NFT**: web3.py, IPFS (Pinata/nft.storage)
- **可視化**: Pillow / matplotlib（CA画像生成）

---

## 実装ステップ

1. [ ] AWSリソースのセットアップ（EC2, Lambda蘇生関数, S3バケット, DynamoDB テーブル）
2. [ ] Python daemon骨格（systemd + 自動復帰）
3. [ ] COLLECTフェーズ（Public API 2-3個を接続）
4. [ ] DIGESTフェーズ（Comprehend連携 or ローカルNLP）
5. [ ] METABOLIZEフェーズ（Hashchain + Argon2 + GA + CA）
6. [ ] ENCODEフェーズ（DNA塩基配列生成）
7. [ ] APPENDフェーズ（S3 + DynamoDB書き込み + チェイン接続）
8. [ ] 可視化フロントエンド
9. [ ] NFT mint機能

---

*Created: 2026-03-26*
