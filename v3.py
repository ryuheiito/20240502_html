
import folium
from folium import FeatureGroup, LayerControl
from folium.plugins import MarkerCluster, HeatMap
import pandas as pd


# CSVファイルのパス
csv_path = 'input/input.csv'
csv_display_path = 'input/input_表示.csv'

# CSVファイルの読み込み
data = pd.read_csv(csv_path, encoding="cp932")
display_data = pd.read_csv(csv_display_path, encoding="cp932")

# 地図の初期設定
map = folium.Map(location=[36.5, 138], zoom_start=6)

# ポップアップのスタイルを定義するCSS
popup_css_style = """
<style>
    .popup-info-container {
        font-family: 'Arial', sans-serif;
        font-size: 14px;
        color: #333333;
        background-color: #f9f9f9;
        border: 1px solid #ccc;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 3px 3px 5px rgba(0,0,0,0.2);
        max-width: 300px;
    }
    .popup-info-header {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .popup-info-row {
        margin-bottom: 3px;
    }
</style>
"""
# リスク項目のリスト（列名から緯度経度を除外）
risk_items = display_data.columns[3:12]

# リスク項目ごとの色
colors = {
    risk_items[0]: "red",
    risk_items[1]: "blue",
    risk_items[2]: "green",
    risk_items[3]: "purple",
    risk_items[4]: "orange",
    risk_items[5]: "darkred",
    risk_items[6]: "lightblue",
    risk_items[7]: "pink",
    risk_items[8]: "beige"
}


# 各リスク項目ごとにフィルタリングしてマーカーを作成
for item in risk_items:
    group = FeatureGroup(name=item, show=False)
    for index, row in display_data.iterrows():
        # マーカーの色を設定
        marker_color = colors[item] if row[item] == 1 else 'lightgray'

        # Googleマップへのリンクを作成
        google_maps_url = f"https://www.google.com/maps?q={row['緯度']},{row['経度']}"

        # 緯度経度を除いたポップアップ情報
        popup_info = "<br>".join([f"{col}: {data.iloc[index][col]}" for col in data.columns[2:]])

        # Googleマップリンクをポップアップに追加
        popup_info += f"<br><a href='{google_maps_url}' target='_blank'>Google Maps</a>"
        if  row[item] == 1:
            folium.Marker(
            location=[row["緯度"], row["経度"]],
            popup=folium.Popup(popup_info, max_width=300),
            icon=folium.Icon(color=marker_color, icon='flag', prefix='fa')
            ).add_to(group)
        else:
            folium.Marker(
            location=[row["緯度"], row["経度"]],
            popup=folium.Popup(popup_info, max_width=300),
            icon=folium.Icon(color=marker_color, icon='minus', prefix='fa')
            ).add_to(group)
    group.add_to(map)


    
# ヒートマップレイヤー
heat_data = [[row[0], row[1]] for index, row in data.iterrows()]
heatmap_group = FeatureGroup(name='参考_拠点密度ヒートマップ', show=False)
HeatMap(heat_data).add_to(heatmap_group)
map.add_child(heatmap_group)

folium.raster_layers.TileLayer(
    tiles = 'https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg',
    fmt = 'image/png',
    attr = '&copy; <a href="https://maps.gsi.go.jp/development/ichiran.html">国土地理院</a>',
    name = '国土地理院地図_全国最新写真（シームレス）'
).add_to(map)

folium.raster_layers.TileLayer(
    tiles = 'https://cyberjapandata.gsi.go.jp/xyz/relief/{z}/{x}/{y}.png',
    fmt = 'image/png',
    attr = '&copy; <a href="https://maps.gsi.go.jp/development/ichiran.html">国土地理院</a>',
    name = '国土地理院地図_色別標高図'
).add_to(map)
# レイヤーコントロールの追加
LayerControl().add_to(map)

# 地図をHTMLファイルとして保存
map.save('output/map_with_risk_color.html')
