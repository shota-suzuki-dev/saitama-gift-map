# さいたま市商品券対応店舗マップ

[shop.saitama-tsunagu.com](https://shop.saitama-tsunagu.com) に掲載されている商品券対応店舗（約2,700件）をGoogle Maps上で確認できるサイトです。

## 使い方

GitHub Pages で公開中: `https://{username}.github.io/saitama-gift-map/`

## データ収集（開発者向け）

```bash
uv run python scraper/pipeline.py
```

`stores.json` が生成されます。

## 技術スタック

- スクレイパー: Python (requests, BeautifulSoup4)
- ジオコーディング: 国土地理院API
- 地図: Leaflet.js + OpenStreetMap

## 注意

店舗データは © 株式会社ツナグ。非商用・情報提供目的での利用。
