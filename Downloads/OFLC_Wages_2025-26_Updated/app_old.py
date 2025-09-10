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
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 读取CSV文件
    print("正在读取数据文件...")
    
    # 读取主要薪资数据
    alc_data = pd.read_csv('ALC_Export.csv')
    alc_data.columns = ['area', 'soc_code', 'geo_lvl', 'level1', 'level2', 'level3', 'level4', 'average', 'label']
    
    # 读取地理信息
    geo_data = pd.read_csv('Geography.csv')
    geo_data.columns = ['area', 'area_name', 'state_ab', 'state', 'county_town_name']
    
    # 读取职业信息
    occ_data = pd.read_csv('oes_soc_occs.csv')
    occ_data.columns = ['soc_code', 'title', 'description']
    
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

@app.route('/api/search/forward', methods=['POST'])
def forward_search():
    """正向查询：职位名称+地区 → Level 1-4薪资"""
    data = request.json
    position = data.get('position', '').strip()
    location = data.get('location', '').strip()
    
    if not position or not location:
        return jsonify({'error': '职位名称和地区不能为空'}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询匹配的职业
    cursor.execute('''
        SELECT DISTINCT soc_code, title 
        FROM occupations 
        WHERE title LIKE ? OR description LIKE ?
    ''', (f'%{position}%', f'%{position}%'))
    
    occupations = cursor.fetchall()
    
    if not occupations:
        conn.close()
        return jsonify({'error': '未找到匹配的职业'}), 404
    
    results = []
    
    for soc_code, title in occupations:
        # 查询地理信息
        cursor.execute('''
            SELECT DISTINCT g.area, g.area_name, g.state, g.county_town_name
            FROM geography g
            WHERE g.area_name LIKE ? OR g.state LIKE ? OR g.county_town_name LIKE ?
        ''', (f'%{location}%', f'%{location}%', f'%{location}%'))
        
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
                results.append({
                    'occupation': title,
                    'soc_code': soc_code,
                    'location': f"{area_name}, {state}",
                    'county': county_town,
                    'level1': level1,
                    'level2': level2,
                    'level3': level3,
                    'level4': level4,
                    'average': average,
                    'label': label
                })
    
    conn.close()
    
    if not results:
        return jsonify({'error': '未找到匹配的薪资数据'}), 404
    
    return jsonify({'results': results})

@app.route('/api/search/reverse', methods=['POST'])
def reverse_search():
    """反向查询：薪资范围+地区 → 符合条件的职位及level"""
    data = request.json
    min_salary = float(data.get('min_salary', 0))
    max_salary = float(data.get('max_salary', 0))
    location = data.get('location', '').strip()
    
    if not min_salary or not max_salary or not location:
        return jsonify({'error': '薪资范围和地区不能为空'}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询地理信息
    cursor.execute('''
        SELECT DISTINCT g.area, g.area_name, g.state, g.county_town_name
        FROM geography g
        WHERE g.area_name LIKE ? OR g.state LIKE ? OR g.county_town_name LIKE ?
    ''', (f'%{location}%', f'%{location}%', f'%{location}%'))
    
    locations = cursor.fetchall()
    
    if not locations:
        conn.close()
        return jsonify({'error': '未找到匹配的地区'}), 404
    
    results = []
    
    for area, area_name, state, county_town in locations:
        # 查询薪资数据
        cursor.execute('''
            SELECT w.soc_code, w.level1, w.level2, w.level3, w.level4, w.average, w.label,
                   o.title
            FROM wage_data w
            JOIN occupations o ON w.soc_code = o.soc_code
            WHERE w.area = ? AND (
                (w.level1 IS NOT NULL AND w.level1 >= ? AND w.level1 <= ?) OR
                (w.level2 IS NOT NULL AND w.level2 >= ? AND w.level2 <= ?) OR
                (w.level3 IS NOT NULL AND w.level3 >= ? AND w.level3 <= ?) OR
                (w.level4 IS NOT NULL AND w.level4 >= ? AND w.level4 <= ?)
            )
        ''', (area, min_salary, max_salary, min_salary, max_salary, 
              min_salary, max_salary, min_salary, max_salary))
        
        wage_data = cursor.fetchall()
        
        for soc_code, level1, level2, level3, level4, average, label, title in wage_data:
            # 确定哪个level符合薪资范围
            matching_levels = []
            if level1 and min_salary <= level1 <= max_salary:
                matching_levels.append({'level': 1, 'salary': level1})
            if level2 and min_salary <= level2 <= max_salary:
                matching_levels.append({'level': 2, 'salary': level2})
            if level3 and min_salary <= level3 <= max_salary:
                matching_levels.append({'level': 3, 'salary': level3})
            if level4 and min_salary <= level4 <= max_salary:
                matching_levels.append({'level': 4, 'salary': level4})
            
            if matching_levels:
                results.append({
                    'occupation': title,
                    'soc_code': soc_code,
                    'location': f"{area_name}, {state}",
                    'county': county_town,
                    'matching_levels': matching_levels,
                    'level1': level1,
                    'level2': level2,
                    'level3': level3,
                    'level4': level4,
                    'average': average,
                    'label': label
                })
    
    conn.close()
    
    if not results:
        return jsonify({'error': '未找到符合条件的薪资数据'}), 404
    
    return jsonify({'results': results})

@app.route('/api/search/location', methods=['POST'])
def location_search():
    """地区查询：职位和薪资水平 → 显示哪个州可以达到指定level的水平"""
    data = request.json
    position = data.get('position', '').strip()
    target_level = int(data.get('target_level', 2))
    target_salary = float(data.get('target_salary', 0))
    
    if not position or not target_level or not target_salary:
        return jsonify({'error': '职位名称、目标级别和目标薪资不能为空'}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询匹配的职业
    cursor.execute('''
        SELECT DISTINCT soc_code, title 
        FROM occupations 
        WHERE title LIKE ? OR description LIKE ?
    ''', (f'%{position}%', f'%{position}%'))
    
    occupations = cursor.fetchall()
    
    if not occupations:
        conn.close()
        return jsonify({'error': '未找到匹配的职业'}), 404
    
    results = []
    
    for soc_code, title in occupations:
        # 查询薪资数据
        level_column = f'level{target_level}'
        cursor.execute(f'''
            SELECT w.area, w.{level_column}, w.level1, w.level2, w.level3, w.level4, w.average, w.label,
                   g.area_name, g.state, g.county_town_name
            FROM wage_data w
            JOIN geography g ON w.area = g.area
            WHERE w.soc_code = ? AND w.{level_column} IS NOT NULL AND w.{level_column} >= ?
            ORDER BY w.{level_column} ASC
        ''', (soc_code, target_salary))
        
        wage_data = cursor.fetchall()
        
        for row in wage_data:
            area, target_level_salary, level1, level2, level3, level4, average, label, area_name, state, county_town = row
            results.append({
                'occupation': title,
                'soc_code': soc_code,
                'location': f"{area_name}, {state}",
                'county': county_town,
                'target_level': target_level,
                'target_level_salary': target_level_salary,
                'level1': level1,
                'level2': level2,
                'level3': level3,
                'level4': level4,
                'average': average,
                'label': label
            })
    
    conn.close()
    
    if not results:
        return jsonify({'error': '未找到符合条件的地区'}), 404
    
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

if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
    # 启动应用
    app.run(debug=True, host='0.0.0.0', port=5000)
