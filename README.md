# 従業員管理システム

従業員の登録と日々の勤怠管理を行うための、軽量なファイルベースのCLI（コマンドライン）アプリケーションです。

## 主な機能

* 部署や役職情報を含めて従業員を登録
* 登録済みの従業員一覧を表示
* 出勤・退勤時刻を記録
* 当日または指定日の勤怠記録を確認

## はじめに

このツールは Python の標準ライブラリのみを使用しており、追加ライブラリのインストールは不要です。

Python 3.10 以上を使用してください。

```bash
python employment_cli.py --help
```

## ブラウザで利用する

以下のコマンドでWebアプリを起動できます。

```bash
python web_app.py
```

起動後、ブラウザで以下にアクセスしてください。

```text
http://127.0.0.1:8000
```

ブラウザ版でもCLIと同じ `data/employees.json` にデータを保存します。

## 従業員を登録する

例：営業部のアカウントマネージャーとして「Alice Example」を登録します。

```bash
python employment_cli.py add-employee "Alice Example" Sales "Account Manager"
```

## 従業員一覧を表示する

```bash
python employment_cli.py list
```

## 出勤・退勤を記録する

従業員IDが「1」の場合

### 出勤

```bash
python employment_cli.py clock-in 1
```

### 退勤

```bash
python employment_cli.py clock-out 1
```

## 勤怠レポートを表示する

### 本日の勤怠を表示

```bash
python employment_cli.py report
```

### 特定日の勤怠を表示

例：2024年8月1日の勤怠を表示します。

```bash
python employment_cli.py report --date 2024-08-01
```

## データ保存場所

従業員情報と勤怠データは以下のファイルにJSON形式で保存されます。

```text
data/employees.json
```

JSON形式で保存されるため、データの移行やバックアップが容易です。

## アプリ概要

このシステムは、従業員の登録・出勤・退勤・勤怠確認を行うためのCLIアプリケーションです。

Python標準ライブラリのみで実装されており、データはJSONファイルで管理しています。
