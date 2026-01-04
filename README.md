# GoogleColab-cc-demo-001

Google Colab環境で役立つユーティリティ関数を提供するデモリポジトリです。

## 機能

このリポジトリには、Google Colabでの作業を効率化する3つのユーティリティ関数が含まれています：

### 1. `is_colab()` - Colab環境判定

現在の実行環境がGoogle Colabかどうかを判定します。

```python
from colab_utils import is_colab

if is_colab():
    print("Google Colab環境で実行中")
else:
    print("ローカル環境で実行中")
```

### 2. `setup_colab_environment()` - 環境セットアップ

Colab環境の基本的な設定を行い、環境情報を取得します。

```python
from colab_utils import setup_colab_environment

# 環境情報を取得して表示
env_info = setup_colab_environment(verbose=True)

# 詳細設定
env_info = setup_colab_environment(
    verbose=True,           # セットアップ情報を表示
    matplotlib_inline=True  # matplotlib のインライン表示を有効化
)

print(f"Python バージョン: {env_info['python_version']}")
print(f"作業ディレクトリ: {env_info['working_directory']}")
```

### 3. `download_from_url()` - ファイルダウンロード

URLからファイルをダウンロードして保存します。

```python
from colab_utils import download_from_url

# デフォルト（カレントディレクトリに保存）
path = download_from_url("https://example.com/data.csv")
print(f"ダウンロード先: {path}")

# 保存先を指定
path = download_from_url(
    "https://example.com/data.csv",
    destination="/content/my_data.csv",
    verbose=True  # ダウンロード進捗を表示
)
```

## インストールと使用方法

### 基本的な使用

```bash
# リポジトリをクローン
git clone https://github.com/Sunwood-ai-labs/GoogleColab-cc-demo-001.git
cd GoogleColab-cc-demo-001

# Pythonから直接インポート
python -c "from colab_utils import is_colab; print(is_colab())"
```

### Google Colabでの使用

```python
# Colabノートブックで以下を実行
!git clone https://github.com/Sunwood-ai-labs/GoogleColab-cc-demo-001.git
import sys
sys.path.append('/content/GoogleColab-cc-demo-001')

from colab_utils import is_colab, setup_colab_environment, download_from_url

# 環境セットアップ
env_info = setup_colab_environment()

# ファイルダウンロード
download_from_url("https://example.com/sample.txt")
```

## テスト

### テスト環境のセットアップ

```bash
# テスト用依存関係をインストール
pip install -r requirements.txt
```

### テストの実行

```bash
# すべてのテストを実行
python -m pytest tests/ -v

# カバレッジ付きでテスト実行
python -m pytest tests/ --cov=colab_utils --cov-report=html

# 特定のテストクラスのみ実行
python -m pytest tests/test_colab_utils.py::TestIsColab -v
```

### テスト結果

- **18個のテスト**: すべてのテストが成功
- **カバレッジ**: 主要な関数とエッジケースをカバー
- **テスト項目**:
  - 環境判定機能のテスト（4件）
  - 環境セットアップ機能のテスト（6件）
  - ファイルダウンロード機能のテスト（7件）
  - メイン実行ブロックのテスト（1件）

## 依存関係

このプロジェクトは主に標準ライブラリを使用しており、最小限の外部依存で動作します：

- **実行時**: Python 3.7以上（標準ライブラリのみ）
- **テスト時**:
  - `pytest >= 7.4.0`
  - `pytest-cov >= 4.1.0`
- **オプション** (Google Colabには標準搭載):
  - `matplotlib` (グラフ表示用)
  - `IPython` (インタラクティブ機能用)

## ライセンス

MIT License

## 貢献

プルリクエストやイシューの報告を歓迎します！