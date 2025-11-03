import json
from datetime import datetime, timezone

def json_to_kml(json_input_path, kml_output_path):
    """
    将设备轨迹JSON数据转换为完整KML文件
    :param json_input_path: 原始JSON数据文件路径（如 data.json）
    :param kml_output_path: 生成的KML文件路径（如 device_track.kml）
    """
    # 1. 读取并解析JSON数据
    try:
        with open(json_input_path, 'r', encoding='utf-8') as f:
            # 处理原始数据可能的格式（若JSON外层有[]，直接加载；若无则包裹为列表）
            raw_data = f.read().strip()
            if raw_data.startswith('[') and raw_data.endswith(']'):
                data_list = json.loads(raw_data)
            else:
                # 若单条数据，转为列表（适配可能的格式差异）
                data_list = [json.loads(raw_data)]
    except FileNotFoundError:
        print(f"错误：输入文件 {json_input_path} 未找到，请检查路径！")
        return
    except json.JSONDecodeError:
        print(f"错误：输入文件 {json_input_path} 不是合法的JSON格式！")
        return

    # 2. 初始化KML基础结构（包含样式定义）
    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>AGRIFZ01设备完整轨迹</name>
    <description>生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</description>
    
    <!-- 轨迹样式：红色标记点 + 红色轨迹线 -->
    <Style id="trackStyle">
      <LineStyle>
        <color>FF0000FF</color> <!-- 线条颜色：红色（ARGB格式） -->
        <width>3</width>       <!-- 线条宽度 -->
      </LineStyle>
      <PointStyle>
        <color>FF0000FF</color> <!-- 标记点颜色：红色 -->
        <scale>1.1</scale>     <!-- 标记点大小 -->
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href>
        </Icon>
      </PointStyle>
    </Style>

    <!-- 3. 轨迹线（包含所有数据点坐标） -->
    <Placemark>
      <name>设备轨迹线</name>
      <styleUrl>#trackStyle</styleUrl>
      <LineString>
        <extrude>1</extrude>        <!-- 开启高度拉伸（连接地面） -->
        <tessellate>1</tessellate>  <!-- 适应地形弯曲 -->
        <altitudeMode>absolute</altitudeMode> <!-- 海拔为绝对高度（米） -->
        <coordinates>
"""

    # 4. 循环处理每个数据点：补充轨迹线坐标 + 生成单个点位标记
    for idx, data in enumerate(data_list, 1):
        # 提取核心字段（容错：若字段缺失则用默认值）
        lon = data.get('longitude', 0.0)
        lat = data.get('latitude', 0.0)
        alt = data.get('altitude', 0.0)
        timestamp = data.get('time', 0)
        unique_no = data.get('uniqueNo', '未知')
        job_id = data.get('jobId', '未知')
        terminal_no = data.get('terminalNo', '未知')
        product_code = data.get('productCode', '未知')

        # 时间戳转换：毫秒级→UTC可读时间（若需本地时间，将timezone.utc改为None）
        try:
            utc_time = datetime.fromtimestamp(timestamp / 1000, timezone.utc)
            readable_time = utc_time.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            readable_time = f"无效时间戳：{timestamp}"

        # 4.1 补充轨迹线坐标（格式：经度,纬度,海拔）
        kml_content += f"          {lon},{lat},{alt}\n"

        # 4.2 生成单个点位标记（每个数据点一个Placemark，含详情）
        kml_content += f"""
    </Placemark>
    <Placemark>
      <name>数据点 {idx}（{readable_time}）</name>
      <styleUrl>#trackStyle</styleUrl>
      <Point>
        <altitudeMode>absolute</altitudeMode>
        <coordinates>{lon},{lat},{alt}</coordinates>
      </Point>
      <description>
        <![CDATA[
        <h3>设备状态详情</h3>
        <p>1. 时间：{readable_time}</p>
        <p>2. 设备编号：{unique_no}</p>
        <p>3. 终端编号：{terminal_no}</p>
        <p>4. 产品型号：{product_code}</p>
        <p>5. 任务ID：{job_id}</p>
        <p>6. 海拔：{alt} 米</p>
        <p>7. 经纬度：({lat}, {lon})</p>
        ]]>
      </description>
"""

    # 5. 闭合KML标签
    kml_content += """
      </LineString>
    </Placemark>
  </Document>
</kml>
"""

    # 6. 保存KML文件
    try:
        with open(kml_output_path, 'w', encoding='utf-8') as f:
            f.write(kml_content)
        print(f"成功生成KML文件！路径：{kml_output_path}")
        print(f"共处理 {len(data_list)} 个数据点，可直接导入谷歌地图。")
    except Exception as e:
        print(f"保存KML文件失败：{str(e)}")


# ------------------- 使用说明 -------------------
if __name__ == "__main__":
    # 请根据你的文件路径修改以下两个参数
    INPUT_JSON_PATH = "device_data.json"   # 你的原始JSON数据文件（需手动准备）
    OUTPUT_KML_PATH = "device_full_track.kml"  # 生成的KML文件路径

    # 执行转换
    json_to_kml(INPUT_JSON_PATH, OUTPUT_KML_PATH)
