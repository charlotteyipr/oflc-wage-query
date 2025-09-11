# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import pandas as pd
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# 数据库文件路径
DB_PATH = 'wage_data.db'

def init_database():
    """初始化数据库并导入数据"""
    if os.path.exists(DB_PATH):
        print("数据库已存在，跳过初始化")
        return
    
    print("开始初始化数据库...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 读取CSV文件
    print("正在读取数据文件...")
    
    try:
        # 检查CSV文件是否存在
        csv_files = ['ALC_Export.csv', 'Geography.csv', 'oes_soc_occs.csv']
        for file in csv_files:
            if not os.path.exists(file):
                print(f"错误：文件 {file} 不存在")
                conn.close()
                return
            else:
                print(f"文件 {file} 存在")
        
        # 读取主要薪资数据
        print("读取ALC_Export.csv...")
        alc_data = pd.read_csv('ALC_Export.csv')
        alc_data.columns = ['area', 'soc_code', 'geo_lvl', 'level1', 'level2', 'level3', 'level4', 'average', 'label']
        print(f"ALC数据行数: {len(alc_data)}")
        
        # 读取地理信息
        print("读取Geography.csv...")
        geo_data = pd.read_csv('Geography.csv')
        geo_data.columns = ['area', 'area_name', 'state_ab', 'state', 'county_town_name']
        print(f"地理数据行数: {len(geo_data)}")
        
        # 读取职业信息
        print("读取oes_soc_occs.csv...")
        occ_data = pd.read_csv('oes_soc_occs.csv')
        occ_data.columns = ['soc_code', 'title', 'description']
        print(f"职业数据行数: {len(occ_data)}")
        
    except Exception as e:
        print(f"读取CSV文件时出错: {e}")
        print(f"当前工作目录: {os.getcwd()}")
        print(f"目录中的文件: {os.listdir('.')}")
        conn.close()
        return
    
    # 创建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wage_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area TEXT,
            soc_code TEXT,
            geo_lvl INTEGER,
            level1 REAL,
            level2 REAL,
            level3 REAL,
            level4 REAL,
            average REAL,
            label TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS geography (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area TEXT,
            area_name TEXT,
            state_ab TEXT,
            state TEXT,
            county_town_name TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS occupations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            soc_code TEXT,
            title TEXT,
            description TEXT
        )
    ''')
    
    # 插入数据
    print("正在导入薪资数据...")
    alc_data.to_sql('wage_data', conn, if_exists='append', index=False)
    
    print("正在导入地理数据...")
    geo_data.to_sql('geography', conn, if_exists='append', index=False)
    
    print("正在导入职业数据...")
    occ_data.to_sql('occupations', conn, if_exists='append', index=False)
    
    # 创建索引以提高查询性能
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_wage_area ON wage_data(area)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_wage_soc ON wage_data(soc_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_geo_area ON geography(area)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_geo_state ON geography(state)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_occ_soc ON occupations(soc_code)')
    
    conn.commit()
    conn.close()
    print("数据库初始化完成！")

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/debug')
def debug():
    """调试页面，显示数据库状态"""
    try:
        # 检查数据库文件是否存在
        if not os.path.exists(DB_PATH):
            return f"""
            <h1>数据库调试信息</h1>
            <p style="color: red;">数据库文件不存在: {DB_PATH}</p>
            <p>当前工作目录: {os.getcwd()}</p>
            <p>目录中的文件: {', '.join(os.listdir('.'))}</p>
            <p><a href="/api/init-db" target="_blank">强制重新初始化数据库 (新窗口)</a></p>
            <p><a href="/init-db-simple">简单重新初始化数据库</a></p>
            <p><a href="/">返回主页</a></p>
            """
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        if 'wage_data' not in table_names:
            return f"""
            <h1>数据库调试信息</h1>
            <p style="color: red;">数据库表不存在</p>
            <p>数据库文件: {DB_PATH}</p>
            <p>现有表: {', '.join(table_names) if table_names else '无'}</p>
            <p>当前工作目录: {os.getcwd()}</p>
            <p>CSV文件检查:</p>
            <ul>
            <li>ALC_Export.csv: {'存在' if os.path.exists('ALC_Export.csv') else '不存在'}</li>
            <li>Geography.csv: {'存在' if os.path.exists('Geography.csv') else '不存在'}</li>
            <li>oes_soc_occs.csv: {'存在' if os.path.exists('oes_soc_occs.csv') else '不存在'}</li>
            </ul>
            <p><a href="/api/init-db" target="_blank">强制重新初始化数据库 (新窗口)</a></p>
            <p><a href="/init-db-simple">简单重新初始化数据库</a></p>
            <p><a href="/">返回主页</a></p>
            """
        
        # 检查各表的数据量
        cursor.execute("SELECT COUNT(*) FROM wage_data")
        wage_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM geography")
        geo_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM occupations")
        occ_count = cursor.fetchone()[0]
        
        # 检查一些样本数据
        cursor.execute("SELECT title FROM occupations LIMIT 5")
        sample_occupations = cursor.fetchall()
        
        conn.close()
        
        return f"""
        <h1>数据库调试信息</h1>
        <p>数据库文件: {DB_PATH}</p>
        <p>薪资数据行数: {wage_count}</p>
        <p>地理数据行数: {geo_count}</p>
        <p>职业数据行数: {occ_count}</p>
        <h3>样本职业数据:</h3>
        <ul>
        {''.join([f'<li>{occ[0]}</li>' for occ in sample_occupations])}
        </ul>
        <p><a href="/init-db-simple">强制重新初始化数据库</a></p>
        <p><a href="/">返回主页</a></p>
        """
    except Exception as e:
        return f"""
        <h1>数据库错误</h1>
        <p>错误信息: {str(e)}</p>
        <p>当前工作目录: {os.getcwd()}</p>
        <p>目录中的文件: {', '.join(os.listdir('.'))}</p>
        <p><a href='/'>返回主页</a></p>
        """

@app.route('/api/search/forward', methods=['POST'])
def forward_search():
    """正向查询：职位名称+地区 → Level 1-4薪资"""
    data = request.json
    position = data.get('position', '').strip()
    location = data.get('location', '').strip()
    county = data.get('county', '').strip()
    
    if not position or not location:
        return jsonify({'error': 'Job title and location cannot be empty'}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询匹配的职业
    cursor.execute('''
        SELECT DISTINCT soc_code, title 
        FROM occupations 
        WHERE title LIKE ? OR description LIKE ?
    ''', ('%' + position + '%', '%' + position + '%'))
    
    occupations = cursor.fetchall()
    
    if not occupations:
        conn.close()
        return jsonify({'error': 'No matching occupations found'}), 404
    
    results = []
    seen_combinations = set()  # 用于去重
    
    for soc_code, title in occupations:
        # 查询地理信息
        if county:
            cursor.execute('''
                SELECT DISTINCT g.area, g.area_name, g.state, g.county_town_name
                FROM geography g
                WHERE (g.area_name LIKE ? OR g.state LIKE ? OR g.county_town_name LIKE ?)
                AND g.county_town_name LIKE ?
            ''', ('%' + location + '%', '%' + location + '%', '%' + location + '%', '%' + county + '%'))
        else:
            cursor.execute('''
                SELECT DISTINCT g.area, g.area_name, g.state, g.county_town_name
                FROM geography g
                WHERE g.area_name LIKE ? OR g.state LIKE ? OR g.county_town_name LIKE ?
            ''', ('%' + location + '%', '%' + location + '%', '%' + location + '%'))
        
        locations = cursor.fetchall()
        
        for area, area_name, state, county_town in locations:
            # 查询薪资数据
            cursor.execute('''
                SELECT level1, level2, level3, level4, average, label
                FROM wage_data
                WHERE area = ? AND soc_code = ?
            ''', (area, soc_code))
            
            wage_data = cursor.fetchone()
            
            if wage_data:
                level1, level2, level3, level4, average, label = wage_data
                
                # 创建唯一标识符用于去重
                unique_key = f"{title}_{area_name}_{state}_{county_town}"
                
                if unique_key not in seen_combinations:
                    seen_combinations.add(unique_key)
                    
                    # 将时薪转换为年薪（假设每年工作2080小时）
                    results.append({
                        'occupation': title,
                        'soc_code': soc_code,
                        'location': area_name + ', ' + state,
                        'county': county_town,
                        'level1': round(level1 * 2080, 2) if level1 else None,
                        'level2': round(level2 * 2080, 2) if level2 else None,
                        'level3': round(level3 * 2080, 2) if level3 else None,
                        'level4': round(level4 * 2080, 2) if level4 else None,
                        'label': label
                    })
    
    conn.close()
    
    if not results:
        return jsonify({'error': 'No matching wage data found'}), 404
    
    return jsonify({'results': results})

@app.route('/api/search/reverse', methods=['POST'])
def reverse_search():
    """根据薪资查询：年薪范围+地区 → 符合条件的职位及level"""
    data = request.json
    min_salary = float(data.get('min_salary', 0))
    max_salary = float(data.get('max_salary', 0))
    location = data.get('location', '').strip()
    county = data.get('county', '').strip()
    
    if not min_salary or not max_salary or not location:
        return jsonify({'error': 'Salary range and location cannot be empty'}), 400
    
    # 将年薪转换为时薪进行比较
    min_hourly = min_salary / 2080
    max_hourly = max_salary / 2080
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询地理信息
    if county:
        cursor.execute('''
            SELECT DISTINCT g.area, g.area_name, g.state, g.county_town_name
            FROM geography g
            WHERE (g.area_name LIKE ? OR g.state LIKE ? OR g.county_town_name LIKE ?)
            AND g.county_town_name LIKE ?
        ''', ('%' + location + '%', '%' + location + '%', '%' + location + '%', '%' + county + '%'))
    else:
        cursor.execute('''
            SELECT DISTINCT g.area, g.area_name, g.state, g.county_town_name
            FROM geography g
            WHERE g.area_name LIKE ? OR g.state LIKE ? OR g.county_town_name LIKE ?
        ''', ('%' + location + '%', '%' + location + '%', '%' + location + '%'))
    
    locations = cursor.fetchall()
    
    if not locations:
        conn.close()
        return jsonify({'error': 'No matching locations found'}), 404
    
    results = []
    
    for area, area_name, state, county_town in locations:
        # 查询薪资数据 - 只查询Level 2在指定年薪范围内的职位
        cursor.execute('''
            SELECT w.soc_code, w.level1, w.level2, w.level3, w.level4, w.average, w.label,
                   o.title
            FROM wage_data w
            JOIN occupations o ON w.soc_code = o.soc_code
            WHERE w.area = ? AND w.level2 IS NOT NULL AND w.level2 >= ? AND w.level2 <= ?
        ''', (area, min_hourly, max_hourly))
        
        wage_data = cursor.fetchall()
        
        for soc_code, level1, level2, level3, level4, average, label, title in wage_data:
            # 由于查询已经过滤了Level 2在范围内的职位，直接添加结果
            results.append({
                'occupation': title,
                'soc_code': soc_code,
                'location': area_name + ', ' + state,
                'county': county_town,
                'matching_levels': [{'level': 2, 'salary': round(level2 * 2080, 2)}],
                'level1': round(level1 * 2080, 2) if level1 else None,
                'level2': round(level2 * 2080, 2) if level2 else None,
                'level3': round(level3 * 2080, 2) if level3 else None,
                'level4': round(level4 * 2080, 2) if level4 else None,
                'label': label
            })
    
    conn.close()
    
    if not results:
        return jsonify({'error': 'No matching salary data found'}), 404
    
    return jsonify({'results': results})

@app.route('/api/search/location', methods=['POST'])
def location_search():
    """地区查询：职位和薪资水平 → 显示哪个州可以达到指定level的水平"""
    data = request.json
    position = data.get('position', '').strip()
    target_level = int(data.get('target_level', 2))
    target_salary = float(data.get('target_salary', 0))
    
    if not position or not target_level or not target_salary:
        return jsonify({'error': 'Job title, target level and target salary cannot be empty'}), 400
    
    # 将年薪转换为时薪进行比较
    target_hourly = target_salary / 2080
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询匹配的职业
    cursor.execute('''
        SELECT DISTINCT soc_code, title 
        FROM occupations 
        WHERE title LIKE ? OR description LIKE ?
    ''', ('%' + position + '%', '%' + position + '%'))
    
    occupations = cursor.fetchall()
    
    if not occupations:
        conn.close()
        return jsonify({'error': 'No matching occupations found'}), 404
    
    results = []
    seen_combinations = set()  # 用于按州和县去重
    
    for soc_code, title in occupations:
        # 查询薪资数据，按州和县分组
        level_column = 'level' + str(target_level)
        cursor.execute('''
            SELECT w.level1, w.level2, w.level3, w.level4, w.average, w.label,
                   g.state, g.county_town_name, 
                   MIN(w.''' + level_column + ''') as min_target_salary
            FROM wage_data w
            JOIN geography g ON w.area = g.area
            WHERE w.soc_code = ? AND w.''' + level_column + ''' IS NOT NULL AND w.''' + level_column + ''' >= ?
            GROUP BY g.state, g.county_town_name
            ORDER BY min_target_salary ASC
        ''', (soc_code, target_hourly))
        
        wage_data = cursor.fetchall()
        
        for row in wage_data:
            level1, level2, level3, level4, average, label, state, county_town, min_target_salary = row
            
            # 创建唯一标识符用于去重（职位+州+县）
            unique_key = f"{title}_{state}_{county_town}"
            
            if unique_key not in seen_combinations:
                seen_combinations.add(unique_key)
                
                results.append({
                    'occupation': title,
                    'soc_code': soc_code,
                    'location': state,  # 只显示州名称
                    'county': county_town,
                    'target_level': target_level,
                    'target_level_salary': round(min_target_salary * 2080, 2),  # 转换为年薪
                    'level1': round(level1 * 2080, 2) if level1 else None,
                    'level2': round(level2 * 2080, 2) if level2 else None,
                    'level3': round(level3 * 2080, 2) if level3 else None,
                    'level4': round(level4 * 2080, 2) if level4 else None,
                    'label': label
                })
    
    conn.close()
    
    if not results:
        return jsonify({'error': 'No matching locations found'}), 404
    
    return jsonify({'results': results})

@app.route('/api/occupations')
def get_occupations():
    """获取所有职业列表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT soc_code, title FROM occupations ORDER BY title')
    occupations = cursor.fetchall()
    
    conn.close()
    
    return jsonify({'occupations': [{'soc_code': soc, 'title': title} for soc, title in occupations]})

@app.route('/api/locations')
def get_locations():
    """获取所有地区列表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT state, area_name FROM geography ORDER BY state, area_name')
    locations = cursor.fetchall()
    
    conn.close()
    
    return jsonify({'locations': [{'state': state, 'area_name': area} for state, area in locations]})

@app.route('/api/search/occupations')
def search_occupations():
    """搜索职业"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'occupations': []})
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 改进搜索逻辑：优先匹配标题，然后匹配描述
    cursor.execute('''
        SELECT DISTINCT soc_code, title 
        FROM occupations 
        WHERE title LIKE ?
        ORDER BY 
            CASE 
                WHEN title LIKE ? THEN 1
                WHEN title LIKE ? THEN 2
                ELSE 3
            END,
            title
        LIMIT 20
    ''', ('%' + query + '%', query + '%', '%' + query + '%'))
    
    occupations = cursor.fetchall()
    conn.close()
    
    return jsonify({'occupations': [{'soc_code': soc, 'title': title} for soc, title in occupations]})

@app.route('/api/search/states')
def search_states():
    """搜索州"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'states': []})
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT state, state_ab
        FROM geography 
        WHERE state LIKE ? OR state_ab LIKE ?
        ORDER BY state
        LIMIT 20
    ''', ('%' + query + '%', '%' + query + '%'))
    
    states = cursor.fetchall()
    conn.close()
    
    return jsonify({'states': [{'state': state, 'state_ab': state_ab} for state, state_ab in states]})

@app.route('/api/search/counties')
def search_counties():
    """搜索县/镇"""
    query = request.args.get('q', '').strip()
    state = request.args.get('state', '').strip()
    
    if not query:
        return jsonify({'counties': []})
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if state:
        cursor.execute('''
            SELECT DISTINCT county_town_name
            FROM geography 
            WHERE county_town_name LIKE ? AND state LIKE ?
            ORDER BY county_town_name
            LIMIT 20
        ''', ('%' + query + '%', '%' + state + '%'))
    else:
        cursor.execute('''
            SELECT DISTINCT county_town_name
            FROM geography 
            WHERE county_town_name LIKE ?
            ORDER BY county_town_name
            LIMIT 20
        ''', ('%' + query + '%',))
    
    counties = cursor.fetchall()
    conn.close()
    
    return jsonify({'counties': [{'county': county[0]} for county in counties]})

@app.route('/api/init-db', methods=['POST'])
def force_init_db():
    """强制重新初始化数据库"""
    try:
        # 删除现有数据库
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            print("已删除现有数据库")
        
        # 重新初始化
        init_database()
        
        # 检查数据
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM wage_data")
        wage_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM geography")
        geo_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM occupations")
        occ_count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '数据库重新初始化成功',
            'data_counts': {
                'wage_data': wage_count,
                'geography': geo_count,
                'occupations': occ_count
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/init-db-simple')
def init_db_simple():
    """简单的数据库重新初始化页面"""
    try:
        # 删除现有数据库
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            print("已删除现有数据库")
        
        # 重新初始化
        init_database()
        
        # 检查数据
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM wage_data")
        wage_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM geography")
        geo_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM occupations")
        occ_count = cursor.fetchone()[0]
        conn.close()
        
        return f"""
        <h1>数据库重新初始化完成</h1>
        <p style="color: green;">✅ 数据库重新初始化成功！</p>
        <p>薪资数据行数: {wage_count}</p>
        <p>地理数据行数: {geo_count}</p>
        <p>职业数据行数: {occ_count}</p>
        <p><a href="/debug">查看详细调试信息</a></p>
        <p><a href="/">返回主页测试搜索功能</a></p>
        """
    except Exception as e:
        return f"""
        <h1>数据库重新初始化失败</h1>
        <p style="color: red;">❌ 错误: {str(e)}</p>
        <p><a href="/debug">返回调试页面</a></p>
        <p><a href="/">返回主页</a></p>
        """

if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
    # 检查数据库是否为空
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM wage_data")
    wage_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM geography")
    geo_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM occupations")
    occ_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"数据库状态 - 薪资数据: {wage_count}, 地理数据: {geo_count}, 职业数据: {occ_count}")
    
    # 生产环境配置
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # 启动应用
    app.run(debug=debug, host='0.0.0.0', port=port)
